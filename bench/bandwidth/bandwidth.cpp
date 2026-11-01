// Memory bandwidth B(t) for the roofline (CLAUDE.md §8). One thread count per run.
//
//   taskset -c 0-<t-1> bandwidth --threads <t> [--kernel read|triad|both] [--reps 30]
//                                [--streams 1,2,4,8] [--hugepage]
//
// Two kernels:
//   read  - every thread sums its own slice of one big buffer of 64-bit integers with NEON loads.
//           Decode reads weights and writes almost nothing, so this is the roofline input.
//           With --streams k the thread splits its slice into k equal parts and each loop step
//           reads one 128-byte block from each part, so k sequential streams advance together
//           (ADR-017: one stream per core does not reach the memory limit). B(t) is the best
//           median over k; the k = 1 result is kept as the simple-sequential reference.
//           --hugepage (diagnostic only, never B(t)) asks for transparent huge pages with
//           madvise(MADV_HUGEPAGE) before the first touch and records how many were granted.
//   triad - STREAM-style a[i] = b[i] + s*c[i] on doubles, counted as 24 bytes per element (as
//           STREAM does; write-allocate traffic is not counted). Reported for comparison only.
//
// Thread i is pinned to core i (pthread_setaffinity_np, then checked with sched_getcpu()); the
// Python wrapper also runs the whole program under taskset so t = 1 is pinned the same way
// llama-bench will be. Every page is touched by the thread that later reads it, before timing.
// Each timed repetition is one start barrier, the kernel, one end barrier. Results are one JSON
// object on stdout; the exit code is non-zero if a checksum or a pin check failed.
//
// Build: g++ -O3 -mcpu=native -std=c++17 -fopenmp bandwidth.cpp -o bandwidth

#include <omp.h>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>
#include <unistd.h>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#if defined(__ARM_NEON)
#include <arm_neon.h>
#endif

// ---- read kernel ------------------------------------------------------------------------
// ACC independent vector accumulators, so the loop is limited by the loads and not by the
// latency of one chain of adds; K streams, each read 2 * ACC elements (128 bytes for ACC = 8)
// per loop step. n must be a multiple of K * 2 * ACC.
template <int ACC, int K>
static inline uint64_t read_slice_impl(const uint64_t* p, size_t n) {
    const size_t part = n / K;  // elements per stream
#if defined(__ARM_NEON)
    uint64x2_t acc[ACC];
    for (int a = 0; a < ACC; a++) acc[a] = vdupq_n_u64(0);
    for (size_t i = 0; i < part; i += 2 * ACC)
        for (int s = 0; s < K; s++)
            for (int a = 0; a < ACC; a++)
                acc[a] = vaddq_u64(acc[a], vld1q_u64(p + s * part + i + 2 * a));
    uint64x2_t sum = acc[0];
    for (int a = 1; a < ACC; a++) sum = vaddq_u64(sum, acc[a]);
    return vgetq_lane_u64(sum, 0) + vgetq_lane_u64(sum, 1);
#else  // portable fallback so the file also compiles off-target (not used for results)
    uint64_t acc[2 * ACC] = {0};
    for (size_t i = 0; i < part; i += 2 * ACC)
        for (int s = 0; s < K; s++)
            for (int a = 0; a < 2 * ACC; a++) acc[a] += p[s * part + i + a];
    uint64_t sum = 0;
    for (int a = 0; a < 2 * ACC; a++) sum += acc[a];
    return sum;
#endif
}

// Separate, named, never-inlined copies: the disassembly of read_slice_acc8_k1 is committed as
// evidence of what the timed loop really is. The (4,8,16)-accumulator copies at k = 1 and k = 8
// are for the accumulator check; k = 2 and 4 only exist with 8 accumulators.
#define READ_SLICE(ACC, K)                                                               \
    extern "C" __attribute__((noinline, noclone)) uint64_t read_slice_acc##ACC##_k##K(   \
        const uint64_t* p, size_t n) {                                                   \
        return read_slice_impl<ACC, K>(p, n);                                            \
    }
READ_SLICE(4, 1)
READ_SLICE(4, 8)
READ_SLICE(8, 1)
READ_SLICE(8, 2)
READ_SLICE(8, 4)
READ_SLICE(8, 8)
READ_SLICE(16, 1)
READ_SLICE(16, 8)

typedef uint64_t (*read_fn)(const uint64_t*, size_t);
static read_fn read_fn_for(int acc, int streams) {
#define PICK(A, K) \
    if (acc == A && streams == K) return read_slice_acc##A##_k##K
    PICK(4, 1);
    PICK(4, 8);
    PICK(8, 1);
    PICK(8, 2);
    PICK(8, 4);
    PICK(8, 8);
    PICK(16, 1);
    PICK(16, 8);
#undef PICK
    fprintf(stderr, "unsupported --acc %d with --streams %d\n", acc, streams);
    exit(2);
}

// ---- triad kernel -----------------------------------------------------------------------
extern "C" __attribute__((noinline, noclone)) void triad_slice(
    double* __restrict a, const double* __restrict b, const double* __restrict c, double s,
    size_t n) {
    for (size_t i = 0; i < n; i++) a[i] = b[i] + s * c[i];
}

// ---- harness ----------------------------------------------------------------------------
using clk = std::chrono::steady_clock;

struct Result {
    std::string kernel;
    int acc = 0;
    int streams = 0;         // read streams per thread; 0 for triad
    bool hugepage = false;   // madvise(MADV_HUGEPAGE) requested (diagnostic runs only)
    long anon_huge_kb = -1;  // AnonHugePages after the first touch, -1 if unreadable
    size_t buffer_bytes = 0, bytes_per_rep = 0;
    int warmup = 0, reps = 0;
    std::vector<double> samples;  // bytes/s
    bool checksum_ok = true, getcpu_ok = true;
    std::vector<int> cpus;  // core each thread was seen on
};

static void* alloc_pages(size_t bytes, bool hugepage = false) {
    void* p = nullptr;
    // 2 MiB alignment lets a transparent huge page cover the buffer from its first byte.
    if (posix_memalign(&p, hugepage ? (2u << 20) : 4096, bytes) != 0) {
        fprintf(stderr, "cannot allocate %zu bytes\n", bytes);
        exit(2);
    }
    if (hugepage) madvise(p, bytes, MADV_HUGEPAGE);  // advice only; the kernel may decline
    return p;
}

// AnonHugePages (kB) of this process, from /proc/self/smaps_rollup; -1 if it cannot be read.
static long anon_huge_kb() {
    FILE* f = fopen("/proc/self/smaps_rollup", "r");
    if (!f) return -1;
    char line[256];
    long kb = -1;
    while (fgets(line, sizeof line, f))
        if (sscanf(line, "AnonHugePages: %ld kB", &kb) == 1) break;
    fclose(f);
    return kb;
}

// Pin the calling thread to `core`; returns true if the kernel agrees afterwards.
static bool pin_to(int core) {
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core, &set);
    if (pthread_setaffinity_np(pthread_self(), sizeof(set), &set) != 0) return false;
    return sched_getcpu() == core;
}

static double secs(clk::time_point a, clk::time_point b) {
    return std::chrono::duration<double>(b - a).count();
}

static Result run_read(int t, size_t total_bytes, int warmup, int reps, int acc, int streams,
                       bool hugepage) {
    Result r;
    r.kernel = "read";
    r.acc = acc;
    r.streams = streams;
    r.hugepage = hugepage;
    r.warmup = warmup;
    r.reps = reps;
    r.cpus.assign(t, -1);
    read_fn fn = read_fn_for(acc, streams);

    size_t slice = (total_bytes / sizeof(uint64_t)) / t;
    slice -= slice % (32 * 8);  // each of up to 8 streams a multiple of 2 * the largest ACC
    const size_t m = slice * t;
    r.buffer_bytes = r.bytes_per_rep = m * sizeof(uint64_t);
    uint64_t* buf = (uint64_t*)alloc_pages(r.buffer_bytes, hugepage);
    // Element i holds i, so the sum of all of them is known: m*(m-1)/2. Every element is read
    // exactly once however the slice is split into streams, so the sum does not depend on k.
    const uint64_t expected = (uint64_t)(((unsigned __int128)m * (m - 1)) / 2);

    std::vector<uint64_t> partial(t, 0);
    std::vector<clk::time_point> start(t), end(t);
    std::vector<char> pin_ok(t, 1);

#pragma omp parallel num_threads(t)
    {
        const int tid = omp_get_thread_num();
        if (omp_get_num_threads() != t) pin_ok[tid] = 0;
        bool ok = pin_to(tid);
        // First touch by the thread that will read the slice.
        for (size_t i = 0; i < slice; i++) buf[tid * slice + i] = (uint64_t)tid * slice + i;
#pragma omp barrier
        if (tid == 0) r.anon_huge_kb = anon_huge_kb();
        for (int rep = -warmup; rep < reps; rep++) {
#pragma omp barrier
            start[tid] = clk::now();
            partial[tid] = fn(buf + tid * slice, slice);
            end[tid] = clk::now();
#pragma omp barrier
            if (tid == 0) {
                uint64_t sum = 0;
                for (int k = 0; k < t; k++) sum += partial[k];
                if (sum != expected) r.checksum_ok = false;
                if (rep >= 0) {
                    auto s0 = *std::min_element(start.begin(), start.end());
                    auto e1 = *std::max_element(end.begin(), end.end());
                    r.samples.push_back((double)r.bytes_per_rep / secs(s0, e1));
                }
            }
        }
        ok = ok && sched_getcpu() == tid;  // still where we were put
        r.cpus[tid] = sched_getcpu();
        if (!ok) pin_ok[tid] = 0;
    }
    for (int k = 0; k < t; k++)
        if (!pin_ok[k]) r.getcpu_ok = false;
    free(buf);
    return r;
}

static Result run_triad(int t, size_t array_bytes, int warmup, int reps) {
    Result r;
    r.kernel = "triad";
    r.acc = 0;
    r.warmup = warmup;
    r.reps = reps;
    r.cpus.assign(t, -1);

    size_t slice = (array_bytes / sizeof(double)) / t;
    slice -= slice % 8;
    const size_t m = slice * t;
    r.buffer_bytes = 3 * m * sizeof(double);
    r.bytes_per_rep = 24 * m;  // STREAM counting: 2 reads + 1 write of 8 bytes per element
    double* a = (double*)alloc_pages(m * sizeof(double));
    double* b = (double*)alloc_pages(m * sizeof(double));
    double* c = (double*)alloc_pages(m * sizeof(double));
    const double s = 3.0;  // a = 2.0 + 3.0 * 0.5 = 3.5; every value is exact in binary
    std::vector<double> partial(t, 0.0);
    std::vector<clk::time_point> start(t), end(t);
    std::vector<char> pin_ok(t, 1);

#pragma omp parallel num_threads(t)
    {
        const int tid = omp_get_thread_num();
        if (omp_get_num_threads() != t) pin_ok[tid] = 0;
        bool ok = pin_to(tid);
        for (size_t i = 0; i < slice; i++) {
            a[tid * slice + i] = 0.0;
            b[tid * slice + i] = 2.0;
            c[tid * slice + i] = 0.5;
        }
#pragma omp barrier
        for (int rep = -warmup; rep < reps; rep++) {
#pragma omp barrier
            start[tid] = clk::now();
            triad_slice(a + tid * slice, b + tid * slice, c + tid * slice, s, slice);
            end[tid] = clk::now();
#pragma omp barrier
            if (tid == 0 && rep >= 0) {
                auto s0 = *std::min_element(start.begin(), start.end());
                auto e1 = *std::max_element(end.begin(), end.end());
                r.samples.push_back((double)r.bytes_per_rep / secs(s0, e1));
            }
        }
        ok = ok && sched_getcpu() == tid;
        r.cpus[tid] = sched_getcpu();
        if (!ok) pin_ok[tid] = 0;
        // Untimed check that the triad really wrote a = 3.5 everywhere.
        double sum = 0;
        for (size_t i = 0; i < slice; i++) sum += a[tid * slice + i];
        partial[tid] = sum;
    }
    double total = 0;
    for (int k = 0; k < t; k++) total += partial[k];
    r.checksum_ok = (total == 3.5 * (double)m);
    for (int k = 0; k < t; k++)
        if (!pin_ok[k]) r.getcpu_ok = false;
    free(a);
    free(b);
    free(c);
    return r;
}

static void print_result(const Result& r, bool last) {
    printf("    {\"kernel\": \"%s\", \"acc\": %d, \"streams\": %d, \"hugepage\": %s, "
           "\"anon_huge_kb\": %ld, \"buffer_bytes\": %zu, \"bytes_per_rep\": %zu, "
           "\"reps_warmup\": %d, \"reps_timed\": %d, \"checksum_ok\": %s, \"getcpu_ok\": %s,\n",
           r.kernel.c_str(), r.acc, r.streams, r.hugepage ? "true" : "false", r.anon_huge_kb,
           r.buffer_bytes, r.bytes_per_rep, r.warmup, r.reps, r.checksum_ok ? "true" : "false",
           r.getcpu_ok ? "true" : "false");
    printf("     \"observed_cpus\": [");
    for (size_t i = 0; i < r.cpus.size(); i++) printf("%s%d", i ? ", " : "", r.cpus[i]);
    printf("],\n     \"samples_bytes_per_s\": [");
    for (size_t i = 0; i < r.samples.size(); i++) printf("%s%.1f", i ? ", " : "", r.samples[i]);
    printf("]}%s\n", last ? "" : ",");
}

static std::vector<int> parse_int_list(const std::string& s) {
    std::vector<int> out;
    size_t pos = 0;
    while (pos <= s.size()) {
        size_t comma = s.find(',', pos);
        if (comma == std::string::npos) comma = s.size();
        if (comma > pos) out.push_back(atoi(s.substr(pos, comma - pos).c_str()));
        pos = comma + 1;
    }
    return out;
}

int main(int argc, char** argv) {
    // The CPU set the process was started with (taskset). Read it first: the threads below
    // pin themselves, and a read after that would show one core (Day 2 recording bug).
    cpu_set_t allowed;
    CPU_ZERO(&allowed);
    sched_getaffinity(0, sizeof(allowed), &allowed);

    int threads = 1, reps = 30, warmup = 3, acc = 8;
    size_t read_mib = 1024, triad_mib = 512;  // 1 GiB read buffer; 3 x 512 MiB for triad
    std::string kernel = "both";
    std::vector<int> streams = {1};
    bool acc_check = false, hugepage = false;
    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        auto next = [&]() -> const char* {
            if (i + 1 >= argc) { fprintf(stderr, "%s needs a value\n", a.c_str()); exit(2); }
            return argv[++i];
        };
        if (a == "--threads") threads = atoi(next());
        else if (a == "--kernel") kernel = next();
        else if (a == "--reps") reps = atoi(next());
        else if (a == "--warmup") warmup = atoi(next());
        else if (a == "--acc") acc = atoi(next());
        else if (a == "--streams") streams = parse_int_list(next());
        else if (a == "--hugepage") hugepage = true;
        else if (a == "--read-mib") read_mib = atoll(next());
        else if (a == "--triad-mib") triad_mib = atoll(next());
        else if (a == "--small") { read_mib = 16; triad_mib = 8; }  // for unit tests only
        else if (a == "--acc-check") acc_check = true;
        else { fprintf(stderr, "unknown argument %s\n", a.c_str()); return 2; }
    }
    if (threads < 1 || reps < 1 || streams.empty()) {
        fprintf(stderr, "bad --threads/--reps/--streams\n");
        return 2;
    }
    omp_set_dynamic(0);

    std::vector<Result> results;
    if (acc_check) {  // read kernel with 4, 8 and 16 accumulators, at each requested stream count
        for (int k : streams)
            for (int a : {4, 8, 16})
                if (!(k != 1 && k != 8 && a != 8))
                    results.push_back(run_read(threads, read_mib << 20, warmup, reps, a, k, false));
    } else {
        if (kernel == "read" || kernel == "both")
            for (int k : streams)
                results.push_back(run_read(threads, read_mib << 20, warmup, reps, acc, k, hugepage));
        if ((kernel == "triad" || kernel == "both") && !hugepage)
            results.push_back(run_triad(threads, triad_mib << 20, warmup, reps));
    }

    printf("{\n  \"program\": \"bandwidth\", \"threads\": %d, \"process_cpus\": [", threads);
    bool first = true;
    for (int c = 0; c < CPU_SETSIZE; c++)
        if (CPU_ISSET(c, &allowed)) { printf("%s%d", first ? "" : ", ", c); first = false; }
    printf("],\n  \"results\": [\n");
    bool ok = true;
    for (size_t i = 0; i < results.size(); i++) {
        print_result(results[i], i + 1 == results.size());
        ok = ok && results[i].checksum_ok && results[i].getcpu_ok;
    }
    printf("  ]\n}\n");
    return ok ? 0 : 3;
}

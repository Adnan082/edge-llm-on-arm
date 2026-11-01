// Memory bandwidth B(t) for the roofline (CLAUDE.md §8). One thread count per run.
//
//   taskset -c 0-<t-1> bandwidth --threads <t> [--kernel read|triad|both] [--reps 30]
//
// Two kernels:
//   read  - every thread sums its own slice of one big buffer of 64-bit integers with NEON loads.
//           Decode reads weights and writes almost nothing, so this is the roofline input.
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
// latency of one chain of adds. n must be a multiple of 2 * ACC.
template <int ACC>
static inline uint64_t read_slice_impl(const uint64_t* p, size_t n) {
#if defined(__ARM_NEON)
    uint64x2_t acc[ACC];
    for (int a = 0; a < ACC; a++) acc[a] = vdupq_n_u64(0);
    for (size_t i = 0; i < n; i += 2 * ACC)
        for (int a = 0; a < ACC; a++) acc[a] = vaddq_u64(acc[a], vld1q_u64(p + i + 2 * a));
    uint64x2_t s = acc[0];
    for (int a = 1; a < ACC; a++) s = vaddq_u64(s, acc[a]);
    return vgetq_lane_u64(s, 0) + vgetq_lane_u64(s, 1);
#else  // portable fallback so the file also compiles off-target (not used for results)
    uint64_t acc[2 * ACC] = {0};
    for (size_t i = 0; i < n; i += 2 * ACC)
        for (int a = 0; a < 2 * ACC; a++) acc[a] += p[i + a];
    uint64_t s = 0;
    for (int a = 0; a < 2 * ACC; a++) s += acc[a];
    return s;
#endif
}

// Separate, named, never-inlined copies: the disassembly of read_slice_acc8 is committed as
// evidence of what the timed loop really is.
#define READ_SLICE(ACC)                                                                  \
    extern "C" __attribute__((noinline, noclone)) uint64_t read_slice_acc##ACC(          \
        const uint64_t* p, size_t n) {                                                   \
        return read_slice_impl<ACC>(p, n);                                               \
    }
READ_SLICE(4)
READ_SLICE(8)
READ_SLICE(16)

typedef uint64_t (*read_fn)(const uint64_t*, size_t);
static read_fn read_fn_for(int acc) {
    switch (acc) {
        case 4: return read_slice_acc4;
        case 8: return read_slice_acc8;
        case 16: return read_slice_acc16;
    }
    fprintf(stderr, "--acc must be 4, 8 or 16\n");
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
    size_t buffer_bytes = 0, bytes_per_rep = 0;
    int warmup = 0, reps = 0;
    std::vector<double> samples;  // bytes/s
    bool checksum_ok = true, getcpu_ok = true;
    std::vector<int> cpus;  // core each thread was seen on
};

static void* alloc_pages(size_t bytes) {
    void* p = nullptr;
    if (posix_memalign(&p, 4096, bytes) != 0) {
        fprintf(stderr, "cannot allocate %zu bytes\n", bytes);
        exit(2);
    }
    return p;
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

static Result run_read(int t, size_t total_bytes, int warmup, int reps, int acc) {
    Result r;
    r.kernel = "read";
    r.acc = acc;
    r.warmup = warmup;
    r.reps = reps;
    r.cpus.assign(t, -1);
    read_fn fn = read_fn_for(acc);

    size_t slice = (total_bytes / sizeof(uint64_t)) / t;
    slice -= slice % 32;  // multiple of 2 * the largest ACC
    const size_t m = slice * t;
    r.buffer_bytes = r.bytes_per_rep = m * sizeof(uint64_t);
    uint64_t* buf = (uint64_t*)alloc_pages(r.buffer_bytes);
    // Element i holds i, so the sum of all of them is known: m*(m-1)/2.
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
    printf("    {\"kernel\": \"%s\", \"acc\": %d, \"buffer_bytes\": %zu, \"bytes_per_rep\": %zu, "
           "\"reps_warmup\": %d, \"reps_timed\": %d, \"checksum_ok\": %s, \"getcpu_ok\": %s,\n",
           r.kernel.c_str(), r.acc, r.buffer_bytes, r.bytes_per_rep, r.warmup, r.reps,
           r.checksum_ok ? "true" : "false", r.getcpu_ok ? "true" : "false");
    printf("     \"observed_cpus\": [");
    for (size_t i = 0; i < r.cpus.size(); i++) printf("%s%d", i ? ", " : "", r.cpus[i]);
    printf("],\n     \"samples_bytes_per_s\": [");
    for (size_t i = 0; i < r.samples.size(); i++) printf("%s%.1f", i ? ", " : "", r.samples[i]);
    printf("]}%s\n", last ? "" : ",");
}

int main(int argc, char** argv) {
    int threads = 1, reps = 30, warmup = 3, acc = 8;
    size_t read_mib = 1024, triad_mib = 512;  // 1 GiB read buffer; 3 x 512 MiB for triad
    std::string kernel = "both";
    bool acc_check = false;
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
        else if (a == "--read-mib") read_mib = atoll(next());
        else if (a == "--triad-mib") triad_mib = atoll(next());
        else if (a == "--small") { read_mib = 16; triad_mib = 8; }  // for unit tests only
        else if (a == "--acc-check") acc_check = true;
        else { fprintf(stderr, "unknown argument %s\n", a.c_str()); return 2; }
    }
    if (threads < 1 || reps < 1) { fprintf(stderr, "bad --threads/--reps\n"); return 2; }
    omp_set_dynamic(0);

    std::vector<Result> results;
    if (acc_check) {  // read kernel with 4, 8 and 16 accumulators at the given thread count
        for (int a : {4, 8, 16}) results.push_back(run_read(threads, read_mib << 20, warmup, reps, a));
    } else {
        if (kernel == "read" || kernel == "both")
            results.push_back(run_read(threads, read_mib << 20, warmup, reps, acc));
        if (kernel == "triad" || kernel == "both")
            results.push_back(run_triad(threads, triad_mib << 20, warmup, reps));
    }

    cpu_set_t allowed;
    CPU_ZERO(&allowed);
    sched_getaffinity(0, sizeof(allowed), &allowed);
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

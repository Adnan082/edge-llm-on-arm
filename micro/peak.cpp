// Peak instruction throughput C(t) for the roofline (CLAUDE.md §8, ADR-015). One thread count
// per run.
//
//   taskset -c 0-<t-1> peak --threads <t> [--classes sdot,smmla,fmla_f16,fmlal,fma32]
//                           [--acc 16 | --acc 8,16,28] [--reps 20] [--target-ms 100]
//
// Each class is a loop of independent instructions on registers only (no loads, stores or
// memory in the loop): the number of dependency chains is the "accumulators" count, so a loop
// with more chains than latency x pipes keeps every pipe busy. The program reports instructions
// per second summed over threads; Python multiplies by the operations per instruction (one
// multiply-accumulate = 2 operations; the constants live in src/edge_llm/peak.py, once).
//
//   sdot      NEON SDOT   (vdotq_s32)            16 int8 MACs per instruction
//   smmla     NEON SMMLA  (vmmlaq_s32)           2x8 times 8x2 int8 = 32 MACs per instruction
//   fmla_f16  NEON FP16 FMLA (vfmaq_f16)         8 half-precision MACs per instruction
//   fma32     NEON F32 FMLA (vfmaq_f32)          4 single-precision MACs per instruction; the
//             ceiling for attention, which ggml computes in F32 (ADR-020)
//   fmlal     SVE2 FMLALB / FMLALT (svmlalb_f32 / svmlalt_f32, as ggml's vec.h uses): FP16 inputs,
//             FP32 accumulate, 4 MACs per 128 bits per instruction; half the chains use the
//             bottom form, half the top form
//
// Thread i is pinned to core i like every measured program (ADR-014). The hot loops are named,
// never inlined and unrolled by hand only: micro/run_peak.py disassembles each one and checks
// that the expected instruction (and nothing but loop overhead) is in the loop.
//
// Build: g++ -O3 -mcpu=native -std=c++17 -fopenmp peak.cpp -o peak

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
#if defined(__ARM_FEATURE_SVE2)
#include <arm_sve.h>
#endif

// Operand seeds come from memory the compiler cannot see through, so no loop can be folded.
static volatile int8_t g_i8[4] = {3, -5, 7, 11};
static volatile float g_f[4] = {0.5f, 0.25f, 1.0f, 2.0f};

// Lists of accumulator indices; a macro, not an array, because SVE vectors cannot be array
// elements. FE<N>(M) expands to M(0) M(1) ... M(N-1).
#define FE8(M) M(0) M(1) M(2) M(3) M(4) M(5) M(6) M(7)
#define FE16(M) FE8(M) M(8) M(9) M(10) M(11) M(12) M(13) M(14) M(15)
#define FE28(M) FE16(M) M(16) M(17) M(18) M(19) M(20) M(21) M(22) M(23) M(24) M(25) M(26) M(27)

struct Kernel {
    const char* cls;
    int accumulators;
    int instr_per_iter;  // instructions of the class executed by one loop iteration
    uint64_t (*fn)(uint64_t iters);
};
static std::vector<Kernel> g_kernels;

#if defined(__ARM_NEON)

// ---- SDOT ---------------------------------------------------------------------------------
#define SDOT_DECL(i) int32x4_t s##i = vdupq_n_s32(i + 1);
#define SDOT_STEP(i) s##i = vdotq_s32(s##i, x, y);
#define SDOT_SUM(i) tot = vaddq_s32(tot, s##i);
#define DEFINE_SDOT(A, FE)                                                               \
    extern "C" __attribute__((noinline, noclone)) uint64_t peak_sdot_a##A(uint64_t iters) { \
        const int8x16_t x = vdupq_n_s8(g_i8[0]), y = vdupq_n_s8(g_i8[1]);                 \
        FE(SDOT_DECL)                                                                      \
        _Pragma("GCC unroll 1") for (uint64_t it = 0; it < iters; it++) { FE(SDOT_STEP) }  \
        int32x4_t tot = vdupq_n_s32(0);                                                    \
        FE(SDOT_SUM)                                                                       \
        return (uint32_t)vaddvq_s32(tot);                                                  \
    }
DEFINE_SDOT(8, FE8)
DEFINE_SDOT(16, FE16)
DEFINE_SDOT(28, FE28)

// ---- SMMLA --------------------------------------------------------------------------------
#if defined(__ARM_FEATURE_MATMUL_INT8)
#define SMMLA_STEP(i) s##i = vmmlaq_s32(s##i, x, y);
#define DEFINE_SMMLA(A, FE)                                                                 \
    extern "C" __attribute__((noinline, noclone)) uint64_t peak_smmla_a##A(uint64_t iters) { \
        const int8x16_t x = vdupq_n_s8(g_i8[2]), y = vdupq_n_s8(g_i8[3]);                  \
        FE(SDOT_DECL)                                                                       \
        _Pragma("GCC unroll 1") for (uint64_t it = 0; it < iters; it++) { FE(SMMLA_STEP) }  \
        int32x4_t tot = vdupq_n_s32(0);                                                     \
        FE(SDOT_SUM)                                                                        \
        return (uint32_t)vaddvq_s32(tot);                                                   \
    }
DEFINE_SMMLA(8, FE8)
DEFINE_SMMLA(16, FE16)
DEFINE_SMMLA(28, FE28)
#endif

// ---- FP16 FMLA ----------------------------------------------------------------------------
// Each chain adds x*y and then -x*y so the half-precision accumulators stay finite for any
// number of iterations; that makes two instructions per chain per loop iteration.
#if defined(__ARM_FEATURE_FP16_VECTOR_ARITHMETIC)
#define HFMA_DECL(i) float16x8_t h##i = vdupq_n_f16((float16_t)0.0f);
#define HFMA_STEP(i) h##i = vfmaq_f16(h##i, x, y); h##i = vfmaq_f16(h##i, x, ny);
#define HFMA_SUM(i)                                                         \
    tot = vaddq_f32(tot, vcvt_f32_f16(vget_low_f16(h##i)));                 \
    tot = vaddq_f32(tot, vcvt_high_f32_f16(h##i));
#define DEFINE_HFMA(A, FE)                                                                  \
    extern "C" __attribute__((noinline, noclone)) uint64_t peak_fmla_f16_a##A(uint64_t iters) { \
        const float16x8_t x = vdupq_n_f16((float16_t)g_f[0]);                              \
        const float16x8_t y = vdupq_n_f16((float16_t)g_f[1]);                              \
        const float16x8_t ny = vnegq_f16(y);                                               \
        FE(HFMA_DECL)                                                                       \
        _Pragma("GCC unroll 1") for (uint64_t it = 0; it < iters; it++) { FE(HFMA_STEP) }   \
        float32x4_t tot = vdupq_n_f32(0.0f);                                                \
        FE(HFMA_SUM)                                                                        \
        float sum = vaddvq_f32(tot);                                                        \
        uint32_t bits;                                                                      \
        memcpy(&bits, &sum, sizeof bits);                                                   \
        return bits;                                                                        \
    }
DEFINE_HFMA(8, FE8)
DEFINE_HFMA(16, FE16)
DEFINE_HFMA(28, FE28)
#endif

// ---- F32 FMLA -----------------------------------------------------------------------------
// One instruction per chain per loop iteration. Each chain adds x*y = 0.125 per iteration, so
// the sums stay finite for any iteration count a repetition can reach (they stop growing at 2^24).
#define F32_DECL(i) float32x4_t w##i = vdupq_n_f32(0.0f);
#define F32_STEP(i) w##i = vfmaq_f32(w##i, x, y);
#define F32_SUM(i) tot = vaddq_f32(tot, w##i);
#define DEFINE_FMA32(A, FE)                                                                   \
    extern "C" __attribute__((noinline, noclone)) uint64_t peak_fma32_a##A(uint64_t iters) {  \
        const float32x4_t x = vdupq_n_f32(g_f[0]), y = vdupq_n_f32(g_f[1]);                  \
        FE(F32_DECL)                                                                          \
        _Pragma("GCC unroll 1") for (uint64_t it = 0; it < iters; it++) { FE(F32_STEP) }      \
        float32x4_t tot = vdupq_n_f32(0.0f);                                                  \
        FE(F32_SUM)                                                                           \
        float sum = vaddvq_f32(tot);                                                          \
        uint32_t bits;                                                                        \
        memcpy(&bits, &sum, sizeof bits);                                                     \
        return bits;                                                                          \
    }
DEFINE_FMA32(8, FE8)
DEFINE_FMA32(16, FE16)
DEFINE_FMA32(28, FE28)

#endif  // __ARM_NEON

// ---- SVE2 FMLALB / FMLALT ------------------------------------------------------------------
// Even-numbered chains use FMLALB, odd-numbered ones FMLALT: one instruction per chain per loop
// iteration, half of each kind, as ggml's decode dot product issues them.
#if defined(__ARM_FEATURE_SVE2)
#define LAL_DECL(i) svfloat32_t f##i = svdup_n_f32(0.0f);
#define LAL_STEP(i) f##i = ((i) % 2 == 0) ? svmlalb_f32(f##i, x, y) : svmlalt_f32(f##i, x, y);
#define LAL_SUM(i) tot = svadd_f32_x(pg32, tot, f##i);
#define DEFINE_LAL(A, FE)                                                                   \
    extern "C" __attribute__((noinline, noclone)) uint64_t peak_fmlal_a##A(uint64_t iters) { \
        const svbool_t pg16 = svptrue_b16(), pg32 = svptrue_b32();                          \
        const svfloat16_t x = svdup_n_f16((float16_t)g_f[0]);                               \
        const svfloat16_t y = svdup_n_f16((float16_t)g_f[1]);                               \
        (void)pg16;                                                                         \
        FE(LAL_DECL)                                                                        \
        _Pragma("GCC unroll 1") for (uint64_t it = 0; it < iters; it++) { FE(LAL_STEP) }    \
        svfloat32_t tot = svdup_n_f32(0.0f);                                                \
        FE(LAL_SUM)                                                                         \
        float sum = svaddv_f32(pg32, tot);                                                  \
        uint32_t bits;                                                                      \
        memcpy(&bits, &sum, sizeof bits);                                                   \
        return bits;                                                                        \
    }
DEFINE_LAL(8, FE8)
DEFINE_LAL(16, FE16)
DEFINE_LAL(28, FE28)
#endif

static void register_kernels() {
#if defined(__ARM_NEON)
    g_kernels.push_back({"sdot", 8, 8, peak_sdot_a8});
    g_kernels.push_back({"sdot", 16, 16, peak_sdot_a16});
    g_kernels.push_back({"sdot", 28, 28, peak_sdot_a28});
#if defined(__ARM_FEATURE_MATMUL_INT8)
    g_kernels.push_back({"smmla", 8, 8, peak_smmla_a8});
    g_kernels.push_back({"smmla", 16, 16, peak_smmla_a16});
    g_kernels.push_back({"smmla", 28, 28, peak_smmla_a28});
#endif
#if defined(__ARM_FEATURE_FP16_VECTOR_ARITHMETIC)
    g_kernels.push_back({"fmla_f16", 8, 16, peak_fmla_f16_a8});
    g_kernels.push_back({"fmla_f16", 16, 32, peak_fmla_f16_a16});
    g_kernels.push_back({"fmla_f16", 28, 56, peak_fmla_f16_a28});
#endif
    g_kernels.push_back({"fma32", 8, 8, peak_fma32_a8});
    g_kernels.push_back({"fma32", 16, 16, peak_fma32_a16});
    g_kernels.push_back({"fma32", 28, 28, peak_fma32_a28});
#endif
#if defined(__ARM_FEATURE_SVE2)
    g_kernels.push_back({"fmlal", 8, 8, peak_fmlal_a8});
    g_kernels.push_back({"fmlal", 16, 16, peak_fmlal_a16});
    g_kernels.push_back({"fmlal", 28, 28, peak_fmlal_a28});
#endif
}

// ---- harness ------------------------------------------------------------------------------
using clk = std::chrono::steady_clock;

struct Result {
    std::string cls;
    int accumulators = 0, instr_per_iter = 0;
    uint64_t iters = 0;
    int warmup = 0, reps = 0;
    std::vector<double> samples;  // instructions/s, summed over threads
    uint64_t checksum = 0;
    bool getcpu_ok = true;
    std::vector<int> cpus;
};

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

// Iterations that make one repetition last about `target_ms` on one core.
static uint64_t calibrate(const Kernel& k, double target_ms) {
    uint64_t iters = 1 << 14;
    for (;;) {
        auto t0 = clk::now();
        volatile uint64_t sink = k.fn(iters);
        (void)sink;
        double ms = 1e3 * secs(t0, clk::now());
        if (ms >= 5.0) return std::max<uint64_t>(1, (uint64_t)(iters * (target_ms / ms)));
        iters *= 4;
    }
}

static Result run_kernel(const Kernel& k, int t, int warmup, int reps, double target_ms) {
    Result r;
    r.cls = k.cls;
    r.accumulators = k.accumulators;
    r.instr_per_iter = k.instr_per_iter;
    r.warmup = warmup;
    r.reps = reps;
    r.cpus.assign(t, -1);
    pin_to(0);
    r.iters = calibrate(k, target_ms);

    std::vector<uint64_t> partial(t, 0);
    std::vector<clk::time_point> start(t), end(t);
    std::vector<char> pin_ok(t, 1);
    const double instr_per_rep = (double)t * k.instr_per_iter * (double)r.iters;

#pragma omp parallel num_threads(t)
    {
        const int tid = omp_get_thread_num();
        if (omp_get_num_threads() != t) pin_ok[tid] = 0;
        bool ok = pin_to(tid);
        for (int rep = -warmup; rep < reps; rep++) {
#pragma omp barrier
            start[tid] = clk::now();
            partial[tid] = k.fn(r.iters);  // every result is stored, then printed
            end[tid] = clk::now();
#pragma omp barrier
            if (tid == 0 && rep >= 0) {
                auto s0 = *std::min_element(start.begin(), start.end());
                auto e1 = *std::max_element(end.begin(), end.end());
                r.samples.push_back(instr_per_rep / secs(s0, e1));
            }
        }
        ok = ok && sched_getcpu() == tid;
        r.cpus[tid] = sched_getcpu();
        if (!ok) pin_ok[tid] = 0;
    }
    for (int i = 0; i < t; i++) {
        if (!pin_ok[i]) r.getcpu_ok = false;
        r.checksum ^= partial[i] + 0x9e3779b97f4a7c15ULL * (uint64_t)(i + 1);
    }
    return r;
}

static void print_result(const Result& r, bool last) {
    printf("    {\"class\": \"%s\", \"accumulators\": %d, \"instr_per_iter\": %d, \"iters\": %llu, "
           "\"reps_warmup\": %d, \"reps_timed\": %d, \"getcpu_ok\": %s, \"checksum\": \"0x%016llx\",\n",
           r.cls.c_str(), r.accumulators, r.instr_per_iter, (unsigned long long)r.iters, r.warmup,
           r.reps, r.getcpu_ok ? "true" : "false", (unsigned long long)r.checksum);
    printf("     \"observed_cpus\": [");
    for (size_t i = 0; i < r.cpus.size(); i++) printf("%s%d", i ? ", " : "", r.cpus[i]);
    printf("],\n     \"samples_instr_per_s\": [");
    for (size_t i = 0; i < r.samples.size(); i++) printf("%s%.1f", i ? ", " : "", r.samples[i]);
    printf("]}%s\n", last ? "" : ",");
}

static std::vector<std::string> split(const std::string& s) {
    std::vector<std::string> out;
    size_t pos = 0;
    while (pos <= s.size()) {
        size_t comma = s.find(',', pos);
        if (comma == std::string::npos) comma = s.size();
        if (comma > pos) out.push_back(s.substr(pos, comma - pos));
        pos = comma + 1;
    }
    return out;
}

int main(int argc, char** argv) {
    // The CPU set the process started with, read before any thread pins itself.
    cpu_set_t allowed;
    CPU_ZERO(&allowed);
    sched_getaffinity(0, sizeof(allowed), &allowed);

    int threads = 1, reps = 20, warmup = 3;
    double target_ms = 100.0;
    std::string classes = "sdot,smmla,fmla_f16,fmlal,fma32", accs = "16";
    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        auto next = [&]() -> const char* {
            if (i + 1 >= argc) { fprintf(stderr, "%s needs a value\n", a.c_str()); exit(2); }
            return argv[++i];
        };
        if (a == "--threads") threads = atoi(next());
        else if (a == "--classes") classes = next();
        else if (a == "--acc") accs = next();
        else if (a == "--reps") reps = atoi(next());
        else if (a == "--warmup") warmup = atoi(next());
        else if (a == "--target-ms") target_ms = atof(next());
        else if (a == "--small") target_ms = 5.0;  // for unit tests only
        else { fprintf(stderr, "unknown argument %s\n", a.c_str()); return 2; }
    }
    if (threads < 1 || reps < 1) { fprintf(stderr, "bad --threads/--reps\n"); return 2; }
    omp_set_dynamic(0);
    register_kernels();

    int sve_bits = 0;
#if defined(__ARM_FEATURE_SVE)
    sve_bits = (int)(svcntb() * 8);
#endif

    std::vector<Result> results;
    for (const std::string& cls : split(classes)) {
        bool found = false;
        for (const std::string& acc : split(accs))
            for (const Kernel& k : g_kernels)
                if (cls == k.cls && k.accumulators == atoi(acc.c_str())) {
                    found = true;
                    results.push_back(run_kernel(k, threads, warmup, reps, target_ms));
                }
        if (!found) {
            fprintf(stderr, "class %s with --acc %s is not available in this build\n", cls.c_str(),
                    accs.c_str());
            return 2;
        }
    }

    printf("{\n  \"program\": \"peak\", \"threads\": %d, \"sve_vector_bits\": %d, \"process_cpus\": [",
           threads, sve_bits);
    bool first = true;
    for (int c = 0; c < CPU_SETSIZE; c++)
        if (CPU_ISSET(c, &allowed)) { printf("%s%d", first ? "" : ", ", c); first = false; }
    printf("],\n  \"results\": [\n");
    bool ok = true;
    for (size_t i = 0; i < results.size(); i++) {
        print_result(results[i], i + 1 == results.size());
        ok = ok && results[i].getcpu_ok;
    }
    printf("  ]\n}\n");
    return ok ? 0 : 3;
}

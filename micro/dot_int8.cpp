// RQ4: a decode-shaped int8 matrix-vector product in five instruction variants (CLAUDE.md §5, §9).
//
//   y[m] = sum_k W[m][k] * x[k]      W: M rows x K int8, x: K int8, y: M int32, K = 4096
//
// Variants (the scalar and auto-vectorised ones live in dot_int8_ref.cpp, compiled twice):
//   scalar     plain C, auto-vectorisation off
//   autovec    the same C loop, plain -O3; GCC picks the instructions (that is a finding)
//   sdot_aN    NEON SDOT (vdotq_s32), 16 int8 MACs per instruction, N independent accumulators
//   smmla_aN   i8mm SMMLA (vmmlaq_s32) on a 2-row tile: 2x8 weights times 8x2 activations, so it
//              needs TWO activation vectors (like prefill with 2 tokens). It does 32 MACs per
//              instruction and twice the MACs per weight byte of the other variants
//   sve_aN     SVE SDOT (svdot_s32) with svld1_s8; vector length read at run time (svcntb())
// N is 4 or 8: both are kept as variants and the best is reported, as for the peak chains (ADR-022).
//
// Two working sets, one core (thread 0 on core 0, ADR-014; run under `taskset -c 0`):
//   L1    M = 4 rows,       W = 16 KiB   (fits the 64 KiB L1d; the call is repeated until a
//                                         timed repetition lasts >= 10 ms)
//   DRAM  M = 262144 rows,  W = 1 GiB    (at least 4x the 80 MiB L3)
//
//   dot_int8 --check [--seeds 6]
//       every variant against the scalar one on random and extreme (-128 / 127) inputs, bit for
//       bit; SMMLA against a scalar reference for two vectors. Exit 1 on any difference.
//   dot_int8 --time [--sets L1,DRAM] [--variants all|a,b] [--reps 30] [--warmup 3]
//                   [--target-ms 25] [--dram-mib 1024]
//       times the variants; each timed output is compared with scalar's too. Prints JSON.
//
// The hot loops are named, never inlined, and not unrolled by the compiler (`GCC unroll 1`):
// micro/run_micro.py disassembles each one and checks that the expected instruction is in it.
//
// Build (micro/run_micro.py does it): g++ -O3 -mcpu=native -std=c++17 dot_int8.cpp scalar.o autovec.o

#include <pthread.h>
#include <sched.h>
#include <unistd.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#if defined(__ARM_NEON)
#include <arm_neon.h>
#endif
#if defined(__ARM_FEATURE_SVE)
#include <arm_sve.h>
#endif

// Defined in dot_int8_ref.cpp (two builds of the same loop).
extern "C" {
void dot_scalar(const int8_t* W, const int8_t* x, int32_t* y, int64_t M, int64_t K);
void dot_autovec(const int8_t* W, const int8_t* x, int32_t* y, int64_t M, int64_t K);
}

// Every kernel has this shape. For SMMLA the arguments are the packed weights, the packed pair of
// activation vectors, the output (4 int32 per row pair) and the number of row PAIRS.
using KernelFn = void (*)(const int8_t*, const int8_t*, int32_t*, int64_t, int64_t);

// Lists of accumulator indices (a macro, not an array: SVE vectors cannot be array elements).
#define FE4(M) M(0) M(1) M(2) M(3)
#define FE8(M) FE4(M) M(4) M(5) M(6) M(7)

#if defined(__ARM_NEON)
// Accumulator declaration and final sum, shared by the SDOT and SMMLA kernels.
#define SD_DECL(i) int32x4_t s##i = vdupq_n_s32(0);
#define SD_SUM(i) tot = vaddq_s32(tot, s##i);
#endif

#if defined(__ARM_NEON) && defined(__ARM_FEATURE_DOTPROD)
// ---- NEON SDOT ----------------------------------------------------------------------------
// One row at a time: N accumulators, each fed by its own 16-byte slice of the row, so N SDOTs are
// in flight; the accumulators are added and reduced once per row.
#define SD_STEP(i) s##i = vdotq_s32(s##i, vld1q_s8(w + k + 16 * (i)), vld1q_s8(x + k + 16 * (i)));
#define DEFINE_SDOT(A, FE)                                                                      \
    extern "C" __attribute__((noinline, noclone)) void dot_sdot_a##A(                           \
        const int8_t* __restrict W, const int8_t* __restrict x, int32_t* __restrict y,         \
        int64_t M, int64_t K) {                                                                 \
        for (int64_t m = 0; m < M; m++) {                                                       \
            const int8_t* w = W + m * K;                                                        \
            FE(SD_DECL)                                                                         \
            _Pragma("GCC unroll 1") for (int64_t k = 0; k < K; k += 16 * A) { FE(SD_STEP) }     \
            int32x4_t tot = vdupq_n_s32(0);                                                     \
            FE(SD_SUM)                                                                          \
            y[m] = vaddvq_s32(tot);                                                             \
        }                                                                                       \
    }
DEFINE_SDOT(4, FE4)
DEFINE_SDOT(8, FE8)
#endif

#if defined(__ARM_NEON) && defined(__ARM_FEATURE_MATMUL_INT8)
// ---- i8mm SMMLA ---------------------------------------------------------------------------
// vmmlaq_s32(acc, a, b): a is 2 rows x 8 int8 (row 0 = a[0..7], row 1 = a[8..15]); b is 8x2 stored
// as two columns (column 0 = b[0..7], column 1 = b[8..15]); acc is the 2x2 int32 result in the
// order [r0c0, r0c1, r1c0, r1c1]. So one instruction multiplies two weight rows by two activation
// vectors: 32 MACs, which is 2 MACs per weight byte.
//
// The weights are packed (before timing; same bytes as W, like ggml's repack) so that a row pair is
// one contiguous run of 2K bytes: chunk c (c = 0 .. K/8 - 1) holds row 2p bytes [8c, 8c+8) then row
// 2p+1 bytes [8c, 8c+8). The two activation vectors are packed the same way into Xp (2K bytes).
// Output: out[4p + 2i + j] = (row 2p+i) . (vector j).
#define MM_STEP(i) s##i = vmmlaq_s32(s##i, vld1q_s8(wp + c + 16 * (i)), vld1q_s8(Xp + c + 16 * (i)));
#define DEFINE_SMMLA(A, FE)                                                                     \
    extern "C" __attribute__((noinline, noclone)) void dot_smmla_a##A(                          \
        const int8_t* __restrict Wp, const int8_t* __restrict Xp, int32_t* __restrict out,     \
        int64_t pairs, int64_t K) {                                                             \
        for (int64_t p = 0; p < pairs; p++) {                                                   \
            const int8_t* wp = Wp + p * 2 * K;                                                  \
            FE(SD_DECL)                                                                         \
            _Pragma("GCC unroll 1") for (int64_t c = 0; c < 2 * K; c += 16 * A) { FE(MM_STEP) } \
            int32x4_t tot = vdupq_n_s32(0);                                                     \
            FE(SD_SUM)                                                                          \
            vst1q_s32(out + 4 * p, tot);                                                        \
        }                                                                                       \
    }
DEFINE_SMMLA(4, FE4)
DEFINE_SMMLA(8, FE8)
#endif

#if defined(__ARM_FEATURE_SVE)
// ---- SVE SDOT -----------------------------------------------------------------------------
// The same loop as NEON SDOT with scalable vectors: svld1_vnum_s8 loads vector number i of the
// slice, svdot_s32 is SDOT (z-form). One vector is svcntb() bytes (16 on Neoverse V2).
#define SV_DECL(i) svint32_t s##i = svdup_n_s32(0);
#define SV_STEP(i) \
    s##i = svdot_s32(s##i, svld1_vnum_s8(pg, w + k, (i)), svld1_vnum_s8(pg, x + k, (i)));
#define SV_SUM(i) tot = svadd_s32_x(pg32, tot, s##i);
#define DEFINE_SVE(A, FE)                                                                       \
    extern "C" __attribute__((noinline, noclone)) void dot_sve_a##A(                            \
        const int8_t* __restrict W, const int8_t* __restrict x, int32_t* __restrict y,         \
        int64_t M, int64_t K) {                                                                 \
        const svbool_t pg = svptrue_b8(), pg32 = svptrue_b32();                                 \
        const int64_t step = (int64_t)svcntb() * A;                                             \
        for (int64_t m = 0; m < M; m++) {                                                       \
            const int8_t* w = W + m * K;                                                        \
            FE(SV_DECL)                                                                         \
            _Pragma("GCC unroll 1") for (int64_t k = 0; k < K; k += step) { FE(SV_STEP) }       \
            svint32_t tot = svdup_n_s32(0);                                                     \
            FE(SV_SUM)                                                                          \
            y[m] = (int32_t)svaddv_s32(pg32, tot);                                              \
        }                                                                                       \
    }
DEFINE_SVE(4, FE4)
DEFINE_SVE(8, FE8)
#endif

// ---- variants -----------------------------------------------------------------------------
struct Variant {
    const char* name;
    const char* family;
    int accumulators;          // 0 for scalar / autovec
    int macs_per_weight_byte;  // 2 for SMMLA (two activation vectors), else 1
    bool paired;               // SMMLA: packed weights, two vectors, row pairs
    KernelFn fn;
};
static std::vector<Variant> g_variants;

static void register_variants() {
    g_variants.push_back({"scalar", "scalar", 0, 1, false, dot_scalar});
    g_variants.push_back({"autovec", "autovec", 0, 1, false, dot_autovec});
#if defined(__ARM_NEON) && defined(__ARM_FEATURE_DOTPROD)
    g_variants.push_back({"sdot_a4", "sdot", 4, 1, false, dot_sdot_a4});
    g_variants.push_back({"sdot_a8", "sdot", 8, 1, false, dot_sdot_a8});
#endif
#if defined(__ARM_NEON) && defined(__ARM_FEATURE_MATMUL_INT8)
    g_variants.push_back({"smmla_a4", "smmla", 4, 2, true, dot_smmla_a4});
    g_variants.push_back({"smmla_a8", "smmla", 8, 2, true, dot_smmla_a8});
#endif
#if defined(__ARM_FEATURE_SVE)
    g_variants.push_back({"sve_a4", "sve", 4, 1, false, dot_sve_a4});
    g_variants.push_back({"sve_a8", "sve", 8, 1, false, dot_sve_a8});
#endif
}

static int sve_bytes() {
#if defined(__ARM_FEATURE_SVE)
    return (int)svcntb();
#else
    return 0;
#endif
}

// Can this variant run with this K? (Each loop step consumes a whole number of slices.)
static bool supports(const Variant& v, int64_t K) {
    std::string f = v.family;
    if (f == "sdot") return K % (16 * v.accumulators) == 0;
    if (f == "smmla") return (2 * K) % (16 * v.accumulators) == 0 && K % 8 == 0;
    if (f == "sve") return sve_bytes() > 0 && K % ((int64_t)sve_bytes() * v.accumulators) == 0;
    return true;
}

// ---- data ---------------------------------------------------------------------------------
static uint64_t splitmix(uint64_t& s) {
    uint64_t z = (s += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

// mode 0: uniform random int8; 1..4: constants (W, x) = (-128,-128) (127,-128) (-128,127) (127,127);
// 5: random picks from {-128, 127} only.
static void fill(int8_t* p, size_t n, int mode, int which /*0 = W, 1 = x*/, uint64_t seed) {
    uint64_t s = seed;
    if (mode == 0) {
        size_t i = 0;
        for (; i + 8 <= n; i += 8) {
            uint64_t v = splitmix(s);
            memcpy(p + i, &v, 8);
        }
        uint64_t v = splitmix(s);
        for (; i < n; i++, v >>= 8) p[i] = (int8_t)(v & 0xff);
    } else if (mode <= 4) {
        const int8_t wv = (mode == 1 || mode == 3) ? -128 : 127;
        const int8_t xv = (mode == 1 || mode == 2) ? -128 : 127;
        memset(p, which == 0 ? wv : xv, n);
    } else {
        for (size_t i = 0; i < n; i++) p[i] = (splitmix(s) & 1) ? (int8_t)127 : (int8_t)-128;
    }
}

static int8_t* alloc_i8(size_t n) {
    size_t rounded = (n + 4095) / 4096 * 4096;
    void* p = aligned_alloc(4096, rounded);
    if (!p) { fprintf(stderr, "out of memory (%zu bytes)\n", rounded); exit(2); }
    return (int8_t*)p;
}

struct Data {
    int64_t M = 0, K = 0;
    int8_t *W = nullptr, *Wp = nullptr, *x0 = nullptr, *x1 = nullptr, *Xp = nullptr;
    std::vector<int32_t> ref0, ref1;  // scalar results for x0 and x1 (M each)
    std::vector<int32_t> y, out;      // outputs: y has M, out has 2M (SMMLA)
    bool has_packed = false;
    ~Data() { free(W); free(Wp); free(x0); free(x1); free(Xp); }
};

// An independent reference in 64-bit arithmetic, to check the scalar variant itself.
static bool scalar_matches_int64(const Data& d, const int8_t* x, const std::vector<int32_t>& got) {
    for (int64_t m = 0; m < d.M; m++) {
        int64_t acc = 0;
        for (int64_t k = 0; k < d.K; k++) acc += (int64_t)d.W[m * d.K + k] * (int64_t)x[k];
        if (acc != (int64_t)got[m]) return false;
    }
    return true;
}

// Weights and activations, the scalar reference for both vectors, and the packed SMMLA layout.
// Returns false if the scalar variant disagrees with the 64-bit reference.
static bool setup(Data& d, int64_t M, int64_t K, int mode, uint64_t seed, bool pack,
                  bool verify_scalar) {
    d.M = M;
    d.K = K;
    d.W = alloc_i8((size_t)M * K);
    d.x0 = alloc_i8(K);
    d.x1 = alloc_i8(K);
    fill(d.W, (size_t)M * K, mode, 0, seed);
    fill(d.x0, K, mode, 1, seed + 1);
    fill(d.x1, K, mode, 1, seed + 2);
    d.ref0.assign(M, 0);
    d.ref1.assign(M, 0);
    d.y.assign(M, 0);
    d.out.assign(2 * M, 0);
    dot_scalar(d.W, d.x0, d.ref0.data(), M, K);
    dot_scalar(d.W, d.x1, d.ref1.data(), M, K);
    if (verify_scalar &&
        !(scalar_matches_int64(d, d.x0, d.ref0) && scalar_matches_int64(d, d.x1, d.ref1)))
        return false;
    if (pack && M % 2 == 0 && K % 8 == 0) {
        d.Wp = alloc_i8((size_t)M * K);
        d.Xp = alloc_i8(2 * (size_t)K);
        for (int64_t p = 0; p < M / 2; p++)
            for (int64_t c = 0; c < K / 8; c++) {
                // Row pair p starts at 2K * p; chunk c is the 16 bytes at 16c within it.
                memcpy(d.Wp + p * 2 * K + c * 16, d.W + (2 * p) * K + c * 8, 8);
                memcpy(d.Wp + p * 2 * K + c * 16 + 8, d.W + (2 * p + 1) * K + c * 8, 8);
            }
        for (int64_t c = 0; c < K / 8; c++) {
            memcpy(d.Xp + c * 16, d.x0 + c * 8, 8);
            memcpy(d.Xp + c * 16 + 8, d.x1 + c * 8, 8);
        }
        d.has_packed = true;
    }
    return true;
}

static const int32_t kPoison = 0x5a5a5a5a;  // far outside any real result (|sum| < 2^27)

static void run_variant(const Variant& v, Data& d) {
    if (v.paired) v.fn(d.Wp, d.Xp, d.out.data(), d.M / 2, d.K);
    else v.fn(d.W, d.x0, d.y.data(), d.M, d.K);
    asm volatile("" ::: "memory");  // the result is observable: the call cannot be merged or hoisted
}

// Index of the first output element that differs from scalar, or -1.
static int64_t first_mismatch(const Variant& v, const Data& d) {
    if (!v.paired) {
        for (int64_t m = 0; m < d.M; m++)
            if (d.y[m] != d.ref0[m]) return m;
        return -1;
    }
    for (int64_t p = 0; p < d.M / 2; p++)
        for (int i = 0; i < 2; i++)
            for (int j = 0; j < 2; j++) {
                const int32_t want = (j == 0 ? d.ref0 : d.ref1)[2 * p + i];
                if (d.out[4 * p + 2 * i + j] != want) return 4 * p + 2 * i + j;
            }
    return -1;
}

// Run once on poisoned output and compare with scalar.
static int64_t verify(const Variant& v, Data& d) {
    std::fill(d.y.begin(), d.y.end(), kPoison);
    std::fill(d.out.begin(), d.out.end(), kPoison);
    run_variant(v, d);
    return first_mismatch(v, d);
}

// ---- timing -------------------------------------------------------------------------------
using clk = std::chrono::steady_clock;
static double secs(clk::time_point a, clk::time_point b) {
    return std::chrono::duration<double>(b - a).count();
}

static bool pin_to(int core) {
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core, &set);
    if (pthread_setaffinity_np(pthread_self(), sizeof(set), &set) != 0) return false;
    return sched_getcpu() == core;
}

// FNV-style fold of an output vector, so every result is consumed and shows up in the record.
static uint64_t fold(uint64_t h, const int32_t* p, size_t n) {
    for (size_t i = 0; i < n; i++) h = (h ^ (uint32_t)p[i]) * 1099511628211ULL;
    return h;
}

struct Point {
    std::string variant, family, ws;
    int accumulators = 0, macs_per_weight_byte = 1;
    int64_t rows = 0, k = 0, calls = 1;
    double weight_bytes = 0;
    int warmup = 0, reps = 0;
    bool match = false, pin_ok = true;
    int cpu = -1;
    uint64_t checksum = 0;
    std::vector<double> ns;  // nanoseconds per call, one per timed repetition
};

static Point time_variant(const Variant& v, Data& d, const char* ws, int warmup, int reps,
                          double target_ms) {
    Point pt;
    pt.variant = v.name;
    pt.family = v.family;
    pt.ws = ws;
    pt.accumulators = v.accumulators;
    pt.macs_per_weight_byte = v.macs_per_weight_byte;
    pt.rows = d.M;
    pt.k = d.K;
    pt.weight_bytes = (double)d.M * (double)d.K;
    pt.warmup = warmup;
    pt.reps = reps;
    pt.match = verify(v, d) < 0;  // the output of the very kernel that is about to be timed

    auto trial = [&](int64_t n) {
        auto t0 = clk::now();
        for (int64_t i = 0; i < n; i++) run_variant(v, d);
        return secs(t0, clk::now());
    };
    // Calls per repetition: enough that one repetition lasts about target_ms (1 for the DRAM case).
    int64_t calls = 1;
    double s = trial(calls);
    while (s < 0.005) {
        calls *= 4;
        s = trial(calls);
    }
    calls = std::max<int64_t>(1, (int64_t)std::llround((double)calls * (target_ms * 1e-3) / s));
    pt.calls = calls;

    for (int w = 0; w < warmup; w++) trial(calls);
    uint64_t h = 1469598103934665603ULL;
    for (int r = 0; r < reps; r++) {
        const double t = trial(calls);
        pt.ns.push_back(t * 1e9 / (double)calls);
        h = v.paired ? fold(h, d.out.data(), d.out.size()) : fold(h, d.y.data(), d.y.size());
    }
    pt.checksum = h;
    pt.cpu = sched_getcpu();
    pt.pin_ok = pt.cpu == 0;
    return pt;
}

static void print_point(const Point& p, bool last) {
    printf("    {\"variant\": \"%s\", \"family\": \"%s\", \"accumulators\": %d, \"working_set\": \"%s\","
           " \"rows\": %lld, \"k\": %lld, \"weight_bytes\": %.0f, \"macs_per_weight_byte\": %d,"
           " \"calls_per_rep\": %lld, \"reps_warmup\": %d, \"reps_timed\": %d,"
           " \"observed_cpu\": %d, \"getcpu_ok\": %s, \"output_matches_scalar\": %s,"
           " \"checksum\": \"0x%016llx\",\n     \"samples_ns_per_call\": [",
           p.variant.c_str(), p.family.c_str(), p.accumulators, p.ws.c_str(), (long long)p.rows,
           (long long)p.k, p.weight_bytes, p.macs_per_weight_byte, (long long)p.calls, p.warmup,
           p.reps, p.cpu, p.pin_ok ? "true" : "false", p.match ? "true" : "false",
           (unsigned long long)p.checksum);
    for (size_t i = 0; i < p.ns.size(); i++) printf("%s%.3f", i ? ", " : "", p.ns[i]);
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

static void print_features() {
#if defined(__ARM_NEON)
    const bool neon = true;
#else
    const bool neon = false;
#endif
#if defined(__ARM_FEATURE_DOTPROD)
    const bool dot = true;
#else
    const bool dot = false;
#endif
#if defined(__ARM_FEATURE_MATMUL_INT8)
    const bool i8mm = true;
#else
    const bool i8mm = false;
#endif
#if defined(__ARM_FEATURE_SVE)
    const bool sve = true;
#else
    const bool sve = false;
#endif
    printf("\"sve_vector_bits\": %d, \"features\": {\"neon\": %s, \"dotprod\": %s, \"i8mm\": %s, "
           "\"sve\": %s}",
           sve_bytes() * 8, neon ? "true" : "false", dot ? "true" : "false",
           i8mm ? "true" : "false", sve ? "true" : "false");
}

// ---- --check ------------------------------------------------------------------------------
struct CheckTally {
    long long cases = 0, mismatches = 0, skipped = 0;
    long long first_case = -1, first_index = -1;
};

static int run_check(int seeds) {
    std::vector<CheckTally> tally(g_variants.size());
    long long cases = 0;
    bool ok = true;
    const int64_t Ks[] = {4096, 1152};  // 1152 = 9 x 128: another trip count for every slice width
    const int64_t Ms[] = {2, 8, 34};
    for (int64_t K : Ks)
        for (int64_t M : Ms)
            for (int mode = 0; mode <= 5; mode++) {
                // mode 0 and 5 use several seeds; modes 1..4 are fixed patterns (one case each).
                const int n_seeds = (mode == 0 || mode == 5) ? seeds : 1;
                for (int sd = 0; sd < n_seeds; sd++) {
                    Data d;
                    const uint64_t seed = 1000ULL * (uint64_t)(sd + 1) + (uint64_t)(M * 7 + K);
                    if (!setup(d, M, K, mode, seed, true, true)) {
                        fprintf(stderr, "scalar disagrees with the 64-bit reference (M=%lld K=%lld "
                                "mode=%d seed=%llu)\n", (long long)M, (long long)K, mode,
                                (unsigned long long)seed);
                        ok = false;
                        continue;
                    }
                    cases++;
                    for (size_t i = 0; i < g_variants.size(); i++) {
                        const Variant& v = g_variants[i];
                        if (!supports(v, K) || (v.paired && !d.has_packed)) {
                            tally[i].skipped++;
                            continue;
                        }
                        tally[i].cases++;
                        const int64_t bad = verify(v, d);
                        if (bad >= 0) {
                            tally[i].mismatches++;
                            ok = false;
                            if (tally[i].first_case < 0) {
                                tally[i].first_case = cases;
                                tally[i].first_index = bad;
                                fprintf(stderr, "MISMATCH %s: case %lld (M=%lld K=%lld mode=%d "
                                        "seed=%llu) element %lld\n", v.name, cases, (long long)M,
                                        (long long)K, mode, (unsigned long long)seed,
                                        (long long)bad);
                            }
                        }
                    }
                }
            }
    printf("{\n  \"program\": \"dot_int8\", \"mode\": \"check\", ");
    print_features();
    printf(",\n  \"ok\": %s, \"cases\": %lld, \"seeds\": %d,\n  \"variants\": [\n",
           ok ? "true" : "false", cases, seeds);
    for (size_t i = 0; i < g_variants.size(); i++)
        printf("    {\"variant\": \"%s\", \"cases\": %lld, \"skipped\": %lld, \"mismatches\": %lld,"
               " \"first_case\": %lld, \"first_index\": %lld}%s\n",
               g_variants[i].name, tally[i].cases, tally[i].skipped, tally[i].mismatches,
               tally[i].first_case, tally[i].first_index, i + 1 < g_variants.size() ? "," : "");
    printf("  ]\n}\n");
    return ok ? 0 : 1;
}

// ---- --time -------------------------------------------------------------------------------
static int run_time(const std::vector<std::string>& sets, const std::string& want, int reps,
                    int warmup, double target_ms, int dram_mib, const cpu_set_t& allowed) {
    const bool pinned = pin_to(0);
    std::vector<Point> points;
    bool ok = pinned;
    const int64_t K = 4096;
    for (const std::string& ws : sets) {
        const int64_t M = ws == "L1" ? 4 : (int64_t)dram_mib * 1024 * 1024 / K;
        Data d;
        if (!setup(d, M, K, 0, 12345, true, true)) {
            fprintf(stderr, "scalar disagrees with the 64-bit reference in the %s set\n", ws.c_str());
            return 1;
        }
        for (const Variant& v : g_variants) {
            if (want != "all") {
                bool listed = false;
                for (const std::string& n : split(want)) listed = listed || n == v.name;
                if (!listed) continue;
            }
            if (!supports(v, K) || (v.paired && !d.has_packed)) {
                fprintf(stderr, "variant %s not available for K=%lld\n", v.name, (long long)K);
                return 2;
            }
            fprintf(stderr, "timing %s on %s ...\n", v.name, ws.c_str());
            points.push_back(time_variant(v, d, ws.c_str(), warmup, reps, target_ms));
            ok = ok && points.back().match && points.back().pin_ok;
        }
    }
    printf("{\n  \"program\": \"dot_int8\", \"mode\": \"time\", ");
    print_features();
    printf(", \"process_cpus\": [");
    bool first = true;
    for (int c = 0; c < CPU_SETSIZE; c++)
        if (CPU_ISSET(c, &allowed)) { printf("%s%d", first ? "" : ", ", c); first = false; }
    printf("], \"pinned\": %s,\n  \"points\": [\n", pinned ? "true" : "false");
    for (size_t i = 0; i < points.size(); i++) print_point(points[i], i + 1 == points.size());
    printf("  ]\n}\n");
    return ok ? 0 : 3;
}

int main(int argc, char** argv) {
    // The CPU set the process started with, read before this thread pins itself.
    cpu_set_t allowed;
    CPU_ZERO(&allowed);
    sched_getaffinity(0, sizeof(allowed), &allowed);

    bool check = false, time_mode = false;
    int seeds = 6, reps = 30, warmup = 3, dram_mib = 1024;
    double target_ms = 25.0;  // a repetition lasts about this long; the record needs >= 10 ms each
    std::string sets = "L1,DRAM", variants = "all";
    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        auto next = [&]() -> const char* {
            if (i + 1 >= argc) { fprintf(stderr, "%s needs a value\n", a.c_str()); exit(2); }
            return argv[++i];
        };
        if (a == "--check") check = true;
        else if (a == "--time") time_mode = true;
        else if (a == "--seeds") seeds = atoi(next());
        else if (a == "--sets") sets = next();
        else if (a == "--variants") variants = next();
        else if (a == "--reps") reps = atoi(next());
        else if (a == "--warmup") warmup = atoi(next());
        else if (a == "--target-ms") target_ms = atof(next());
        else if (a == "--dram-mib") dram_mib = atoi(next());
        else { fprintf(stderr, "unknown argument %s\n", a.c_str()); return 2; }
    }
    if (check == time_mode || seeds < 1 || reps < 1 || dram_mib < 1) {
        fprintf(stderr, "usage: dot_int8 --check [--seeds N] | --time [--sets L1,DRAM] "
                "[--variants all|a,b] [--reps N] [--warmup N] [--target-ms X] [--dram-mib N]\n");
        return 2;
    }
    register_variants();
    if (check) return run_check(seeds);
    for (const std::string& s : split(sets))
        if (s != "L1" && s != "DRAM") { fprintf(stderr, "unknown set %s\n", s.c_str()); return 2; }
    return run_time(split(sets), variants, reps, warmup, target_ms, dram_mib, allowed);
}

// The plain-C int8 matrix-vector product, y[m] = sum_k W[m][k] * x[k] (RQ4, CLAUDE.md §5, §9).
//
// This one source is compiled twice by micro/run_micro.py, under two names:
//
//   dot_scalar   g++ -O3 -mcpu=native -fno-tree-vectorize ...  -DDOT_REF_NAME=dot_scalar
//                (auto-vectorisation off: at plain -O3 GCC would vectorise this loop, possibly into
//                SDOT itself, and it would no longer be the scalar baseline; ADR-006)
//   dot_autovec  g++ -O3 -mcpu=native ...                      -DDOT_REF_NAME=dot_autovec
//                (nothing forced: whatever instructions GCC picks are the finding, and
//                micro/run_micro.py records them)
//
// It lives in its own translation unit so that dot_int8.cpp (the SIMD variants and the harness)
// cannot change how it is compiled. The function is never inlined, and it is also the reference
// every other variant is compared with, bit for bit.
//
// K must be small enough that a row's int32 sum cannot overflow: |sum| <= K * 128 * 128, so
// K <= 131072. The benchmark uses K = 4096 (sums stay below 2^26).

#include <cstdint>

#ifndef DOT_REF_NAME
#error "compile with -DDOT_REF_NAME=dot_scalar or -DDOT_REF_NAME=dot_autovec"
#endif

extern "C" __attribute__((noinline, noclone)) void DOT_REF_NAME(
    const int8_t* __restrict W, const int8_t* __restrict x, int32_t* __restrict y, int64_t M,
    int64_t K) {
    for (int64_t m = 0; m < M; m++) {
        const int8_t* w = W + m * K;
        int32_t acc = 0;
        for (int64_t k = 0; k < K; k++) acc += (int32_t)w[k] * (int32_t)x[k];
        y[m] = acc;
    }
}

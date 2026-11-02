# Pilot summary, session 2026-11-02T2017Z

Written by `bench/run_sweep.py` after the pilot. Not a measurement of the sweep itself.

## Repeat noise (IQR / median of tokens/s over the repetitions)

| config_id | attempt | reps | median tok/s | IQR tok/s | IQR/median | noisy | wall s |
|---|---|---|---|---|---|---|---|
| large_F16_baseline_t1_pp2048 | 1 | 3 | 8.54 | 0.02 | 0.27 % | no | 976 |
| large_F16_kleidiai_t1_pp2048 | 1 | 3 | 8.54 | 0.00 | 0.02 % | no | 959 |
| small_F16_baseline_t1_pp512 | 1 | 5 | 28.34 | 0.01 | 0.05 % | no | 115 |
| small_F16_baseline_t1_tg128 | 1 | 5 | 19.26 | 0.01 | 0.03 % | no | 33 |
| small_F16_baseline_t1_tg128d2048 | 1 | 5 | 11.15 | 0.00 | 0.00 % | no | 216 |
| small_F16_baseline_t8_pp512 | 1 | 5 | 204.24 | 7.27 | 3.56 % | no | 16 |
| small_F16_baseline_t8_tg128 | 1 | 5 | 107.01 | 2.79 | 2.61 % | no | 6 |
| small_F16_baseline_t8_tg128d2048 | 1 | 5 | 68.89 | 5.47 | 7.94 % | yes | 32 |
| small_F16_baseline_t8_tg128d2048 | 2 | 5 | 69.28 | 0.23 | 0.33 % | no | 32 |
| small_F16_kleidiai_t1_pp512 | 1 | 5 | 28.32 | 0.02 | 0.06 % | no | 109 |
| small_F16_kleidiai_t1_tg128 | 1 | 5 | 19.26 | 0.01 | 0.03 % | no | 33 |
| small_F16_kleidiai_t1_tg128d2048 | 1 | 5 | 11.18 | 0.01 | 0.08 % | no | 214 |
| small_F16_kleidiai_t8_pp512 | 1 | 5 | 202.09 | 7.67 | 3.80 % | no | 16 |
| small_F16_kleidiai_t8_tg128 | 1 | 5 | 106.97 | 0.47 | 0.43 % | no | 6 |
| small_F16_kleidiai_t8_tg128d2048 | 1 | 5 | 66.70 | 4.56 | 6.84 % | yes | 31 |
| small_F16_kleidiai_t8_tg128d2048 | 2 | 5 | 68.94 | 6.15 | 8.92 % | yes | 32 |
| small_Q4_0_baseline_t1_pp512 | 1 | 5 | 51.07 | 0.01 | 0.02 % | no | 63 |
| small_Q4_0_baseline_t1_tg128 | 1 | 5 | 38.66 | 0.32 | 0.84 % | no | 17 |
| small_Q4_0_baseline_t1_tg128d2048 | 1 | 5 | 15.41 | 0.04 | 0.27 % | no | 168 |
| small_Q4_0_baseline_t8_pp512 | 1 | 5 | 344.04 | 25.38 | 7.38 % | yes | 10 |
| small_Q4_0_baseline_t8_pp512 | 2 | 5 | 330.58 | 16.44 | 4.97 % | no | 10 |
| small_Q4_0_baseline_t8_tg128 | 1 | 5 | 182.53 | 0.81 | 0.44 % | no | 4 |
| small_Q4_0_baseline_t8_tg128d2048 | 1 | 5 | 93.56 | 7.78 | 8.32 % | yes | 25 |
| small_Q4_0_baseline_t8_tg128d2048 | 2 | 5 | 93.62 | 0.32 | 0.34 % | no | 25 |
| small_Q4_0_kleidiai_t1_pp512 | 1 | 5 | 49.75 | 0.05 | 0.11 % | no | 63 |
| small_Q4_0_kleidiai_t1_tg128 | 1 | 5 | 45.34 | 0.08 | 0.18 % | no | 15 |
| small_Q4_0_kleidiai_t1_tg128d2048 | 1 | 5 | 16.31 | 0.04 | 0.24 % | no | 167 |
| small_Q4_0_kleidiai_t8_pp512 | 1 | 5 | 336.51 | 17.41 | 5.17 % | yes | 10 |
| small_Q4_0_kleidiai_t8_pp512 | 2 | 5 | 336.92 | 0.12 | 0.04 % | no | 10 |
| small_Q4_0_kleidiai_t8_tg128 | 1 | 5 | 189.41 | 1.12 | 0.59 % | no | 4 |
| small_Q4_0_kleidiai_t8_tg128d2048 | 1 | 5 | 91.29 | 8.70 | 9.53 % | yes | 26 |
| small_Q4_0_kleidiai_t8_tg128d2048 | 2 | 5 | 96.01 | 0.64 | 0.66 % | no | 25 |

## Estimated wall time of the full sweep

- points: 288 (calls of llama-bench, both builds)
- estimate: **13.8 h** (upper bound 40.6 h, with the largest per-GiB overhead seen in the pilot)
- the pilot itself took 58 min for 32 calls
- noisy points in the pilot: 23 % (the same share is added for re-runs)

- baseline: long-prompt correction 0.965 (measured 8.54 tok/s at large_F16_baseline_t1_pp2048, scaling alone predicts 8.86)
- kleidiai: long-prompt correction 0.965 (measured 8.54 tok/s at large_F16_kleidiai_t1_pp2048, scaling alone predicts 8.85)

### By model, format and phase (hours, both builds)

- large_F16_decode: 0.48
- large_F16_prefill: 2.24
- large_Q4_0_decode: 0.26
- large_Q4_0_prefill: 1.45
- large_Q4_K_M_decode: 0.45
- large_Q4_K_M_prefill: 2.50
- large_Q8_0_decode: 0.46
- large_Q8_0_prefill: 2.52
- small_F16_decode: 0.17
- small_F16_prefill: 0.81
- small_Q4_0_decode: 0.09
- small_Q4_0_prefill: 0.45
- small_Q4_K_M_decode: 0.15
- small_Q4_K_M_prefill: 0.78
- small_Q8_0_decode: 0.16
- small_Q8_0_prefill: 0.79

### Method

```
What the Day 3 pilot tells us: repeat noise per point, and the full sweep's wall time.

Input is a list of bench records (dicts, schema BenchRecord) from the pilot session. Nothing here
calls hardware or reads files, so it is tested in CI; bench/run_sweep.py feeds it and writes the
result next to the pilot's records.

Wall-time method (CLAUDE.md §7 item 10), stated so it can be argued with:

  One llama-bench call costs   overhead + warm-up + repetitions x rep_time (+ depth fill).
    pp<N>      warm-up is one full prompt run, so (reps + 1) x N / prefill_tps
    tg<N>      warm-up is one token (negligible), so reps x N / decode_tps
    tg<N>d<D>  as tg, plus the D-token context filled once before the first timed run
  `overhead` is everything else (model load, repacking or KleidiAI conversion, context set-up);
  it is taken from the pilot calls as wall - the terms above, divided by the model file size, and
  scaled to a file's size. The median over the pilot calls of a build is used (a first load from a
  cold disk is in the maximum, reported as the upper bound).

  Speeds for points the pilot did not run are scaled from the pilot's, per build:
    quantisation  a format the pilot did not run takes the speed of the slowest pilot format of
                  that model (an upper bound on time: Q8_0 and Q4_K_M files are smaller than F16)
    threads       t = 2 and 4 by log-log interpolation between t = 1 and t = 8
    model size    prefill is compute-bound: tokens/s scales as N_blk of the reference model over
                  N_blk of the model; decode is bandwidth-bound: tokens/s scales as the file's
                  weight bytes (W_all) of the reference over the model's
    prompt length prefill tokens/s is taken as independent of N, except at N >= 2048, where it is
                  multiplied by the factor (<= 1) that the pilot's extra long-prompt point showed
  Re-runs of noisy points add the pilot's noisy fraction of the total.
```

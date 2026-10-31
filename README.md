# edge-llm-on-arm

Small language models now run on ordinary Arm CPUs, but a tokens/s figure alone does not say
*why* a setup is as fast as it is, or how far it is from what the hardware allows. This
project predicts LLM inference speed on an Arm CPU from the hardware's measured memory
bandwidth and compute peak, measures it with llama.cpp (with and without Arm's KleidiAI
kernels), and explains the difference.

**Status:** Day 1 of 10 (repo skeleton). No measurements yet, so there is no headline result.
The full specification is in [CLAUDE.md](CLAUDE.md); how the parts connect is in
[ARCHITECTURE.md](ARCHITECTURE.md).

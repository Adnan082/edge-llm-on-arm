# Targets follow ARCHITECTURE.md §6. Day 1-4: env, build, models, bandwidth, check-builds, peak,
# predict, bench, test, lint. The rest fail loudly until their day comes, so nothing silently does nothing.
# On a fresh VM run `bash infra/setup_vm.sh` once before any target.

# Use the venv made by setup_vm.sh when it exists.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

# `python -m bench.x` finds bench/ from the repo root; this lets `-m edge_llm.x` find src/.
export PYTHONPATH := $(CURDIR)/src

.PHONY: env build models bandwidth check-builds peak predict bench analyse figures micro test lint

env:  ## machine details -> results/raw/env/<session_id>.json; also starts the session
	$(PYTHON) -m bench.env_capture

build:  ## both llama.cpp builds + results/raw/build/<session_id>_build.json (~15 min)
	bash infra/build_llamacpp.sh

models:  ## HF -> F16 -> every format in work/models, then results/models/*.json
	bash infra/make_models.sh
	$(PYTHON) -m edge_llm.gguf_table

bandwidth:  ## B(t): make bandwidth PHASE=start|end -> results/raw/bandwidth/
	@test -n "$(PHASE)" || { echo "usage: make bandwidth PHASE=start|end"; exit 1; }
	$(PYTHON) -m bench.bandwidth.run_bandwidth --phase $(PHASE)

peak:  ## C(t): SDOT / SMMLA / FP16 FMLA / FMLALB+T / F32 FMLA peaks per thread count -> results/raw/peak/ (~3 min)
	$(PYTHON) -m micro.run_peak

bench:  ## make bench SET=pilot|full -> results/raw/bench/<session_id>/<config_id>.json
	@test -n "$(SET)" || { echo "usage: make bench SET=pilot|full"; exit 1; }
	$(PYTHON) -m bench.run_sweep --set $(SET) $(BENCH_ARGS)

check-builds:  ## KleidiAI activation + buffer types per model/build (smoke runs) -> results/raw/build/
	$(PYTHON) -m bench.check_builds

test:  ## unit tests (add `PYTEST_ARGS="-m hardware"` on the VM for the hardware tests)
	$(PYTHON) -m pytest $(PYTEST_ARGS)

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .

predict:  ## v1 roofline predictions for every full-sweep point -> results/predictions/v1.csv
	$(PYTHON) -m edge_llm.roofline

analyse:
	@echo "not implemented yet (Day 5-6: analyse.py)"; exit 1
figures:
	@echo "not implemented yet (Day 6: plots.py)"; exit 1
micro:
	@echo "not implemented yet (Day 7: micro/dot_int8.cpp)"; exit 1

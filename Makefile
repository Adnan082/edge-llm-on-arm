# Targets follow ARCHITECTURE.md §6. Day 1-4: env, build, models, bandwidth, check-builds, peak,
# predict, bench, test, lint; Day 5-6: analyse, figures; Day 7: micro, micro-table;
# Day 8: day8-variants, day8, day8-analyse.
# On a fresh VM run `bash infra/setup_vm.sh` once before any target.

# Use the venv made by setup_vm.sh when it exists.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

# `python -m bench.x` finds bench/ from the repo root; this lets `-m edge_llm.x` find src/.
export PYTHONPATH := $(CURDIR)/src

.PHONY: env build models bandwidth check-builds peak predict bench analyse figures micro micro-table day8-variants day8 day8-analyse test lint

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

# The sweep session the tables are built from (override: make analyse SESSION=<id>).
SESSION ?= 2026-11-02T2215Z

analyse:  ## raw bench records + v1 predictions -> results/processed/*.csv
	$(PYTHON) -m edge_llm.analyse --session $(SESSION)

figures:  ## results/processed/*.csv -> figures/*.png and *.svg
	$(PYTHON) -m edge_llm.plots

micro:  ## RQ4 int8 dot product: build, --check, disassemble, time, save; then the table
	$(PYTHON) -m micro.run_micro
	$(PYTHON) -m edge_llm.micro

micro-table:  ## newest results/raw/micro/*.json -> results/processed/micro.csv (anywhere)
	$(PYTHON) -m edge_llm.micro

# Day 8 investigation (ADR-025). Runs in the SAME session as Day 7: do not run `make env` again.
DAY8_SESSION ?= $(shell cat work/session_id 2>/dev/null)

day8-variants:  ## Check A files: Q4_0 with output.weight Q8_0 / Q4_0, their tables and the "only output changed" check
	bash infra/make_variants.sh

day8:  ## Checks A (output-layer variants, tg128) and C (perf, pp128), then the tables (VM)
	$(PYTHON) -m bench.day8 all $(DAY8_ARGS)
	$(PYTHON) -m edge_llm.day8 --session $(DAY8_SESSION)

day8-analyse:  ## Check B from kleidiai.csv; also A and C if the session's records are present (anywhere)
	$(PYTHON) -m edge_llm.day8 $(if $(DAY8_SESSION),--session $(DAY8_SESSION),)

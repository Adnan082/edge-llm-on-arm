# Targets follow ARCHITECTURE.md §6. Only `env`, `test` and `lint` exist so far (Day 1);
# the rest fail loudly until their day comes, so nothing silently does nothing.
# On a fresh VM run `bash infra/setup_vm.sh` once before any target.

# Use the venv made by setup_vm.sh when it exists.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: env build models bandwidth peak predict bench analyse figures micro test lint

env:  ## machine details -> results/raw/env/<session_id>.json
	$(PYTHON) bench/env_capture.py

test:  ## unit tests (add `PYTEST_ARGS="-m hardware"` on the VM for the hardware tests)
	$(PYTHON) -m pytest $(PYTEST_ARGS)

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .

build:
	@echo "not implemented yet (Day 2: infra/build_llamacpp.sh)"; exit 1
models:
	@echo "not implemented yet (Day 2: infra/make_models.sh, gguf_table.py)"; exit 1
bandwidth:
	@echo "not implemented yet (Day 2: bench/bandwidth/)"; exit 1
peak:
	@echo "not implemented yet (Day 3: micro/peak.cpp)"; exit 1
predict:
	@echo "not implemented yet (Day 4: roofline.py)"; exit 1
bench:
	@echo "not implemented yet (Day 3: bench/run_sweep.py)"; exit 1
analyse:
	@echo "not implemented yet (Day 5-6: analyse.py)"; exit 1
figures:
	@echo "not implemented yet (Day 6: plots.py)"; exit 1
micro:
	@echo "not implemented yet (Day 7: micro/dot_int8.cpp)"; exit 1

# The project's checks, defined once, in the public tree.
#
# This file exists so there is exactly one definition of the quality gate.
# CI runs `make quality`; a contributor runs `make quality`; the maintainer's
# workflow tooling is configured to shell `make quality`. A second copy of the
# same tool list would drift from this one the first time either changed, and
# a CI verdict that can disagree with a local verdict is worse than no CI.
#
# No product code exists yet. These targets check the repository's own docs
# tooling; see docs/adr/0008-implementation-runtime-python.md.

PYTHON ?= python3

.PHONY: quality lint format test test-unit adr-index help

help:
	@echo "quality    - everything CI runs: lint, format check, ADR index, tests"
	@echo "lint       - ruff check"
	@echo "format     - ruff format (rewrites files)"
	@echo "test       - full test suite"
	@echo "test-unit  - fast unit subset"
	@echo "adr-index  - regenerate docs/adr/README.md"

# Read-only by construction: every step checks, none rewrites. A gate that
# fixes what it finds stops meaning "the tree was already clean".
quality:
	ruff check .
	ruff format --check .
	$(PYTHON) scripts/gen_adr_index.py --check
	$(MAKE) test

lint:
	ruff check .

format:
	ruff format .

# The empty-collection tolerance that used to live here is gone: a suite now
# exists, so pytest's exit 5 would mean the tests stopped being collected —
# exactly the failure worth seeing rather than forgiving.
test:
	pytest -q

# No unit subset exists yet, so the "unit" command IS the full suite. That is
# deliberate: the seal gate runs whatever this names and never silently skips,
# so pointing it at a directory that does not exist fails the gate rather than
# skipping it (pytest exits 4 on a missing path, not the 5 it uses for an empty
# collection). Split this the moment tests/unit exists.
test-unit: test

adr-index:
	$(PYTHON) scripts/gen_adr_index.py

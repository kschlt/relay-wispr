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

# The interpreter floor, enforced rather than assumed. ADR 0008 declares Python
# 3.12 or later; CI installed it and nothing local checked, so this gate was
# observed running green end to end on 3.11 — a local verdict CI could
# contradict, which is the split a single definition of the gate exists to
# prevent.
#
# Checked here, at parse time, rather than inside a target: every target below
# passes through it, including the sub-makes `quality` invokes and any target
# added later. A check that one entry point performs is a check the other entry
# points do not have. It reads a version and changes nothing.
#
# It therefore refuses `make help` too. That is deliberate. On a machine whose
# interpreter is wrong, that is the first thing worth knowing, and a check with
# an exception in it is a check someone will find the exception to.
PYTHON_FLOOR := 3.12
PYTHON_ACTUAL := $(shell $(PYTHON) -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null)
PYTHON_CONFORMS := $(shell $(PYTHON) -c 'import sys; print(sys.version_info[:2] >= tuple(int(n) for n in "$(PYTHON_FLOOR)".split(".")))' 2>/dev/null)

ifeq ($(PYTHON_ACTUAL),)
$(error PYTHON=$(PYTHON) is not a usable interpreter. This project requires Python $(PYTHON_FLOOR) or later — see docs/adr/0008-implementation-runtime-python.md. Re-run with a conforming one, e.g. make PYTHON=python$(PYTHON_FLOOR) <target>)
else ifneq ($(PYTHON_CONFORMS),True)
$(error PYTHON=$(PYTHON) is Python $(PYTHON_ACTUAL). This project requires Python $(PYTHON_FLOOR) or later — see docs/adr/0008-implementation-runtime-python.md. Re-run with a conforming one, e.g. make PYTHON=python$(PYTHON_FLOOR) <target>)
endif

.PHONY: quality lint format test test-unit adr-index privacy help

help:
	@echo "quality    - everything CI runs: lint, format check, ADR index, privacy, tests"
	@echo "lint       - ruff check"
	@echo "format     - ruff format (rewrites files)"
	@echo "test       - full test suite"
	@echo "test-unit  - fast unit subset"
	@echo "adr-index  - regenerate docs/adr/README.md"
	@echo "privacy    - refuse tracked files carrying the private-content marker"

# Read-only by construction: every step checks, none rewrites. A gate that
# fixes what it finds stops meaning "the tree was already clean".
quality:
	ruff check .
	ruff format --check .
	$(PYTHON) scripts/gen_adr_index.py --check
	$(MAKE) privacy
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

# Part of `quality`, not a command anyone has to remember: the leak this
# refuses happens when attention is elsewhere, which is exactly when an
# optional check does not get run. It catches a copied private finding that
# brings its marker along; it cannot recognise unmarked content.
privacy:
	$(PYTHON) scripts/check_private_content.py

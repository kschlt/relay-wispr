"""Tests for the ADR index generator.

The generator's whole justification is that a wrong index cannot be produced
silently, so these tests exercise its REFUSALS and its OUTPUT, never its source
text. A test that greps the implementation passes on a version that has been
rewrapped into uselessness — which nearly happened once already, when a
formatter rewrapped the line a patch was targeting and the patch silently
no-opped.

Each test builds a throwaway tree with the real script in it, because the script
resolves its ADR directory from its own location.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "gen_adr_index.py"
ADRS = REPO / "docs" / "adr"


def build_tree(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    """A throwaway copy of the real repository layout the script expects."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "docs").mkdir()
    shutil.copy(SCRIPT, tmp_path / "scripts" / "gen_adr_index.py")
    shutil.copytree(ADRS, tmp_path / "docs" / "adr")
    return tmp_path


def run(tree: Path, *args: str, opt: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable]
    if opt:
        cmd.append("-OO")
    cmd += [str(tree / "scripts" / "gen_adr_index.py"), *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def adr(tree: Path, prefix: str) -> Path:
    return next((tree / "docs" / "adr").glob(f"{prefix}-*.md"))


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, f"anchor {old!r} not in {path.name}"
    path.write_text(text.replace(old, new, 1))


# --- the rule ADR 0000 declares and nothing checked -------------------------


@pytest.mark.xfail(strict=True, reason="title/heading agreement is not yet checked")
def test_title_heading_mismatch_refused(tmp_path: Path) -> None:
    """A frontmatter title that disagrees with its body heading is refused.

    Silently accepting it produces a wrong index while --check still reports the
    index up to date — the exact failure the strict parser exists to prevent,
    arriving through the one frontmatter rule with no checker.
    """
    tree = build_tree(tmp_path)
    edit(
        adr(tree, "0001"),
        "title: No model in the transport path",
        "title: Something else entirely",
    )

    result = run(tree, "--check")

    assert result.returncode != 0
    assert "0001-no-model-in-the-transport-path.md" in result.stderr
    assert "Something else entirely" in result.stderr
    assert "No model in the transport path" in result.stderr


@pytest.mark.xfail(strict=True, reason="title/heading agreement is not yet checked")
def test_title_heading_match_accepted(tmp_path: Path) -> None:
    """Agreement is accepted; a record with no heading at all is refused.

    Both halves matter. Every heading in this repository reads
    `# ADR NNNN — <title>` while the frontmatter carries only the title, so a
    naive equality check would refuse all eleven records. And a record with no
    heading is as much a defect as one whose heading disagrees — tolerating it
    silently would reproduce the bug in a new place, which is why the accepting
    half is asserted together with that refusal rather than on its own, where it
    would pass vacuously until the check existed.
    """
    tree = build_tree(tmp_path)

    clean = run(tree, "--check")
    assert clean.returncode == 0, clean.stderr
    assert "11 record(s)" in clean.stdout

    target = adr(tree, "0001")
    edit(target, "# ADR 0001 — No model in the transport path\n", "")
    missing = run(tree, "--check")
    assert missing.returncode != 0, "a record with no body heading was accepted"
    assert "0001-no-model-in-the-transport-path.md" in missing.stderr


REFUSALS = [
    ("0003", "id: 0003", "id: 0099", "frontmatter id"),
    ("0002", "status: accepted", "status: agreed", "status"),
    ("0002", "status: accepted", "status: superseded", "superseded-by"),
    ("0004", "superseded-by: none", "superseded-by: 0001", "superseded-by"),
    ("0008", "tags: [toolchain]", "owner: someone", "unknown frontmatter key"),
    ("0009", "date: 2026-09-14", "date: Sept 2026", "date"),
    ("0009", "tags: [process, git]", "tags: process, git", "inline list"),
    ("0005", "supersedes: []", "supersedes: [0042]", "unknown id"),
    ("0001", "title: No model in the transport path", "title: Drifted", "heading"),
]


@pytest.mark.xfail(strict=True, reason="the inventory's last entry has no refusal yet")
def test_existing_refusals_still_fire(tmp_path: Path) -> None:
    """Every fault the generator refuses, refused, with the file named.

    Asserted over the COMPLETE inventory rather than the pre-existing subset, so
    the list is red until the new refusal exists and stays a regression net
    afterwards. A refusal that does not name its offending file was a real defect
    here once, so the filename assertion is not decoration.

    The clean path is checked in the same place: idempotent regeneration is the
    other half of "the generator does not silently produce a wrong index", and it
    is only meaningful alongside the refusals that keep it honest.
    """
    tree = build_tree(tmp_path)
    index = tree / "docs" / "adr" / "README.md"
    before = index.read_text()
    assert run(tree, "--check").returncode == 0
    assert run(tree).returncode == 0
    assert index.read_text() == before, "regeneration is not idempotent"

    failures = []
    for prefix, old, new, expected in REFUSALS:
        case = build_tree(tmp_path / f"case-{len(failures)}-{prefix}-{expected[:12]}")
        edit(adr(case, prefix), old, new)
        result = run(case, "--check")
        if result.returncode == 0:
            failures.append(f"{expected}: accepted a tree it should refuse")
        elif expected not in result.stderr:
            failures.append(
                f"{expected}: refused, but the message does not say why: {result.stderr.strip()}"
            )
        elif ".md" not in result.stderr:
            failures.append(f"{expected}: refusal does not name the offending file")
    assert not failures, "\n".join(failures)


@pytest.mark.xfail(strict=True, reason="__doc__ read is unguarded under -OO")
def test_runs_under_optimised_interpreter(tmp_path: Path) -> None:
    """`python3 -OO` strips docstrings; reading __doc__ unguarded raises there."""
    tree = build_tree(tmp_path)

    result = run(tree, "--help", opt=True)

    assert result.returncode == 0, result.stderr
    assert "AttributeError" not in result.stderr

"""Tests for the private-content guard.

The guard exists so that a private finding copied into this public tree cannot
reach a merge unnoticed. These tests exercise its refusal and its silence, never
its source text: a test that grepped the implementation would pass on a version
that had been rewrapped into uselessness.

The marker literal is assembled from parts here, exactly as the guard assembles
it, and for the same reason — a test file spelling it out in one piece would be a
tracked file carrying the marker, and the guard would refuse the suite that tests
it. Assembling it independently rather than importing it from the guard is
deliberate: a test that imported the constant would still pass on a guard looking
for the wrong string.

Each test builds a throwaway git repository with the real guard tracked inside
it, because the guard reads the tracked-file list of the repository it sits in.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
GUARD_PATH = "scripts/check_private_content.py"
GUARD = REPO / GUARD_PATH

# The sentinel the private instance requires as the first line of every finding
# file, split so this file never carries it whole.
MARKER = "<!-- PRIVATE-DO-NOT" + "-PUBLISH -->"

FINDING = f"{MARKER}\nInvented field shapes, pasted where they must not be.\n"


def git(tree: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(tree), *args], check=True, capture_output=True, text=True
    )
    return done.stdout


def build_tree(tmp_path: Path, guard_at: str = GUARD_PATH) -> Path:
    """A throwaway git repository with the real guard tracked inside it.

    `guard_at` is a parameter because self-exclusion that depends on the guard's
    own path is precisely the defect one of these tests exists to catch.
    """
    tmp_path.mkdir(parents=True, exist_ok=True)
    dest = tmp_path / guard_at
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(GUARD, dest)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "public-note.md").write_text("An ordinary public document.\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "nobody@example.invalid")
    git(tmp_path, "config", "user.name", "Throwaway")
    track(tmp_path)
    return tmp_path


def track(tree: Path) -> None:
    git(tree, "add", "-A")


def run(tree: Path, guard_at: str = GUARD_PATH) -> subprocess.CompletedProcess[str]:
    """Run the guard by its path inside the tree, with no cwd of its own.

    Deliberately not run from inside `tree`: the guard must resolve the
    repository from its own location, not from whatever directory the gate
    happened to be invoked in.
    """
    return subprocess.run(
        [sys.executable, str(tree / guard_at)], capture_output=True, text=True
    )


def test_marked_file_is_refused(tmp_path: Path) -> None:
    """A tracked file carrying the marker fails the gate, named in the message.

    A refusal that does not name the file leaves the reader to search the tree
    for it, and a guard nobody can act on gets bypassed rather than obeyed.
    """
    tree = build_tree(tmp_path)
    (tree / "docs" / "copied-finding.md").write_text(FINDING)
    track(tree)

    result = run(tree)

    assert result.returncode != 0, "a tracked file carrying the marker was accepted"
    assert "docs/copied-finding.md" in result.stderr


def test_clean_tree_passes_and_guard_ignores_itself(tmp_path: Path) -> None:
    """A tree with nothing marked passes — including the guard's own definition.

    The guard necessarily knows the string it looks for, so it is the one file
    guaranteed to be near-miss. The tracked-list assertion is not decoration: if
    the guard were untracked in this fixture the passing half would be vacuous.
    """
    tree = build_tree(tmp_path)
    assert GUARD_PATH in git(tree, "ls-files").split(), (
        "the guard must be tracked here, or self-exclusion is not under test"
    )

    result = run(tree)

    assert result.returncode == 0, result.stderr


def test_self_exclusion_is_not_path_hardcoded(tmp_path: Path) -> None:
    """Renaming and moving the guard breaks neither half of its behaviour.

    Excluding a hard-coded path would pass the first assertion and fail here.
    The refusing half is asserted from the new location too, because a guard that
    went silent after the move would satisfy the passing half perfectly.
    """
    moved = "tools/checks/refuse_private_content.py"
    tree = build_tree(tmp_path, guard_at=moved)

    clean = run(tree, guard_at=moved)
    assert clean.returncode == 0, clean.stderr

    (tree / "docs" / "copied-finding.md").write_text(FINDING)
    track(tree)

    refused = run(tree, guard_at=moved)
    assert refused.returncode != 0, "the guard stopped refusing once it was moved"
    assert "docs/copied-finding.md" in refused.stderr

"""Tests that the toolchain versions this project declares are also enforced.

Two declarations in this repository were honoured by convention rather than by
anything that checked: the interpreter floor, which CI pinned and the Makefile
did not, and the workflow's actions, which floated on mutable tags while the
Python tools beside them were pinned exactly. Pinning either one without a test
leaves the same defect one commit further away — a pin nothing checks decays the
first time someone adds a step in a hurry.

These tests read the declaring files as text, deliberately. The declarations are
text: a SHA in a workflow, a floor in a Makefile, a sentence in an ADR. There is
no running object to interrogate, and the thing worth catching is precisely a
file that stopped saying what it used to say.
"""

from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "quality.yml"
MAKEFILE = REPO / "Makefile"
RUNTIME_ADR = REPO / "docs" / "adr" / "0008-implementation-runtime-python.md"

USES = re.compile(r"^\s*(?:-\s+)?uses:\s*(?P<ref>\S+)(?P<trailing>.*)$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
TAG_COMMENT = re.compile(r"#.*\bv\d+(\.\d+)*\b")


def action_uses() -> list[tuple[int, str, str]]:
    """Every `uses:` line in the workflow, as (line number, ref, trailing text)."""
    found = []
    for number, line in enumerate(WORKFLOW.read_text().splitlines(), start=1):
        match = USES.match(line)
        if match:
            found.append((number, match.group("ref"), match.group("trailing")))
    return found


def declared(path: Path, pattern: str) -> str | None:
    match = re.search(pattern, path.read_text(), re.MULTILINE)
    return match.group(1) if match else None


def test_every_workflow_action_is_pinned_to_a_commit_sha_naming_its_tag():
    """A tag can be repointed under a branch nobody touched; a commit cannot.

    The tag is kept as a comment beside the SHA rather than dropped, because a
    bare forty-character pin tells a reader nothing about which release they are
    on or whether the bump in front of them moves forward or back.
    """
    uses = action_uses()
    assert uses, f"no `uses:` lines parsed from {WORKFLOW} — suspect this parser"

    floating = [
        f"{WORKFLOW.name}:{number}: {ref}"
        for number, ref, _ in uses
        if not COMMIT_SHA.match(ref.partition("@")[2])
    ]
    assert not floating, "actions pinned to a mutable reference: " + "; ".join(floating)

    unlabelled = [
        f"{WORKFLOW.name}:{number}: {ref}"
        for number, ref, trailing in uses
        if not TAG_COMMENT.search(trailing)
    ]
    assert not unlabelled, "pins with no tag comment beside them: " + "; ".join(
        unlabelled
    )


def test_the_python_floor_agrees_across_the_adr_the_makefile_and_the_workflow():
    """One floor, declared in three places that cannot read each other.

    ADR 0008 is the decision; the Makefile enforces it locally; the workflow
    installs the interpreter CI runs. Nothing but this test stops one of the
    three from being bumped alone, which would restore exactly the local-versus-CI
    disagreement the single-definition Makefile exists to prevent.
    """
    adr = declared(RUNTIME_ADR, r"Python (\d+\.\d+) or later")
    assert adr, f"{RUNTIME_ADR.name} no longer states a floor in the expected words"

    makefile = declared(MAKEFILE, r"^PYTHON_FLOOR\s*:?=\s*(\d+\.\d+)")
    assert makefile == adr, (
        f"Makefile declares PYTHON_FLOOR={makefile!r}, ADR 0008 declares {adr!r}"
    )

    workflow = declared(WORKFLOW, r'python-version:\s*"(\d+\.\d+)"')
    assert workflow == adr, (
        f"workflow installs python-version={workflow!r}, ADR 0008 declares {adr!r}"
    )

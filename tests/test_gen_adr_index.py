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


REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "gen_adr_index.py"
ADRS = REPO / "docs" / "adr"


def build_tree(tmp_path: Path) -> Path:
    """A throwaway copy of the real repository layout the script expects."""
    tmp_path.mkdir(parents=True, exist_ok=True)
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


# One row per `raise AdrError` in the generator. `test_every_refusal_is_covered`
# below compares this inventory against the module's actual raise count, so a new
# refusal added without a row fails the suite rather than going unasserted. Each
# row is (edits, expected-fragment); edits are applied in order to one throwaway
# tree, because several refusals need two coordinated changes to reach.
REFUSALS: list[tuple[list[tuple[str, str, str]], str]] = [
    ([("0003", "---\nid: 0003", "id: 0003")], "no YAML frontmatter"),
    ([("0003", "\n---\n\n# ADR 0003", "\n\n# ADR 0003")], "not closed by"),
    (
        [
            (
                "0003",
                "tags: [verification, failure-posture]",
                "a bare line with no colon",
            )
        ],
        "not a 'key: value' line",
    ),
    (
        [("0003", "status: accepted", "status: accepted\nstatus: accepted")],
        "duplicate key",
    ),
    ([("0009", "tags: [process, git]", "tags: process, git")], "inline list"),
    ([("0008", "tags: [toolchain]", "owner: someone")], "unknown frontmatter key"),
    ([("0004", "date: 2026-09-17\n", "")], "missing frontmatter key"),
    ([("0001", "# ADR 0001 —", "# ADR 0002 —")], "heading id"),
    (
        [("0001", "title: No model in the transport path", "title: Drifted")],
        "disagrees with the",
    ),
    (
        [("0003", "id: 0003", "id: 0099"), ("0003", "# ADR 0003 —", "# ADR 0099 —")],
        "filename prefix",
    ),
    ([("0002", "status: accepted", "status: agreed")], "is not one of"),
    ([("0009", "date: 2026-09-14", "date: Sept 2026")], "is not YYYY-MM-DD"),
    (
        [("0002", "status: accepted", "status: superseded")],
        "superseded but superseded-by is 'none'",
    ),
    ([("0004", "superseded-by: none", "superseded-by: 0001")], "but status is"),
    (
        [
            ("0002", "status: accepted", "status: superseded"),
            ("0002", "superseded-by: none", "superseded-by: 0042"),
        ],
        "superseded-by unknown id",
    ),
    ([("0005", "supersedes: []", "supersedes: [0042]")], "supersedes unknown id"),
    (
        [
            ("0002", "status: accepted", "status: superseded"),
            ("0002", "superseded-by: none", "superseded-by: 0005"),
        ],
        "reciprocal",
    ),
    ([("0005", "supersedes: []", "supersedes: [0002]")], "reciprocal"),
    (
        [("0003", "# ADR 0003 — A missing capability is a result\n", "")],
        "body must open",
    ),
]


def test_existing_refusals_still_fire(tmp_path: Path) -> None:
    """Every refusal in the inventory fires, and names its offending file.

    A refusal that does not name its file was a real defect here once, so the
    filename assertion is not decoration. Idempotent regeneration is asserted in
    the same place: "does not silently produce a wrong index" has a clean half and
    a refusing half, and they are only meaningful together.
    """
    tree = build_tree(tmp_path / "clean")
    index = tree / "docs" / "adr" / "README.md"
    before = index.read_text()
    assert run(tree, "--check").returncode == 0
    assert run(tree).returncode == 0
    assert index.read_text() == before, "regeneration is not idempotent"

    failures = []
    for n, (edits, expected) in enumerate(REFUSALS):
        case = build_tree(tmp_path / f"case{n}")
        for prefix, old, new in edits:
            edit(adr(case, prefix), old, new)
        result = run(case, "--check")
        if result.returncode == 0:
            failures.append(f"{expected!r}: accepted a tree it should refuse")
        elif expected not in result.stderr:
            failures.append(
                f"{expected!r}: refused for another reason: {result.stderr.strip()[:120]}"
            )
        elif ".md" not in result.stderr:
            failures.append(f"{expected!r}: refusal does not name the offending file")
    assert not failures, "\n".join(failures)


def test_every_refusal_is_covered(tmp_path: Path) -> None:
    """The inventory tracks the module's refusal count.

    This is the one test that reads the source rather than the behaviour, and it
    does so deliberately: the claim under test IS about source coverage. Its job is
    to fail when someone adds a `raise` without adding a row, which is exactly the
    gap a behavioural test cannot see.

    Three raise sites are covered by dedicated tests below rather than by a row,
    because none is reachable by editing one record's text: the filename-pattern
    refusal needs a rename, the empty-directory refusal needs no records at all, and
    the duplicate-id refusal needs a second file.
    """
    source = SCRIPT.read_text()
    raises = source.count("raise AdrError")
    covered = len(REFUSALS) + 3
    assert covered == raises, (
        f"{raises} raise sites, {covered} covered. Add a REFUSALS row (or a dedicated "
        "test, and bump the constant here) for the new refusal."
    )


def test_filename_pattern_is_refused(tmp_path: Path) -> None:
    """Reached by a rename, so it has no inventory row."""
    tree = build_tree(tmp_path)
    adr(tree, "0007").rename(tree / "docs" / "adr" / "0007_Bad_Name.md")

    result = run(tree, "--check")

    assert result.returncode != 0
    assert "filename must be" in result.stderr
    assert "0007_Bad_Name.md" in result.stderr


def test_empty_directory_is_refused(tmp_path: Path) -> None:
    """Reached by removing every record, so it has no inventory row."""
    tree = build_tree(tmp_path)
    for f in (tree / "docs" / "adr").glob("0*.md"):
        f.unlink()

    result = run(tree, "--check")

    assert result.returncode != 0
    assert "no ADRs found" in result.stderr


def test_duplicate_id_is_refused(tmp_path: Path) -> None:
    """Two files sharing a four-digit prefix — needs a second file, not an edit."""
    tree = build_tree(tmp_path)
    twin = tree / "docs" / "adr" / "0003-a-second-record-with-the-same-id.md"
    twin.write_text(adr(tree, "0003").read_text())

    result = run(tree, "--check")

    assert result.returncode != 0
    assert "already used by" in result.stderr


def test_runs_under_optimised_interpreter(tmp_path: Path) -> None:
    """`python3 -OO` strips docstrings; reading __doc__ unguarded raises there."""
    tree = build_tree(tmp_path)

    result = run(tree, "--help", opt=True)

    assert result.returncode == 0, result.stderr
    assert "AttributeError" not in result.stderr


def test_frontmatter_comment_cannot_pose_as_a_heading(tmp_path: Path) -> None:
    """A `#` line inside the frontmatter is not the body heading.

    The first version of this check scanned the whole document, so a record whose
    real heading had been deleted was ACCEPTED as long as a frontmatter comment
    looked like one — fail-open, and the exact silent acceptance the check exists
    to close. Scoping the scan to the body is what fixes it; this keeps it fixed.
    """
    tree = build_tree(tmp_path)
    target = adr(tree, "0003")
    edit(
        target,
        "tags: [verification, failure-posture]",
        "tags: [verification, failure-posture]\n# ADR 0003 — A missing capability is a result",
    )
    edit(
        target,
        "# ADR 0003 — A missing capability is a result\n\n## Decision",
        "\n## Decision",
    )

    result = run(tree, "--check")

    assert result.returncode != 0, "a frontmatter comment passed as the body heading"
    assert "0003-a-missing-capability-is-a-result.md" in result.stderr
    assert "body must open" in result.stderr


def test_a_heading_later_in_the_body_does_not_satisfy_the_rule(tmp_path: Path) -> None:
    """The heading must be FIRST in the body, not merely present somewhere in it.

    This guards the half of the rule that scoping alone does not. Restore an
    anywhere-in-the-body search and this record is accepted again: its body opens
    with prose, and the only matching heading sits inside a fenced example further
    down — which is how a record quoting the format would slip through, or a draft
    note above the heading would.

    Synthetic on purpose. An earlier version of this test asserted that the real
    ADR 0000 contained such an example; it does not — its only mention is a table
    row carrying the literal `NNNN`, which the four-digit pattern cannot match. The
    claim was false and the assertion pinned nothing.
    """
    tree = build_tree(tmp_path)
    target = adr(tree, "0001")
    edit(
        target,
        "# ADR 0001 — No model in the transport path\n",
        "> Draft note: still being written.\n\n```\n# ADR 0001 — No model in the transport path\n```\n",
    )

    result = run(tree, "--check")

    assert result.returncode != 0, (
        "a heading found only later in the body satisfied the rule"
    )
    assert "body must open" in result.stderr
    assert "0001-no-model-in-the-transport-path.md" in result.stderr

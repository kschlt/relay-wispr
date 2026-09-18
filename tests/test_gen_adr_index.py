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

import ast
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping
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
    naive equality check would refuse all twelve records. And a record with no
    heading is as much a defect as one whose heading disagrees — tolerating it
    silently would reproduce the bug in a new place, which is why the accepting
    half is asserted together with that refusal rather than on its own, where it
    would pass vacuously until the check existed.
    """
    tree = build_tree(tmp_path)

    clean = run(tree, "--check")
    assert clean.returncode == 0, clean.stderr
    assert "12 record(s)" in clean.stdout

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


# --- what the coverage check counts, and how it accounts for it -------------
#
# `test_every_refusal_is_covered` is built on these three, and the proofs below
# exercise them directly rather than by inspection. Each was written failing
# first, and each was then observed catching the mutation it exists to catch.


def count_raise_sites(source: str) -> int:
    """How many places `source` raises — read structurally, not textually.

    This replaces `source.count("raise AdrError")`, which was wrong in both
    directions: a refusal built in one statement and raised in the next is a
    raise it misses, and the same words in a docstring are a raise it invents.
    Every raise statement counts, not only the ones spelled `raise AdrError`: a
    refusal expressed some other way still needs something asserting it, and
    counting it here demands a row rather than excusing one.
    """
    return sum(1 for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Raise))


def dedicated_refusal_scenarios() -> dict[str, tuple[Callable[[Path], str], str]]:
    """Dedicated test name -> (build the offending tree, expected message fragment).

    These are the refusals no inventory row can reach, because none of them is
    reachable by editing one record's text: the filename-pattern refusal needs a
    rename, the empty-directory refusal needs no records at all, and the
    duplicate-id refusal needs a second file. Each setup returns the path text its
    refusal must name, so the dedicated tests carry the same "names what it
    refused" assertion the rows carry.

    The empty-directory refusal has no offending FILE — the directory it searched
    is what it refused, and naming that is the same guarantee, not a weaker one.
    """

    def rename_one(tree: Path) -> str:
        adr(tree, "0007").rename(tree / "docs" / "adr" / "0007_Bad_Name.md")
        return "0007_Bad_Name.md"

    def empty_the_directory(tree: Path) -> str:
        for record in (tree / "docs" / "adr").glob("0*.md"):
            record.unlink()
        return str((tree / "docs" / "adr").resolve())

    def add_a_twin(tree: Path) -> str:
        twin = tree / "docs" / "adr" / "0003-a-second-record-with-the-same-id.md"
        twin.write_text(adr(tree, "0003").read_text())
        return twin.name

    return {
        "test_filename_pattern_is_refused": (rename_one, "filename must be"),
        "test_empty_directory_is_refused": (empty_the_directory, "no ADRs found"),
        "test_duplicate_id_is_refused": (add_a_twin, "already used by"),
    }


def covered_refusals(namespace: Mapping[str, object] | None = None) -> int:
    """Inventory rows, plus the dedicated refusal tests that actually exist.

    Counting the dedicated tests rather than allowing a constant `+ 3` is what
    ties the allowance to them: delete one and this drops by one, so
    `test_every_refusal_is_covered` fails instead of quietly covering less.
    `namespace` exists so that deletion can be simulated without editing the file.
    """
    ns = globals() if namespace is None else namespace
    present = sum(1 for name in dedicated_refusal_scenarios() if callable(ns.get(name)))
    return len(REFUSALS) + present


def assert_dedicated_refusal(tmp_path: Path, name: str) -> None:
    """Run one dedicated refusal scenario and assert it refuses, naming what it refused."""
    setup, fragment = dedicated_refusal_scenarios()[name]
    tree = build_tree(tmp_path)
    offender = setup(tree)

    result = run(tree, "--check")

    assert result.returncode != 0, "accepted a tree it should refuse"
    assert fragment in result.stderr
    assert offender in result.stderr, f"refusal does not name {offender}"


def test_every_refusal_is_covered(tmp_path: Path) -> None:
    """The inventory tracks the module's refusal count.

    This is the one test that reads the source rather than the behaviour, and it
    does so deliberately: the claim under test IS about source coverage. Its job is
    to fail when someone adds a `raise` without adding a row, which is exactly the
    gap a behavioural test cannot see.

    It counts structurally and accounts by existence, because both halves of the
    claim were once fooled by mutation: a two-step raise slipped past a literal
    string count, and the dedicated tests were allowed for by a hand-kept `+ 3`
    that stayed 3 after one of them was deleted. The raise sites reached by
    something other than editing one record's text are named by
    `dedicated_refusal_scenarios`, which is also what the allowance counts.
    """
    raises = count_raise_sites(SCRIPT.read_text())
    covered = covered_refusals()
    assert covered == raises, (
        f"{raises} raise sites, {covered} covered. Add a REFUSALS row for the new "
        "refusal — or, if it cannot be reached by editing one record, a dedicated "
        "test and an entry for it in dedicated_refusal_scenarios()."
    )


def test_raise_counting_is_structural() -> None:
    """Refusals are counted from the parse tree, not from the characters.

    A literal `source.count("raise AdrError")` is wrong in both directions, and
    both directions are asserted here: a refusal built in one statement and
    raised in the next is a raise the count misses, and the same words sitting in
    a docstring are a raise the count invents. Throwaway source is used rather
    than the real generator, because the generator is not this item's subject and
    must not grow a contrived raise to be counted.
    """
    two_step = "def f():\n    err = AdrError('x')\n    raise err\n"
    prose = (
        'def f():\n    """Callers see this when we raise AdrError."""\n    return 1\n'
    )

    assert count_raise_sites(two_step) == 1, "a two-step raise was not counted"
    assert count_raise_sites(prose) == 0, "prose mentioning the words was counted"

    # The literal count answers both the other way round. Asserting that here is
    # what stops this test passing vacuously if the old counting ever comes back.
    assert two_step.count("raise AdrError") == 0
    assert prose.count("raise AdrError") == 1


def test_dedicated_tests_are_accounted_by_existence() -> None:
    """Deleting a dedicated refusal test breaks the coverage check.

    The allowance for refusals reached by a rename, an empty directory or a second
    file used to be the literal `+ 3`, which stays 3 after one of those tests is
    deleted — the refusal then has nothing asserting it and the suite is green.
    Deletion is simulated against a namespace rather than performed on the file,
    so the check is exercised for every one of them in a single run.
    """
    raises = count_raise_sites(SCRIPT.read_text())
    assert covered_refusals() == raises, "coverage does not hold before any deletion"

    for name in dedicated_refusal_scenarios():
        assert callable(globals().get(name)), f"{name} is accounted for but not defined"
        without = {k: v for k, v in globals().items() if k != name}
        assert covered_refusals(without) != raises, (
            f"deleting {name} left the coverage check satisfied"
        )


def test_dedicated_refusals_name_their_file(tmp_path: Path) -> None:
    """Every dedicated refusal names what it refused, as the inventory rows do.

    A refusal that did not name its file was a real defect in this tool once, so
    the guarantee should not depend on which path a refusal happens to be reached
    by. Asserted here independently of the shared helper the dedicated tests call,
    so dropping the assertion from that helper fails this test too.

    The empty-directory refusal has no offending FILE — the directory it searched
    is what it refused, and naming that is the same guarantee, not a weaker one.
    """
    failures = []
    for n, (name, (setup, fragment)) in enumerate(
        dedicated_refusal_scenarios().items()
    ):
        tree = build_tree(tmp_path / f"dedicated{n}")
        offender = setup(tree)
        result = run(tree, "--check")
        if result.returncode == 0:
            failures.append(f"{name}: accepted a tree it should refuse")
        elif fragment not in result.stderr:
            failures.append(
                f"{name}: refused for another reason: {result.stderr.strip()[:120]}"
            )
        elif offender not in result.stderr:
            failures.append(f"{name}: refusal does not name {offender}")
    assert not failures, "\n".join(failures)


def test_filename_pattern_is_refused(tmp_path: Path) -> None:
    """Reached by a rename, so it has no inventory row."""
    assert_dedicated_refusal(tmp_path, "test_filename_pattern_is_refused")


def test_empty_directory_is_refused(tmp_path: Path) -> None:
    """Reached by removing every record, so it has no inventory row."""
    assert_dedicated_refusal(tmp_path, "test_empty_directory_is_refused")


def test_duplicate_id_is_refused(tmp_path: Path) -> None:
    """Two files sharing a four-digit prefix — needs a second file, not an edit."""
    assert_dedicated_refusal(tmp_path, "test_duplicate_id_is_refused")


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

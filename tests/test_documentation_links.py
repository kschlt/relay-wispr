"""Tests for the links between this repository's documents.

Two facts about the tree, both checkable without judgement: a relative link
either resolves or it does not, and a decision record either has a document
pointing at it or it does not. The shape of the prose around them is a different
kind of question and is deliberately not checked here.

The mistake the first test catches is quiet and easy to make: a document under
`docs/` links a record as `adr/NNNN-....md` while a document at the root links
the same record as `docs/adr/NNNN-....md`. Getting that backwards produces a link
that reads correctly in the source and resolves nowhere.

The second test states the claim the cross-links exist for — that a document
resting on a recorded decision points at it — as something measured rather than
asserted. The generated index is excluded: it links every record by construction,
so counting it would make the claim true for a record no human document mentions.

Tracked files are the unit, as they are for the private-content guard: what is
published is what is committed.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent

# Generated, so it is evidence of nothing: the index links every record whether
# or not any document does.
GENERATED = ("docs/adr/README.md",)

RECORD_NAME = re.compile(r"^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(\s*([^)\s]+)\s*\)")
NOT_RELATIVE = re.compile(r"^(?:[a-z][a-z0-9+.\-]*:|//|#)")


def tracked_markdown() -> list[str]:
    """Every tracked markdown file, as a repository-relative POSIX path."""
    done = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "--", "*.md"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in done.stdout.splitlines() if line]


def relative_links() -> list[tuple[str, int, str]]:
    """Every relative markdown link, as (source file, line number, target)."""
    found = []
    for source in tracked_markdown():
        text = (REPO / source).read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            for target in MARKDOWN_LINK.findall(line):
                if not NOT_RELATIVE.match(target):
                    found.append((source, number, target))
    return found


def destination(source: str, target: str) -> Path:
    """Where a link in `source` points, with any fragment dropped."""
    return (REPO / source).parent / target.partition("#")[0]


def decision_records() -> list[str]:
    return sorted(
        path
        for path in tracked_markdown()
        if path.startswith("docs/adr/") and RECORD_NAME.match(Path(path).name)
    )


def test_every_relative_link_resolves():
    links = relative_links()
    assert links, "no relative links collected at all — suspect this collector"

    broken = [
        f"{source}:{number}: {target}"
        for source, number, target in links
        if not destination(source, target).exists()
    ]
    assert not broken, "links that resolve nowhere:\n" + "\n".join(broken)


@pytest.mark.xfail(strict=True, reason="0008, 0009 and 0010 carry no inbound link")
def test_every_decision_record_is_linked_from_a_document():
    records = decision_records()
    assert records, "no decision records found at all — suspect this collector"

    linked = set()
    for source, _number, target in relative_links():
        if source in GENERATED:
            continue
        resolved = destination(source, target).resolve()
        try:
            pointed_at = resolved.relative_to(REPO.resolve()).as_posix()
        except ValueError:
            continue
        if pointed_at != source:
            linked.add(pointed_at)

    missing = [record for record in records if record not in linked]
    assert not missing, "records no document links to:\n" + "\n".join(missing)

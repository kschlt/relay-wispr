#!/usr/bin/env python3
"""Refuse the tree when a tracked file carries the private-content marker.

This repository is public and permanent, and it declares that it carries no real
source data. Until now that was a rule with no mechanism, which is a habit — and
habits fail exactly when attention is elsewhere. The realistic leak is nobody
deciding to publish private material: it is a measurement copied into a document
to explain a point, with the sensitive part carried along unnoticed.

The maintainer's private findings are required to open with a marker. This check
refuses any tracked file carrying it, so a copy that brings its header along
fails the gate instead of merging.

**What it catches and what it does not.** It catches a copied finding that
brings its marker along, which is the common case. It does not catch a marker
that was deliberately or accidentally stripped, and it cannot recognise real
content that was never marked — no heuristic for name-shaped or
transcript-shaped text is attempted here, because it would produce false
confidence and false refusals alike. It also sees only *tracked* files, so
locally it judges what is staged or committed rather than what is merely written
to disk; CI, which runs against the commit, sees everything the pull request
would land. The honest claim is narrow: marked content cannot pass. The care
that actually does the work is that findings are never written here at all.

Read-only by construction: it refuses, and never edits or redacts a file.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# The sentinel the private findings directory requires as the first line of
# every finding file, assembled from two fragments.
#
# That assembly IS the self-exclusion. This file is tracked and would otherwise
# be the one file guaranteed to carry what it looks for; splitting the literal
# means the marker never appears whole in this source, so the check cannot match
# itself. It is a property of the text rather than an entry in a path exclusion
# list, which is why it keeps holding when this file is renamed or moved.
MARKER = ("<!-- PRIVATE-DO-NOT" + "-PUBLISH -->").encode()

HERE = Path(__file__).resolve().parent

REMEDY = """
Private findings live only in the maintainer's private instance, never here.

Remove the file from this repository. Stripping the marker is not the fix — the
marker is a label, and the content underneath it is what must not be published.
If the point needs making publicly, restate it as a synthetic example.

This repository keeps history forever and is world-readable through every fork,
so a commit that lands this cannot be withdrawn.
""".strip()


def repo_root() -> Path:
    """The work repository this script sits in, resolved from its own location.

    Not from the working directory: the gate may be invoked from anywhere, and a
    check that scanned whatever tree it happened to be started in would report a
    clean result about the wrong repository.
    """
    done = subprocess.run(
        ["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if done.returncode != 0:
        raise SystemExit(
            "privacy: cannot determine the repository from "
            f"{HERE} — git said: {done.stderr.strip()}\n"
            "This check reads the tracked-file list and has no answer without "
            "it. It refuses rather than reporting a tree it could not read as "
            "clean."
        )
    return Path(done.stdout.strip())


def tracked_files(root: Path) -> list[str]:
    done = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        text=True,
    )
    if done.returncode != 0:
        raise SystemExit(
            f"privacy: cannot list tracked files in {root} — "
            f"git said: {done.stderr.strip()}"
        )
    return [path for path in done.stdout.split("\0") if path]


def carries_marker(path: Path) -> bool:
    try:
        return MARKER in path.read_bytes()
    except (OSError, ValueError):
        # A tracked path that cannot be read as a file here — a dangling symlink,
        # a submodule directory — carries no marker to find. Reporting it as an
        # offender would be a false refusal.
        return False


def main() -> int:
    root = repo_root()
    tracked = tracked_files(root)
    offenders = [name for name in tracked if carries_marker(root / name)]

    if offenders:
        print(
            "privacy: refused — private content must not reach this tree",
            file=sys.stderr,
        )
        for name in offenders:
            print(f"  {name}: carries the private-content marker", file=sys.stderr)
        print(f"\n{REMEDY}", file=sys.stderr)
        return 1

    print(f"privacy: {len(tracked)} tracked file(s), no private-content marker")
    return 0


if __name__ == "__main__":
    sys.exit(main())

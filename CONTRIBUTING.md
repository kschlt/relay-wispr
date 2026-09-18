# Contributing

Thanks for looking. Please read this first — the project is at an unusual
stage, and what is useful right now is narrower than usual.

## Current stage

The **product** is still design documents only: there is no package, no CLI,
no library, and no adapter code to run.

The repository does now carry a little tooling of its own — an ADR index
generator and a quality gate that runs on every pull request. If you are only
reading, clone it and read; nothing needs setting up. If you are changing
files, run the gate before you push:

```
make quality
```

It needs `ruff` and `pytest` at the pinned versions in `requirements-dev.txt`,
and it checks rather than rewrites, so a green run means the tree was already
clean. `make help` lists the rest.
[ADR 0008](docs/adr/0008-implementation-runtime-python.md) also names `uv`, but
nothing here requires or checks it — `requirements-dev.txt` records which of the
toolchain declarations are enforced and which are deliberately advisory.

The gate also refuses to run at all on an interpreter below the version this
project targets, naming the version it requires and the one it found. There is
no skip and no exception: a green run on an older interpreter is a local
verdict CI can contradict, which is worse than not having run it. If your
default `python3` is older than the floor, point the gate at a newer one — the
refusal says how.

The immediate work is **verifying what the Wispr Flow MCP server can actually
do** — for discovery, reading, pagination, and stable identity, treating
meetings and Scratchpad notes as separate questions. Implementation decisions
depend on those answers, so making them now would be guessing.

## What helps most right now

- **Measured connector behaviour.** If you have used the Wispr Flow MCP server
  and know what it supports — especially around incremental search, pagination
  stability, identifier stability, and whether full bodies can be read — that
  is the single most valuable contribution. Please say how you observed it.
- **Boundary critique.** If the split in
  [docs/architecture.md](docs/architecture.md) is wrong — a responsibility on
  the wrong side, a non-goal that cannot hold — argue it before it is code.
  The reasoning you would be arguing against is in
  [docs/adr/](docs/adr/README.md), including what each decision rejected and
  what would reopen it. Read the relevant record first; it may already answer
  you, and if it does not, it tells you exactly what the counter-argument has
  to beat.
- **Privacy review.** If
  [docs/privacy-and-security.md](docs/privacy-and-security.md) overclaims
  anything, that is a defect worth reporting.

## What is not wanted yet

- Implementation PRs. Until capability verification is done, code would encode
  assumptions we have not tested.
- Features listed as non-goals in [VISION.md](VISION.md). Routing, summarising,
  multi-source support, and inbox behaviour are deliberately other components'
  jobs. Proposals to move that line are welcome as discussion; PRs implementing
  the move are not.

## Working on it

- **Open an issue first** for anything beyond a typo. At this stage, agreement
  on the boundary matters more than the diff.
- **Use a branch and a pull request.** The default branch takes no direct
  pushes; every change after the initial commit lands through a PR
  ([ADR 0009](docs/adr/0009-changes-reach-main-through-pull-requests.md)).
- **One concern per PR**, with a description saying what changed and why.

## Changing a decision

Decisions live in [docs/adr/](docs/adr/README.md), one per record.

An accepted ADR is never rewritten to say something else — its decision is a
historical fact, and the reasoning that looked right at the time is the most
useful thing it carries. Changing course means a **new** record that supersedes
the old one, naming it. [ADR 0000](docs/adr/0000-record-architecture-decisions.md)
has the format and the rules.

Two practical notes: `docs/adr/README.md` is generated — edit frontmatter and
run `make adr-index`, never the index itself. And if a change you are proposing
contradicts an accepted ADR, say so explicitly and name it. Silently working
around one is the failure the directory exists to prevent.

## Documentation standards

The documents in this repository are the product right now, so they are held to
a few rules. How the prose is formatted is not among them — that is left to
review rather than checked by a gate
([ADR 0011](docs/adr/0011-prose-formatting-is-left-to-review.md)). The rules:

- **Do not claim unverified behaviour.** If connector support is unknown, the
  text says it is unknown. "Supports Scratchpad notes" is not something this
  project gets to say until it has been measured.
- **No usage or installation instructions for software that does not exist.**
  A command in a README is a promise.
- **Examples are synthetic.** Never paste a real transcript, a real note, a real
  meeting title, an account identifier, or any other real source data into this
  repository — including in issues and PR descriptions. Invent an example
  instead.

  One narrow part of this is checked rather than trusted: `make quality` refuses
  the tree when a tracked file carries the marker that the maintainer's private
  verification findings are required to open with, and names the file. It
  catches a finding copied in with its header attached — the accident, not the
  decision. It does not catch a stripped marker, it cannot recognise real
  content that was never marked, and it deliberately makes no attempt to guess
  at transcript-shaped text, which would refuse innocent changes and still miss
  real ones. The rest of this rule rests on care, as it did before.
- **Nothing personal or private.** No credentials, no private hostnames, no
  local filesystem paths, no private repository names, no personal
  infrastructure details. This repository is public and permanent.

## Conduct

Be straightforward and civil. Critique designs, not people. Maintainers may
remove contributions or contributors that make the project worse to work on.

## Licensing of contributions

By contributing, you agree your contributions are licensed under the
[Apache License 2.0](LICENSE), matching the project.

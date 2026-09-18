# Agent instructions — relay-wispr

Guidance for AI coding agents working in this repository. Humans: see
[CONTRIBUTING.md](CONTRIBUTING.md), which these rules sit on top of.

## Read this first

**This repository is public and permanent.** Anything committed here is
world-readable forever, including through history and forks. There is no
private mode and no taking it back.

**This project is pre-alpha and contains no code.** It is a set of design
documents. Do not write implementation, scaffolding, build files, packaging, or
tests unless an issue explicitly asks for them. The next step is verifying what
the Wispr Flow MCP server can do, not building on top of assumptions.

## Hard rules for anything you commit here

Never commit, in files, commit messages, issues, or PR descriptions:

- Credentials, tokens, API keys, or account identifiers.
- Real source data — transcripts, note bodies, meeting titles, participant
  names, or source-system identifiers. **Use synthetic examples only.**
- Private repository names, internal hostnames, or anyone's personal
  infrastructure topology.
- Local filesystem paths from a contributor's machine.
- Output pasted from a connected tool or connector.

If you are unsure whether something is safe to publish, leave it out and say
why.

### The one rule with a mechanism behind it

`make quality` refuses the tree when a tracked file carries the marker that the
maintainer's private findings are required to open with (`scripts/check_private_content.py`).
It runs in the gate, so it fires locally and in CI on every pull request without
anyone choosing to run it, and the refusal names the file.

**What it catches and what it does not.** It catches a copied finding that
brings its marker along — the common case, and the one that happens by
accident. It does not catch a marker that was stripped, and it cannot recognise
real source data that was never marked; no heuristic for transcript-shaped or
name-shaped text is attempted, because it would produce false confidence and
false refusals alike. It sees only *tracked* files, so locally it judges what is
staged or committed rather than what is merely written to disk. Every other rule
above is unmechanised and rests on your care. Treat the guard as a seatbelt, not
a vault: a check believed to be complete replaces the attention that does the
real work.

### The interpreter the gate runs on

`make quality` refuses any interpreter below the floor ADR 0008 declares,
naming the required version and the one it found. It is checked when the
Makefile is parsed, so every target passes through it and there is nothing to
forget to call.

If it refuses, point it at a conforming interpreter. Do not lower the floor, do
not add a skip, and do not special-case the environment — each of those puts
the defect back somewhere harder to see. The floor is an accepted decision, so
changing it means a superseding ADR, not an edit to the Makefile.

## Accuracy rules

- **Do not describe unverified behaviour as supported.** Wispr MCP capabilities
  have not been measured. Scratchpad support in particular is an open question,
  and no document here may imply otherwise.
- **Do not add installation or usage commands.** There is no software to
  install or run. A command in a README is a promise this project cannot keep
  yet.
- **Do not add badges, version numbers, or release claims** for things that do
  not exist.
- Keep the pre-alpha status notices in `README.md`, `VISION.md`, and the `docs/`
  files intact. Removing them is a regression.

## Scope discipline

[VISION.md](VISION.md) lists non-goals: routing, inbox behaviour, meeting
intelligence, multi-source ingestion, general MCP tooling. Do not quietly widen
scope into them. If a change seems to require crossing that line, stop and
raise it instead.

## Git workflow

The initial commit is the only commit made directly on the default branch.
Everything after it goes through a branch and a pull request — one concern per
PR, with a description of what changed and why.

Commit subjects follow [Conventional Commits](https://www.conventionalcommits.org)
(`docs:`, `chore:`, `feat:`, `fix:`).

## Repository layout

```
README.md                        entry point and current status
VISION.md                        direction, goals, non-goals, success criteria
CONTRIBUTING.md                  how to contribute at this stage
SECURITY.md                      vulnerability reporting
LICENSE                          Apache-2.0
docs/architecture.md             boundaries, responsibilities, data flow
docs/privacy-and-security.md     data handling and its honest limits
docs/adr/                        architecture decision records (see below)
scripts/gen_adr_index.py         regenerates docs/adr/README.md
scripts/check_private_content.py refuses a tracked file carrying the private marker
```

`scripts/` holds repository tooling, not product code. The "no code" status
above is about the adapter: there is still no package, no CLI, and no library.

## Architecture decisions

Decisions live in `docs/adr/`, one decision per record, with YAML frontmatter and
a status. [ADR 0000](docs/adr/0000-record-architecture-decisions.md) defines the
format, the four states, and the rules — read it before adding or changing one.

Four things to get right:

- **Never edit `docs/adr/README.md`.** It is generated. Change frontmatter and run
  `make adr-index`. The quality gate checks it and refuses a stale index.
- **Never rewrite an accepted ADR to say something else.** Its decision is a
  historical fact. Changing course means a new ADR that supersedes it. Fixing a
  typo or a dead link is not changing the decision.
- **Supersession is reciprocal** and the generator refuses a one-sided link.
- **One decision per record.** Two arguments in one Consequences section means two
  ADRs.

Before proposing something that contradicts an accepted ADR, say so explicitly and
name the ADR. Silently working around one is the failure this directory exists to
prevent.

## Workflow tooling

<!-- aos:begin id=task-workflow rev=1 managed by aos touchpoint writer - do not edit by hand -->
This project's backlog, session protocol, and workflow tooling are managed by **aos** (the meta-workflow layer mounted at `.aos/`). Machinery lives at `.aos/sys/`; the authoritative session protocol is `.aos/sys/core/CLAUDE.md`. Instance state (backlog, specs, work-log) lives in the nested state repo at `.aos/` (host-ignored, its own git history). Do not edit this managed region by hand.
<!-- aos:end id=task-workflow -->

That layer is the maintainer's local workflow tooling. It is **not a dependency
of this project**: relay-wispr does not require it to be built, used, or
contributed to, and nothing in the public tree may be written to depend on it.
Contributors will not have it, and that is expected — ignore it if it is not
present.

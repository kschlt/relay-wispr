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
```

## Workflow tooling

<!-- aos:begin id=task-workflow rev=1 managed by aos touchpoint writer - do not edit by hand -->
This project's backlog, session protocol, and workflow tooling are managed by **aos** (the meta-workflow layer mounted at `.aos/`). Machinery lives at `.aos/sys/`; the authoritative session protocol is `.aos/sys/core/CLAUDE.md`. Instance state (backlog, specs, work-log) lives in the nested state repo at `.aos/` (host-ignored, its own git history). Do not edit this managed region by hand.
<!-- aos:end id=task-workflow -->

That layer is the maintainer's local workflow tooling. It is **not a dependency
of this project**: relay-wispr does not require it to be built, used, or
contributed to, and nothing in the public tree may be written to depend on it.
Contributors will not have it, and that is expected — ignore it if it is not
present.

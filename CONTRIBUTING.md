# Contributing

Thanks for looking. Please read this first — the project is at an unusual
stage, and what is useful right now is narrower than usual.

## Current stage

This repository holds **design documents only**. There is no build, no test
suite, no package, and no code to run. There is therefore nothing to set up:
clone it and read.

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
  pushes; every change after the initial commit lands through a PR.
- **One concern per PR**, with a description saying what changed and why.

## Documentation standards

The documents in this repository are the product right now, so they are held to
a few rules:

- **Do not claim unverified behaviour.** If connector support is unknown, the
  text says it is unknown. "Supports Scratchpad notes" is not something this
  project gets to say until it has been measured.
- **No usage or installation instructions for software that does not exist.**
  A command in a README is a promise.
- **Examples are synthetic.** Never paste a real transcript, a real note, a real
  meeting title, an account identifier, or any other real source data into this
  repository — including in issues and PR descriptions. Invent an example
  instead.
- **Nothing personal or private.** No credentials, no private hostnames, no
  local filesystem paths, no private repository names, no personal
  infrastructure details. This repository is public and permanent.

## Conduct

Be straightforward and civil. Critique designs, not people. Maintainers may
remove contributions or contributors that make the project worse to work on.

## Licensing of contributions

By contributing, you agree your contributions are licensed under the
[Apache License 2.0](LICENSE), matching the project.

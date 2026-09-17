---
id: 0008
title: Implementation runtime is Python
status: accepted
date: 2026-09-17
tags: [toolchain]
supersedes: []
superseded-by: none
---

# ADR 0008 — Implementation runtime is Python

## Decision

The adapter will be written in **Python 3.12 or later**, using **uv** for environments,
**ruff** for linting and formatting, and **pytest** for tests.

No code exists yet. This records the decision, not a working project.

## Consequences

The adapter is I/O glue — speak MCP, receive JSON, write bytes, emit a small record — with
essentially no computation. That shape did most of the deciding:

- The context rule of ADR 0001 is trivially expressible: connector response to file write,
  in ordinary code, with no streaming machinery needed to keep a model out of the path.
- The official MCP SDK for Python is mature and idiomatic. This project is not on the
  frontier of transports, so adequate and boring is the right trade.
- Contributor legibility: someone who would care about a Wispr adapter is likelier to read
  Python than Go.

**Alternatives, and what each lost on.** *TypeScript*: the reference MCP SDK is usually
first to receive new transport and authentication features, but the build step and
dependency tree are heavy for a tool this small. *Go*: a single static binary is the best
deployment story of the four and genuinely tempting for a scheduled process on a personal
machine, but the MCP SDK is less mature and the ceremony is disproportionate to what is
mostly JSON shuffling. *Rust*: nothing here is performance- or memory-constrained.

**What would reopen this.** If the adapter ends up running on a schedule and Python
environment drift becomes the recurring operational annoyance, Go's single binary is the
real argument. That is a rewrite worth weighing only once the thing works at all — and it
would arrive as an ADR superseding this one, not as an edit to it.

Test discipline note: the expected-failure marker used for red-before-green carries
`strict=True`. Without it, a test that unexpectedly passes does not fail the suite, which
defeats the purpose of writing it red first.

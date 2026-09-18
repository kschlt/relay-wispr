---
id: 0005
title: The adapter owns no collection state
status: accepted
date: 2026-09-14
tags: [boundary, state]
supersedes: []
superseded-by: none
---

# ADR 0005 — The adapter owns no collection state

## Decision

relay-wispr **reads** prior collection state — previously seen source identifiers, or a
cursor — and returns what a caller needs to advance it. It does not own the store that
state lives in, nor delivery history, nor an item's downstream fate.

The adapter is close to stateless by design.

## Consequences

An adapter that owned run state would have to know the shape of the pipeline it sits in, and
a second adapter for a second vendor would have to reimplement that store identically. That
coupling is exactly what the source-independent boundary exists to prevent.

The cost lands on idempotence: the property depends on state the adapter does not control.
The storage contract therefore has to specify what the adapter does when that state is
absent or stale, rather than assuming it is always present and correct.

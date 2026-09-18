---
id: 0002
title: Verify before designing
status: accepted
date: 2026-09-14
tags: [process, verification]
supersedes: []
superseded-by: none
---

# ADR 0002 — Verify before designing

## Decision

Connector behaviour is **measured** before anything is built on it. The record schema, the
payload storage contract, and the idempotence mechanism are designed from findings — not
from documentation, not from inference, and not from what a response happened to contain
once.

No design work is ready to start before the measurement it consumes exists. This is enforced
by dependency ordering in the backlog rather than by intent.

## Consequences

The project starts slower, and cannot ship a working adapter until measurement is done. That
is accepted deliberately. The alternative is encoding untested assumptions about which
identifiers are stable and whether timestamps are trustworthy — and those two assumptions are
exactly what decides whether incremental collection is possible at all.

It also binds the documentation. An unverified capability is described as unverified, and no
claim of support is made for a surface nobody has measured.

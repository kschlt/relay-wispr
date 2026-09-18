---
id: 0003
title: A missing capability is a result
status: accepted
date: 2026-09-14
tags: [verification, failure-posture]
supersedes: []
superseded-by: none
---

# ADR 0003 — A missing capability is a result

## Decision

Where the connector cannot do what the adapter needs, the outcome is a **narrowed claimed
scope, stated plainly**. Never a heuristic workaround, never a silent degradation.

An absent capability is recorded as a finding, with what was attempted, carrying the same
weight as a capability that works.

## Consequences

The adapter may end up doing less than first imagined, and will say so. That is the point: a
pipeline that quietly captures less than it appears to is worse than one that fails, because
the shortfall surfaces later and its size cannot be reconstructed.

It also changes what a measurement session is for. Establishing that something is impossible
is a successful session with a useful output, which is what stops absences from going
unrecorded because they felt like failures.

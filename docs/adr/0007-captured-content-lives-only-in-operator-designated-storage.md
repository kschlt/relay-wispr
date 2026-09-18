---
id: 0007
title: Captured content lives only in operator-designated storage
status: accepted
date: 2026-09-17
tags: [privacy, boundary, state]
supersedes: []
superseded-by: none
---

# ADR 0007 — Captured content lives only in operator-designated storage

## Decision

Raw payloads are written **only** to storage the operator explicitly configured for them.

No captured content is written anywhere else — not into this repository, not into whatever
tooling or planning state the maintainer runs alongside it, and not into any working
directory that happens to be convenient and versioned. Tooling state holds work items,
measurements, decisions and **synthetic** fixtures; it never holds real captured content.

Records travel; content does not. A record carries a reference to its payload rather than
the payload itself.

## Consequences

The tempting failure this forecloses is specific: a private, versioned working repository
looks like a safe place to park a payload during development, and it is not. Version control
keeps history, so a transcript committed once is a transcript kept indefinitely, and
whoever gains access to that repository later gains access to it too.

The separation also keeps the blast radius of a misconfiguration legible: exactly one
configured destination holds content, so "where is the captured data" has one answer.

The operator carries the other half. Confirming that the configured destination is private
before any real capture runs is their responsibility, and this adapter cannot discharge it
for them.

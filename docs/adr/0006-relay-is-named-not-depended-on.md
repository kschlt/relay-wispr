---
id: 0006
title: Relay is named, not depended on
status: accepted
date: 2026-09-17
tags: [boundary, documentation]
supersedes: []
superseded-by: none
---

# ADR 0006 — Relay is named, not depended on

## Decision

The documentation names **Relay** as the consumer relay-wispr was built for, because it is
the reason this adapter exists and leaving it unnamed left readers guessing.

Naming it does not make it required. The contract is the **record shape**; the consumer's
identity is not part of it. relay-wispr has no runtime dependency on Relay, and the same
records are readable by a script, a document store, or a plain directory.

What Relay does with a record — where it sends it, how it decides — is Relay's concern and
is not described in this repository.

## Consequences

A reader can understand what this adapter is for without being told they need something they
cannot obtain. The risk the decision accepts is that "Relay adapter" reads as a dependency;
the mitigation is that every description of the contract stays source-independent, and a
second capture vendor gets a second adapter emitting the same records.

The line to hold: if Relay's routing rules, destinations, or delivery state ever start
appearing in this repository's contracts, the substitutability this project is built on has
been lost, and that is a defect rather than a convenience.

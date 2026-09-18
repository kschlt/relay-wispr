---
id: 0004
title: Each source surface is verified independently
status: accepted
date: 2026-09-17
tags: [verification]
supersedes: []
superseded-by: none
---

# ADR 0004 — Each source surface is verified independently

## Decision

Each surface a vendor exposes is a **separate verification question** with its own work item
and its own verdict. A finding established on one surface is never evidence about another,
even where the field names look identical.

For Wispr Flow that means meetings and Scratchpad notes are measured separately, and each
gets an explicit answer on whether it supports incremental collection.

## Consequences

Verification costs one item per surface rather than one item overall. In exchange, a gap on
one surface cannot hide behind a success on another — the averaging failure that a single
rolled-up verification invites, where a mixed result reads as broadly working.

It follows that the adapter's supported scope may honestly differ per surface. "Meetings
supported, Scratchpad not" is a publishable outcome, not an embarrassment to smooth over.

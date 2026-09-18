---
id: 0001
title: No model in the transport path
status: accepted
date: 2026-09-14
tags: [boundary, privacy, correctness]
supersedes: []
superseded-by: none
---

# ADR 0001 — No model in the transport path

## Decision

A language model is never asked to copy, reconstruct, or summarise a transcript or note body
in order to **move** it. Persistence runs from connector response to storage through code.
What returns to an orchestrating model is metadata or a receipt — never content.

Interpretation is **relocated, not banned**. Whichever component owns a decision that needs
the content reads the content at that point, with that decision's context.

## Consequences

The primary reason is correctness. A model retyping a transcript can truncate, paraphrase,
or reorder it and still report success; the failure is silent and the corruption is hard to
detect afterwards. A direct write either succeeds or fails.

Cost follows: long transcripts are expensive to pass through a context window, and doing so
crowds out the reasoning the session actually exists for.

The privacy effect is real but secondary, and is deliberately not overstated — content never
placed in a prompt is not exposed through that prompt, which says nothing about the
surrounding infrastructure.

This binds implementation. Any design that requires a model to read content in order to
place it is a defect in the contract, not an implementation detail to be worked around.

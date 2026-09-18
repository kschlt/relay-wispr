---
id: 0010
title: The public repository carries no real source data
status: accepted
date: 2026-09-14
tags: [privacy, documentation]
supersedes: []
superseded-by: none
---

# ADR 0010 — The public repository carries no real source data

## Decision

Everything committed to this repository is permanently world-readable, including through
history and forks. Accordingly it never carries:

- real transcripts, note bodies, meeting titles, participant names, or source identifiers;
- credentials, tokens, or account identifiers;
- output pasted verbatim from a connector or tool;
- private infrastructure details — internal hostnames, private repository names, or
  contributor filesystem paths.

**Examples are synthetic.** Invented identifiers, invented titles, invented content. This
applies to issues and pull request descriptions as much as to files.

## Consequences

Private material may be rewritten and sanitised into public documentation. The reverse never
happens: a public document is never the reason to publish something private.

The rule is absolute rather than judged case by case, because the failure is irreversible.
A transcript excerpt pasted into an issue to illustrate a bug cannot be recalled once it is
in the history, and the person whose words they were did not choose this repository.

The practical cost is that illustrating a real problem takes slightly more effort — an
invented example that reproduces the shape, instead of the actual payload. That is a small
price and it is paid every time, not when it feels warranted.

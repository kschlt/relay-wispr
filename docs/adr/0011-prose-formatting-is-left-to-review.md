---
id: 0011
title: Prose formatting is left to review
status: accepted
date: 2026-09-18
tags: [documentation, process]
supersedes: []
superseded-by: none
---

# ADR 0011 — Prose formatting is left to review

## Decision

How the prose in this repository is formatted — line width, where lines wrap, heading
style, list punctuation — is **not checked by anything**. No markdown linter and no
line-width check runs in `make quality`, and adding one is not planned work.

This is a decision about *form*. The documents' *claims* are a different matter and stay
mechanised where a claim is settleable: that every relative link resolves, that every
decision record is linked from a document, that the generated index is current, that no
tracked file carries the private-content marker.

## Consequences

The immediate cost is real and was measured rather than imagined: a line in the
architecture document reached 136 characters against that file's own 80 and stayed there,
because nothing objected and no reader happened to notice. Accepting this decision accepts
that it can happen again. The repair is a rewrap, which is cheap.

What made a gate the worse trade is that this repository keeps no single width. The
records here wrap wider than the documents under `docs/`; a markdown table row and an
ASCII diagram cannot be wrapped at all; and a link inserted into settled prose pushes its
line over on its own. A width check would therefore arrive with an exception list already
attached, and the Makefile argues the other half of that case for the interpreter floor: a
check with an exception in it is a check someone will find the exception to. An
exception-free width rule is available only by reflowing every file to one number nobody
has chosen, and by refusing innocent changes afterwards.

The line this draws is between what is true-or-false and what is taste. A link resolves or
it does not; an index is current or stale; a marker is present or absent. A machine settles
those exactly, and a reviewer settles them badly, which is why they are checked. A line's
width is equally measurable, but whether it *should* be that width is a judgement, and a
gate would be enforcing a number rather than a decision.

**What would reopen this.** Two things. If formatting drift starts arriving faster than
review catches it, the balance changes and the cost of a gate is worth paying. More
likely: if this repository adopts a markdown formatter that **rewrites** rather than
refuses — the shape `ruff format` already has for Python here — then there is no exception
list to maintain and no innocent change to reject, and the argument above mostly
evaporates. Either would arrive as a record superseding this one, not as an edit to it.

---
id: 0009
title: Changes reach main through pull requests
status: accepted
date: 2026-09-14
tags: [process, git]
supersedes: []
superseded-by: none
---

# ADR 0009 — Changes reach main through pull requests

## Decision

The repository has exactly **one** commit made directly on the default branch: the initial
commit. Every change after it arrives through a branch and a pull request, one concern per
pull request.

Pull requests are integrated with **merge commits**. Squashing and rebasing onto the default
branch are not used.

Commit subjects follow Conventional Commits.

## Consequences

A single root commit gives the repository a deliberate starting point rather than an
accreted one, and makes every subsequent change reviewable in isolation — including changes
made by an agent, which is the case this project actually has.

Merge commits rather than squashes preserve branch ancestry. The maintainer's planning
tooling advances work items by asking whether a branch is an ancestor of the default branch;
squashing destroys that relationship and forces a slower content-comparison fallback. The
cost is a less linear history, which is accepted.

The rule is enforced by a repository ruleset, not by convention alone — a convention with
nothing behind it is a note, not a rule.

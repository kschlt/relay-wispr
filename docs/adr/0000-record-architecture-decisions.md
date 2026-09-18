---
id: 0000
title: Record architecture decisions
status: accepted
date: 2026-09-14
tags: [process]
supersedes: []
superseded-by: none
---

# ADR 0000 — Record architecture decisions

## Decision

Architecture decisions are recorded here, one decision per file, in the order they were
taken. A file is named `NNNN-slug.md`, carries YAML frontmatter, and states the decision
and its consequences in prose.

`README.md` in this directory is **generated** from the frontmatter by
`scripts/gen_adr_index.py` and is never edited by hand.

### Frontmatter

Every ADR carries exactly these keys:

| key | meaning |
|---|---|
| `id` | Four-digit number, matching the filename prefix. Assigned once and never reused. |
| `title` | The decision, as a short noun phrase. Matches the `# ADR NNNN — ...` heading. |
| `status` | One of the four states below. |
| `date` | ISO date the decision was taken — not the date the file was written. |
| `tags` | Inline list for grouping in the index. May be empty (`[]`). |
| `supersedes` | Inline list of ids this ADR replaces. Empty when it replaces nothing. |
| `superseded-by` | The id that replaced this one, or `none`. |

### States

```
proposed ──► accepted ──► superseded
                 │
                 └──────► deprecated
```

- **proposed** — written down and open to challenge. Not yet binding.
- **accepted** — in force. Work that contradicts it is a defect, not a variation.
- **superseded** — replaced by a later decision. Requires `superseded-by`, and the
  replacing ADR must name this id in its `supersedes`.
- **deprecated** — no longer in force and nothing replaced it. The situation it addressed
  went away.

### Rules

1. **Status only moves forward** along the arrows above. There is no route back to
   `proposed`, and a `superseded` or `deprecated` ADR is terminal.
2. **An accepted ADR is never rewritten to say something else.** Its decision is a
   historical fact. Changing course means writing a new ADR that supersedes it — the old
   reasoning stays readable, which is the whole point of keeping them.
   Fixing a typo or a broken link is not changing the decision.
3. **Supersession is reciprocal.** `supersedes` and `superseded-by` must agree in both
   files. The generator refuses a one-sided link.
4. **Numbers are permanent.** An abandoned draft's number is retired, not recycled.
5. **One decision per ADR.** If the consequences section is arguing for two things, it is
   two ADRs.

## Consequences

Decisions stop living in commit messages and chat logs, where they are unfindable six
months later, and the reasoning survives the person who had it. The cost is a small ritual
on every architectural choice, and a generated file that must be regenerated when
frontmatter changes — enforced by `gen_adr_index.py --check` rather than by memory.

Superseded ADRs staying in the tree means the directory only grows. That is intended: a
decision that was reversed is more informative than one that was never recorded, because it
carries the reason the first answer looked right.

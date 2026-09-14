# Architecture

> Pre-alpha. This describes an intended design. No component below is
> implemented, and the connector behaviour it assumes is not yet verified.

## Position in a pipeline

relay-wispr occupies one narrow slot: **vendor-specific acquisition**. It sits
between a capture vendor's API surface and a source-independent record
boundary.

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────────────┐
│  Wispr Flow  │────►│    relay-wispr    │────►│  downstream consumer │
│  MCP server  │     │  (this project)   │     │  (routing, storage,  │
└──────────────┘     └─────────┬─────────┘     │   processing — not   │
                               │               │   this project)      │
                     ┌─────────▼─────────┐     └──────────────────────┘
                     │  payload storage  │
                     │  (raw, verbatim)  │
                     └───────────────────┘
```

Two things leave the adapter, and the split is the whole design:

- **Payloads** go to durable storage on a direct path — connector response to
  disk, no model in the loop.
- **Records** — small, canonical, source-independent — go to the consumer, each
  carrying a reference to its payload rather than the payload itself.

The consumer is deliberately unspecified here. It is whatever the operator
runs: a routing layer, a document store, a plain directory. The contract is the
record shape, not the consumer's identity.

## Responsibilities

relay-wispr owns:

| Responsibility | Meaning |
|---|---|
| Discovery | Determining which items exist in scope and which are not yet captured |
| Retrieval | Vendor-specific reading, including pagination and result-shape handling |
| Identity preservation | Carrying external identifiers and timestamps through unchanged |
| Durable capture | Writing raw connector payloads directly to storage |
| Normalisation | Producing canonical records from vendor responses |
| Receipts | Returning compact operational summaries to the caller |
| Explicit failure | Reporting absent capabilities and retrieval errors as errors |

relay-wispr does **not** own destination selection, routing policy, delivery
mechanics, content interpretation, or any non-Wispr source.

## Inputs and outputs

**Consumes**

- Results from the Wispr Flow MCP server's search and read operations.
- Prior collection state — previously seen source identifiers, or a cursor —
  supplied by the caller. The adapter reads this state; it does not own the
  store it lives in.
- A requested collection scope (for example, a time window or item kind).

**Produces**

- Preserved raw payloads in storage the operator designated.
- Canonical records, or references to captured payloads.
- Compact receipts.
- Explicit capability and retrieval failures.

It does not produce consumer-specific or project-specific files. Shaping output
for a particular destination is the consumer's job.

## The context boundary

The rule that most constrains the implementation:

> **A model must never be asked to copy, reconstruct, or summarise a transcript
> or note body in order to move it.**

Persistence runs from the connector response to storage through code. What
returns to an orchestrating model is metadata or a receipt.

This is not only a cost argument, though long transcripts are expensive. A
model retyping content is a silent-corruption risk: truncation, paraphrase, and
reordering all look like success. A direct write either succeeds or fails.

Interpretation is not banned — it is **relocated**. Whatever component owns a
decision that needs the content reads the content itself, at that point, with
that decision's context.

## State boundary

The adapter is deliberately close to stateless.

It may **use** collection state to distinguish new items from seen ones, and it
returns what a caller needs to advance that state. It does not own the
persistent store holding cursors, delivery history, or an item's downstream
fate. That belongs to the caller or to the destination.

The reason is replaceability. An adapter that owned run state would need to
know the shape of the pipeline it sits in, and a second adapter would have to
reimplement it identically.

## Idempotence

Re-running the same scope must not capture anything twice. The mechanism is
stable source identity: an item already recorded as captured is skipped.

This matters because the realistic failure modes — a partial run, a network
failure mid-collection, an overlapping schedule, a manual re-run after an error
— all produce overlapping scopes. Idempotence is what makes "just run it again"
a safe response to all of them.

## Failure posture

A missing capability is a **result**, not an exception to swallow. If the
connector cannot do something the adapter needs — no incremental search, no
stable identifier, no full-body read — the adapter says so, naming what is
missing. It does not substitute a degraded path silently.

The alternative is worse than failing: a pipeline that quietly captures less
than it appears to, discovered later, with an unknowable gap in the record.

## Verification comes first

The design above assumes connector capabilities that **have not been measured**.
Before implementation, each of these must be established independently for
meetings and for Scratchpad notes:

- What search and filtering the MCP server supports, and whether results can be
  scoped incrementally.
- How results paginate, and whether pagination is stable across runs.
- Which identifiers are stable across reads, and whether timestamps are
  reliable for incremental collection.
- Whether full item bodies can be read, and what the size limits are.
- What write or update operations exist, if any.

Where a capability is absent, the honest outcome is to narrow the adapter's
claimed scope, not to work around it with heuristics.

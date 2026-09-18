# Vision

## Where this is going

Capture tools should be edges, not centres. relay-wispr exists so that Wispr
Flow can be a thin, replaceable edge on a capture pipeline: something that
collects meetings and notes and hands them onward through a contract that
survives the vendor being swapped out.

The target is an adapter that discovers new items incrementally, preserves them
exactly, and emits canonical records — while the layer consuming those records
stays entirely unaware of which tool produced them.

## Why this is worth building

Two failure modes motivate it, and both come from collapsing distinct jobs into
one piece of code.

**Vendor lock-in by diffusion.** When retrieval, routing, and processing live in
one script, vendor-specific assumptions leak everywhere. The cost of changing
capture tools is then the cost of rewriting the pipeline, which in practice
means never changing it.

**Model-as-transport.** Asking a language model to read a transcript and write
it back out is a bad way to move bytes. It is expensive on long content, it is
lossy in ways that are hard to detect, it fails unpredictably at length limits,
and it exposes full content to model context to accomplish a copy. Persistence
should be a direct path from connector response to storage.

## Goals

- **Replaceability.** Downstream consumers depend on a source-independent
  record contract. Adding a second capture source is a new adapter, not a
  rewrite.
- **Fidelity.** What gets stored is what the source returned, preserved before
  any interpretation happens.
- **Incrementality.** Runs use stable source identity to collect only what is
  new, and repeating a run captures nothing twice.
- **Context economy.** Orchestration sees receipts — counts, identifiers,
  errors — never transcript bodies.
- **Honesty about capability.** Connector behaviour is measured before it is
  depended on, and a missing capability is reported as a missing capability.

## Non-goals

relay-wispr is not, and is not on a path to become:

- a router or destination-selector — it does not decide where an item belongs;
- an inbox, notes hub, or knowledge base;
- a meeting-intelligence tool — no summaries, action extraction, or Q&A over
  transcripts;
- a multi-source ingestion framework — other sources get their own adapters;
- a general-purpose MCP client library;
- a real-time streaming pipeline.

These are not "later" items. They are other people's jobs, and the value of
this project depends on it not taking them on.

Each goal and non-goal above is a decision that was taken rather than a
preference that drifted in. The reasoning, and what was rejected, is in
[docs/adr/](docs/adr/README.md).

## What success looks like

The project has succeeded when all of the following hold:

1. Meetings — and whichever Scratchpad capabilities turn out to exist — can be
   discovered incrementally, without rescanning everything.
2. Raw persistence requires no model-generated copy of the content.
3. Running the same scope twice produces no duplicate captures.
4. Emitted records conform to a source-independent contract, and a consumer of
   those records contains no Wispr-specific logic.
5. Unsupported or absent connector behaviour surfaces as an explicit, actionable
   error rather than silence or a partial result.

## Current phase

**Pre-alpha: boundary definition.** This repository documents what the adapter
is responsible for and what it refuses to do.

The immediate next step is **capability verification** — establishing what the
Wispr Flow MCP server actually supports for discovery, reading, pagination, and
stable identity, for meetings and for Scratchpad notes separately. Record
schemas, storage mechanics, scheduling, and test strategy follow from what that
finds. None of them are settled now, and committing to them before verification
would be guessing.

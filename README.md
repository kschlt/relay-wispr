# relay-wispr

A source adapter that turns [Wispr Flow](https://wisprflow.ai) meetings and
Scratchpad notes into source-independent capture records, without asking a
language model to retype the content.

> ## Status: pre-alpha — no working software yet
>
> This repository currently contains **design documents only**. There is no
> package, no CLI, no library, and nothing to install or run.
>
> The Wispr Flow MCP server's capabilities — what can be searched, what can be
> read, how results paginate, and what identifiers are stable — **have not yet
> been verified**. Everything below describes an intended design, not measured
> behaviour. Interfaces, record shapes, and the scope of supported item types
> will change once verification happens.
>
> In particular, **Scratchpad support is not claimed**. Whether Scratchpad notes
> can be discovered and read incrementally through the MCP server is an open
> question this project intends to answer, not an assumption it builds on.

## The problem

Voice capture tools are good at collecting material and bad at being the final
home for it. Meeting transcripts and dictated notes accumulate in a vendor's
store, and getting them somewhere durable usually means one of two bad options:

- **Hand-rolled integrations** that braid vendor retrieval, routing rules, and
  downstream processing into a single script. When the vendor changes, or a
  second capture source appears, the whole thing is rewritten.
- **Model-mediated copying**, where an agent reads a transcript and writes it
  back out to persist it. This is expensive, lossy, slow on long transcripts,
  and it puts the full content into model context for no reason — the model is
  acting as a very unreliable `cp`.

## The intent

relay-wispr aims to be a **thin, replaceable edge adapter**:

- It discovers which items exist and which have not been captured yet.
- It writes source payloads to durable storage **directly**, without a model
  reproducing the content.
- It emits compact, source-independent records describing what was captured.
- It returns small operational receipts — counts, identifiers, errors — to
  whatever orchestrates it.

The point of the boundary is that the layer consuming these records should not
know that Wispr Flow exists. Adding a second capture source later should mean
writing a second adapter, not reworking everything downstream.

### Illustrative record shape

Synthetic, and **not a stable contract** — it exists to make the boundary
concrete while the design is still moving:

```json
{
  "record_version": "0",
  "source": "wispr",
  "kind": "meeting",
  "source_id": "example-0000-source-identifier",
  "captured_at": "2026-01-01T00:00:00Z",
  "occurred_at": "2025-12-31T15:00:00Z",
  "title": "Example planning discussion",
  "payload_ref": "raw/wispr/meeting/example-0000-source-identifier.json",
  "participant_count": 3
}
```

The record carries *metadata and a reference*. The payload it points at is
written by the capture path, not passed through a model.

## Design principles

- **One adapter owns the vendor.** Wispr-specific knowledge — tool names,
  response shapes, pagination quirks — stays here and nowhere else.
- **Preserve before interpreting.** Raw content is stored first. Any reading,
  summarising, or classifying happens later, in whatever component owns that
  decision.
- **Stable identity drives incremental collection.** Source identifiers and
  timestamps are preserved so a run can tell new from already-seen.
- **Re-running is safe.** A repeated run over the same scope should capture
  nothing twice.
- **Return the smallest useful result.** Orchestration sees receipts, not
  transcripts.
- **Verify, do not assume.** Undocumented connector behaviour gets measured
  before anything is built on it. Where a capability turns out to be missing,
  the adapter reports that explicitly rather than degrading quietly.

## Scope

**In scope:** discovering Wispr items, retrieving them, preserving external
identities and timestamps, durable capture of raw payloads, normalising into
canonical records, compact receipts, and explicit failures when a capability is
absent.

**Out of scope, deliberately:**

- Deciding where a captured item ultimately belongs. relay-wispr does not own
  routing policy or destination selection.
- Being an inbox, a notes hub, or a knowledge base.
- Reading meeting content for meaning — summarising, extracting actions,
  answering questions about a transcript.
- Supporting non-Wispr sources. A different source means a different adapter.
- Being a general-purpose MCP framework.
- Guaranteeing real-time collection. Capture is incremental, not instant.

## On privacy

This project handles meeting transcripts and personal notes, which is about as
sensitive as ordinary work data gets. The design intent — minimise what reaches
model context, keep credentials outside the repository, write payloads only to
storage the operator has designated — and the limits of what that can honestly
promise are in [docs/privacy-and-security.md](docs/privacy-and-security.md).
Read it before pointing anything at real data.

## Documents

| Document | What it covers |
|---|---|
| [VISION.md](VISION.md) | Where this is going and how we would know it worked |
| [docs/architecture.md](docs/architecture.md) | Boundaries, responsibilities, data flow |
| [docs/privacy-and-security.md](docs/privacy-and-security.md) | Data handling, threat boundary, honest limits |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to work on this while it is pre-alpha |
| [SECURITY.md](SECURITY.md) | Reporting a vulnerability |

## Relationship to Wispr Flow

This is an independent, unofficial project. It is not affiliated with,
endorsed by, or supported by Wispr Flow.

## License

[Apache License 2.0](LICENSE).

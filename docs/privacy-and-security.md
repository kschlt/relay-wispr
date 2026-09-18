# Privacy and security

> Pre-alpha. Nothing here is implemented or audited. This document states the
> design intent and, just as importantly, the limits of what that intent can
> promise.

## What this project handles

Meeting transcripts and dictated notes. In practice that means other people's
words, often recorded in settings where they were not thinking about where the
text would end up: colleagues in a meeting, a client on a call, a half-formed
thought dictated while walking.

Treat this as sensitive data by default, and design accordingly.

## Design intent

### Payloads take a direct path

Raw content moves from the connector response to storage through code. No
language model is asked to read content in order to persist it.

The primary reason is correctness — a model retyping a transcript can truncate
or paraphrase it and still look like it succeeded — but the privacy effect is
real: content that is never placed in a model prompt is not exposed through
that prompt.

### Only metadata returns to orchestration

What comes back from a capture run is a receipt: counts, identifiers,
timestamps, errors. Not bodies.

### Credentials stay outside the repository

Connector authentication is the operator's responsibility, held in the
environment or in the MCP client's own configuration. No credential, token, or
account identifier belongs in this repository, in its history, in its issues, or
in its documentation. Nor does any real source data
([ADR 0010](adr/0010-the-public-repository-carries-no-real-source-data.md)).

### Payloads go only where the operator designated

Captured content is written to storage the operator explicitly configured, and
nowhere else — including no working or planning repository that happens to be
private and convenient ([ADR 0007](adr/0007-captured-content-lives-only-in-operator-designated-storage.md)).
Where that storage is private, the burden of keeping it private sits with its
configuration, not with this adapter.

## What this project does **not** claim

These limits are stated plainly because overstating privacy properties is worse
than not claiming them.

- **It does not claim end-to-end confidentiality.** The MCP client, the
  connector, the transport between them, and the vendor's own infrastructure
  all observe source responses. The design reduces exposure to *model context*.
  It does not — and structurally cannot — make the surrounding infrastructure
  blind.
- **It does not claim the vendor's handling is private.** How Wispr Flow stores,
  processes, retains, or shares meeting data is governed by their terms and
  policies, not by anything in this repository.
- **It does not claim compliance with any regulatory framework.** No GDPR,
  HIPAA, SOC 2, or equivalent claim is made or implied.
- **It has not been security-reviewed.** There is no implementation to review.

## Operator responsibilities

Anyone who eventually runs this software owns the following, and the software
cannot own them on their behalf:

- **Consent and legality of recording.** Recording and retaining meetings
  involving other people is subject to law and to reasonable expectation, both
  of which vary by jurisdiction and by relationship. That is the operator's
  call and the operator's liability.
- **Storage visibility.** Confirm that payload storage is private before any
  real capture runs. A misconfigured destination publishes verbatim transcripts.
- **Retention.** This project has no opinion about how long captured content
  should live. Deciding and enforcing that is the operator's job.
- **Third-party content.** Transcripts contain other people's speech. They did
  not choose this pipeline.

## Threat boundary

**In scope for this project's design:**

- Avoiding unnecessary exposure of content to model context.
- Keeping credentials out of version control.
- Writing payloads only to configured destinations.
- Failing loudly rather than capturing partially and silently.

**Out of scope — belongs to the operating environment:**

- Securing the MCP client and its credential store.
- Access control, encryption at rest, and backups for payload storage.
- Network-level protection between components.
- The vendor's own security posture.

## Reporting a problem

See [SECURITY.md](../SECURITY.md).

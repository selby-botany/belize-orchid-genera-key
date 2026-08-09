# Prototype 04: genus key and validation analytics

Phase 2 of the project's long-term goal (root [README](../README.md)): a
genus-level identification key for the Belize orchid genera captured by
[prototype 03](../prototype-03/README.md) (Phase 1), plus analytics that
measure how well that key actually works.

Phase 1 turned scanned pages into 69 structured, provenance-carrying
genus records. This prototype exists to answer the question Phase 1
deliberately left open: **can those genus records, on their own, produce
a working identification key — and how good is it?**

**Status:** planning documents in `doc/`; pipeline not yet implemented.

## What this prototype does (planned)

1. Defines a fixed, hand-curated character vocabulary from real Phase 1
   genus text — the characters and states a key can actually ask about.
2. Extracts a character-state proposal for every genus/field pair, each
   carrying a literal supporting quote from Phase 1's own text.
3. Verifies every quote mechanically before it's trusted, and assembles
   one character matrix — one row per genus, one column per character,
   an explicit "not stated" for anything the text doesn't support.
4. Generates a draft dichotomous key from the matrix, in the same
   numbered-couplet style McLeish's own book uses.
5. Validates the key: does it correctly separate the genera it was built
   from, how many questions does it take, which characters does it lean
   on, and which genera end up sharing an ambiguous leaf — reported by
   name, not hidden.
6. Emits a review queue for anything the pipeline can't resolve on its
   own, following prototype 03's own carry-forward-on-resolution
   discipline.

## Documents

Read in this order — document 1 is the entry point, including for a
non-technical reader:

1. [Problem overview and motivation](doc/20260808-claude-sonnet-5-problem-overview.md) — everyone
2. [Requirements](doc/20260808-claude-sonnet-5-requirements.md) — everyone, botanist-critical
3. [Architecture and design](doc/20260808-claude-sonnet-5-architecture.md) — everyone
4. [Data formats and relationships](doc/20260808-claude-sonnet-5-data.md) — everyone, mostly engineer
5. [Detailed module design](doc/20260808-claude-sonnet-5-detailed-design.md) — engineer
6. [Implementation and test plan](doc/20260808-claude-sonnet-5-implementation-plan.md) — engineer

## Layout

```text
doc/        planning documents and, later, a pilot/full-run results note
data/       the hand-curated character vocabulary — control input, never generated
bin/        pipeline scripts (Python)
manifest/   review-queue artifacts — generated
analysis/   character matrix, generated key, validation report — generated
test/       unit tests for the matrix, key-generation, and validation tooling
```

This prototype's only input is `prototype-03/analysis/genera.jsonl`,
treated as read-only (requirements document, §3). It does not use
`doc/20260808-belize-orchid-characteristic-of-taxa.md` or its
`doc/research/` working notes as a data source — see the problem
overview, §6, for why that boundary matters here specifically.

## Requirements

Same as the repository overall: Docker for the `../bin/` wrappers. See
the [repository README](../README.md). Unlike prototype 03, this phase
has no macOS/Vision dependency — it operates entirely on Phase 1's
already-extracted text, not on the scanned images.

## Source material

Indirectly, McLeish, I., Pearce, N. R., Adams, B. R., & Briggs, J. S.
(1995). *Native orchids of Belize*. A.A. Balkema — by way of
`prototype-03/analysis/genera.jsonl`, not by reading the scans directly.

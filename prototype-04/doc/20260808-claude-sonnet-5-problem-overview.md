# Prototype 04: problem overview and motivation

- [Prototype 04: problem overview and motivation](#prototype-04-problem-overview-and-motivation)
  - [Purpose of this document](#purpose-of-this-document)
  - [1. What the project is building](#1-what-the-project-is-building)
  - [2. What Phase 1 delivered, in real numbers](#2-what-phase-1-delivered-in-real-numbers)
  - [3. Why the data is harder than a textbook key-building exercise](#3-why-the-data-is-harder-than-a-textbook-key-building-exercise)
  - [4. What Phase 2 is](#4-what-phase-2-is)
  - [5. What Phase 2 delivers, and what it doesn't](#5-what-phase-2-delivers-and-what-it-doesnt)
  - [6. Relationship to the characteristic-of-taxa document](#6-relationship-to-the-characteristic-of-taxa-document)
  - [7. Relationship to the botanical-keys-overview document](#7-relationship-to-the-botanical-keys-overview-document)
  - [8. How to read this document set](#8-how-to-read-this-document-set)
  - [Metadata](#metadata)

## Purpose of this document

To explain, to a botanist who has never looked at this repository's code,
what problem prototype 04 solves, why it can only start now that
prototype 03's real output exists, what makes this harder than "run a
decision-tree algorithm," and what "done" means for this phase. A reader
who stops after this document should be able to judge whether the plan is
sound and whether the eventual key is worth reviewing — without needing to
read anything else.

## 1. What the project is building

The long-term goal of this repository, stated in the root
[README](../../README.md), is a **genus key**: a tool that lets someone
holding an orchid plant found in Belize narrow it down to a genus by
answering a short sequence of observable questions, without needing to
already know what they're looking at.

[Prototype 03](../../prototype-03/README.md) (Phase 1) built the raw
material for that: a structured, provenance-carrying description of every
genus the McLeish scans document, extracted faithfully from the book's own
text. It deliberately stopped short of building the key itself — see its
problem overview, §5. **Phase 2 (this prototype) is the rest of the
sentence: turn those genus descriptions into a working identification key,
and test how well it actually works.**

## 2. What Phase 1 delivered, in real numbers

Phase 1's real, committed output (`prototype-03/analysis/genera.jsonl`,
summarized for a general reader in
`prototype-03/analysis/20260808-results-summary.md`) is the only input
this phase starts from:

- **69 genus records**, covering the genera whose treatment falls within
  pages 1-190 of the book (the pages actually captured and processed;
  see prototype 03's problem overview, §5, for why this is not the whole
  book). 51 are complete with no open questions; 18 carry a specific,
  legible review flag.
- Each genus record carries a **free-text field per organ or topic** the
  book itself uses — `Roots`, `Leaves`, `Stem`/`Stems`, `Inflorescence`/
  `Inflorescences`, `Flowers`, `Sepals`, `Petals`, `Lip`, `Column`,
  `Capsule`, plus the book's own labeled fields (`ETYMOLOGY`,
  `GENERAL DISTRIBUTION`, `DISTRIBUTION IN BELIZE`, `HABITAT`,
  `FLOWERING SEASON`, `NOTE`), and a catch-all `SUMMARY` for sentences
  that didn't fit a named field. Every field carries the source image and
  an OCR confidence score.
- Coverage of those fields is real but uneven — not every genus has every
  field, because the book itself doesn't always describe every organ for
  every genus (a monotypic genus's species page often carries fields the
  genus header doesn't). Across the 69 records: `Flowers` appears 29
  times, `Lip` 28, `Leaves` 26, `Column` 25, `Sepals` 23, `Inflorescence`/
  `Inflorescences` combined 25, `Petals` 14, `Stem`/`Stems` combined 11,
  `Roots` 3, `Rhizome` 2, `Capsule` 1. `SUMMARY` (the catch-all) appears
  65 times — meaning most genus records still carry at least one sentence
  the pipeline couldn't confidently attribute to a named organ.
- Each species entry nested under a genus carries its own copy of the
  same field vocabulary, generally more complete than the genus-level
  entry (species pages tend to carry the full battery of distribution/
  habitat/flowering fields — see prototype 03's detailed design, finding
  on page-050).

## 3. Why the data is harder than a textbook key-building exercise

The standard recipe for building a botanical key by computer — see
`doc/20260707-botanical-keys-overview.md`, §7 and §10 — starts from a
**character matrix**: one row per taxon, one column per character, each
cell a discrete state ("lip 3-lobed" vs. "lip not 3-lobed"). Building a
decision tree from a matrix like that is the easy part.

Phase 1's output is not that matrix. It is free-flowing prose, faithfully
transcribed and organized by organ, but not yet reduced to discrete,
comparable states. `"Lip free, 3-lobed; disc with 3 longitudinal calli."`
and `"Lip large, saccate, entire."` are both real `Lip` field text from
two different real genus records, and nothing in Phase 1's output says
that the first pair share a "3-lobed" state while the second doesn't —
that comparison has to be made by reading the sentences.

This is a deliberate, honest consequence of Phase 1's own scope boundary
(prototype 03's requirements document, §1.3: faithful transcription,
never auto-corrected or silently interpreted). It means **the character
matrix a key needs does not exist yet, and building it is real,
non-trivial work — the first substantive engineering problem this phase
has to solve**, not a data-loading step.

## 4. What Phase 2 is

Phase 2 turns Phase 1's per-genus free text into:

1. A **character matrix**: genera × characters, each cell a state drawn
   from a controlled vocabulary, each state traceable back to the
   specific field and source image it was read from (never invented,
   never guessed past what the text actually says).
2. A **draft identification key** built from that matrix — most likely a
   dichotomous decision tree, per the recommended approach in
   `doc/20260707-botanical-keys-overview.md`, §10, though the
   architecture document (doc 3) is where that choice is actually made
   and justified.
3. **Validation analytics**: a way to measure how well the key actually
   performs — not just whether it's mathematically valid, but whether it
   reaches the right genus, how many questions it takes on average, how
   much it leans on a small number of "expensive" or fragile characters,
   and where it becomes unreliable because too many genera are described
   too thinly to separate.

## 5. What Phase 2 delivers, and what it doesn't

**Delivers:**

- A genus-level character matrix covering the 69 genera in Phase 1's
  output, with every state traceable to source text.
- A draft dichotomous (or otherwise human-usable) key over those 69
  genera.
- A validation report: accuracy against the source material itself
  (does the key correctly separate the genus each couplet was built
  from?), coverage (how many of the 69 genera does the key actually
  reach a clean answer for, and which ones does it not), and an honest
  account of where thin data limits the key's reliability.

**Does not deliver, by design:**

- **A species-level key.** Phase 1 captured species data where the book
  provides it, but Phase 2's key operates at genus level, matching the
  root README's stated goal.
- **Coverage beyond the 69 genera.** The same page-range boundary that
  limited Phase 1 limits Phase 2 — a genus whose treatment falls outside
  pages 1-190 is not in this key, and the validation report says so
  plainly rather than implying completeness.
- **Field-testing against real plant material.** "Validation" here means
  testing the key's logical structure against the source descriptions it
  was built from, not testing it in the field against live specimens —
  that is a distinct, later kind of validation this phase does not
  attempt.
- **Any fact sourced from outside the McLeish scans.** See §6.

## 6. Relationship to the characteristic-of-taxa document

Prototype 03's problem overview, §6, already drew this boundary for
Phase 1; it applies identically here, restated because it matters most
exactly where it would be easiest to reach for a shortcut: building a
character matrix by hand is real work, and
`doc/20260808-belize-orchid-characteristic-of-taxa.md` (and the working
notes under `doc/research/`) already contains a much larger, differently
sourced character matrix covering 104 genera.

**Phase 2 does not use that document's data.** Every character state in
this phase's matrix is read from a Phase 1 genus record's field text, with
a citation back to it. Reusing that document's engineering *method* —
recording provenance per assertion, using a controlled vocabulary instead
of free-text matching — is fair game, exactly as prototype 03's problem
overview already established; reusing its *facts* is not, regardless of
how well it might make the key perform.

## 7. Relationship to the botanical-keys-overview document

`doc/20260707-botanical-keys-overview.md` is a different kind of document
from the characteristic-of-taxa one: it is general, source-independent
background on how botanical keys are built and judged, not a set of facts
about Belize orchid genera. It contains no claims about any specific
genus, so drawing on it for method — the character/state/couplet
vocabulary used throughout this document set, the accuracy/efficiency/
robustness criteria the validation report is built around, the
recommendation to treat this as a semi-automated, human-reviewed pipeline
rather than a fully automatic one — is not a boundary violation. Where
this phase's documents reference "the overview document," this is what
they mean.

## 8. How to read this document set

Read in this order — document 1 is the entry point, including for a
non-technical reader:

1. Problem overview and motivation (this document) — everyone
2. Requirements — everyone, botanist-critical
3. Architecture and design — everyone
4. Data formats and relationships — everyone, mostly engineer
5. Detailed module design — engineer
6. Implementation and test plan — engineer

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

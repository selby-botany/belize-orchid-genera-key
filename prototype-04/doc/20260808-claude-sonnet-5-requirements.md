# Prototype 04, Phase 2: requirements

Read this document in full if you are the botanist reviewing this project.
It states plainly what this phase must do, how good its output has to be
before it's trusted, and — separately — which decisions it deliberately does
not make on its own, because they're judgment calls that belong to a
botanist rather than to code.

- [Prototype 04, Phase 2: requirements](#prototype-04-phase-2-requirements)
  - [Purpose](#purpose)
  - [1. Functional requirements](#1-functional-requirements)
    - [1.1 Coverage](#1-1-coverage)
    - [1.2 No invented states](#1-2-no-invented-states)
    - [1.3 Provenance on every character state](#1-3-provenance-on-every-character-state)
    - [1.4 A controlled vocabulary, not free-text matching](#1-4-a-controlled-vocabulary-not-free-text-matching)
    - [1.5 Missing data is a real, recorded state](#1-5-missing-data-is-a-real-recorded-state)
    - [1.6 Key generation from the matrix](#1-6-key-generation-from-the-matrix)
    - [1.7 Validation analytics](#1-7-validation-analytics)
    - [1.8 Human review, scoped to what needs it](#1-8-human-review-scoped-to-what-needs-it)
  - [2. Quality and acceptance thresholds](#2-quality-and-acceptance-thresholds)
  - [3. Non-functional requirements](#3-non-functional-requirements)
  - [4. Governance inputs: decisions reserved for the botanist](#4-governance-inputs-decisions-reserved-for-the-botanist)
  - [5. Out of scope for Phase 2](#5-out-of-scope-for-phase-2)
  - [Metadata](#metadata)

## Purpose

Requirements, not design: this document says what this phase must
accomplish and what it must never do, not how it's built. See the
architecture document for how.

## 1. Functional requirements

### 1.1 Coverage

The character matrix and the key built from it cover exactly the 69 genus
records in `prototype-03/analysis/genera.jsonl` — no more (no genus from
outside that set is invented or imported from another source) and no
fewer (a genus with thin field data is still a row in the matrix, flagged
where its data can't support a character, never silently dropped from the
key's scope; see §1.5).

### 1.2 No invented states

A character state assigned to a genus must be directly supported by that
genus's own Phase 1 field text — a literal, quotable sentence or clear
paraphrase of one. It is never inferred from general orchid knowledge,
never filled in because "most genera in this group are probably like
that," and never borrowed from another genus's record. This is the same
discipline prototype 03's requirements document holds OCR transcription
to (§1.2 there), applied one level up: faithful *reading*, not faithful
*guessing*.

### 1.3 Provenance on every character state

Every cell in the character matrix records: the genus, the character, the
assigned state, the Phase 1 field it was read from, that field's source
image, and the literal text span that supports the assignment. A matrix
cell with no traceable source text is not a valid cell — this mirrors
prototype 03's requirements, §1.3, one layer up the pipeline.

### 1.4 A controlled vocabulary, not free-text matching

Characters and their allowed states are defined once, as a fixed
vocabulary, and every extraction is checked against that vocabulary rather
than matched ad hoc against whatever wording a given genus happens to use.
This is the one idea prototype 03's problem overview (§6) already flagged
as fair to reuse from the characteristic-of-taxa document's *method* —
the vocabulary's actual states are built from Phase 1's genus text, not
copied from that document.

### 1.5 Missing data is a real, recorded state

A genus that has no supporting text for a given character gets an explicit
"not stated" state for that character-genus cell, not a default value, not
an omitted row, and not a silent exclusion from the matrix. A genus whose
*entire* record is too thin to support any character (in practice, one
where every field lands in the `SUMMARY` catch-all — see §4) is still a
row in the matrix, entirely "not stated," and is reported as such in the
validation output rather than dropped.

### 1.6 Key generation from the matrix

A draft identification key is generated from the character matrix. Its
exact form (dichotomous decision tree vs. some other structure) is an
architecture decision, not a requirement — but whatever form is chosen,
every couplet/split in the generated key must be traceable back to the
specific character and states that produced it, matching §1.3's
provenance discipline one layer further up.

### 1.7 Validation analytics

The key's own quality is measured and reported, not assumed. At minimum:

- **Self-consistency**: walking the key using each genus's own recorded
  character states must arrive back at that genus (or at a leaf
  containing that genus, if the leaf is genuinely ambiguous — see §2).
  A key that fails to separate the very data it was built from is
  reported as failing, not silently accepted.
- **Efficiency**: how many questions, on average and at maximum, the key
  takes to reach an answer.
- **Character usage**: which characters the key actually relies on, and
  how often — surfacing over-dependence on one or two characters, per
  the overview document's §3.4 (robustness) and §4.2 (over-dependence on
  an expensive character).
- **Coverage and ambiguity**: how many of the 69 genera the key resolves
  to a single, unambiguous answer, versus how many end in a leaf shared
  with one or more other genera because the extracted data doesn't
  distinguish them — reported by name, not just by count.

### 1.8 Human review, scoped to what needs it

An uncertain character extraction (ambiguous wording, a state that only
partly matches the vocabulary) and a key split a botanist should look at
before trusting (an unbalanced couplet, a character that's biologically
questionable as a discriminator, an ambiguous leaf) are both recorded in a
review artifact with a legible reason — the same discipline prototype 03
built into its own review queue, applied to this phase's two new kinds of
judgment call.

## 2. Quality and acceptance thresholds

Self-consistency (§1.7) against the key's own source data is the
non-negotiable floor: if the generated tree, walked with a genus's own
recorded states, does not reach that genus (or a leaf that honestly
contains it alongside others it cannot be distinguished from), the tree is
not accepted, full stop — this is a strictly lower bar than performing
well on unseen specimens, and a key that cannot clear it is not ready for
any further use.

An ambiguous leaf (two or more genera sharing every extracted character
state) is not, by itself, an acceptance failure. It is an accurate report
of a real limit in Phase 1's captured data — some genus pairs may
genuinely not be distinguishable using only what McLeish's text says and
what this phase managed to extract from it. What's required is that every
ambiguous leaf is reported explicitly, by genus name, with the shared
states that caused it — never merged into one genus silently, never
hidden by dropping one of the tied genera from the key.

## 3. Non-functional requirements

- **Docker**, via this repository's `bin/` wrappers, for every tool this
  phase needs — no tool installed directly on the host, matching the
  whole repository's convention (root README, `bin/README.md`).
- **No unsourced network dependency for facts.** Nothing about a specific
  Belize orchid genus is fetched from an external source and folded into
  the matrix — the same boundary as prototype 03's requirements, §3,
  restated because it is the boundary the characteristic-of-taxa document
  (§6, problem overview) exists to warn against crossing. This does not
  by itself rule out using a general-purpose extraction tool (including a
  model) *as a reading aid* over Phase 1's own text — see the governance
  question in §4; it rules out that tool, or any other source, supplying
  a botanical fact Phase 1's text does not already contain.
- **Reproducibility.** Given the same `prototype-03/analysis/genera.jsonl`
  and the same phase-2 pipeline version, re-running it produces the same
  matrix and the same key. Generated artifacts are always rebuildable from
  Phase 1's output plus this phase's own code and any recorded manual
  review decisions — never hand-edited directly, matching prototype 03's
  own convention (its requirements document, §3).
- **No modification of Phase 1's output.** `prototype-03/analysis/` and
  `prototype-03/manifest/` are read-only inputs to this phase. A defect
  found in Phase 1's data during this work is reported back to prototype
  03 (a fix there, in its own commit history), never patched around
  silently inside prototype 04.

## 4. Governance inputs: decisions reserved for the botanist

These are not implementation details and this project does not decide them
by default. Each is recorded, with the default this plan uses until told
otherwise, so the choice is visible rather than buried in code:

| # | Question | Default used until confirmed otherwise |
| --- | --- | --- |
| 1 | What technique extracts character states from Phase 1's free text — hand-written pattern rules, model-assisted classification, or a hybrid? | Deferred to the architecture document (doc 3), which is where prototype 03 deferred its own comparable technical forks (its implementation plan, pilot gate). Whatever is chosen must satisfy §1.2/§1.3 (no invention, full provenance) regardless. |
| 2 | Should the `SUMMARY` catch-all field (present in 65 of 69 genus records — Phase 1's own bucket for sentences it couldn't attribute to a named organ) be mined for further characters, or left untouched as Phase 1's final word on that text? | Mined, under the same quote-and-cite discipline as every other field — it is real McLeish text, just not yet organ-labeled; leaving it untouched would discard real signal Phase 1 already captured but didn't title. |
| 3 | Should a monotypic (or near-monotypic) genus's species-level fields be allowed to corroborate a genus-level character when the genus header itself omits that field? (Real case: `Psilochilus`'s genus record has no `HABITAT` field, but its one species record does.) | Not by default — genus-level characters are read from genus-level fields only, to keep the matrix's provenance chain simple and the genus/species distinction Phase 1 preserved intact. Revisited if genus-level coverage turns out too thin to be useful without it. |
| 4 | When a genus's entire record is too thin to support any character (every field lands in `SUMMARY`), is it still worth a row in the key, or excluded and reported separately? | Still a row, entirely "not stated," per §1.5 — excluding it would be a silent coverage loss of exactly the kind this project has repeatedly found and fixed in Phase 1. |
| 5 | Who has authority to resolve a review-queue item (§1.8) once this phase flags it? | Not decided by this document — whoever is doing the botanical review in practice, same answer as prototype 03's requirements, §4, item 5. |

## 5. Out of scope for Phase 2

- A species-level key — this phase's key is genus-level only, per the
  problem overview, §5.
- Any character state, or any fact about a specific genus, sourced from
  `doc/20260808-belize-orchid-characteristic-of-taxa.md` or its
  `doc/research/` working notes — problem overview, §6.
- Field-testing the key against real, live plant material — problem
  overview, §5.
- Visual or photographic characters — Phase 1's captured data is OCR'd
  text; no image-based character extraction is attempted this phase.
- Coverage of any genus outside the 69 in Phase 1's output — problem
  overview, §5.
- Automatically resolving an ambiguous leaf or an awkward couplet by
  fabricating a distinguishing character — that is the "review the tree
  with a botanist" step the overview document (§7.3) describes, and it
  belongs to a human, not to this phase's code.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

# Prototype 04, Phase 2: architecture and design

- [Prototype 04, Phase 2: architecture and design](#prototype-04-phase-2-architecture-and-design)
  - [Purpose](#purpose)
  - [1. Design principles](#1-design-principles)
  - [2. The pipeline, six stages](#2-the-pipeline-six-stages)
  - [3. The central decision: how character states get extracted](#3-the-central-decision-how-character-states-get-extracted)
    - [3.1 Option A: pure pattern/regex extraction](#3-1-option-a-pure-patternregex-extraction)
    - [3.2 Option B: model-assisted classification, unverified](#3-2-option-b-model-assisted-classification-unverified)
    - [3.3 Option C: hybrid, with mandatory quote verification](#3-3-option-c-hybrid-with-mandatory-quote-verification)
    - [3.4 Recommendation](#3-4-recommendation)
  - [4. Stage-by-stage narrative](#4-stage-by-stage-narrative)
    - [4.1 Stage A — character vocabulary](#4-1-stage-a—-character-vocabulary)
    - [4.2 Stage B — character extraction](#4-2-stage-b—-character-extraction)
    - [4.3 Stage C — matrix assembly](#4-3-stage-c—-matrix-assembly)
    - [4.4 Stage D — key generation](#4-4-stage-d—-key-generation)
    - [4.5 Stage E — validation analytics](#4-5-stage-e—-validation-analytics)
    - [4.6 Stage F — review queue](#4-6-stage-f—-review-queue)
  - [5. Prove the approach, then scale it](#5-prove-the-approach-then-scale-it)
  - [6. What's not in this document](#6-whats-not-in-this-document)
  - [Metadata](#metadata)

## Purpose

How Phase 2 is built, at a level a botanist can follow without programming
knowledge, and — because this phase's central technical choice is a real
fork with tradeoffs, not an obvious default — a reasoned comparison of the
options for it. The module-by-module version, for an engineer, is the
detailed design document.

## 1. Design principles

Adapted from prototype 03's five (its architecture document, §1), which
this phase inherits rather than reinvents:

1. **Never invent a state.** Every character-state assignment traces to a
   literal quote from Phase 1's own field text (requirements, §1.2/§1.3).
   This is Phase 1's "never trust a filename alone" principle, restated
   one layer up: never trust a plausible-sounding classification without
   checking it against the actual source text.
2. **A quote is not evidence until it's checked.** Whatever technique
   proposes a character state (§3), the proposal is not trusted until a
   separate, mechanical step confirms its supporting quote is a real
   substring of the field text it claims to come from. This is this
   phase's version of "confidence is not a quality gate by itself" —
   a plausible-looking classification is not accepted on its own say-so.
3. **Provenance travels with every fact**, unchanged from Phase 1: a
   character state with no recorded source field/image/quote is not in
   the matrix — it's in the review queue.
4. **Generated and hand-curated files are never ambiguous.** The
   character vocabulary (§4.1) is hand-curated — a human decision about
   which characters matter, informed by reading real data, not something
   the pipeline regenerates on its own. Everything downstream of it
   (the matrix, the key, the validation report) is fully generated,
   rebuildable from Phase 1's output plus the vocabulary plus this
   phase's own code.
5. **Prove the approach on a small, deliberately telling sample before
   running it at scale.** See §5.

## 2. The pipeline, six stages

| Stage | Purpose | Input | Output |
| --- | --- | --- | --- |
| A. Character vocabulary | Define the fixed set of characters and allowed states this phase will extract | A representative sample of real Phase 1 field text, read by hand | `data/character_vocabulary.json` (hand-curated) |
| B. Character extraction | Propose a character-state assignment, with a supporting quote, for every (genus, field) pair | `prototype-03/analysis/genera.jsonl`, the vocabulary | Proposed assignments, each carrying its quote |
| C. Matrix assembly | Verify every quote, assemble one matrix, fill genuinely unassigned cells with an explicit "not stated" | Stage B's proposals | `analysis/character_matrix.jsonl` |
| D. Key generation | Build a dichotomous decision tree from the matrix | The matrix | `analysis/genus_key.json`, a rendered Markdown key |
| E. Validation analytics | Measure self-consistency, efficiency, character usage, and ambiguous leaves | The matrix, the tree | `analysis/validation_report.json` + Markdown |
| F. Review queue | Surface every uncertain extraction and every questionable key split | Every stage's flagged items | `manifest/review_queue.csv` |

This has one more stage than Phase 1's five because Phase 2 has a genuine
curation step (A) that Phase 1 didn't need — Phase 1's "vocabulary" (the
book's own field labels: `ETYMOLOGY`, `HABITAT`, ...) was already fixed by
the source text itself; Phase 2's character vocabulary has to be defined
by a person, because McLeish's prose doesn't come pre-labeled with
"character: lip lobing; states: entire, 3-lobed, 4-lobed."

## 3. The central decision: how character states get extracted

Requirements document, governance question #1, defers this choice here.
It matters more than any other decision in this phase because it
determines how much of the real signal in Phase 1's prose this phase can
actually reach, and how that reach is checked.

### 3.1 Option A: pure pattern/regex extraction

Hand-write matching patterns per character — e.g., a regex that turns
`"pollinia 4"` into `Pollinia_count = four`, or `"[Ll]ip .*3-lobed"` into
`Lip_lobing = three_lobed`.

**Pros:** fully deterministic and reproducible; no dependency beyond this
repository's own tooling; every match is inherently traceable, because the
pattern *is* the check.

**Cons:** McLeish's prose is not formulaic outside a handful of numeric or
near-boilerplate characters (pollinia count, presence/absence of an organ).
Qualitative characters are described with wide lexical variety — real
`Lip` text in the corpus ranges from `"Lip free, 3-lobed; disc with 3
longitudinal calli."` to `"Lip large, saccate, entire."` to phrasing this
document hasn't sampled yet. Reaching acceptable recall on anything beyond
the simplest characters would mean writing and maintaining a very large,
continually-extended pattern library — a cost that scales with vocabulary
breadth, not with genus count, so it gets worse exactly as the key gets
more useful.

### 3.2 Option B: model-assisted classification, unverified

Ask a model to read a genus's field text and propose a character/state
assignment against the fixed vocabulary, and trust the result.

**Pros:** much better recall on varied natural language than Option A,
with far less hand-written pattern maintenance.

**Cons:** violates design principle 2 outright. A model can misread,
paraphrase past what the text actually supports, or — in the failure mode
this whole project has been built to guard against — assert something the
source text doesn't say. Nothing here checks that. This option is
rejected, not because model assistance is unwelcome, but because
*unverified* model output is exactly the "trust a plausible-sounding
classification" failure mode design principle 1 exists to prevent.

### 3.3 Option C: hybrid, with mandatory quote verification

Use pattern rules (Option A) for the small set of characters McLeish
phrases near-formulaically (counts, organ presence/absence). For
qualitative characters, use model-assisted classification (Option B's
recall advantage), but require every proposed assignment to carry a
literal quote, and mechanically verify — by exact substring match against
the genus's own Phase 1 field text — that the quote is real before the
assignment is allowed anywhere near the matrix. A proposal whose quote
doesn't verify is not "accepted with low confidence" — it is rejected
outright and the cell is treated as unextracted, falling to §1.5's
explicit "not stated" handling; the review queue exists for cases worth a
human's attention, not for silently lowering the bar.

**Pros:** the recall of model-assisted reading, without the trust problem —
the verification step doesn't need to trust the model's *judgment*, only
mechanically confirm that its *cited evidence* is real. Simple characters
still get a fully deterministic path.

**Cons:** classification choices (which valid quote gets matched to which
state, when a sentence could plausibly support more than one) are not
perfectly reproducible run-to-run in the way a regex match is. This is
mitigated, not eliminated, by §1.8's human review path for genuinely
ambiguous cases, and by never allowing an unverified quote through
regardless of how the classification was produced.

### 3.4 Recommendation

**Option C.** It is the only one of the three that satisfies design
principles 1 and 2 while remaining practical to build for a vocabulary
broad enough to make the resulting key worth reviewing. Option A alone
would either take an impractical amount of hand-tuning to reach usable
recall, or ship a key built from only the handful of characters simple
enough to pattern-match — a materially worse key. Option B alone is
rejected on trust grounds, not effort grounds. This is a recommendation
this document is making, not a decision already exercised elsewhere in
this project's history; it is recorded here, with reasoning, precisely so
it can be reviewed and overridden before Stage B is implemented, per
requirements document §4, item 1.

## 4. Stage-by-stage narrative

### 4.1 Stage A — character vocabulary

A person reads a representative sample of real Phase 1 field text across
organs, and writes down a fixed list of characters and their allowed
states — including an explicit "not stated" state for every character,
since §1.5 requires it to be a first-class, not a fallback-only, value.
This artifact is hand-curated: nothing in stages B-F ever regenerates or
edits it. Detailed design (doc 5) specifies its exact file shape.

### 4.2 Stage B — character extraction

For every (genus, field) pair in `prototype-03/analysis/genera.jsonl`,
propose zero or more character-state assignments per §3.3/§3.4, each
carrying a literal supporting quote from that field's text and the field's
own existing provenance (source image, OCR confidence) carried through
unchanged.

### 4.3 Stage C — matrix assembly

Every proposal from Stage B is quote-verified (§3.3) before being kept.
Verified proposals are assembled into one matrix: one row per genus, one
column per character, each cell either a verified state (with its full
provenance) or the explicit "not stated" state (§1.5). A genus whose
entire row is "not stated" is still a row, flagged for the review queue
(Stage F).

### 4.4 Stage D — key generation

Builds a dichotomous decision tree from the matrix. Per the overview
document's recommendation (§10) and algorithm list (§6.4), a greedy,
information-gain-style splitting approach is the right starting point for
a genus-count problem this size (69 rows) — an exact/optimal-tree
formulation is not warranted at this scale. The split-selection weighting
(§1.7's efficiency and character-usage concerns) penalizes characters with
a high "not stated" fraction, so the tree doesn't lean on a character most
genera don't actually have data for. Every split records which character
and states produced it, and every leaf records its genus set — one genus
if the tree separated it cleanly, more than one if the leaf is genuinely
ambiguous (requirements, §2).

### 4.5 Stage E — validation analytics

Walks the generated tree using each genus's own matrix row and checks it
lands in a leaf containing that genus (requirements §1.7/§2's
self-consistency floor). Computes tree depth (average and max), a
character-usage frequency table, and an explicit, by-name list of every
ambiguous leaf and the states its member genera share. Produces both a
machine-readable report and a Markdown version for a botanist, following
the same dual-output convention as Phase 1's `genera.jsonl`/
`mcleish.genera.md` pair and its results-summary document.

### 4.6 Stage F — review queue

Collects: a Stage B/C proposal that failed quote verification and was
worth a human decision rather than a silent drop; a genus whose entire
row is "not stated" (§4.3); an ambiguous leaf from Stage E; and a key
split a botanist should sanity-check (a couplet the splitting algorithm
chose that looks statistically fine but biologically odd is not something
code can detect on its own — it's flagged for the same reason a human
review path exists at all). Same shape and discipline as
`prototype-03/bin/export_review_queue.py`'s queue: one row per item, one
legible reason each, carry-forward of a prior resolution by stable item
ID across regenerations.

## 5. Prove the approach, then scale it

Before this pipeline runs over all 69 genus records, it runs once over a
small, deliberately telling sample — chosen, like Phase 1's pilot, to be
hard rather than representative: a genus with rich, complete field
coverage (to prove the happy path actually produces a sensible matrix
row); a genus whose record is almost entirely `SUMMARY` catch-all text (to
prove §1.5's "not stated" handling and Stage F's flagging both work, not
just in theory); and at least one pair of genera plausible enough to share
matrix states that an ambiguous leaf is a realistic outcome to test for,
not just a hypothetical branch in the code. The implementation plan
document (doc 6) names the actual genera for this sample, the same way
Phase 1's implementation plan named actual files rather than describing
the selection criteria in the abstract.

**Pass condition:** every genus in the pilot sample produces a matrix row
with correct provenance on every non-"not stated" cell, the generated
tree (restricted to the pilot sample) is self-consistent for every genus
in it, and the review queue correctly flags the thin-data genus without
crashing or silently dropping it. On failure, the specific gap is fixed
and the pilot re-run before scaling — identical discipline to Phase 1's
pilot gate (its implementation plan, §3), for the identical reason.

## 6. What's not in this document

The exact character vocabulary (which characters, which states) is a
Stage A work product, not an architectural decision — see doc 5 for its
file shape and doc 6 for when it's actually written. The exact
quote-verification algorithm, matrix file schema, tree file schema, and
splitting-weight formula are detailed design (doc 5). The commit sequence
and test plan are the implementation plan (doc 6).

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

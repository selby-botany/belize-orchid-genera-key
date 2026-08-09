# Results summary: genus key and validation analytics

This is a plain-language summary of what `prototype-04` actually produced
from prototype-03's genus data, for a botanist reviewing the output
rather than the code. It reports coverage honestly: what the key can do
today, what it can't yet, and why.

## What went in

- **69 genus records** from `prototype-03/analysis/genera.jsonl` (Phase
  1's real output), read strictly as-is.
- A hand-curated set of **17 established orchid genus-level characters**
  (growth habit, pseudobulb presence, leaf vernation and texture,
  inflorescence position and flower count, sepal/petal torsion, lip
  lobing/attachment/spur, column shape/torsion, anther position,
  rostellum sensitivity, pollinia count/attachment) — standard
  categories in orchid taxonomy, several visible in McLeish's own
  dichotomous key to genera, not facts specific to any excluded source.
- Every genus's field text was read, once, by hand, and checked for
  a character state it could confidently support with a literal
  quote — never guessed at.

## What came out

- **8 of the 69 genera** produced at least one verified character:
  Psilochilus, Epistephium, Pelexia, Platythelys, Leochilus,
  Psygmorchis, Comparettia, Leucohyle.
- **61 of the 69** produced none at all — every character `not_stated`,
  by design (requirements document, §1.5), not by omission.
- The generated key (`analysis/genus_key.md`) is a real, working
  five-question dichotomous key. It correctly, cleanly separates all 8
  data-bearing genera from each other and from everyone else. The other
  61 genera land together in one large, explicitly-named leaf.
- **Self-consistency: 0 failures out of 69.** Every genus, walked with
  its own recorded characters, reaches a leaf containing itself — the
  key never contradicts the data it was built from.

## Why 61 genera produced nothing

This is the honest, load-bearing finding of this pass, not a shortfall
to gloss over. Three real, distinct reasons, found by actually reading
the text rather than assumed in advance:

1. **Residual OCR/reading-order noise.** A meaningful share of Phase 1's
   genus records still carry caption fragments, citation soup, or
   multi-species text concatenated together (prototype-03's own
   documented, known limitations — module docstring findings 7 and 8 in
   `parse_genus_page.py`). Extracting a character from garbled or
   ambiguous text would violate this project's first rule (never invent
   a state) just as surely as inventing one from nothing.
2. **Field-label mismatches.** Partway through this pass, several
   plausible-looking characters turned out to sit in a field whose label
   didn't match its content (e.g., column or lip facts appearing inside
   an `ETYMOLOGY` field) — the same reading-order scrambling in a milder
   form. A stricter rule was adopted and applied consistently for the
   rest of the pass: only `SUMMARY` or a character's own designated
   field counts as evidence. Two already-extracted proposals were
   retracted once this rule was set, for consistency.
3. **Large, species-rich genera have no clean genus-level text at all.**
   Oncidium, Sobralia, Habenaria, Encyclia, Epidendrum, and others like
   them have their per-organ fields concatenated across several species'
   entries by Phase 1's own parser, with no reliable way to tell which
   sentence describes the genus as a whole versus one particular
   species.

Three genera — Cranichis, Trichopilia, Eulophia — are excluded entirely:
prototype-03 flags them `possible_cross_genus_content` (their record may
contain a *different* genus's real facts). Extracting characters from
flagged, possibly-wrong text would defeat the point of the flag.

## A related defect found, not yet fixed

While working through Malaxis, a **different**, messier version of the
same underlying problem turned up: on one page, fragments of Malaxis,
Liparis, and Vanilla's real text are interleaved within a single OCR
column, with a genus header (Liparis's) buried mid-column rather than
isolated the way prototype-03's existing detector expects. That detector
correctly did not fire here — the pattern is real but different — so
Malaxis and Liparis are excluded from this pass's extraction rather than
risk pulling wrong facts, but the underlying data defect in
`prototype-03/analysis/genera.jsonl` is not fixed. This is flagged here
as a known, real, unresolved item for a future, dedicated pass — not
silently absorbed into "not stated."

## What still needs a human look

`manifest/review_queue.csv`: **62 open rows** — 61 `all_not_stated` (one
per thin genus, each naming the genus) and 1 `ambiguous_leaf` (the
61-genus tie, naming every member and the exact shared states that
caused it).

## What this does *not* claim

- This key covers the **69 genera in Phase 1's captured page range
  only** — no claim about the rest of the book.
- An `all_not_stated` genus is not "no data exists" — it means *this
  pass*, with *this* 17-character vocabulary and *this* extraction
  standard, found nothing it could confidently attribute. A larger
  vocabulary, a cleaner Phase 1 corpus (the two defect classes above,
  fixed), or the deferred `SUMMARY`-mining/species-corroboration
  governance questions revisited (requirements document, §4) would
  likely raise this considerably.
- The ambiguous leaf is not a claim that those 61 genera are
  indistinguishable in real life — it is an honest statement that
  *this data, today,* does not distinguish them.
- Nothing here has been cross-checked against
  `doc/20260808-belize-orchid-characteristic-of-taxa.md`, by the same
  design boundary Phase 1 holds (problem overview, §6).

## Where to look next

- `analysis/genus_key.md` — the readable key.
- `analysis/character_matrix.jsonl` — the full matrix, machine-readable,
  full provenance per verified cell.
- `analysis/validation_report.md` — the full validation detail.
- `manifest/review_queue.csv` — the 62 open items above.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

# Results summary: genus key and validation analytics

This is a plain-language summary of what `prototype-04` actually produced
from prototype-03's genus data, for a botanist reviewing the output
rather than the code. It reports coverage honestly: what the key can do
today, what it can't yet, and why.

## What went in

- **69 genus records** from `prototype-03/analysis/genera.jsonl` (Phase
  1's real output), read strictly as-is — and re-read from scratch for
  this pass, because Phase 1's corpus changed underneath it. Half the
  book's pages had been scanned upside down, so the descriptions this
  phase read the first time were partly the *neighbouring* genus's text. This is the **corrected**
  corpus: half the page scans turned out to be upside down, and fixing
  that is what made most of the improvement below possible (Phase 1's
  own results summary has the detail).
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

- **19 of the 69 genera** produced at least one verified character, up
  from 8 before the scan-orientation fix: Arpophyllum, Brassavola,
  Comparettia, Corymborkis, Coryanthes, Dichaea, Epidanthus,
  Epistephium, Eulophia, Gongora, Koellensteinia, Leochilus, Liparis,
  Pelexia, Platythelys, Psilochilus, Psygmorchis, Trichopilia, Vanilla.
- **76 verified characters** in total, up from 30, and every one of them
  passed quote verification against Phase 1's own field text — **0
  proposals were dropped.**
- **50 of the 69** produced none at all — every character `not_stated`,
  by design (requirements document, §1.5), not by omission.
- The generated key (`analysis/genus_key.md`) is a real, working
  dichotomous key, 13 numbered couplets deep at most 6 questions. It
  cleanly separates all 19 data-bearing genera from each other and from
  everyone else. The other 50 land together in one large,
  explicitly-named leaf.
- **Self-consistency: 0 failures out of 69.** Every genus, walked with
  its own recorded characters, reaches a leaf containing itself — the
  key never contradicts the data it was built from.
- The key now draws on **11 of the 17 characters** (was 5), with
  `plant_habit` and `pollinia_count` doing most of the separating.

## Why 50 genera still produce nothing

This is the honest, load-bearing finding of this pass, not a shortfall to
gloss over. The single biggest cause of the *previous* pass's emptiness
has now been removed — half the page scans were upside down, which
scrambled reading order and spliced sentences across the column gutter —
and that alone took the data-bearing genera from 8 to 19. What remains
has two distinct causes, both found by reading the text rather than
assumed in advance:

1. **Large, species-rich genera still have no genus-level description
   to read.** Oncidium, Encyclia, Epidendrum, Maxillaria, Habenaria,
   Lycaste, Sobralia and others like them have their genus-level fields
   filled with the book's own *dichotomous key couplets* ("Leaves less
   than 7 mm wide. Leaves less than 9 mm wide.") rather than a
   diagnostic paragraph. A couplet states a contrast between species, not
   a fact about the genus, so nothing in it can be attributed to the
   genus without inventing. These are the richest genera in the book, and
   they remain the largest single prize left on the table.
2. **Several genus records carry a single species' description**, full
   of measurements and specimen colour, where the book gives its
   treatment under the species rather than the genus. Qualitative
   statements from those records (lobing, attachment, pollinia count)
   were used; measurements and colours were not.

**Extraction standard, unchanged from the previous pass:** only
`SUMMARY` or a character's own designated field counts as evidence, and
every quote must appear verbatim in Phase 1's own field text. Stage C
re-verifies all of it mechanically — **0 of the 76 proposals were
dropped.**

**One genus is excluded outright:** `Cranichis`, whose record genuinely
does contain Habenaria's description (Phase 1 flags it both
`possible_cross_genus_content` and `foreign_genus_etymology`, and the
text was re-read to confirm). Corymborkis, Eulophia, Arpophyllum and
Trichopilia were excluded on that same flag in the previous pass and are
**included now**: with the page orientation corrected, each was re-read
and demonstrably carries its own text — Corymborkis its own *corymbos* +
*orchis* etymology, Arpophyllum its own *harpe* + *phyllon*. Phase 1's
layout-based flag has largely outlived the defect it was built for.

## What still needs a human look

`manifest/review_queue.csv`: **51 open rows** — 50 `all_not_stated` (one
per thin genus, each naming the genus) and 1 `ambiguous_leaf` (the
50-genus tie, naming every member and the exact shared states that
caused it). That is down from 62.

## What this does *not* claim

- This key covers the **69 genera in Phase 1's captured page range
  only** — no claim about the rest of the book.
- An `all_not_stated` genus is not "no data exists" — it means *this
  pass*, with *this* 17-character vocabulary and *this* extraction
  standard, found nothing it could confidently attribute. A larger
  vocabulary, a cleaner Phase 1 corpus (the causes above, addressed), or
  the deferred `SUMMARY`-mining/species-corroboration
  governance questions revisited (requirements document, §4) would
  likely raise this considerably.
- The ambiguous leaf is not a claim that those 50 genera are
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
- `manifest/review_queue.csv` — the 51 open items above.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Opus 5
generator-model-token: claude-opus-5
generator-provider: Anthropic
generation-date: 2026-08-09
generator-responsibility: implementation
```

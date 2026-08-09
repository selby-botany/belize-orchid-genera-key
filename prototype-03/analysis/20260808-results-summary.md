# Results summary: McLeish genera extraction

This is a plain-language summary of what the pipeline in `prototype-03`
actually produced from the McLeish scans, for a botanist reviewing the
output rather than the code. It reports coverage honestly: what was
captured, what wasn't, and where a human needs to look before trusting a
given fact.

## What was processed

- **242 image files** in `images/20260804-page-scans/` were inventoried.
  3 have a filename or size anomaly (see "Files that needed a closer
  look" below) — none were silently skipped.
- **190 of those files are numbered book pages** (1-190, the "captured
  page range" for this pass). The rest are front matter, colour plates,
  and a few unexplained outliers, none of which are genus text.
- Of the 190 pages, **188 were readable enough to extract text from**;
  2 were rejected outright because they contain too little text to be a
  real page (both are photographic plates, correctly recognized as
  non-text rather than misread).

## What came out

- **69 genus records**, each with the genus name, author citation, page
  number(s), and whatever fields (etymology, habitat, distribution,
  flowering season, notes, ...) the pipeline could confidently attribute.
  Every field carries the page image it came from and a confidence score
  — nothing in `analysis/genera.jsonl` is unsourced.
- **57 of the 69** genus records are complete: no open questions, no
  flags.
- **12 of the 69** carry at least one review flag (listed by name below)
  — not defects, but places where the pipeline found something it could
  not confidently resolve on its own, and said so rather than guessing.
- **194 individual species entries** nested under 37 of the genera, each
  with its own name, author citation, and field text. The book presents
  species two different ways — a bare name (`Psilochilus macrophyllus
  (Lindl.) Ames ...`) and a numbered list under a species-rich genus
  (`1. Epidendrum acuñae Dressler in Am. Orch. Soc. ...`) — and both are
  now parsed. Before this pass only the bare form was, and the corpus
  held just 19 species entries under 13 genera: the largest genera in
  the book (Epidendrum, now 30 species; Encyclia 26; Maxillaria 25;
  Habenaria 24; Oncidium 10; Dichaea 8; ...) had **zero** entries each,
  bar a single one under Epidendrum, their per-species text
  concatenated together into genus-level fields.
- The rendered document a person actually reads is
  `analysis/mcleish.genera.md` — one genus per section, species nested
  underneath, in the order the book presents them.

## What still needs a human look

`manifest/review_queue.csv` lists every item, one row per issue, each
with a plain-language reason. As of this run: **268 open rows**.

| Category | Count | What it means |
| --- | --- | --- |
| `uncertain_field` | 245 | A sentence was captured but the pipeline couldn't confidently label which field it belongs to (it's filed under a generic "SUMMARY" bucket instead). The text is present, just not sorted. |
| `discontinuity` | 8 | A page's running head named a *different* genus than the one the pipeline had open. Something changed between pages that the pipeline couldn't account for on its own (a skipped page, a page out of order, or a genus treatment the pipeline mis-bounded). |
| `ambiguous_genus_boundary` | 4 | A page had real content and an open genus record, but neither a genus header nor a readable running head to confirm which genus it belongs to. Filed under the genus that was open going in — flagged so a person can confirm it. |
| `image_anomaly` | 4 | A source file itself has a naming or size problem (see below). |
| `ocr_reject` | 4 | A page's text was too sparse or too low-confidence to accept (largely the 2 non-text plates, counted twice for two different reasons each). |
| `possible_cross_genus_content` | 3 | A rare page layout prints two genus headers side by side in their own narrow columns; the pipeline found a specific, confirmed pattern where one genus's real description can attach to the *other* genus's record. Flagged so a person checks the source image before trusting any field on the affected record. |

The count of `uncertain_field` rows rose sharply this run — from 80 to
245 — and that rise is a **consequence of the numbered-species-list fix
above, not a regression**. Each of the 194 newly-separated species
entries carries its own field text, and each unlabeled sentence in it now
gets its own reviewable row, where previously that same text sat
undifferentiated inside a single genus-level bucket and produced one row
(or none). The other categories are unchanged: `discontinuity` 8,
`ambiguous_genus_boundary` 4, `possible_cross_genus_content` 3, exactly
as before. More rows here means more text has been resolved down to the
species that owns it, not that more text became doubtful.

The 12 genus records carrying a flag, by name: Arpophyllum, Corymborkis,
Cranichis, Cycnoches, Eulophia, Galeandra, Huntleya, Ionopsis,
Liparis, Maxillaria, Mormolyca, Trichopilia. Most carry exactly one
`ambiguous_genus_boundary` or `discontinuity` flag against a single page
— a small, specific thing to check, not a wholesale re-review of the
genus.

A note on `uncertain_field`, the largest category: a second
pass on the underlying pipeline found that a real share of what used to
land in a genus's generic `SUMMARY` bucket was not unattributed McLeish
prose at all, but plate-caption and photo-index text that had never been
taught to the parser as page furniture — see
`prototype-03/bin/parse_genus_page.py`'s module docstring, finding 7, for
the detail. That fix (committed separately) cut the number of genus
records affected from 36 of 65 down to 9 of 65; those 9 are documented,
known residual cases (multi-line caption fragments split across a page
boundary in a way the current furniture filter doesn't yet catch), not
newly discovered gaps.

A separate, more serious pattern (finding 8 in the same module docstring)
surfaced afterward, while building Phase 2's character extraction: on a
small number of pages, two genus headers are printed side by side in
their own narrow columns, and one genus's *real* description can attach
to the *other* genus's record instead — not missing or garbled text, but
a different genus's real facts under the wrong name. `Cranichis`'s record,
for example, contained Habenaria's own description verbatim before this
was caught. Three genus records (`Cranichis`, `Eulophia`, `Trichopilia`)
are now flagged `possible_cross_genus_content` rather than silently
reporting "complete" while carrying this risk. Fixing this fully — moving
only the misattributed lines, without disturbing a neighboring genus's
own legitimate trailing content mixed in the same column — is a larger
change than this pass took on; for now, treat any field on these three
records as unverified until checked against the source image.

## Files that needed a closer look (Stage A)

Of the 242 image files: one has an unreadable/corrupt filename pattern
(`page-065 1.jpeg`, a known corrupt duplicate of `page-065.jpeg`, correctly
never confused with the real page), and two others have naming or size
issues logged in `manifest/scan_inventory.json` and carried into the
review queue as `image_anomaly` rows. None of the 242 files disappeared
without a trace.

## What this does *not* claim

- This covers pages **1 through 190 only** — the page range actually
  scanned and captured for this pass. It does not claim to cover the
  whole book, and it makes no claim about content on any page outside
  that range.
- A genus record with no review flag is not a guarantee of perfect
  transcription — OCR is not perfect, and this pipeline never silently
  "corrects" what it reads. It means the pipeline found no *structural*
  reason to doubt the attribution. Spot-checking a sample of records
  against the source images (`images/20260804-page-scans/`) before
  relying on this data for anything downstream is still worthwhile.
- Nothing here has been cross-checked against
  `doc/20260808-belize-orchid-characteristic-of-taxa.md` by design — this
  extraction is meant to be an independent read of the image data, not a
  confirmation of that document.

## Where to look next

- `analysis/mcleish.genera.md` — the readable corpus.
- `analysis/genera.jsonl` — the same data, machine-readable, with full
  provenance per field.
- `manifest/review_queue.csv` — the 268 open items above; each row can be
  marked `resolved` with a `resolution`/`resolved_by`/`resolved_date` and
  that resolution will be carried forward automatically the next time the
  pipeline runs.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-09
generator-responsibility: implementation
```

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
- **51 of the 69** genus records are complete: no open questions, no
  flags.
- **18 of the 69** carry at least one review flag (listed by name below)
  — not defects, but places where the pipeline found something it could
  not confidently resolve on its own, and said so rather than guessing.
- The rendered document a person actually reads is
  `analysis/mcleish.genera.md` — one genus per section, species nested
  underneath, in the order the book presents them.

## What still needs a human look

`manifest/review_queue.csv` lists every item, one row per issue, each
with a plain-language reason. As of this run: **114 open rows**.

| Category | Count | What it means |
| --- | --- | --- |
| `uncertain_field` | 84 | A sentence was captured but the pipeline couldn't confidently label which field it belongs to (it's filed under a generic "SUMMARY" bucket instead). The text is present, just not sorted. |
| `ambiguous_genus_boundary` | 13 | A page had real content and an open genus record, but neither a genus header nor a readable running head to confirm which genus it belongs to. Filed under the genus that was open going in — flagged so a person can confirm it. |
| `discontinuity` | 8 | A page's running head named a *different* genus than the one the pipeline had open. Something changed between pages that the pipeline couldn't account for on its own (a skipped page, a page out of order, or a genus treatment the pipeline mis-bounded). |
| `image_anomaly` | 4 | A source file itself has a naming or size problem (see below). |
| `ocr_reject` | 4 | A page's text was too sparse or too low-confidence to accept (largely the 2 non-text plates, counted twice for two different reasons each). |
| `numbered_species_list_unparsed` | 1 | Epidendrum, a genus with "several hundred" species per the book's own text, numbers its own internal species list. The pipeline correctly recognized this is still Epidendrum (not a separate genus) but did not attempt to parse the individual numbered species out of it — that would need its own dedicated logic, out of scope for this pass. The genus's full text is captured; it's just not split by species. |

The 18 genus records carrying a flag, by name: Corymborkis, Pelexia,
Liparis, Galeandra, Clowesia, Cycnoches, Huntleya, Xylobium, Maxillaria,
Mormolyca, Ionopsis, Leucohyle, Psygmorchis, Bletia, Arpophyllum,
Cattleya, Dimerandra, Epidendrum. Most (13 of 18) carry exactly one
`ambiguous_genus_boundary` or `discontinuity` flag against a single page
— a small, specific thing to check, not a wholesale re-review of the
genus.

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
- `manifest/review_queue.csv` — the 114 open items above; each row can be
  marked `resolved` with a `resolution`/`resolved_by`/`resolved_date` and
  that resolution will be carried forward automatically the next time the
  pipeline runs.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

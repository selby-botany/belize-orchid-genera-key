# Prototype 03, Phase 1: implementation and test plan

Engineer audience.

- [Prototype 03, Phase 1: implementation and test plan](#prototype-03-phase-1-implementation-and-test-plan)
  - [Purpose](#purpose)
  - [1. Commit sequence](#1-commit-sequence)
  - [2. Test plan](#2-test-plan)
    - [2.1 Convention](#2-1-convention)
    - [2.2 `test_build_scan_inventory.py`](#2-2-test_build_scan_inventorypy)
    - [2.3 `test_parse_genus_page.py`](#2-3-test_parse_genus_pagepy)
    - [2.4 `test_export_review_queue.py`](#2-4-test_export_review_queuepy)
    - [2.5 OCR harness: smoke check, not a unit test](#2-5-ocr-harness-smoke-check-not-a-unit-test)
  - [3. Pilot gate](#3-pilot-gate)
  - [4. Full-run acceptance checklist](#4-full-run-acceptance-checklist)
  - [Metadata](#metadata)

## Purpose

The order of work, and how each piece of it is verified, so review and
implementation can proceed commit by commit rather than as one large,
hard-to-audit change.

## 1. Commit sequence

Subjects follow this repository's own convention (`type(scope): summary`,
observed directly in its git log — not the multi-paragraph commit-body
convention that governs the separate 1121-citrus project). Commits land
locally as work proceeds; nothing is pushed to any remote without asking
first.

| # | Subject | Gist |
| --- | --- | --- |
| 1 | `docs(prototype-03): add problem overview and motivation` | Doc 1 |
| 2 | `docs(prototype-03): add requirements` | Doc 2 |
| 3 | `docs(prototype-03): add architecture and design overview` | Doc 3 |
| 4 | `docs(prototype-03): add data formats and relationships` | Doc 4 |
| 5 | `docs(prototype-03): add detailed module design` | Doc 5 |
| 6 | `docs(prototype-03): add implementation and test plan` | Doc 6 (this document) |
| 7 | `docs(prototype-03): add prototype README` | Navigation stub, document index |
| 8 | `feat(prototype-03): add scan inventory and audit tooling` | `build_scan_inventory.py` + tests |
| 9 | `feat(prototype-03): add preprocessing QA and transform` | `preprocess_scan.py` + tests; recipe applied only if evidence shows it's needed |
| 10 | `feat(prototype-03): add page OCR harness` | Forked `ocr_page.swift` + accept/reject thresholds |
| 11 | `feat(prototype-03): add genus and field structural parser` | `parse_genus_page.py` + tests — the core new logic |
| 12 | `feat(prototype-03): add review queue export` | `export_review_queue.py` + tests |
| 13 | `feat(prototype-03): add pipeline orchestrator` | `run_pipeline`, `--pilot` and full-range modes |
| 14 | `feat(prototype-03): run pilot extraction over a representative sample` | Pilot output + a short pilot report (§3) |
| 15 | `feat(prototype-03): run extraction over the captured page range` | Full-run output, only after the pilot gate passes |
| 16 | `docs(prototype-03): add results summary for botanist review` | Coverage, review-queue size, known gaps — plain language |

## 2. Test plan

### 2.1 Convention

`unittest`, run through `../bin/python3`, loading the module under test
directly by file path — exactly `prototype-02/test/test_build_scan_manifest.py`'s
own pattern (`importlib.util.spec_from_file_location`). No pytest
dependency, no package structure, no new test framework introduced.

Every test fixture is a small, synthetic, hand-written input (a handful of
`Line`/`PageOCRRecord`-shaped objects or a tiny temp-directory image set) —
never a dependency on running real Vision OCR at test time. Vision is
macOS-only and its output is not byte-reproducible across runs by
construction; a test that depended on it would not be a pure function of
the commit under test. Real OCR is exercised only by the pilot and full
runs themselves (§3, §4), which are commits with recorded, reviewed output
— not by the unit-test suite.

### 2.2 `test_build_scan_inventory.py`

- `sha256_of` is stable across two reads of the same file.
- `parse_claimed_identity` correctly classifies one example each of `page`,
  `plate`, front matter, and an unrecognized name (`m276.jpeg`-shaped).
- `detect_anomalies` flags a sub-threshold-dimension file as `too_small`
  (the `page-065 1.jpeg` case) and flags two entries sharing a `sha256` as
  duplicates of each other.
- Review-state carry-forward: given a previous inventory and an unchanged
  file, `review_status` carries forward; given a previous inventory and a
  file whose `sha256` changed, `review_status` resets to `unreviewed` with a
  remark naming the superseded checksum — the direct regression test for
  defect #1 (detailed design, §8).

### 2.3 `test_parse_genus_page.py`

- `find_genus_headers` matches a numbered, title-case genus-plus-author
  line and does not match ordinary body prose.
- `segment_fields` assigns lines under each of the closed field labels
  correctly on a synthetic two-genus page (modeled directly on the real
  page 50 sample: `Psilochilus`/`Epistephium`, `ETYMOLOGY`, `GENERAL
  DISTRIBUTION`, `DISTRIBUTION IN BELIZE`, `HABITAT`, `FLOWERING SEASON`,
  `NOTE`), and marks an unrecognized label span `uncertain` rather than
  guessing.
- `build_genus_records` stitches a genus whose treatment spans two
  synthetic pages using running-head continuity, and flags a synthetic
  discontinuity (a skipped genus number) as a review-queue item rather than
  silently proceeding.
- A synthetic species entry nested under a genus appears in that genus's
  `species` list and not merged into its `fields`.

### 2.4 `test_export_review_queue.py`

- Each `queue_from_*` function produces rows with the documented columns
  from a small synthetic input.
- `merge_with_previous` preserves `status`/`resolution`/`resolved_by`/
  `resolved_date` for a row whose `item_id` recurs in the new run, and adds
  new rows untouched — the direct regression test for defect #2.

### 2.5 OCR harness: smoke check, not a unit test

`ocr_page.swift` is exercised by running it against one small fixture image
checked into `test/fixtures/` and confirming the output is well-formed
`page_ocr.jsonl` (parses as JSON, has the documented fields, `columns >=
1`). This is a smoke check, not a correctness test — Vision's actual
recognition is not mocked and is not asserted against a fixed expected
transcription, matching how prototype-02 validated this same script
originally (by running it and inspecting real output).

## 3. Pilot gate

Before the full 1–190 range is processed (commit 15), the pipeline runs
once over a small sample chosen to be **hard**, not representative:

| File(s) | Why it's in the pilot |
| --- | --- |
| `page-050.jpeg` | Clean two-column text page, already inspected during design; the known-good case |
| `titlepage.jpeg` | Front matter — must be inventoried, must not reach the parser |
| `page-030p1.jpeg`, `page-030p2.jpeg` | Colour-plate pair — classification and linkage to page 30 |
| `page-064.jpeg`, `page-065.jpeg`, `page-065 1.jpeg`, `page-066.jpeg` | The corrupt-stub neighborhood — the stub must be flagged, not silently merged with or mistaken for the real page 65 |
| `m276.jpeg` | The unexplained outlier — must be flagged for identification, not guessed at or silently dropped |

**Pass condition:** every file above resolves to exactly one of accepted
extraction, review-queue item with a legible reason, or a recorded
anomaly — none crash the pipeline and none disappear. On `page-050.jpeg`
specifically, both genus records (`Psilochilus`, `Epistephium`) are
produced with correct `genus_number`, non-empty `ETYMOLOGY` and `HABITAT`
fields, and provenance pointing back to `page-050.jpeg`.

**On failure:** the run is not scaled up. The specific failure is fixed (or,
if it reveals a scope question rather than a bug, added to the requirements
document's governance-inputs table), and the pilot re-run, before commit 15
is attempted. This is the direct implementation of the "prove the approach,
then produce the corpus" principle named in the architecture document, §5.

## 4. Full-run acceptance checklist

Before Phase 1 is called complete:

1. Every file in `images/20260804-page-scans/` is accounted for in
   `manifest/scan_inventory.json` — accepted, flagged, or excluded, never
   silently absent.
2. `manifest/review_queue.csv` contains only genuine residual items, each
   with a legible reason.
3. Every record in `analysis/genera.jsonl` carries provenance
   (`source_pages`, and per-field `source_image`/`confidence`).
4. `analysis/mcleish.genera.md` is regenerated and reads as plausible
   prose on a manual spot check — not just schema-valid.
5. The results-summary document (commit 16) states coverage honestly: how
   many of the 190 captured pages produced accepted genus records, how many
   are in the review queue, and why — no implied completeness beyond what
   was actually captured (requirements, §1.1).

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

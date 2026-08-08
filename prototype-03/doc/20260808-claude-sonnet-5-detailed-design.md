# Prototype 03, Phase 1: detailed module design

Engineer audience. Assumes the architecture document's five stages and the
data document's file schemas.

- [Prototype 03, Phase 1: detailed module design](#prototype-03-phase-1-detailed-module-design)
  - [Purpose](#purpose)
  - [1. Module map](#1-module-map)
  - [2. `bin/build_scan_inventory.py` (Stage A)](#2-binbuild_scan_inventorypy-stage-a)
  - [3. `bin/preprocess_scan.py` (Stage B)](#3-binpreprocess_scanpy-stage-b)
  - [4. `bin/ocr_page.swift` (Stage C, forked)](#4-binocr_pageswift-stage-c-forked)
  - [5. `bin/parse_genus_page.py` (Stage D)](#5-binparse_genus_pagepy-stage-d)
  - [6. `bin/export_review_queue.py` (Stage E)](#6-binexport_review_queuepy-stage-e)
  - [7. `bin/run_pipeline` (orchestrator)](#7-binrun_pipeline-orchestrator)
  - [8. Carried-forward defects, and where each is fixed](#8-carried-forward-defects-and-where-each-is-fixed)
  - [Metadata](#metadata)

## Purpose

Script-by-script design: inputs, outputs, main functions, and — explicitly —
which of prototype-02's review-documented defects each module exists to not
repeat.

## 1. Module map

| Script | Stage | Language | Status |
| --- | --- | --- | --- |
| `bin/build_scan_inventory.py` | A | Python, via `../bin/python3` | New |
| `bin/preprocess_scan.py` | B | Python, via `../bin/python3` + `../bin/imagemagick` | New; recipe body copied from prototype-02 |
| `bin/ocr_page.swift` | C | Swift (macOS, Vision) | Forked from `prototype-02/bin/ocr_page.swift` |
| `bin/parse_genus_page.py` | D | Python, via `../bin/python3` | New — no prior art in this repository |
| `bin/export_review_queue.py` | E | Python, via `../bin/python3` | New; shape modeled on prototype-01's review queue |
| `bin/run_pipeline` | orchestration | bash | New |

All Python scripts follow prototype-02's test convention exactly (§Test
plan, implementation plan document): pure functions importable via
`importlib.util.spec_from_file_location`, no package structure, no
third-party test framework.

## 2. `bin/build_scan_inventory.py` (Stage A)

Reads `images/20260804-page-scans/`, writes
`manifest/scan_inventory.json` (data document, §2).

```text
sha256_of(path: Path) -> str
identify(path: Path) -> ImageFacts            # width, height, colorspace via PIL — Image.open(path).size / .mode; no shell-out, matching classify_captures.py's own approach rather than invoking ../bin/imagemagick from inside Python
parse_claimed_identity(filename: str) -> ClaimedIdentity
    # kind: page | front_matter | plate | unrecognized
    # regex families: r"^page-(\d{3})\.jpeg$", r"^page-(\d{3})p([12])\.jpeg$"
    # front_matter: matched against a fixed, explicit list of known labels
    #   (titlepage, copyrightpage, dedication-page, acknowledgments-1,
    #   forward-1, frontis-1, frontis-plate-1, preface-1, preface-2,
    #   toc-1..toc-5) — extending this list is a one-line change, not a
    #   silent broadening of the page-number regex (defect #3, §8)
detect_anomalies(entry: Entry, all_entries: list[Entry]) -> list[str]
    # too_small: min(width, height) below a fixed floor (catches
    #   page-065 1.jpeg-class stubs)
    # duplicate_of:<filename>: identical sha256 to an earlier entry
    # unparseable_filename: claimed_identity.kind == "unrecognized"
    # colorspace_mismatch: kind == "plate" and colorspace != "sRGB", or
    #   kind == "page" and colorspace != "Gray"
load_previous_inventory(path: Path) -> dict[sha256, ReviewState] | None
build_inventory(source_dir: Path, previous: dict | None) -> Inventory
main() -> None
```

`load_previous_inventory`/`build_inventory` together implement the
checksum-keyed carry-forward that fixes defect #1 (§8): a file's
`review_status` follows its `sha256`, so replacing file content resets
review state and renaming or reordering files does not lose it.

## 3. `bin/preprocess_scan.py` (Stage B)

Reads inventory entries with `kind in {page, plate}`, writes derived,
OCR-ready images (path convention: mirrors the source tree under a
`derived/` subdirectory of wherever the orchestrator places working
output — not committed, generated only).

```text
measure_background_stats(path: Path) -> BrightnessStats
    # percentile brightness, same method prototype-02's Verification
    # section used to confirm its own recipe worked
needs_transform(stats: BrightnessStats) -> bool
    # evidence-based decision, not a default — see architecture, §3.2
transform_text(path: Path, out_path: Path) -> None
    # shells to ../bin/imagemagick with prototype-02's documented recipe,
    # unchanged: -colorspace Gray, blur-and-divide flat field, -level
    # 0%,90%, unsharp
transform_plate(path: Path, out_path: Path) -> None
    # -channel RGB -contrast-stretch 0.2%x0.05% +channel
main() -> None
```

If `needs_transform` is false for the sampled set, this stage's role
shrinks to a pass-through copy (or is skipped entirely and Stage C reads
source images directly) — that determination, and its evidence, is recorded
in the pilot report (implementation plan document), not hardcoded here in
advance.

## 4. `bin/ocr_page.swift` (Stage C, forked)

Starts from `prototype-02/bin/ocr_page.swift` unchanged for `recognize` and
`assignColumns` — both are already correct and already tested against real
pages. Additions:

```text
struct PageResult {
    // existing fields (image, lineCount, meanConfidence, lowConfidenceCount,
    // columns, text), plus:
    let acceptStatus: String        // "accepted" | "rejected"
    let rejectReasons: [String]
}

acceptPage(_ result: PageResult, thresholds: Thresholds) -> (Bool, [String])
    // combines a confidence/low-confidence-count check with a structural
    // check (line-count band); never accepts on confidence alone
    // (requirements, §2) — this is the direct fix for the "confidence is
    // worthless as a quality gate" finding in prototype-02's own README
```

Output changes from a single pretty-printed JSON array to one JSON object
per line (`analysis/page_ocr.jsonl`), so a partial run's output is still
valid line-by-line and large runs don't require holding one array in
memory.

Running-head extraction (page number, genus number/name in the top text
band) is **not** duplicated here: Stage C's job is text recognition, and the
running head is just another line in its output. The genus-number
continuity check that uses it belongs to Stage D (§5), which has the
cross-page context Stage C, operating one page at a time, does not.

## 5. `bin/parse_genus_page.py` (Stage D)

Reads `analysis/page_ocr.jsonl`, writes `analysis/genera.jsonl` and
`analysis/mcleish.genera.md`. The core new logic in this project.

```text
FIELD_LABELS: frozenset[str]     # ETYMOLOGY, GENERAL DISTRIBUTION,
                                  # DISTRIBUTION IN BELIZE, HABITAT,
                                  # FLOWERING SEASON, NOTE, ...
ORGAN_LEADS: frozenset[str]      # Roots, Stems, Leaves, Inflorescences,
                                  # Flowers, Sepals, Petals, Lip, Column, ...

find_genus_headers(lines: list[Line]) -> list[GenusHeaderMatch]
    # pattern: numbered, bold genus name + author, e.g. "18. Psilochilus
    # Barb. Rodr." — matched structurally (leading number, period, title
    # case), not against a fixed name list, since the genus list itself is
    # exactly what's being discovered

cross_check_running_head(page: PageOCRRecord) -> RunningHeadMatch | None
    # "<number> <Genus>" in the top text band; validates a header match
    # and links treatments spanning more than one page

find_species_entries(lines: list[Line], genus: GenusHeaderMatch) -> list[SpeciesMatch]
    # binomial + author + publication + synonymy block, nested under the
    # owning genus, never merged into its fields (requirements, §4 item 6)

segment_fields(lines: list[Line], start: int, end: int) -> dict[str, FieldMatch]
    # assigns each line span to a FIELD_LABEL or ORGAN_LEAD, or marks it
    # "uncertain" — never guesses past that point (requirements, §1.5)

build_genus_records(pages: list[PageOCRRecord]) -> list[GenusRecord]
    # stitches multi-page treatments using genus-number continuity from
    # cross_check_running_head; a discontinuity is a review-queue item,
    # not a silently accepted skip

render_markdown(records: list[GenusRecord]) -> str
    # emits analysis/mcleish.genera.md in prototype-01's own corpus style,
    # with a source-page line added under each heading

main() -> None
```

## 6. `bin/export_review_queue.py` (Stage E)

Reads the inventory, OCR records, and genus records; writes
`manifest/review_queue.csv` (data document, §3).

```text
queue_from_inventory(inventory: Inventory) -> list[QueueRow]
queue_from_ocr(pages: list[PageOCRRecord]) -> list[QueueRow]
queue_from_genera(records: list[GenusRecord]) -> list[QueueRow]
merge_with_previous(new_rows: list[QueueRow], previous_path: Path) -> list[QueueRow]
    # carries forward status/resolution/resolved_by/resolved_date by
    # item_id — the fix for defect #2 (§8): a reviewer's resolution is
    # never silently discarded by the next run
write_csv(rows: list[QueueRow], path: Path) -> None
main() -> None
```

## 7. `bin/run_pipeline` (orchestrator)

A bash driver, in the style of `prototype-02/scripts/build-qa-reports`:
runs Stages A through E in order, with a `--pilot FILE...` flag that
restricts Stages B–E to a named file list (the pilot sample, architecture
document §5) and a default full-range mode that processes every page found
by Stage A. Never invokes a stage's script directly with a hand-built image
list outside these two modes, so the pilot and full runs exercise exactly
the same code path.

## 8. Carried-forward defects, and where each is fixed

From `prototype-02/doc/20260727-claude-opus-5-text-extraction-plan.md`,
"Defects in the current tooling":

| # | Defect | Fixed in |
| --- | --- | --- |
| 1 | Stale review decisions survive a file replacement | `build_scan_inventory.py`, checksum-keyed carry-forward (§2) |
| 2 | Reviewer edits to a CSV are silently discarded on regeneration | `export_review_queue.py`, `merge_with_previous` (§6) |
| 3 | Page range and filename pattern hardcoded; one stray file aborts the build | `build_scan_inventory.py`, `detect_anomalies` records rather than raises (§2) |
| 4 | Audit report shows contradictory encoded vs. display dimensions | Not applicable here — this capture set carries EXIF orientation `TopLeft` uniformly on every file sampled; `build_scan_inventory.py` still records raw `width`/`height` from PIL, which is correct only because rotation isn't in play, and this assumption is verified across the full set during the audit, not just assumed from the sample |
| 5 | No personal-information field | Out of scope for Phase 1 — the McLeish scans, unlike prototype-02's phone captures, don't carry a documented PII risk; revisit if evidence emerges |
| 6 | No capture-condition metadata (EXIF timestamp, camera) extracted | Deferred — not required by any Phase 1 requirement; can be added to `build_scan_inventory.py`'s `identify()` without a schema break if it becomes useful |
| 7 | No focus/near-duplicate detection | Near-duplicate detection exists via `sha256` equality (exact only); perceptual near-duplicate detection is deferred as not required for this capture batch |
| 8–11 | Review workflow, path handling, `.gitignore`, missing `test/` in the plan | Addressed structurally: `manifest/review_queue.csv` is a paste-able single table (§6); `run_pipeline` computes paths relative to the repository root, never hardcoded; `images/` is already covered by the root `.gitignore`'s `images/` rule; `prototype-03/test/` exists from the first commit (implementation plan document) |

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

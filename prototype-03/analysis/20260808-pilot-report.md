# Pilot run report

Ran `bin/run_pipeline --pilot` over the sample specified in the
implementation plan document, §3: `page-050.jpeg`, `titlepage.jpeg`,
`page-030p1.jpeg`/`page-030p2.jpeg`, the `page-064`/`page-065`/
`page-065 1`/`page-066` neighborhood, and `m276.jpeg`. This is a
deliberately hard, non-representative sample -- it exists to break the
pipeline in ways a clean run of contiguous pages would not.

## Pass condition (implementation plan document, §3)

> Every file above resolves to exactly one of accepted extraction,
> review-queue item with a legible reason, or a recorded anomaly -- none
> crash the pipeline and none disappear. On `page-050.jpeg` specifically,
> both genus records (`Psilochilus`, `Epistephium`) are produced with
> correct `genus_number`, non-empty `ETYMOLOGY` and `HABITAT` fields, and
> provenance pointing back to `page-050.jpeg`.

**Met.** Per file:

| File | Outcome |
| --- | --- |
| `page-050.jpeg` | Accepted. `Psilochilus` (genus 18) and `Epistephium` (genus 19) both extracted -- see below. |
| `titlepage.jpeg` | Accepted by OCR, correctly never reaches the parser (front matter, no page number). |
| `page-030p1.jpeg`, `page-030p2.jpeg` | Rejected by OCR (`line_count_below_band` -- a photograph, not text) -- in the review queue, not silently dropped. |
| `page-064.jpeg` | Accepted by OCR (a figure-caption page); running head reads `27 Catasetum`, which correctly does not match the open `Epistephium` record -- flagged `discontinuity`, not silently merged. |
| `page-065.jpeg` | Accepted. Contains genus 28's own header (`Clowesia`) -- extracted as its own record. |
| `page-065 1.jpeg` | Rejected by OCR (the known corrupt stub, 0 lines) -- also independently flagged `too_small` + `unparseable_filename` by Stage A. Never confused with the real `page-065.jpeg`. |
| `page-066.jpeg` | Accepted by OCR. No genus header of its own, and its running head ("28 Clowesia") was split by Vision into two separate line observations -- flagged `ambiguous_genus_boundary` against `Clowesia` rather than silently dropped (see below). |
| `m276.jpeg` | Rejected by OCR (`line_count_below_band`); independently flagged `unparseable_filename` by Stage A. |

`Psilochilus`'s fields, confirmed non-empty with provenance:

```json
{
  "genus_number": "18",
  "source_pages": [50],
  "etymology": "From the Greek psilo (smooth) and chilus (lipped) in reference to the appearance of the lip.",
  "habitat": "On leaf litter over sandy soil on the forest floor and on mossy tree branches about 3 m above the ground.",
  "source_image": "page-050.jpeg"
}
```

Nothing crashed. Nothing disappeared without a trace: every file above
is accounted for in `scan_inventory.json`, `page_ocr.jsonl`,
`genera.jsonl`, or `review_queue.csv` -- most of them in more than one.

## Two real defects found and fixed during this pilot

Both are documented in code comments at the point they were fixed
(`parse_genus_page.py`, `export_review_queue.py`) and in their own commits
(`ba6dd8f`); summarized here because a pilot run's purpose is to surface
exactly this kind of finding before it reaches the full 190-page range.

1. **Silent data loss on a split running head.** `page-066.jpeg`'s running
   head ("28 Clowesia") was recognized by Vision as two separate line
   observations, which defeated the single-line "`<number>` `<Genus>`"
   pattern. The original code treated "no readable running head" the same
   as "confirmed not a continuation" and silently skipped the page --
   losing a real synonymy block for `Clowesia` with no trace anywhere.
   Fixed: a substantive page with an open genus record and no readable
   running head is now flagged `ambiguous_genus_boundary` instead.
2. **Misleading review-queue detail text.** The fix for (1) reused the
   `discontinuity` case's review-queue wording ("running head named a
   different genus than expected"), which is inaccurate when no running
   head was found at all. Fixed with a reason-specific explanation.

## What this means for the full run

- The two genus records this pilot flagged `needs_review`
  (`Epistephium`, `Clowesia`) are not defects in themselves -- they are
  the pipeline correctly reporting genuine gaps created by the pilot's
  deliberately non-contiguous file list (page 50 next to page 64-66 is
  not how the real page range will be processed). Running the full
  1-190 range, where pages are contiguous, should produce far fewer
  `discontinuity`/`ambiguous_genus_boundary` flags in practice --
  reserved for real anomalies (a torn page, a genuinely garbled running
  head) rather than an artifact of pilot sampling.
- The acceptance thresholds in `ocr_page.swift` (`Thresholds`, still
  labeled provisional in that file's own comments) produced sensible
  accept/reject decisions on every pilot file, including the two
  adversarial cases (the corrupt stub, the near-blank plates). No
  threshold adjustment is made on the strength of this one pilot; if the
  full run's review-queue volume turns out disproportionate, that is the
  point to revisit them with real evidence rather than now, with six.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

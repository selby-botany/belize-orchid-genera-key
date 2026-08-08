# Prototype 03: pipeline-driven feature extraction from the McLeish scan set

Replaces the hand-curation half of `../prototype-01/` with a pipeline, on a
new and much larger capture set than either prior prototype had. This
prototype exists to answer one question: **can a pipeline turn a scan of
this book into a reviewable genus characteristic corpus, at the scale of the
whole taxonomic treatment rather than eight hand-picked genera?**

Prototype 01 built a genus corpus by hand for 8 genera because its OCR page
mapping failed. Prototype 02 proved the image-capture and OCR approach on 6
pages but never ran it over the book. This prototype has 243 new captures —
190 contiguous, already page-identified pages of body text plus front matter
and colour plates — and the job of extracting structured genus text from
them at that scale.

**Status:** planning documents in `doc/`; pipeline not yet implemented.

## What this prototype does (planned)

1. Audits `images/20260804-page-scans/` — identity, checksum, dimensions,
   colorspace, and anomaly flags — without discarding or silently trusting
   any file's filename-claimed page number.
2. Preprocesses and classifies scans for OCR, reusing prototype-02's
   validated recipe only where the audit shows this capture batch actually
   needs it.
3. Runs column-aware OCR (forked from `prototype-02/bin/ocr_page.swift`)
   over genus-treatment pages.
4. Parses the OCR'd text into structured genus and species records using
   the book's own field vocabulary (`ETYMOLOGY`, `DISTRIBUTION IN BELIZE`,
   `HABITAT`, italic organ leads, and so on), with provenance back to source
   image and OCR confidence on every field.
5. Emits both a machine-readable corpus and a regenerated
   `prototype-01/doc/mcleish.genera.md`-style Markdown corpus for botanist
   review, plus a review queue for anything the pipeline can't resolve on
   its own.

## Documents

Read in this order — document 1 is the entry point, including for a
non-technical reader:

1. [Problem overview and motivation](doc/20260808-claude-sonnet-5-problem-overview.md) — everyone
2. [Requirements](doc/20260808-claude-sonnet-5-requirements.md) — everyone, botanist-critical
3. [Architecture and design](doc/20260808-claude-sonnet-5-architecture.md) — everyone
4. [Data formats and relationships](doc/20260808-claude-sonnet-5-data.md) — everyone, mostly engineer
5. [Detailed module design](doc/20260808-claude-sonnet-5-detailed-design.md) — engineer
6. [Implementation and test plan](doc/20260808-claude-sonnet-5-implementation-plan.md) — engineer

## Layout

```text
doc/        planning documents and, later, a pilot/full-run results note
bin/        pipeline scripts (Python; a forked Swift OCR harness)
manifest/   scan inventory and review-queue artifacts — generated
analysis/   extracted feature descriptions: JSONL and regenerated Markdown — generated
test/       unit tests for the manifest and parsing tooling
images/     capture set — large binaries, excluded from version control
```

`analysis/` and `manifest/` follow prototype-01 and prototype-02's own
naming. This prototype deliberately does not use a `prototype-03/data/`
directory, which `doc/20260808-belize-orchid-characteristic-of-taxa.md`
already reserves for a different, explicitly out-of-scope data source (see
the problem overview).

## Requirements

Same as the repository overall: Docker for the `../bin/` wrappers, and
macOS with the Xcode command line tools for the Vision-based OCR stage. See
the [repository README](../README.md).

## Source material

McLeish, I., Pearce, N. R., Adams, B. R., & Briggs, J. S. (1995). *Native
orchids of Belize*. A.A. Balkema. The scans in `images/` are held for
private research use and are not redistributed.

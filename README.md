# Genera key of Belize orchids

A dichotomous identification key for the orchid genera of Belize, built
from scanned pages of a source reference text and a curated genus
characteristic corpus.

## Project status

The key itself does not exist yet, but the structured genus data it will
be built from does. Work so far spans four prototypes:

- [`prototype-01/README.md`](prototype-01/README.md) — a completed page-ordering and genus-characteristic
  pipeline: OCR-assisted page recovery for the source scan set, a
  hand-curated characteristic corpus for eight genera, and
  characteristic/morphological clustering analysis. See
  [`prototype-01/README.md`](prototype-01/README.md).
- [`prototype-02/README.md`](prototype-02/README.md) — capture auditing and OCR preprocessing work that
  proved the image-capture and OCR approach on a small sample, superseded
  by prototype-03's larger capture set before running over the full book.
  See [`prototype-02/README.md`](prototype-02/README.md).
- [`prototype-03/README.md`](prototype-03/README.md) — **complete (Phase 1)**: a pipeline-driven extraction
  that turned 190 contiguous captured pages into 69 structured,
  provenance-carrying genus records, at the scale of the whole captured
  treatment rather than a hand-picked sample. See
  [`prototype-03/README.md`](prototype-03/README.md) and its
  [results summary](prototype-03/analysis/20260808-results-summary.md).
- `prototype-04/README.md`](prototype-03/README.md) — **planning (Phase 2)**: turning prototype-04's genus
  records into a working identification key, plus analytics that measure
  how well it performs. See
  [`prototype-04/README.md`](prototype-04/README.md).

## Repository layout

- `doc/` — project-level design documents
- `prototype-01/mcleish/` — raw page-scan images used by prototype-01;
  large binary captures, excluded from version control (see
  `.gitignore`)
- `prototype-01/` — page-mapping pipeline, genus corpus, and
  characteristic analysis (complete)
- `prototype-02/` — image capture auditing and OCR extraction tooling
  (superseded by prototype-03's capture set for full-book extraction)
- `prototype-03/` — pipeline-driven genus/species extraction from a
  190-page capture set (Phase 1, complete); its own `images/` directory
  holds that capture set, also excluded from version control
- `prototype-04/` — genus key and validation analytics, built from
  prototype-03's output (Phase 2, planning)
- `bin/` — shared Docker-backed tool wrappers (`imagemagick`, `jq`, `node`,
  `python3`)
- `docker/` — build contexts for the locally built tool images

## Requirements

**Docker**, for the tool wrappers in `bin/`. Everything they provide —
ImageMagick, jq, Node.js, and a Python carrying numpy, scipy, and Pillow — is
containerized and version-pinned, so nothing needs installing on the host and
the tooling is a property of this repository rather than of the machine.
`bin/python3` builds its image from `docker/python-imaging/` on first use; the
others use pinned upstream images.

**macOS with the Xcode command line tools**, for the OCR stages. This one
cannot be containerized and is not optional:

| Script | Frameworks |
| --- | --- |
| `prototype-01/bin/extract_mcleish_header_candidates.swift` | Vision, AppKit |
| `prototype-01/bin/render_mcleish_review_sheets.swift` | CoreImage, AppKit |
| `prototype-02/bin/extract_mcleish_page_text.swift` | Vision, AppKit |
| `prototype-02/bin/ocr_page.swift` | Vision, AppKit |
| `prototype-03/bin/ocr_page.swift` | Vision, AppKit |

Prototype 04 has no OCR stage — it reads prototype-03's already-extracted
text, not the scanned images, so it needs no macOS/Vision dependency.

Vision, AppKit, and CoreImage are Apple frameworks. Swift itself runs on
Linux, but those frameworks do not exist there, so no container can run these
scripts. Every prototype therefore depends on a macOS host for text
recognition, even though the rest of the pipeline is portable. Scripts that
shell out to `swift` check for it first and explain the requirement rather
than failing with `command not found`.

Replacing the OCR stage with a containerizable engine — Tesseract, PaddleOCR,
or a hosted vision model — would remove the constraint, but that is a change
of engine rather than of packaging and has not been evaluated.

## Source material

The genus descriptions originate from scanned pages of *Native orchids of
Belize*[^mcleish]. The raw scans live under `prototype-01/mcleish/` and
`prototype-03/images/`, neither committed to this repository (see
`.gitignore`). The curated, machine-readable output derived from that
source — page-mapped images, extracted genus text, characteristic data —
lives under `prototype-01`](prototype-01/README.md), [`prototype-02`](prototype-02/README.md), and, at Phase 1 completion,
(`prototype-03/analysis/`)[`prototype-03`](prototype-03/README.md).

## License

© 2026 Marie Selby Botanical Gardens

AGPL-3.0-or-later — see [LICENSE.md](LICENSE.md).

[^mcleish] McLeish, I., Pearce, N. R., Adams, B. R., & Briggs, J. S. (1995).
*Native orchids of Belize*. A.A. Balkema.

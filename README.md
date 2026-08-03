# Genera key of Belize orchids

A dichotomous identification key for the orchid genera of Belize, built
from scanned pages of a source reference text and a curated genus
characteristic corpus.

## Project status

The key itself does not exist yet. Work so far builds the pipeline and
data a key will be generated from, across two prototypes:

- `prototype-01/` — a completed page-ordering and genus-characteristic
  pipeline: OCR-assisted page recovery for the source scan set, a
  hand-curated characteristic corpus for eight genera, and
  characteristic/morphological clustering analysis. See
  [prototype-01/README.md](prototype-01/README.md).
- `prototype-02/` — in-progress capture auditing and OCR preprocessing
  work, aimed at a higher-fidelity replacement for the raw scan set used
  by prototype-01. See `prototype-02/doc/`.

## Repository layout

- `doc/` — project-level design documents
- `mcleish/` — raw page-scan images of the source reference text; large
  binary captures, excluded from version control (see `.gitignore`)
- `prototype-01/` — page-mapping pipeline, genus corpus, and
  characteristic analysis (complete)
- `prototype-02/` — image capture auditing and OCR extraction tooling
  (in progress)
- `bin/` — shared Docker-backed tool wrappers (for example `imagemagick`)

## Source material

The genus descriptions originate from scanned pages of *Native orchids of Belize*[^mcleish]. The raw scans live in `mcleish/` and
are not committed to this repository. The curated, machine-readable
output derived from that source — page-mapped images, extracted genus
text, characteristic data — lives under `prototype-01/` and
`prototype-02/`.

## License

© 2026 Marie Selby Botanical Gardens

AGPL-3.0-or-later — see [LICENSE.md](LICENSE.md).


[^mcleish] McLeish, I., Pearce, N. R., Adams, B. R., & Briggs, J. S. (1995). *Native orchids of Belize*. A.A. Balkema.

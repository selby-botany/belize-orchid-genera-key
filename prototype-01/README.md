# Prototype 01: page mapping and genus characteristic corpus

First working pipeline for this project. Complete for the eight genera it
covers (McLeish pages 13, 15, 41–48); superseded for image handling by the
capture-auditing work in `../prototype-02/`, but its genus corpus and
analysis tooling remain the current source of characteristic data.

## What this prototype does

1. Recovers the true source-document page number for each raw scan in
   `../mcleish/` from OCR header candidates, with manual override and
   set-aside controls for ambiguous or unusable captures.
2. Resolves duplicate captures of the same page and emits a rename plan
   that renumbers scans to their page number without discarding
   alternates.
3. Holds a hand-curated characteristic corpus (`doc/mcleish.genera.md`)
   for the eight genera extracted from the stabilized page set.
4. Computes characteristic and morphological clustering analysis over
   that corpus.

## Genera covered

Corymborkis, Erythrodes, Goodyera, Habenaria, Hetaeria, Liparis, Malaxis,
Spiranthes.

## Layout

- `bin/` — pipeline scripts (Swift OCR extraction, Python postprocessing,
  Node.js analysis); see [bin/README.md](bin/README.md)
- `analysis/` — machine-readable pipeline state and analysis outputs; see
  [analysis/README.md](analysis/README.md)
- `doc/` — the curated genus corpus and generated clustering write-ups

## Requirements

jq, Node.js, and Python come from the wrappers in `../bin/` and need Docker
only. The Swift stages do not: `extract_mcleish_header_candidates.swift` uses
Vision and `render_mcleish_review_sheets.swift` uses CoreImage, both
macOS-only frameworks, so this prototype's page-mapping pipeline runs only on
macOS. See the requirements section of the [repository README](../README.md).

## Status

The page-mapping and rename-plan tooling in `bin/` operates on
`../mcleish/`, the raw scan directory, which is not committed to this
repository. The files under `analysis/` and `doc/` in this prototype are
the durable output of already having run that pipeline; they do not
require the raw scans to be present to be read or reused.

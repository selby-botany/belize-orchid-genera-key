# Text extraction plan

- [Text extraction plan](#text-extraction-plan)
  - [Goal](#goal)
  - [Initial scan assessment](#initial-scan-assessment)
  - [Guiding principles](#guiding-principles)
  - [Phase 1: Audit scans and decide what to retake](#phase-1-audit-scans-and-decide-what-to-retake)
    - [1. Build the source manifest](#1-build-the-source-manifest)
    - [2. Produce a visual audit sheet](#2-produce-a-visual-audit-sheet)
    - [3. Apply explicit retake criteria](#3-apply-explicit-retake-criteria)
    - [4. Retake consistently](#4-retake-consistently)
  - [Phase 2: Establish the extraction benchmark](#phase-2-establish-the-extraction-benchmark)
  - [Phase 3: Preprocess without altering the evidence](#phase-3-preprocess-without-altering-the-evidence)
  - [Phase 4: Segment layout and run OCR](#phase-4-segment-layout-and-run-ocr)
  - [Phase 5: Create canonical and derived representations](#phase-5-create-canonical-and-derived-representations)
  - [Phase 6: Proofread and validate](#phase-6-proofread-and-validate)
  - [Suggested project layout](#suggested-project-layout)
  - [Execution order](#execution-order)
  - [Completion criteria](#completion-criteria)
  - [Metadata](#metadata)

## Goal

Create a complete, faithful, and auditable text representation of the scanned
book pages in reading order. The result must preserve botanical names,
typographic distinctions, identification keys, captions, page boundaries, and
uncertainties while also providing clean text suitable for search and further
processing.

The scans remain the source of record. No OCR or corrected transcription will
replace or modify them.

## Initial scan assessment

The current corpus contains:

- 388 JPEG files.
- 247 base page files named for printed pages 013 through 261.
- 141 alternate captures using `-scan2` through `-scan7` suffixes.
- No base files for printed pages 016 and 017.
- Fourteen pages with at least three captures: 040, 041, 060, 064, 066, 068,
  076, 078, 089, 117, 120, 126, 168, and 256.

Representative inspection included pages 013, 014, 015, 040, 041, 066, 076,
089, 140, 200, 256, and 261 and several of their alternate captures. The
following properties recur:

- Most type is sharp enough for OCR and manual proofreading.
- A file generally targets the printed page matching its filename, although
  part or all of the facing page is often visible.
- Perspective varies, and text lines curve toward the gutter on some pages.
- Illumination and white balance vary across and between captures.
- Background papers, hands, neighboring pages, and the book edge occur in the
  frame but usually do not cover the target text.
- Some close captures improve character detail while cutting off lower text or
  figure captions. Wider captures preserve more content but introduce more
  perspective distortion.
- Later `-scanN` suffixes are not consistently better than earlier captures.
- Figures, dichotomous keys, dot leaders, running heads, captions, italic
  scientific names, author abbreviations, diacritics, and multiplication signs
  all require layout-aware handling.

These observations are from a representative review, not a page-by-page
acceptance audit. That audit is the first execution phase.

## Guiding principles

1. Preserve provenance. Every extracted region must identify its source image.
2. Select sources by visible evidence, never by filename suffix alone.
3. Separate recognition from correction. Retain raw OCR and record every human
   correction in version control.
4. Preserve the printed wording. Dictionaries may flag suspicious text but
   must not silently modernize spelling, nomenclature, punctuation, or units.
5. Preserve logical reading order while retaining page and layout anchors.
6. Mark uncertainty explicitly; do not guess at illegible characters.
7. Generate convenient formats from one reviewed canonical transcription.

## Phase 1: Audit scans and decide what to retake

Complete this phase before production OCR. Retaking pages after transcription
begins creates avoidable rework and provenance ambiguity.

### 1. Build the source manifest

Create a machine-readable manifest with one record per printed page and these
fields:

- Printed page number.
- All candidate image filenames.
- Pixel dimensions, orientation, file size, and checksum.
- Selected primary image and optional supplemental image regions.
- Status: `unreviewed`, `accepted`, `composite`, `retake`, or `missing`.
- Review reasons using controlled terms such as `blur`, `crop`, `gutter`,
  `glare`, `perspective`, `shadow`, `occlusion`, and `incomplete`.
- Reviewer, review date, and free-text remarks.

Confirm whether pages 016 and 017 are genuinely missing, intentionally outside
scope, or represented under incorrect filenames. Compare page 015, page 018,
the table of contents, running heads, and textual continuity. Mark the corpus
incomplete until this is resolved.

### 2. Produce a visual audit sheet

Generate contact sheets that place every candidate for a printed page together,
ordered by filename. Add page number, filename, dimensions, and automated image
quality indicators. Automated indicators should include:

- Focus or edge-strength score.
- Highlight and shadow clipping percentages.
- Estimated page quadrilateral and perspective skew.
- Text-region coverage near every page edge.
- Duplicate or near-duplicate detection.

Use these indicators only to prioritize manual review. Botanical illustrations
and large blank areas can make generic quality scores misleading.

Review first the missing pages, the fourteen pages with three or more captures,
and any page flagged by automated checks. Then review every remaining page at
full resolution.

### 3. Apply explicit retake criteria

Accept a page when one image, or documented regions from multiple images,
contains every printed character and caption sharply enough for reliable human
reading. Retake a page when any of the following remains true across all
captures:

- Text or a caption is outside the frame.
- The gutter hides or severely compresses one or more characters.
- Motion blur or missed focus makes similar characters indistinguishable.
- Glare, shadow, a finger, or another object covers printed content.
- Perspective or page curl cannot be corrected without merging or destroying
  characters.
- Compression artifacts erase punctuation, diacritics, or fine italic forms.
- The page sequence cannot be established confidently.

Do not retake solely because a page is rotated, includes background clutter, or
has mild uneven illumination when preprocessing can correct those defects
without changing content.

### 4. Retake consistently

For required retakes:

- Use a fixed copy stand with the camera sensor parallel to the page.
- Support the book in a non-destructive cradle; use a clear platen only if it
  is safe for the binding and introduces no glare.
- Photograph one complete printed page per frame with margin on all four sides.
- Use two diffuse, high-color-rendering lights placed symmetrically.
- Lock focus, exposure, white balance, focal length, and camera position.
- Capture enough detail for at least 400 pixels per printed inch when practical.
- Prefer RAW plus highest-quality JPEG; retain both if RAW is available.
- Keep hands, clips, and weights outside the printed area.
- Include a color and scale target in a calibration frame for each session, not
  over page content.
- Name retakes without deleting prior images, then update the manifest.

Run the same audit on each retake before declaring the image set complete.

## Phase 2: Establish the extraction benchmark

Select a 12- to 20-page pilot that spans the difficult layouts in the book.
Include at least:

- Ordinary descriptive prose.
- A chapter or genus opening such as page 013.
- A dense dichotomous key such as page 089.
- Pages with figures and captions such as 066 and 076.
- Pages with multiple captures such as 040, 041, 256.
- Later pages such as 261 to test whether capture conditions changed.
- Italic names, author citations, diacritics, fractions, multiplication signs,
  dot leaders, and text continuing across a page boundary.

Create a manually transcribed ground-truth set for the pilot. Have a second
reviewer compare it directly with the images before using it to score OCR.

Evaluate at least two OCR approaches with layout coordinates. Suitable
candidates include Tesseract with ALTO or hOCR output and a modern document OCR
engine such as PaddleOCR, Kraken, or a commercial engine if one is already
licensed. Do not choose an engine from a few visually pleasing examples.
Measure:

- Character error rate and word error rate.
- Accuracy for italic scientific names and author abbreviations.
- Reading-order accuracy.
- Key numbering, indentation, dot-leader, and destination accuracy.
- Caption detection and separation from body text.
- Page-number and running-head exclusion from body text.

Choose the most accurate reproducible pipeline. If engines have complementary
strengths, retain both outputs and use disagreement to prioritize review rather
than automatically blending their text.

## Phase 3: Preprocess without altering the evidence

Create derived working images; never overwrite source JPEGs.

For each selected source:

1. Crop to the target printed page named by the file, excluding the facing page.
2. Correct orientation and coarse perspective from the page boundary.
3. Dewarp curved text lines near the gutter when the correction improves the
   pilot OCR score and does not deform characters.
4. Normalize illumination and contrast conservatively.
5. Preserve a color derivative for figures and a grayscale derivative optimized
   for text.
6. Record every transform and parameter in a reproducible processing manifest.

When no single capture contains a satisfactory complete page, process separate
regions from two accepted captures. Record region polygons and source filenames;
do not create an undocumented visual composite.

## Phase 4: Segment layout and run OCR

Segment each page into ordered regions before recognition:

- Running head and printed page number.
- Body text.
- Section and taxon headings.
- Dichotomous keys and other indented lists.
- Figure or photograph.
- Figure or photograph caption.
- Footnote or other marginal text, if present.

Assign stable region identifiers based on printed page and reading order. Run
OCR on text-bearing regions and retain word or line coordinates and confidence.
Figures should become ordered placeholders linked to their source region;
captions remain transcribed text.

Use a botanical lexicon assembled from names occurring in the book and, where
useful, external taxonomic authorities. Use it to flag low-confidence tokens and
inconsistent spellings only. Historical names and apparent printing errors must
remain as printed unless an editorial annotation explicitly records otherwise.

## Phase 5: Create canonical and derived representations

Retain three layers:

1. **Source layer:** original and accepted derived images plus manifests.
2. **Evidence layer:** raw ALTO XML or equivalent OCR with coordinates,
   confidence, region IDs, and source-image references.
3. **Reviewed text layer:** corrected TEI P5 XML in logical reading order.

TEI is recommended for the canonical reviewed text because it can represent:

- Page boundaries with `<pb>` and links to scans.
- Column or region boundaries with `<cb>` or linked divisions where needed.
- Headings, paragraphs, lists, keys, figures, and captions.
- Italics with `<hi rend="italic">`.
- Taxonomic names and author citations without changing their spelling.
- Original line-break hyphenation where it is significant.
- Illegible, supplied, and uncertain text explicitly.
- Printing errors separately from optional editorial corrections.

Generate UTF-8 plain text and Markdown from the reviewed TEI. In those derived
formats:

- Remove running heads and page numbers from the prose stream but retain page
  markers.
- Join words split only by a printed line break.
- Preserve lexical hyphens.
- Keep paragraphs, headings, lists, and key indentation.
- Insert figure placeholders and captions at their printed reading position.
- Never emit an editorial correction as though it were printed text.

## Phase 6: Proofread and validate

Every page requires image-based human review; confidence scores are triage aids,
not acceptance criteria.

Use two passes:

1. A first proofreader corrects OCR while viewing the exact source region.
2. A second proofreader reviews all scientific names, author citations,
   measurements, punctuation, keys, captions, low-confidence OCR, and all
   first-pass changes.

Validation should include automated checks for:

- One reviewed record for every in-scope printed page.
- Monotonic page sequence and explicit documentation of gaps.
- Valid XML and resolvable image and region references.
- Balanced italics and structurally valid headings, lists, and keys.
- Key couplets whose destination numbers exist.
- Suspicious substitutions such as `1`/`l`/`I`, `0`/`O`, `rn`/`m`, dropped
  decimal points, and altered multiplication signs.
- Text continuity at every page boundary.
- Duplicate paragraphs caused by overlapping captures.
- Captions that were omitted or accidentally inserted into body prose.

Target zero known omissions, zero unmarked uncertainties, and 100 percent
agreement for page numbers, taxon headings, scientific names, author citations,
measurements, and key destinations. Report character error rate on a stratified
sample after proofreading; do not claim a numeric accuracy level without that
measurement.

## Suggested project layout

```text
page-scans/                 Original images, unchanged
manifest/
  pages.csv                 Human-readable page and source selection
  pages.json                Machine-readable equivalent
  transforms.json           Reproducible preprocessing provenance
derived-images/
  page/                     Cropped and corrected page images
  regions/                  Optional difficult-region derivatives
ocr/
  raw/                      Engine-native output
  alto/                     Normalized coordinate-bearing OCR
transcription/
  tei/                      Canonical reviewed text
  markdown/                 Generated readable text
  plain/                    Generated processing-oriented text
qa/
  ground-truth/             Pilot and sampled manual transcriptions
  reports/                  OCR scores, completeness, and review reports
scripts/                    Reproducible inventory, processing, and QA tools
```

Generated files should identify the source manifest revision and extraction
tool versions. Large derived artifacts may be reproducibly regenerated rather
than committed, but manifests, canonical transcription, scripts, and QA reports
should be versioned.

## Execution order

1. Inventory all files and create checksums and the page manifest.
2. Resolve missing pages 016 and 017.
3. Complete visual audit and retake all rejected pages.
4. Freeze source selection for the pilot.
5. Build and independently review pilot ground truth.
6. Benchmark OCR and layout pipelines.
7. Freeze preprocessing, segmentation, and OCR versions and parameters.
8. Process the full corpus in page order.
9. Proofread each page and run boundary and structure checks continuously.
10. Perform the second specialist review and final completeness audit.
11. Generate Markdown and plain-text derivatives from reviewed TEI.
12. Publish a QA report containing scope, missing material, marked
    uncertainties, measured sample accuracy, and exact tool versions.

## Completion criteria

The extraction is complete only when:

- Every in-scope printed page has an accepted source or documented composite.
- Missing pages are recovered or explicitly documented as unavailable.
- Every text-bearing region and caption is represented in reading order.
- Every reviewed text segment links back to a source page or region.
- No unresolved reading is hidden; each is encoded and listed in the QA report.
- Keys, headings, captions, page transitions, italics, names, citations, and
  measurements pass manual and automated validation.
- Canonical TEI validates and all generated formats are reproducible from it.
- A final stratified comparison against images reports measured accuracy and
  the remaining limitations.

## Metadata

```text
generator-name: GitHub Copilot
generator-model-id: github-copilot
generation-date: 2026-07-25
generator-responsibility: planning
```

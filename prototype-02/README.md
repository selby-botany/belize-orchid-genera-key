# Prototype 02: capture, preprocessing, and OCR

Replaces the image-handling half of `../prototype-01/`. This prototype exists
to answer one question: **how do we get clean, correctly ordered text out of
*Native orchids of Belize* at a quality the genus key can be built on?**

Prototype 01 answered it partly, by hand — all 388 page assignments in its
corpus were manual, because its OCR stage failed. This prototype works the
problem from the other end: fix the *images*, and the OCR stops being hard.

**Status.** Capture method decided; preprocessing and OCR validated end to end
on a scanner test set. Not yet run over the whole book.

- [Prototype 02: capture, preprocessing, and OCR](#prototype-02-capture-preprocessing-and-ocr)
  - [Conclusion](#conclusion)
  - [Three capture routes, and how they compared](#three-capture-routes-and-how-they-compared)
    - [Route 1 — handheld phone](#route-1--handheld-phone)
    - [Route 2 — phone on a tripod, dark background](#route-2--phone-on-a-tripod-dark-background)
    - [Route 3 — flatbed scanner](#route-3--flatbed-scanner)
  - [The preprocessing recipe](#the-preprocessing-recipe)
  - [OCR results](#ocr-results)
  - [Learnings](#learnings)
    - [About OCR](#about-ocr)
    - [About imaging](#about-imaging)
    - [About method](#about-method)
    - [About the tooling](#about-the-tooling)
  - [Layout](#layout)
  - [Reproducing](#reproducing)
  - [Open items](#open-items)
  - [Source](#source)

## Conclusion

**Use the flatbed scanner.** It is faster to collect, needs no rig, and
produces materially better input than either photographic route: flat, square,
evenly lit, free of perspective and page curl, with no facing page, fingers, or
background in frame. Every problem the photographic routes spent three rounds
fighting simply does not arise.

With scans through the pipeline, Apple Vision OCR returns clean text in correct
reading order — including the two-column body and the three-column index.

## Three capture routes, and how they compared

| | Route 1 handheld | Route 2 tripod | Route 3 scanner |
| --- | --- | --- | --- |
| Images | 388 + 341 | 41 test | 12 test |
| Effective resolution | ~410 ppi | ~310 ppi | 300 dpi |
| Page detectable | no | yes | not by edge |
| Perspective and curl | significant | reduced | none |
| Facing page in frame | usually | no | no |
| Illumination spread | large | ~3% | negligible |
| Effort per page | high | high | low |

### Route 1 — handheld phone

Two shoots: `images/20260725-page-scans/` (388 frames, prototype-01's source)
and `images/20260729-page-scans-original/` (341 frames, cover to cover).

What went wrong, in order of cost:

- **No page detection.** Shot on a white marble counter, so cream paper against
  a white ground gave almost no edge. A brightness-based detector flagged
  roughly 95% of frames — useless. Nothing could be cropped, so every OCR call
  would see a strip of the facing page.
- **Wrong lens.** 338 of 341 frames used the ultra-wide (1.54 mm f/2.4) camera
  — the softest of the three, with no stabilization and significant geometric
  distortion that bends the page outline detection has to fit.
- **Auto white balance and auto exposure**, both drifting. Median
  red-minus-blue cast of 64/255, and the drift was content-driven: a page
  filled with a green photograph white-balanced differently from a page of
  text.
- **Two capture phases**, ten days apart — 30 prototype frames and 358
  systematic ones — with materially different quality.
- **Third-party personal documents** visible in frame in at least two captures.

The 20260725 set has no captures at all for printed pages 016 and 017. Those
are the verso and recto of a single opening — established from page-number
parity (015 is a recto, 018 a verso) and confirmed by the running heads
(`3 Goodyera` on 015, `5 Prescottia` on 018, so genus 4 falls entirely in the
gap). One skipped page turn, not a missing leaf.

### Route 2 — phone on a tripod, dark background

`images/20260730-test-shots/` — 41 frames, 1x lens throughout, ISO locked.

This fixed the important things. Brightness became cleanly bimodal (background
below 85, page above 145, an empty valley between), so **page detection worked
on every frame**, and crop, rotate, and transform were demonstrated end to end.
Illumination was excellent: paper brightness varied only about 3% across a
page. That demonstration is not among the rebuildable QA reports — the
dark-background detector behind it was exploratory and was not kept, the route
having been superseded before it was worth committing.

Two problems remained. The page filled only about half the frame, costing
roughly a quarter of the linear resolution against the earlier shoot (~310 ppi
against ~410). And 14 frames had the page running off the frame edge, with
framing drifting through the session — as pages accumulate under the
photographed leaf, its surface height changes.

### Route 3 — flatbed scanner

`images/20260803-test-scans-01/` — 12 files covering 6 pages (text, figure, and
index), from a Canon SOHO printer/scanner.

Better on every axis that matters, and easier to collect. Two properties need
handling rather than fixing:

- **No dark surround.** Page and scanner bed are both white (border median
  195–233 against a page median of 227–232), so page-edge detection does not
  apply. Cropping to the *printed content* is both more robust and what is
  actually wanted.
- **Half the scans arrive rotated 180 degrees** — natural when turning a bound
  book on the platen.

Scans are 300 dpi (letter, 2548x3300). The page is 6.80 x 9.70 in, so a page at
300 dpi is 2040 x 2910 px; measured crops land within a few percent of that.

## The preprocessing recipe

Two paths, because one recipe cannot serve both.

**Text and line art** — flat-field to a white ground, keep grayscale:

```text
-colorspace Gray
( +clone -blur 0x60 ) -compose Divide_Src -composite
-level 0%,90%
-unsharp 0x1.2+0.8+0.02
```

Dividing the frame by a heavily blurred copy of itself estimates the
illumination and paper tone, removing colour cast, gradient, and vignetting in
one operation. Blur radius 60 was chosen against 20 (tracks the text, leaves
ghosting) and 120 (no gain). The 90% white point clips show-through without
thinning strokes; 74% and 82% visibly lightened the stipple in the botanical
drawings.

**Colour plates, covers, maps** — white balance only:

```text
-channel RGB -contrast-stretch 0.2%x0.05% +channel
```

Flat-fielding a photograph blows out its highlights and destroys tonality. That
was tested, not assumed.

Classification between the two is automatic (`scripts/classify_captures.py`):
saturation after a gray-world white balance, with the threshold taken from the
widest gap in the score distribution rather than hardcoded. On the 341-frame
phone set it selected 48 frames; visual review found two more (a colour
title-page illustration and a muted-tone plate), both now forced by name. That
the plates appear as consecutive pairs — one opening each — gave an independent
structural check that no other plate was missed.

## OCR results

Apple Vision, via `bin/ocr_page.swift`, with language correction **disabled** —
left on, it silently "corrects" Latin binomials into English.

On the processed scan of page 178: 106 lines, both columns in correct reading
order, mean confidence 1.000, zero low-confidence lines. Faithful down to the
multiplication sign in `5.5 x 2.3 mm`, and it preserved the book's own typo
("streched") rather than fixing it.

The pipeline measurably beats raw scans:

| page | raw lines | processed lines |
| --- | --- | --- |
| p276-2 | 51 | 194 |
| m177 | 57, garbage first line | 47, correct |
| p179 | 26, inverted order | 28, correct |
| m176 | 101 | 101 |

The p276-2 result is the striking one — the raw scan lost about 75% of the
index. On an already-clean page the pipeline is exactly neutral, which is what
you want from it.

## Learnings

### About OCR

**Confidence is worthless as a quality gate.** Mean confidence stayed at
0.99–1.00 on upside-down pages emitting pure garbage. Only line counts and
inspection caught those. Never gate acceptance on confidence.

**Column-aware reading order is the dominant failure mode — not character
errors.** The index is set in three columns; a splitter that assumed two
interleaved columns 2 and 3 into alphabetical nonsense. Nothing about the
output *looks* wrong, which makes it far more expensive to catch downstream
than a misread character. Discover the column count from the distribution of
line left-edges; never assume it.

**Disable language correction.** It is built to normalise English prose, and
this book is mostly Latin nomenclature.

### About imaging

- A **white background defeats page detection**; a dark one makes it trivial.
  This single choice decided whether routes 1 and 2 were usable.
- **Flat-field division** fixes colour cast, illumination gradient, and
  vignetting together — and must never touch a photograph.
- **Do not binarize.** Modern OCR binarizes internally and does better from
  grayscale. Thresholding attacks exactly what this book depends on: italic
  scientific names, diacritics, dot leaders, and figure stipple.
- **Do not use Preview's contrast boost.** It reaches a white ground but
  visibly fattens glyphs, which will close counters in the smallest type. The
  automated recipe gets the same background with faithful stroke weight; the
  `scan-contrast` QA report shows the two side by side.
- For photography, **consistency beats correctness**: a uniform wrong colour
  cast is one transform away from gone, drift is not.

### About method

**Sampling bias produced a wrong recommendation.** An early quality assessment
inspected three pages, two of which happened to come from the 30-frame
prototype phase — the worst 8% of the corpus. That produced a confident
"re-shoot the entire book" conclusion. Session provenance from EXIF later
showed only 10 of 249 pages actually lacked a good capture. Stratify samples by
provenance before generalizing from them.

**A plausible heuristic is not a working one.** Detecting 180-degree rotation
was first attempted from ascender-versus-descender mass, which is sound in
principle and wrong on 4 of 6 test pages — the projection threshold clips
ascenders and inverts the signal. What works is structural: the running head
sits alone above the body, separated by a gap much larger than any body line
gap. Confirmed independently by page-number corner position, which also yields
recto or verso and matched page-number parity on all six.

**Do not discard expensive human judgment.** Prototype 01's 388 manual page
assignments are the costliest artifact in the project. They survive its tooling
being superseded.

### About the tooling

- `bin/imagemagick` runs `docker run --interactive`, which **consumes stdin** —
  it silently eats the remaining input of a `while read` loop. Redirect with
  `< /dev/null`.
- `mogrify` does not support `+clone`, so flat-fielding cannot be batched that
  way. Batch instead by passing many parenthesised groups to one `magick`
  invocation.
- When rotation is applied *after* cropping, the crop box must stay in source
  coordinates. Computing it on a flipped mask silently crops the wrong region.

## Layout

```text
bin/        OCR tools (Swift, Apple Vision)
doc/        design documents and reviews, dated and model-attributed
images/     capture sets — large binaries, excluded from version control
manifest/   page and capture manifests
qa/reports/ contact sheets and comparisons — generated, not tracked
scripts/    manifest, classification, geometry, and transform tooling
test/       unit tests for the manifest and audit tooling
```

Image directories, in order of capture:

| directory | contents |
| --- | --- |
| `20260725-page-scans` | 388 handheld frames; prototype-01's source set |
| `20260729-page-scans-original` | 341 handheld frames, cover to cover |
| `20260729-page-scans` | the above, transformed |
| `20260730-test-shots` | 41 tripod frames on a dark background |
| `20260803-test-scans-01` | 12 flatbed scans |
| `20260803-test-scans-01-processed` | the above, cropped and transformed |

## Reproducing

Scanner route, per page:

```bash
# emits crop box, rotation, and recto or verso per scan
bin/python3 prototype-02/scripts/scan_page_geometry.py SCAN...
# then crop, rotate, and apply the monochrome recipe above
swift prototype-02/bin/ocr_page.swift PROCESSED...
```

Phone route, whole set:

```bash
bin/python3 prototype-02/scripts/classify_captures.py \
    --force-colour IMG_8822.jpeg IMG_8848.jpeg
prototype-02/scripts/transform-for-ocr
```

QA artifacts — contact sheets, the crop demonstration, the contrast
comparison, and the audit report — are build output rather than source, so
they are excluded from version control. Rebuild them from the capture sets
with:

```bash
prototype-02/scripts/build-qa-reports            # everything
prototype-02/scripts/build-qa-reports scan-crop  # one report
```

### Dependencies

Docker must be running. Everything else the tooling needs is containerized
and pinned, so there is nothing to install on the host.

- `../bin/imagemagick` — ImageMagick 7.
- `../bin/jq` — jq 1.8.1.
- `../bin/node` — Node.js 22.
- `../bin/python3` — Python 3.13 with numpy, scipy, and Pillow, built from
  `../docker/python-imaging/` on first use. The base image is pinned by
  digest and the packages by exact version, so the interpreter is a property
  of this repository rather than of the host.

**Except OCR.** `bin/ocr_page.swift` and `bin/extract_mcleish_page_text.swift`
use Apple's Vision and AppKit frameworks, which exist only on macOS. Swift
runs on Linux; those frameworks do not, so no container can run them. The
recognition stage of this prototype requires a macOS host with the Xcode
command line tools, and the OCR results below were produced there. See the
requirements section of the [repository README](../README.md).

That second wrapper matters more than it looks. `scan_page_geometry.py` and
`classify_captures.py` need numpy, scipy, and PIL, and the host `python3` may
well not have them — on the machine this was developed on it resolves to a
wrapper deferring to CommandLineTools Python 3.9.6, which has none of the
three. Scripts invoked as `python3 foo.py` therefore succeeded or failed on
PATH order alone.

Run them through the repository interpreter:

```bash
bin/python3 prototype-02/scripts/scan_page_geometry.py SCAN...
bin/python3 --rebuild-image        # after changing the Dockerfile
```

`build-qa-reports` picks it up automatically. Set `QA_PYTHON` to override
with a host interpreter that already carries the stack.

Two caveats inherited from the container pattern: only the working directory
is mounted, so script and data paths must sit beneath it; and standard input
is attached, so a call inside a `while read` loop consumes the loop's input
unless redirected with `< /dev/null`.

## Open items

1. **Colour plates are untested on scanner output.** No plate was in the scan
   test set. Scan one before a production run.
2. **The column-count heuristic over-segments** — it reports 3 columns for a
   two-column page and 5 for the index. Reading order came out correct on all
   six samples anyway, but this needs hardening before a full run.
3. **Small-capital field labels come through inconsistently cased**
   (`DISTRIBUTION IN BELIZe`, `NOTEs`, `Etymology`). A closed set of about
   eight structural markers, so normalisation is safe.
4. **Running heads sort into the body text stream.** They need extracting as
   their own region.
5. **A fixed-size crop box** — 2040 x 2910 at 300 dpi, anchored at the
   page-number corner — would remove the residual width variance between
   scans. Not implemented; does not affect OCR quality.
6. **Try 600 dpi.** Body text is fine at 300; the index and author citations
   are the smallest type in the book and would have more margin.
7. **No page mapping exists** for either the 20260729 captures or the scans.
   Filenames are still capture sequence numbers.
8. `scripts/transform-for-ocr` targets the 20260729 phone set; it needs
   generalising for the scanner route.

## Source

McLeish, I., Pearce, N. R., Adams, B. R., & Briggs, J. S. (1995).
*Native orchids of Belize*. A.A. Balkema. Page trim 6.80 x 9.70 in.

Scans are held for private research use and are not redistributed.

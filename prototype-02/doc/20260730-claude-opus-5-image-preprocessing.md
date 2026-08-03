# Image preprocessing for the OCR stage

How the 2026-07-29 capture set was assessed and transformed, why each
operation was chosen, and what remains unsolved.

- [Image preprocessing for the OCR stage](#image-preprocessing-for-the-ocr-stage)
  - [Result](#result)
  - [What the new capture set looks like](#what-the-new-capture-set-looks-like)
  - [Defects that mattered](#defects-that-mattered)
  - [The transform](#the-transform)
    - [Text and line art](#text-and-line-art)
    - [Colour plates, covers, and the map](#colour-plates-covers-and-the-map)
  - [Choosing between colour and monochrome](#choosing-between-colour-and-monochrome)
  - [What was rejected, and why](#what-was-rejected-and-why)
  - [Verification](#verification)
  - [Known limitations](#known-limitations)
  - [Reproducing](#reproducing)
  - [Metadata](#metadata)

## Result

| Property | Value |
| --- | --- |
| Source | `20260729-page-scans-original/`, 341 JPEG, 2.2 GB |
| Output | `20260729-page-scans/`, 341 JPEG, 586 MB |
| Monochrome (text, line art) | 291 |
| Colour (plates, covers, map) | 50 |
| Resolution | 3024x4032 preserved throughout |
| Filenames | unchanged (`IMG_NNNN.jpeg` to `IMG_NNNN.jpg`) |

Filenames were deliberately **not** renamed to page numbers. No verified
page mapping exists for this capture set yet, and inventing one here would
bury an unreviewed guess inside filenames that everything downstream trusts.

## What the new capture set looks like

The 2026-07-29 shoot is a single session, cover to cover, and is a large
improvement on its predecessor:

- One session, 341 frames, no mixed capture phases.
- Uniform 3024x4032 with EXIF orientation 1 throughout — no rotation to undo.
- One printed page per frame.
- Complete coverage: front cover, front matter, list of maps and photographs,
  the distribution map, the taxonomic text, the colour plate section, the
  index, and the back cover.
- Only two gaps in the `IMG_` sequence (8999 to 9001 and 9159 to 9161),
  consistent with two frames deleted at capture time.

## Defects that mattered

Ranked by how much they cost OCR:

1. **Heavy tungsten colour cast.** The median red-minus-blue difference across
   the set is 64 of 255. Everything is amber.
2. **Illumination gradient and vignetting.** Brightness falls off across each
   frame, so a single global contrast stretch cannot reach white paper without
   crushing the dark corner.
3. **Show-through.** Print from the reverse of each leaf is visible on light
   areas, and any naive contrast boost amplifies it into something OCR may
   read as text.
4. **Facing-page content in frame.** Most frames include a strip of the
   opposite page.
5. **Fingers at the bottom edge**, holding the book open.
6. **Residual page curl** near the gutter, and mild rotation.

Items 1 to 3 are fixed below. Items 4 to 6 are not; see
[Known limitations](#known-limitations).

## The transform

### Text and line art

```text
-auto-orient
-colorspace Gray
( +clone -blur 0x60 ) -compose Divide_Src -composite
-level 0%,90%
-unsharp 0x1.2+0.8+0.02
-quality 95
```

Dividing the frame by a heavily blurred copy of itself is the load-bearing
step. The blurred copy is an estimate of the illumination and paper tone, so
the division removes the colour cast, the gradient, and the vignetting in one
operation, leaving near-white paper and near-black ink across the whole frame.
A blur radius of 60 was chosen against 20 and 120: at 20 the estimate tracks
the text itself and leaves ghosting; 120 works but gains nothing over 60.

`-level 0%,90%` sets the white point below paper white, which clips residual
show-through to pure white. This was compared against 74%, 82%, and no level
adjustment at all. Without it, show-through survives and is clearly visible.
At 74% and 82% the fine stipple in the botanical line drawings visibly
lightens. 90% removes the show-through with no measurable loss of line weight.

The unsharp mask is mild and recovers definition in the smallest type — the
author citations and key dot leaders.

### Colour plates, covers, and the map

```text
-auto-orient
-channel RGB -contrast-stretch 0.2%x0.05% +channel
-quality 95
```

A per-channel contrast stretch removes the cast by stretching red, green, and
blue independently, which is enough to neutralize the tungsten light while
leaving photographic tonality intact. Plate captions remain legible for OCR.

## Choosing between colour and monochrome

Saturation alone does not separate the two populations, because the colour
cast saturates every frame equally. Applying a gray-world white balance first
makes the separation clean: the score is the fraction of pixels whose
saturation exceeds 0.22 after balancing.

The threshold is not hardcoded. `scripts/classify_captures.py` picks the
midpoint of the widest gap in the score distribution, which for this set falls
at 0.1772 — between a text population topping out near 0.15 and a plate
population starting near 0.20.

The result was checked visually rather than trusted. Two frames scored below
the threshold but are genuinely colour, and are forced by name:

- `IMG_8822`, the title-page colour illustration — a single small colour
  region on an otherwise white page.
- `IMG_8848`, a plate of muted forest habitat photographs.

`IMG_8848` was caught by a structural check: plate pages appear as
consecutive pairs, one opening per pair, and `IMG_8847` was classified colour
while its partner was not. Every other pair in the set is intact, which is
good evidence that no further plate was missed.

## What was rejected, and why

- **Flat-fielding the colour plates.** Tested and clearly wrong — it blows out
  photographic highlights and wrecks tonality. Plates get white balance only.
- **Bilevel binarization.** The user's request named "monochrome," but hard
  binarization was not used. Modern OCR engines binarize internally and do
  better from grayscale, and thresholding attacks exactly the features this
  book depends on: italic scientific names, diacritics, dot leaders, and the
  stipple shading in the figures. Grayscale keeps the antialiasing.
- **Automatic cropping to the page block.** See below.
- **Deskew.** `-deskew` operates on the whole frame, which here includes a
  facing page and fingers, so its skew estimate is not trustworthy. Rotation
  in this set is mild and OCR engines tolerate it.

## Verification

- 341 inputs produced 341 outputs with no missing files.
- Colourspace tally matches the classification exactly: 291 `Gray`, 50 `sRGB`.
- All outputs retain 3024x4032.
- Background brightness across the monochrome set is tight — 5th percentile
  242, median 246, 95th percentile 250 of 255 — confirming the flat-field
  worked uniformly rather than only on the sampled pages.
- The ten darkest frames were inspected individually; all are clean. Their
  slightly lower means come from carrying more of the adjacent page block or
  fore-edge, not from a failed transform.
- Contact sheets of input and output were compared across the whole set.
- `scripts/transform-for-ocr` was re-run from scratch on a sample and produces
  byte-identical output to what was delivered.

## Known limitations

These are real and unresolved. None of them is safe to fix blindly.

- **Facing-page content is still in frame.** Cropping to the target page is
  the obvious next step and was deliberately not automated. The book was shot
  on a white marble countertop, so the page and the background have almost no
  contrast, and page-boundary detection by brightness does not work — an
  earlier attempt on the previous capture set flagged roughly 95 percent of
  frames. A silent over-crop that removes a line of text is worse than the
  facing-page strip it would fix. The originals are retained, so this can be
  added later as a reviewed step.
- **Fingers remain at the bottom edge** of most frames, for the same reason.
- **Page curl near the gutter is uncorrected.** Dewarping needs a reliable
  page boundary, so it is blocked behind the same problem.
- **No page mapping exists.** Filenames are still capture sequence numbers.
- **The transform is tuned on this session's lighting.** Re-running it on a
  differently lit set without re-checking the blur radius and white point
  would be unwise.

If the book is re-shot again, a matte black background would make page
detection tractable and unblock cropping, dewarping, and the finger problem
together.

## Reproducing

```bash
cd mcleish--orchids-of-belize
python3 scripts/classify_captures.py --force-colour IMG_8822.jpeg IMG_8848.jpeg
scripts/transform-for-ocr
```

`scripts/transform-for-ocr` reads
`manifest/capture-classification.json`, batches ten images per ImageMagick
invocation to amortize container startup, and runs six invocations in
parallel. Override with `TRANSFORM_JOBS` and `TRANSFORM_CHUNK`. The full set
takes roughly fifteen minutes.

All image work goes through `bin/imagemagick`, the project's Docker-backed
ImageMagick 7 wrapper.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Opus 5
generator-model-token: claude-opus-5
generator-provider: Anthropic
generation-date: 2026-07-30
generator-responsibility: implementation
```

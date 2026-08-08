# Prototype 03, Phase 1: problem overview and motivation

This is the entry point for the document set. It assumes no botanical
training and no software background — everything specific to either is
introduced when it's first needed. Later documents in the set get
progressively more technical; this one does not.

- [Prototype 03, Phase 1: problem overview and motivation](#prototype-03-phase-1-problem-overview-and-motivation)
  - [Purpose of this document](#purpose-of-this-document)
  - [1. What the project is building](#1-what-the-project-is-building)
  - [2. Why McLeish, why now](#2-why-mcleish-why-now)
  - [3. What the two prior prototypes established](#3-what-the-two-prior-prototypes-established)
    - [3.1 Prototype 01: a hand-built corpus for eight genera](#3-1-prototype-01-a-hand-built-corpus-for-eight-genera)
    - [3.2 Prototype 02: a proven but unscaled capture-and-OCR method](#3-2-prototype-02-a-proven-but-unscaled-capture-and-ocr-method)
  - [4. What's different about prototype 03's data](#4-whats-different-about-prototype-03s-data)
  - [5. What Phase 1 delivers, and what it doesn't](#5-what-phase-1-delivers-and-what-it-doesnt)
  - [6. Relationship to the characteristic-of-taxa document](#6-relationship-to-the-characteristic-of-taxa-document)
  - [7. How to read this document set](#7-how-to-read-this-document-set)
  - [Metadata](#metadata)

## Purpose of this document

To explain, to a botanist who has never looked at this repository's code,
what problem prototype 03 solves, why it exists on top of two earlier
attempts, what its new raw data actually looks like, and what "done" means
for this first phase of the work. A reader who stops after this document
should be able to judge whether the plan is sound and whether the eventual
output is worth reviewing — without needing to read anything else.

## 1. What the project is building

The long-term goal of this repository is a **genus key**: a tool that lets
someone holding an unfamiliar orchid plant — often without a flower, since
most orchids are sterile most of the time — work out which of the genera
found in Belize it belongs to, by answering a short sequence of questions
about what they can see. `doc/20260707-botanical-keys-overview.md` at the
repository root explains what a botanical key is and how one is built in
more depth; the short version is that a key is only as good as the
underlying description of each genus it separates.

That description has to come from somewhere. This repository's source is a
single physical book: *Native Orchids of Belize* (McLeish et al. 1995), a
systematic treatment that describes each genus known from the country in
turn — growth habit, stems, leaves, roots, flowers, distribution, habitat,
flowering season — genus by genus, page by page. Building the key means
first turning photographs of those pages into text a computer (and a human
reviewer) can work with, and then turning that text into structured,
comparable facts about each genus. **Phase 1 is the first half of that: get
faithful, structured genus descriptions out of the scanned pages.** Phase 2,
planned separately once Phase 1's real output exists, is building the key
itself and testing how well it works.

## 2. Why McLeish, why now

McLeish is the only source this phase of the project uses, and that is a
deliberate, explicit boundary, not an oversight — see §6. It's a good
starting source for a Belize-specific key: it's Belize-specific by design,
it treats every genus the same way with the same fields, and — critically
for this phase — a substantial, well-photographed capture of it now exists.
Two earlier attempts at working with this book are the direct reason the
project is at prototype 03; understanding what they found is the fastest way
to understand what's different now.

## 3. What the two prior prototypes established

### 3.1 Prototype 01: a hand-built corpus for eight genera

Prototype 01 started from an earlier, rougher set of page photographs and
tried to have software work out which photograph corresponded to which
printed page number, by reading the page number printed on each page. That
OCR step failed on the large majority of captures, so every one of the 388
photographs in that set had its page number assigned by a person, by
looking at it. That is legitimate, careful work — and expensive work, which
is why it covers only eight genera (Corymborkis, Erythrodes, Goodyera,
Habenaria, Hetaeria, Liparis, Malaxis, Spiranthes, from pages 13, 15, and
41–48) rather than the whole book. The resulting characteristic corpus
(`prototype-01/doc/mcleish.genera.md`) is still the best real-world example
of what a "genus feature description" for this project should look like:
short, categorized bullet points — growth habit, rhizome, roots, stem,
leaf arrangement/attachment/texture/shape, overall size, and so on — under
each genus's heading.

### 3.2 Prototype 02: a proven but unscaled capture-and-OCR method

Prototype 02 set the page-mapping problem aside and asked a narrower
question: given a clean photograph of a page, can software reliably read
its text? It found that a flatbed scanner beats a handheld or tripod-mounted
phone camera on every measured axis — sharper, flatter, more evenly lit, no
facing-page bleed — and built a working pipeline: a documented ImageMagick
recipe that removes colour cast and illumination gradient without touching
text sharpness, a rule that tells colour plates from text pages so each gets
the right treatment, and an Apple Vision OCR tool that works out the number
of text columns on a page from the actual layout rather than assuming two
(the index is set in three), which matters because misreading column order
produces text that reads fine at a glance and is completely wrong — a much
more dangerous failure than a misspelled word.

That pipeline was validated on 6 pages. It was never run over the book. A
subsequent review of the plan (986 lines,
`prototype-02/doc/20260727-claude-opus-5-text-extraction-plan.md`) found
real gaps before it should be: the column-handling above was missing from
the *original* plan and had to be added; running heads (the small genus
number and name printed at the top of each page) were identified as a free,
independent way to check page order and catch errors a page-number check
alone would miss; and a list of concrete tooling defects was catalogued —
among them, a script that aborts entirely if it meets one unexpectedly-named
file, and a review spreadsheet whose edits get silently overwritten the next
time the tool runs. Phase 1 exists in part to not repeat those.

## 4. What's different about prototype 03's data

`prototype-03/images/20260804-page-scans/` is a new capture: 243 files.
Unlike either earlier set, most of it already carries a real identity in its
filename rather than a bare capture-sequence number — `page-013.jpeg`
rather than `013.jpg` with no known page number yet. Checked directly:

| Fact | Value |
| --- | --- |
| Body-text pages, contiguous | 1 through 190, no gaps |
| Named front matter | title page, copyright page, dedication, acknowledgments, foreword, preface (2 pp.), frontispiece, table of contents (5 pp.) |
| Colour-plate pairs | `page-NNNp1.jpeg` / `p2.jpeg`, alongside several main-sequence pages |
| Typical page image | ~4350×6450 px, already grayscale, ~640 dpi at the book's trim size |
| Typical plate image | ~5096×6600 px, colour |

This is a real structural advantage: the hardest problem prototype-01
fought — recovering page identity — looks largely pre-solved by how these
were captured and named. It is not, however, clean data, and treating the
filenames as ground truth without checking would repeat exactly the mistake
prototype-02's review had to correct elsewhere. Two problems were found by
direct inspection, not assumption:

- `page-065 1.jpeg` is 192×152 pixels, 14 KB — not a duplicate of the real
  `page-065.jpeg`, but a corrupt or thumbnail-sized stub with a page's name.
- `m276.jpeg` is a genuine outlier: 8812×12944 pixels, far larger than every
  other capture, with a filename that doesn't fit the `page-NNN` pattern and
  no confirmed identity yet.

Phase 1's pipeline is built to find problems like these automatically and
flag them for a person to look at, rather than either trusting every
filename or refusing to run until every file is perfect (see the
requirements document, §Governance inputs, for what specifically gets
flagged to the botanist rather than decided in code).

## 5. What Phase 1 delivers, and what it doesn't

**Delivers:** for however much of the captured 1–190 page range OCRs and
parses cleanly, a genus-by-genus (and, where the book gives it, species-by-
species) structured record of what McLeish says — growth habit, stem,
leaves, roots, distribution, habitat, and the other fields the book itself
uses — each fact traceable back to the specific source image and OCR
confidence it came from. That record is delivered two ways: a
machine-readable form for later processing, and a human-readable Markdown
corpus in the style of `prototype-01/doc/mcleish.genera.md`, so a botanist
can review it directly without needing to read JSON.

**Does not deliver, by design:**

- **A key.** Turning these descriptions into a working identification tool,
  and testing how well it performs, is Phase 2 — planned once Phase 1's
  real output exists to design against.
- **Species-level completeness.** The book gives species-level detail in
  places; Phase 1 keeps it as separate, subordinate records rather than
  merging it into genus-level facts, but does not attempt to make it
  exhaustive.
- **Guaranteed full-book coverage.** The capture itself is explicitly
  incomplete — it covers roughly the first two-thirds of the book by page
  count, and `m276.jpeg` hints at more beyond that not yet captured. Phase 1
  processes what exists and reports honestly on what it could and couldn't
  extract; it does not wait for a complete scan to start being useful.
- **Corrected nomenclature.** Where the book's 1995 names differ from
  current usage, Phase 1 preserves the book's own wording rather than
  silently updating it — see the requirements document.

## 6. Relationship to the characteristic-of-taxa document

`doc/20260808-belize-orchid-characteristic-of-taxa.md`, at the repository
root, is a large (3,594-line), explicitly non-normative exploratory
document — it says so of itself — synthesizing what several AI models
produced when asked to sketch a much bigger, literature-sourced key covering
104 genera across Belize and the surrounding region, using sources like the
Biodiversity Heritage Library and Flora Mesoamericana. It even reserves a
`prototype-03/data/` file layout for that larger effort, with McLeish
treated there as only a secondary, confirmatory check against those other
sources.

**This project's Phase 1 and Phase 2 do not use that document's data.**
Every fact this pipeline produces comes from OCR of the McLeish scans in
`images/20260804-page-scans/` and nothing else. This is a firm, explicit
scope boundary, not an oversight: mixing in facts sourced from outside
McLeish would defeat the point of keeping this project's key traceable to a
single, physically verifiable source. To avoid even the appearance of using
that document's file contract, this prototype's output deliberately lives
under `analysis/` and `manifest/` rather than `prototype-03/data/`.

What *is* reused from that document, because it's a matter of engineering
method rather than fact, are ideas like recording where every assertion came
from, and keeping a controlled vocabulary of descriptive terms rather than
matching free text. Reusing a well-thought-out record shape is not the same
as reusing the facts recorded in it, and none of the latter appear anywhere
in this project's output.

## 7. How to read this document set

| # | Document | Audience |
| --- | --- | --- |
| 1 | Problem overview and motivation (this document) | Everyone |
| 2 | Requirements | Everyone — read fully if you are the botanist |
| 3 | Architecture and design | Everyone |
| 4 | Data formats and relationships | Everyone, mostly engineer |
| 5 | Detailed module design | Engineer |
| 6 | Implementation and test plan | Engineer |

A botanist reviewing this work should read documents 1 through 3 in full,
skim 4, and treat 5 and 6 as available for reference rather than required
reading.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: research
```

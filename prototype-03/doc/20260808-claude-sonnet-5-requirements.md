# Prototype 03, Phase 1: requirements

Read this document in full if you are the botanist reviewing this project.
It states plainly what the pipeline must do, how good its output has to be
before it's trusted, and — separately — which decisions it deliberately does
not make on its own, because they're judgment calls that belong to a
botanist rather than to code.

- [Prototype 03, Phase 1: requirements](#prototype-03-phase-1-requirements)
  - [Purpose](#purpose)
  - [1. Functional requirements](#1-functional-requirements)
    - [1.1 Coverage](#1-1-coverage)
    - [1.2 Faithful transcription](#1-2-faithful-transcription)
    - [1.3 Provenance on every fact](#1-3-provenance-on-every-fact)
    - [1.4 Use the book's own field vocabulary](#1-4-use-the-books-own-field-vocabulary)
    - [1.5 Human review, scoped to what needs it](#1-5-human-review-scoped-to-what-needs-it)
  - [2. Quality and acceptance thresholds](#2-quality-and-acceptance-thresholds)
  - [3. Non-functional requirements](#3-non-functional-requirements)
  - [4. Governance inputs: decisions reserved for the botanist](#4-governance-inputs-decisions-reserved-for-the-botanist)
  - [5. Out of scope for Phase 1](#5-out-of-scope-for-phase-1)
  - [Metadata](#metadata)

## Purpose

Requirements, not design: this document says what the pipeline must
accomplish and what it must never do, not how it's built. See the
architecture document for how.

## 1. Functional requirements

### 1.1 Coverage

The pipeline must attempt every genus-treatment page captured in
`images/20260804-page-scans/` — the pages numbered 1 through 190, which is
the full extent of the current capture (see the problem overview, §4). It
must not silently skip a page because it's hard; a page it can't extract
cleanly must appear in the review queue (§1.5), not disappear.

It is explicitly **not** required to cover the whole book. The capture
itself stops well short of that (`m276.jpeg` is evidence more of the book
exists uncaptured). Coverage is bounded by what has been scanned, and Phase
1 reports that boundary honestly rather than implying completeness it
doesn't have.

### 1.2 Faithful transcription

Every piece of extracted text must represent what is actually printed on
the page, not a corrected or modernized version of it. Concretely:

- OCR language correction must stay disabled, as prototype-02 established —
  autocorrect silently turns Latin binomials into English words.
- A genus or species name is recorded exactly as McLeish printed it. Where
  that name is now outdated, that is recorded as a fact about the source
  (§4 covers whether and how to also record a modern equivalent) — it is
  never quietly replaced.
- A typo in the source stays a typo in the transcription. Prototype-02
  demonstrated this is achievable (its OCR preserved the book's own
  "streched" rather than correcting it) and Phase 1 must not regress on it.
- Where OCR is uncertain about a specific word or character, that
  uncertainty is recorded, not silently resolved by picking the more
  plausible reading.

### 1.3 Provenance on every fact

Every extracted field — a genus's leaf description, a distribution
statement, anything — must be traceable back to the specific source image
it came from and the OCR confidence of the text it was read from. A fact
with no source is not usable output; it belongs in the review queue instead,
not in the corpus. This is what makes the corpus something a botanist can
audit rather than something they have to take on faith.

### 1.4 Use the book's own field vocabulary

McLeish structures every genus treatment the same way: a small, closed set
of field labels (`ETYMOLOGY`, `GENERAL DISTRIBUTION`, `DISTRIBUTION IN
BELIZE`, `HABITAT`, `FLOWERING SEASON`, `NOTE`, and others), plus a
consistent set of italic organ leads in the descriptive paragraph (*Roots*,
*Stems*, *Leaves*, *Inflorescences*, *Flowers*, *Sepals*, *Petals*, *Lip*,
*Column*, and others). The pipeline must recognize this vocabulary
structurally, not invent its own categories — it is the book's structure,
already used successfully in `prototype-01/doc/mcleish.genera.md`, and
reusing it keeps the extracted corpus recognizable to anyone who has read
the source.

### 1.5 Human review, scoped to what needs it

The pipeline must produce a review queue of exactly what it could not
resolve on its own — a low-confidence OCR span, an ambiguous genus
boundary, a file that doesn't fit any expected pattern — and nothing else.
It must not require a person to look at all 190+ pages to get usable output
(that would just be prototype-01 again, at greater cost), and it must not
guess silently on something it isn't confident about rather than flagging
it.

## 2. Quality and acceptance thresholds

Prototype-02's own finding was that OCR confidence alone is not a safe
signal — a page turned upside down by mistake can still average a
confidence near 1.0 while producing pure garbage. Consequently, acceptance
is never gated on confidence alone. A page's OCR output is accepted only
when **both**:

- its mean line confidence and low-confidence line count fall inside
  thresholds fixed in advance (not tuned after seeing results), and
- a structural sanity check passes: a plausible line count for a body page,
  and (where the page carries one) a running-head page number and genus
  number consistent with its neighbors.

A page failing either check goes to the review queue, tagged with which
check failed. The exact numeric thresholds are set in the detailed design
document and are revisited, with reasons recorded, only after the pilot run
(§Pilot gate, implementation plan document) — never adjusted quietly to make
a bad run look acceptable.

The structural parser (genus/field extraction, §Data document) is held to
the same discipline: a genus record with a field it can't confidently
segment gets that field flagged for review rather than a best guess.

## 3. Non-functional requirements

- **macOS with Xcode command line tools** is required for the OCR stage —
  inherited from the whole repository, see its root README. This cannot be
  containerized; Apple's Vision framework does not exist outside macOS.
- **Docker**, via this repository's `bin/` wrappers, is required for every
  other tool that needs one (ImageMagick, Python, jq, Node). No tool is
  installed directly on the host; see `bin/README.md` at the repository
  root for what's already wrapped.
- **No network dependency.** Everything Phase 1 needs — the scans, the
  tooling — is local. This is a direct consequence of §1.2 and §Relationship
  to the characteristic-of-taxa document (problem overview, §6): nothing
  is fetched from an external source and folded into the corpus.
- **Reproducibility.** Given the same input images and the same pipeline
  version, re-running it produces the same output. Generated artifacts
  (`manifest/`, `analysis/`) are always rebuildable from source images plus
  the pipeline's own code and any recorded manual review decisions — never
  hand-edited directly, matching this repository's established convention
  in `prototype-01/analysis/README.md` and `prototype-02/README.md`.
- **No destructive operations on source images.** `images/` is read-only to
  every pipeline stage. Anything preprocessing produces is a derived copy.

## 4. Governance inputs: decisions reserved for the botanist

These are not implementation details and this project does not decide them
by default. Each is recorded, with the default this plan uses until told
otherwise, so the choice is visible rather than buried in code:

| # | Question | Default used until confirmed otherwise |
| --- | --- | --- |
| 1 | Record McLeish's own (possibly outdated) genus and species names verbatim, or normalize to current usage? | Verbatim, per §1.2 — a normalization pass is a distinct, later step if wanted, never silent |
| 2 | What is `m276.jpeg`? | Flagged for identification, not guessed at |
| 3 | What should happen to `page-065 1.jpeg` (and any similar corrupt/stub file the audit finds)? | Flagged as unusable and excluded from extraction; not silently dropped from the inventory, and not silently treated as a duplicate of the real page |
| 4 | Should front matter and colour plates be transcribed at all, beyond being inventoried? | No — they cannot carry genus characteristic text (problem overview, §5); a plate's link to its facing text page is recorded for possible future use |
| 5 | Who has authority to resolve a review-queue item once the pipeline flags it? | Not decided by this document — whoever is doing the botanical review in practice |
| 6 | Should extracted species-level detail be kept at all, or discarded as out of scope? | Kept, as subordinate records separate from genus-level facts (problem overview, §5) — not merged, not discarded |

## 5. Out of scope for Phase 1

- Building the key itself, or any distance/clustering/statistical analysis
  over the extracted corpus — Phase 2.
- Any data source other than the McLeish scans in `images/` — see problem
  overview, §6.
- A complete-book guarantee — bounded by what's captured, per §1.1.
- Modernizing nomenclature — governance input #1 above.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: other
```

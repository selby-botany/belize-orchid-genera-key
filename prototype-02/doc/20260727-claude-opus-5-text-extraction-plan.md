# Text extraction plan review

Review of [20260725-github-copilot-text-extraction-plan.md](20260725-github-copilot-text-extraction-plan.md)
and of the tooling committed alongside it.

Revised after the project owner answered the open questions. The answers are
recorded in [Project context](#project-context) and materially change the
recommended strategy.

- [Text extraction plan review](#text-extraction-plan-review)
  - [Verdict](#verdict)
  - [Project context](#project-context)
  - [Prior art in the Selby repository](#prior-art-in-the-selby-repository)
    - [P1. The page mapping is hand-adjudicated and trustworthy](#p1-the-page-mapping-is-hand-adjudicated-and-trustworthy)
    - [P2. Header OCR failed on 83 percent of captures](#p2-header-ocr-failed-on-83-percent-of-captures)
    - [P3. The genus corpus is about 11 percent complete](#p3-the-genus-corpus-is-about-11-percent-complete)
    - [P4. The scans are already excluded from version control](#p4-the-scans-are-already-excluded-from-version-control)
  - [Two tracks: prove the approach, then produce the corpus](#two-tracks-prove-the-approach-then-produce-the-corpus)
  - [Headline recommendation: re-shoot cover to cover](#headline-recommendation-re-shoot-cover-to-cover)
    - [What a controlled corpus buys](#what-a-controlled-corpus-buys)
    - [Shooting order](#shooting-order)
    - [Correcting the quality claim behind the original recommendation](#correcting-the-quality-claim-behind-the-original-recommendation)
    - [A capture setup a volunteer can actually achieve](#a-capture-setup-a-volunteer-can-actually-achieve)
    - [What happens to the existing 388 captures](#what-happens-to-the-existing-388-captures)
  - [What the plan gets right](#what-the-plan-gets-right)
  - [Corpus facts verified](#corpus-facts-verified)
  - [Resolved by the owner's answers](#resolved-by-the-owners-answers)
    - [R1. Scope is now cover to cover](#r1-scope-is-now-cover-to-cover)
    - [R2. Rights position is private research use](#r2-rights-position-is-private-research-use)
    - [R3. Personal information becomes a disposal task](#r3-personal-information-becomes-a-disposal-task)
    - [R4. Version control has a defined destination](#r4-version-control-has-a-defined-destination)
    - [R5. The retake gate is no longer a risk](#r5-the-retake-gate-is-no-longer-a-risk)
  - [Gaps the answers made larger](#gaps-the-answers-made-larger)
    - [L1. One non-botanist cannot proofread nomenclature](#l1-one-non-botanist-cannot-proofread-nomenclature)
    - [L2. The botanist's time is the scarcest resource and is unbudgeted](#l2-the-botanists-time-is-the-scarcest-resource-and-is-unbudgeted)
    - [L3. The deliverable is not TEI, and is possibly not the whole book](#l3-the-deliverable-is-not-tei-and-is-possibly-not-the-whole-book)
    - [L4. Cover-to-cover scope breaks the page identifier scheme](#l4-cover-to-cover-scope-breaks-the-page-identifier-scheme)
  - [Method gaps that still stand](#method-gaps-that-still-stand)
    - [M1. Two-column layout is the dominant case and is unaddressed](#m1-two-column-layout-is-the-dominant-case-and-is-unaddressed)
    - [M2. Filename-to-printed-page verification was already done by hand](#m2-filename-to-printed-page-verification-was-already-done-by-hand)
    - [M3. Running heads are an unused ordering signal](#m3-running-heads-are-an-unused-ordering-signal)
    - [M4. No vision-language model is benchmarked](#m4-no-vision-language-model-is-benchmarked)
    - [M5. Ground truth is single-keyed](#m5-ground-truth-is-single-keyed)
    - [M6. No accept or reject thresholds anywhere](#m6-no-accept-or-reject-thresholds-anywhere)
    - [M7. The hyphenation rule is unsafe for botanical prose](#m7-the-hyphenation-rule-is-unsafe-for-botanical-prose)
    - [M8. Italic detection has no strategy, only a metric](#m8-italic-detection-has-no-strategy-only-a-metric)
    - [M9. Region taxonomy omits real features of this book](#m9-region-taxonomy-omits-real-features-of-this-book)
    - [M10. Cross-reference integrity is only half checked](#m10-cross-reference-integrity-is-only-half-checked)
    - [M11. Show-through is not mentioned](#m11-show-through-is-not-mentioned)
  - [Defects in the current tooling](#defects-in-the-current-tooling)
  - [Quick win: pages 016 and 017 are one missed page turn](#quick-win-pages-016-and-017-are-one-missed-page-turn)
  - [Revised execution order](#revised-execution-order)
  - [Residual questions](#residual-questions)
  - [Metadata](#metadata)

## Verdict

The plan is sound in method and unusually disciplined about provenance,
uncertainty, and the separation of recognition from correction. Those parts
should be kept as written.

The largest change is one of scale rather than method. The plan is built around
a heavyweight audit of an uncontrolled corpus, and the corpus turns out not to
need it: 239 of 249 pages come from a single systematic run whose sampled
output is good, ten pages need re-shooting, and the material outside the
taxonomic text has simply never been shot. What the plan treats as a phase is
an afternoon.

Two further discoveries reshape the work more than any finding about OCR
method. The page mapping for all 388 images is already hand-adjudicated and
should be carried forward rather than redone. And the genus corpus that feeds
the existing analysis pipeline covers 8 of more than 72 genera, which is the
real bottleneck and the thing a rough cut has to move.

Three findings survive unchanged and remain the substantive risks:

- The body text is two-column, and the segmentation design has no column
  model. Reading order for the actual mixed layout is undefined.
- The one available proofreader is a non-botanist, and the plan's quality bar
  assumes specialist review of every page.
- The committed manifest tooling has two defects that silently discard review
  work.

## Project context

Supplied by the project owner on 2026-07-27.

| Question | Answer |
| --- | --- |
| Physical book accessible? | Yes; opens flat; unlimited retakes cover to cover |
| Rights position | Private project for a professional colleague; scans not public |
| Plate and photograph section in scope? | Yes |
| Front and back matter in scope? | Yes, including the index |
| Proofreading capacity | Primarily the owner, a non-botanist volunteer |
| Specialist review | A botanist reviews milestone results |
| Ultimate customer | The botanist |
| Repository | Temporary location; real home is `~/Programming/selby/belize-orchid-genera-key`, to become a branch if the approach pans out |

## Prior art in the Selby repository

Investigating the branch question surfaced completed work on this exact corpus
that changes several findings below. The prior runbook is
`doc/20260724-gpt-5.3-codex-page-images-to-genera-analysis-process.md` in the
Selby repository, and its artifacts are on the local `dev` branch.

### P1. The page mapping is hand-adjudicated and trustworthy

`analysis/mcleish_manual_overrides.json` assigns a printed page to all 388
images, and the postprocessed manifest summary reports:

```text
manual_override_entries: 388
ocr_anchor_entries: 0
strict_interpolation_entries: 0
set_aside_retake_entries: 0
unresolved_entries: 0
```

Every filename in `page-scans/` therefore encodes a human judgment about which
printed page the image shows. That is a stronger guarantee than the
verification pass this review originally recommended, and it is the most
expensive human artifact in the project. It must not be discarded — see
[R4](#r4-version-control-has-a-defined-destination) on the branch point.

It also explains the `-scanN` convention. Those suffixes were not assigned by
the photographer: `bin/generate_mcleish_rename_plan.py` ranks the captures for
a page, renames the best to `NNN.jpg`, and renames the remainder to
`NNN-scan2.jpg` onward, best to worst. The original plan's observation that
later suffixes are "not consistently better than earlier captures" is therefore
expected rather than surprising — the base file is the tool's pick and the
ranking descends by construction.

### P2. Header OCR failed on 83 percent of captures

The same pipeline ran an OCR pass over the running-head band, via
`bin/extract_mcleish_header_candidates.swift`, and it produced nothing usable.
322 of 388 entries are flagged `needs_review`, and zero entries resolved from an
OCR anchor. The mapping is entirely manual because the machine proposal stage
did not work.

This is the most useful empirical datum in the repository, and it cuts two
ways:

- Reading a page number from a running head is close to the easiest OCR task
  this corpus offers — large type, high contrast, isolated from body text, and
  a tiny space of plausible values. An 83 percent review rate on that task is
  strong evidence that classical OCR of full pages from these captures will not
  succeed. It supports both the re-shoot recommendation and the
  vision-language model benchmark in
  [M4](#m4-no-vision-language-model-is-benchmarked).
- The failure could equally lie in the extractor rather than the images — crop
  region, orientation handling, or an over-conservative confidence gate. Before
  concluding anything about the corpus, re-run header extraction on a handful
  of known-good captures such as `200.jpg` with a different engine. That is an
  hour of work, and the answer determines whether the re-shoot is urgent or
  merely worthwhile.

### P3. The genus corpus is about 11 percent complete

`doc/mcleish.genera.md` is the input to the downstream clustering and
morphological analyses, and its own subtitle records its scope: "Source:
McLeish Pages 13, 15, 41-48". It holds 8 genus entries. The running head on
page 200 reads `72 Jacquiniella`, so the book treats at least 72 genera.

This is the actual bottleneck. The analysis pipeline is already built and
running — on an eighth of the data. Getting from 8 genera to more than 72 is
what demonstrating promise requires, and it is a text-extraction problem, which
is precisely the concern this branch is meant to isolate.

### P4. The scans are already excluded from version control

`mcleish` is listed in the Selby `.gitignore`, and `page-scans/` here is a copy
of `~/Programming/selby/belize-orchid-genera-key/mcleish/` — identical filename
sets, and identical checksums on sampled files. The storage question raised in
[R4](#r4-version-control-has-a-defined-destination) is therefore already
answered by existing practice: images stay out of git. Keep that decision, make
it explicit rather than incidental, and rely on the tracked manifest's SHA-256
records so the untracked image set stays verifiable.

## Two tracks: prove the approach, then produce the corpus

The owner's immediate goal is a rough cut demonstrating that the approach has
promise. The plan under review — and most of this document — describes a
production run. These are different projects, and collapsing them into one
sequence is what makes the work feel heavy.

**Track A, prove the approach.** Days rather than weeks. It needs no re-shoot,
no TEI, no two-pass proofreading, and no double-keyed ground truth.

1. Use the existing captures unchanged. Page mapping is already done per
   [P1](#p1-the-page-mapping-is-hand-adjudicated-and-trustworthy), so the
   corpus is usable as it stands.
2. Select genera whose pages are known-good captures — page 200 is
   representative of the quality a tripod shoot would produce anyway.
3. Run a vision-language model over those pages to produce genus text in the
   structure `doc/mcleish.genera.md` already uses.
4. Feed the result to the existing characteristic and morphological analyses.
5. Show the botanist clustering output over 30 or 40 genera instead of 8.

The question Track A answers is whether the extracted text is good enough to
support the analysis — not whether it is archivally faithful. Those bars are
far apart, and the analysis bar is much lower: morphological feature extraction
tolerates character-level errors that a transcription never would. Do not let
the fidelity requirements in this document gate the spike.

**Track B, produce the corpus.** Everything else here. Start it once Track A
shows promise, and let Track A's failures determine which parts of Track B
actually matter. If the model handles two-column reading order cleanly,
[M1](#m1-two-column-layout-is-the-dominant-case-and-is-unaddressed) shrinks. If
nomenclature comes through clean against a taxonomic backbone,
[L1](#l1-one-non-botanist-cannot-proofread-nomenclature) shrinks.

The one Track B item worth starting early regardless is the re-shoot: the book
is available, the setup is cheap, and every later decision is better informed
with a clean corpus. It is not on Track A's critical path.

## Headline recommendation: re-shoot cover to cover

Photograph the whole book under controlled conditions, and demote the existing
388 captures to a fallback and cross-check rather than the source of record.

With operator time not a constraint, the question is not what the smallest
sufficient re-shoot would be. It is what a clean corpus is worth — and capture
quality propagates into every later decision, so the answer is larger than it
looks.

### What a controlled corpus buys

- **One parameter set for the whole book.** Uniform illumination, perspective,
  and scale make a single preprocessing configuration valid everywhere, instead
  of per-page tuning or per-session branches.
- **Benchmarks that measure the engine.** With capture variance removed, the
  Phase 2 comparison measures the pipeline rather than the photography.
  Otherwise a weak engine on good pages and a strong engine on poor pages are
  hard to tell apart.
- **An answer to the 83 percent header-OCR failure** in
  [P2](#p2-header-ocr-failed-on-83-percent-of-captures). If the cause is the
  images, a controlled shoot fixes it outright. If it is the extractor, a clean
  corpus makes that unambiguous.
- **Show-through suppressed at source.** Backing each leaf with black card
  removes it at capture; no later processing recovers that as cleanly. Page 261
  shows how heavy it gets on sparse pages.
- **The personal-information problem deleted rather than managed.** A complete
  clean corpus lets the old frames be discarded wholesale instead of screened,
  per [R3](#r3-personal-information-becomes-a-disposal-task).
- **One naming regime.** A single cover-to-cover shoot in physical order
  resolves the identifier scheme in
  [L4](#l4-cover-to-cover-scope-breaks-the-page-identifier-scheme) directly,
  rather than merging two regimes after the fact.
- **The rig is being built regardless** for the plates, front matter, and
  index, so the marginal cost of continuing through the text pages is small.

### Shooting order

Sequence the shoot so that an interruption never leaves a content gap. Steps 1
to 3 close every known hole in the corpus; step 4 is the quality upgrade.

1. Pages 016 and 017 — the only content with no capture at all, and a single
   opening.
2. The eight prototype-only pages: 013, 014, 015, 018, 021, 022, 027, 029.
3. Everything the systematic run deliberately excluded, which the owner reports
   is readily obtainable: covers, front matter, title and copyright pages,
   contents, the color plate section, the index, and remaining back matter.
   Scope is cover to cover per [R1](#r1-scope-is-now-cover-to-cover), and the
   book cross-references at least 176 numbered photographs that exist nowhere
   on disk.
4. The remaining text pages, 019 through 261.

### Correcting the quality claim behind the original recommendation

This section first argued for a full re-shoot on the grounds that capture
quality was poor and highly variable. **That evidence was bad, and the
correction is worth recording even though the conclusion survives.** The three
pages inspected were 015, 018, and 200. The first two belong to the 2026-07-14
prototype session; only 200 came from the systematic run. Two of three samples
were drawn from the worst 8 percent of the corpus, and the conclusion
generalized from them.

The corpus has two distinct phases, visible in EXIF and confirmed by the owner:

| Phase | Sessions | Images | Purpose |
| --- | --- | --- | --- |
| Prototype | 07-12, 07-14, 07-21 | 30 | Trial captures behind the 8-genus prototype in `doc/mcleish.genera.md` |
| Systematic | 07-23, 07-24 | 358 | The full taxonomic-text run, pages 013 to 261 |

Session provenance localizes the damage precisely:

- **239** of the 249 pages in range have a capture from the systematic run.
- **8** pages have prototype captures only: 013, 014, 015, 018, 021, 022, 027,
  and 029.
- **2** pages have no capture at all: 016 and 017.

Spot checks of the systematic run found it sound. Pages 200, 261, and 089 are
each complete in frame, sharp, and legible edge to edge — including 089, the
most-recaptured page in the corpus at seven exposures. Page 089 shows moderate
curl and rotation at the lower left, and page 261 heavy show-through across its
half-empty lower page, but neither costs a character.

Two consequences follow, and both matter:

- The re-shoot is a **quality and uniformity upgrade**, not a rescue. Framing it
  as a rescue would set the wrong bar for accepting the new corpus: the
  standard is better than 239 already-adequate pages, not merely legible.
- The existing captures remain a genuine fallback for pages 019 to 261. If the
  re-shoot stalls, is interrupted, or produces a worse frame for some page,
  there is a working alternative for all but ten pages — and those ten are
  named above.

### A capture setup a volunteer can actually achieve

This does not require buying a copy stand. The existing captures are 12
megapixels, which is sufficient: a page filling the frame at 3024 pixels across
a seven-inch page width yields roughly 430 ppi, comfortably above the plan's
400 ppi target. The camera was never the problem. The lack of control was.

- Mount the phone on a tripod with an overhead or horizontal arm so the sensor
  is parallel to the page and the position does not change between frames.
- Place the book on a **matte black or dark gray** mat — not white. The pages
  are cream, so a white background destroys the contrast that page-boundary
  detection depends on, which is precisely why the edge-clipping probe
  described above failed. A dark mat also reduces bounce flare into the lens.
  Black foam board or black felt is sufficient. Use a cradle or foam wedges if
  the binding resists lying flat.
- Use two matching lamps at roughly 45 degrees on opposite sides, with room
  lighting off and blinds closed, so illumination does not drift with the time
  of day.
- Lock exposure, focus, and white balance. Disable HDR and Live Photo. Use the
  self-timer or a remote so touching the phone does not shake the frame.
- Frame one printed page per exposure, with the page nearly filling the frame
  and a small margin on all four sides.
- Shoot a test frame first and inspect all four corners at full magnification
  before continuing. Repeat that check whenever the setup is disturbed.
- Back the photographed leaf with black card to suppress show-through.
- Keep hands, clips, weights, and every other object outside the frame.
- Shoot in page order and batch-rename from the EXIF sequence afterward, then
  verify the naming with the running-head pass described in
  [M2](#m2-filename-to-printed-page-verification-was-already-done-by-hand).

A tripod eliminates perspective distortion, which is the larger defect in the
current captures. What remains is page curl near the gutter, and it is worth
attacking at capture time rather than in software. In rough order of value:
shoot one page per frame with the target page lying flat rather than shooting
spreads; weight the outer margins with book snakes, outside the printed area;
and consider a glass or acrylic platen, which flattens completely at the cost
of reflections — angle the lamps near 45 degrees so the reflection cone misses
the lens, and skip the platen entirely if the binding objects. Residual curl
dewarps well when the page boundary is clean and text baselines are available
to fit, which is the common case here. Full-page plates are the exception:
with no baselines, the fit has to come from the page boundary and gutter
curve, so those pages benefit most from the platen.

Include the covers, endpapers, title page, copyright page, contents, all
front matter, every plate, and all back matter including the index.

### What happens to the existing 388 captures

Keep them read-only until the new corpus passes a completeness check — they
are the only evidence that certain pages exist, and they cost nothing to
retain during the transition.

After the new corpus is verified complete, the old captures have no further
role, and the frames containing personal documents should be deleted rather
than archived. Screening them is the one triage pass worth running regardless
of path, and it is cheap: the existing audit report already renders every
capture as a browsable contact sheet, so screening is a few seconds per image
by eye. Record the outcome as a manifest field so the disposal decision is
auditable, then delete.

## What the plan gets right

Keep these without modification:

- Three-layer separation of source, evidence, and reviewed text.
- TEI P5 as the canonical layer with generated derivatives, and the rule that
  no editorial correction is ever emitted as printed text.
- Principle 4 — preserve printed wording; dictionaries flag but never rewrite.
  This is exactly right for a flora, where historical synonymy and printer's
  errors are themselves data.
- The refusal to blend disagreeing OCR engines automatically, using
  disagreement as a review-priority signal instead.
- The refusal to accept confidence scores as acceptance criteria.
- Explicit encoding of illegible and uncertain readings rather than guessing.

## Corpus facts verified

All figures below were measured directly against `page-scans/` and
`manifest/pages.json`, not taken from the plan.

| Property | Measured value |
| --- | --- |
| JPEG files | 388 |
| Corpus size on disk | 2.4 GB |
| Printed pages with at least one capture | 247 |
| Printed pages with no capture | 2 (016, 017) |
| Pages with exactly one capture | 129 |
| Pages with two captures | 104 |
| Pages with three or more captures | 14 |
| Largest capture set | page 089, seven captures |
| Encoded dimensions | 3024x4032 for 387 files; 4032x3024 for `224.jpg` |
| Effective display orientation | portrait for all 388 |
| File size | 2.70 MiB minimum, 8.68 MiB maximum, 6.22 MiB mean |
| Distinct capture sessions in EXIF | five: 07-12, 07-14, 07-21, 07-23, 07-24 |

The plan's own counts are accurate. Three observations extend them:

- The corpus was shot across five sessions ten days apart, with 353 of 388
  captures taken on 2026-07-23.
- `page-scans/.DS_Store` is present, and no `.gitignore` excludes it.
- The plan describes pages 016 and 017 as having "no base files." They have no
  files at all.

Direct inspection of pages 015, 018, and 200 establishes the layout:

- Body text is set in **two columns**.
- Figures are full page width and are followed by full-width captions of two
  to three lines, after which two-column body text resumes on the same page.
- Running heads carry a genus sequence number and italic genus name, for
  example `3 Goodyera`, `5 Prescottia`, `72 Jacquiniella`.
- Page numbers sit outer: top left on versos, top right on rectos.
- Keys use small capitals for field labels, dot leaders, and destination
  numbers followed by italic species names.
- Fractions appear as vulgar glyphs and magnifications as multiplication
  signs, for example `x 2/3`, `x 24`, `x 40`.
- Show-through from the reverse of the leaf is visible on light areas.

Capture quality splits along session lines rather than varying at random. Page
200, from the systematic run, is complete, square to the sensor, sharp, and
generously margined; so are 261 and 089. Page 018, from the prototype session,
is **clipped on two edges** — the final body lines run off the bottom of the
frame mid-sentence and the right column of the key is truncated mid-word. See
[Correcting the quality claim](#correcting-the-quality-claim-behind-the-original-recommendation)
for the phase breakdown and the ten pages that lack a systematic capture.

## Resolved by the owner's answers

### R1. Scope is now cover to cover

Front matter, the plate and photograph section, back matter, and the index are
all in scope. This resolves the largest open question in the original plan and
removes the risk that `Photo. N` cross-references resolve to nothing.

It also invalidates the hardcoded page range in the tooling. See
[L4](#l4-cover-to-cover-scope-breaks-the-page-identifier-scheme).

### R2. Rights position is private research use

The project supports a professional colleague, and the scans are not publicly
available. This lowers the rights question from blocking to a recorded
assumption, and the original plan's final step of publishing a QA report should
be restated as delivering it to the botanist.

Two things are still worth doing, both cheap. Capture the title-page
bibliographic details during the re-shoot — they are needed to cite the source
in any derived work, and the title page is being photographed anyway. And write
the rights assumption down in the repository: private research use, no public
distribution of scans or transcription, so that a future reader who inherits
the work does not have to reconstruct the basis for it.

### R3. Personal information becomes a disposal task

Because the scans stay private, the personal documents visible in the frames
are a hygiene problem rather than a disclosure one. The frames include a voter
registration or identification card in `015.jpg`, and a medical history form
and an order confirmation bearing an order identifier in `200.jpg`. There are
almost certainly more.

The owner's instinct to identify and discard these is right, and the re-shoot
makes it clean: screen the old corpus, delete the affected frames once the new
corpus is verified complete, and do not carry them forward. Until then, do not
copy the old corpus anywhere it would be harder to delete.

### R4. Version control has a defined destination

The work belongs on a branch of `~/Programming/selby/belize-orchid-genera-key`.
That is better than initializing a new standalone repository here, and it
removes the concern about polluting the unrelated enclosing repository.

Do not wait for the approach to prove out before putting this under version
control, though. Initialize a repository in place now and commit the scripts,
manifests, and documents — not the scans. The risk is not that the approach
fails; it is that a few hundred accumulated review decisions live in an
untracked temporary directory in the meantime. When the move happens, the
established pattern applies: add the temporary repository as a remote in the
Selby repository and fast-forward onto a branch, rather than replaying commits
by hand.

The storage decision is already made in practice — `mcleish` is gitignored in
the Selby repository, per
[P4](#p4-the-scans-are-already-excluded-from-version-control). Keep that,
state it deliberately, and lean on the manifest's SHA-256 records so the
untracked image set remains verifiable.

**Branch point: take it from `55a4506`, the current local `dev` head.**

The tempting alternative is `e055437`, the last commit shared by `main`,
`staging`, `dev`, and all three remotes. It is a clean base, but its tree holds
only `.gitignore`, `LICENSE.md`, `README.md`, and the keys-overview document.
Branching there discards the 388 hand-adjudicated page assignments in
[P1](#p1-the-page-mapping-is-hand-adjudicated-and-trustworthy), the genus
corpus in [P3](#p3-the-genus-corpus-is-about-11-percent-complete), and the
analysis pipeline this extraction work exists to feed. Those five commits on
`dev` are the on-topic prior art, not the part you were unhappy with — the
dissatisfaction was with the process, and its most valuable output was human
adjudication that survives the process being replaced.

Nothing obliges the new branch to keep the superseded tooling. Deleting files on
a branch is cheap; recovering them from an ancestor you branched away from is
not.

Two things to handle first:

- The `dev` working tree is dirty: modified analysis JSON files, deleted review
  sheets under `analysis/mcleish_review_sheets/`, a rename of
  `doc/20260707-botanical-keys-overview.md` to the model-tokened filename, and
  two untracked documents. Commit or stash deliberately — a branch cut from a
  dirty tree carries the mess forward.
- Local `dev` is five commits ahead of `origin/dev` and none of it is pushed,
  so the new branch will depend on commits that exist only on this machine
  until that changes. Worth knowing; not worth blocking on.

### R5. The retake gate is no longer a risk

The original plan's hardest structural risk — a mandatory retake phase with no
fallback if the book proved inaccessible — does not apply. No fallback branch
is needed.

## Gaps the answers made larger

### L1. One non-botanist cannot proofread nomenclature

The plan requires a second specialist pass over all scientific names, author
citations, and measurements. The available capacity is one non-botanist
volunteer, with a botanist reviewing at milestones. A non-specialist reading
`Epipactis erosa Ames & C. Schweinf.` against an image cannot reliably tell a
faithful transcription from a plausible corruption, because nothing in the
reader's knowledge objects to the wrong version.

The owner's position — that this is automatable against public taxonomic
services — is correct, and Orchidaceae is the best-covered family for it, since
Kew's World Checklist of Selected Plant Families began with orchids. Treat this
as an automated data-quality stage rather than a human review burden.

Usable resources, all public:

- **GBIF species match.** Free, no API key, fuzzy matching that returns a match
  type and confidence. The high-value behavior for this project is that a
  `FUZZY` match at small edit distance both flags the OCR error and proposes
  the correction, which a pure membership test cannot do.
- **POWO and IPNI**, Kew. The `pykew` Python client wraps both. POWO carries
  synonym-to-accepted mappings, which is what supports the taxonomic updating
  described below.
- **World Flora Online**, which offers name matching and a downloadable
  taxonomic backbone.
- **WCVP**, the World Checklist of Vascular Plants, available as a bulk
  dataset.

Two points of interpretation matter more than the choice of service:

- This is a 1990s flora, so many printed names are now synonyms. **A name
  matching a synonym record is evidence the transcription is correct**, not
  evidence the name is stale. A name matching nothing at all — neither accepted
  name nor synonym — is the strong OCR-error signal. That distinction is what
  converts a taxonomic judgment into a mechanical lookup.
- Per principle 4, no authority match ever rewrites a printed name in the
  canonical text. Record the printed name and the resolved accepted name as
  separate fields. The owner's "gravy" — updated genus and species
  designations — then falls out of the synonym mapping for free, as a derived
  layer rather than an edit to the source.

One caveat that cuts against live API calls. This plan pins tool versions for
reproducibility, and taxonomic backbones change: a name that resolves today may
resolve differently in a year, so a live-API pipeline is not reproducible. Use
live APIs for exploration, but pin a **dated snapshot** of WCVP, WFO, or the
GBIF backbone for the pipeline itself, and record its version in the QA report
alongside the tool versions. A local snapshot also removes rate limits and
makes a full-corpus pass cheap to repeat.

Apply the same mechanical treatment to measurements and magnifications: range
plausibility and unit consistency are checkable without botanical knowledge,
and implausible values are exactly where `1`/`l` and `0`/`O` substitutions land.

### L2. The botanist's time is the scarcest resource and is unbudgeted

The botanist is both the reviewer of last resort and the customer, and neither
the plan nor the answers bound how much of their time is available. Every
design decision downstream should be evaluated against whether it spends that
time well.

Practical consequences:

- Never ask the botanist to read prose or hunt for errors. Present a compact
  decision list: the flagged item, the surrounding printed context, a crop of
  the source region, and the proposed reading.
- Batch flags by genus rather than by page, so related judgments are made
  together in one context.
- Define what a milestone is in advance — a completed genus, a completed key,
  or a fixed page count — and what the botanist is being asked to confirm at
  each, so review is bounded rather than open-ended.
- Track the flag rate. If it does not fall as the pipeline is tuned, the
  pipeline is the problem, not the reviewing.

### L3. The deliverable is not TEI, and is possibly not the whole book

The customer is a botanist who must be delighted. No botanist will open a TEI
file. TEI remains the right canonical layer, but it is an intermediate here,
and the plan should say so explicitly and name the actual deliverables. Likely
candidates, in rough order of value:

- A clean, searchable reading copy of the text.
- Structured extracts of the repeating data fields — taxon, synonymy, general
  distribution, distribution in Belize, habitat, flowering season, etymology,
  notes — as tabular data. This book's treatments are highly regular, as the
  inspected pages show, which makes the extraction tractable and the result
  genuinely more useful than the prose.
- The keys, in a form that can be followed or executed rather than only read.

That last point raises a scope question the answers did not settle. The
destination repository is named `belize-orchid-genera-key`, which suggests the
actual goal may be a working key to genera rather than a full-book
transcription. Those differ by roughly an order of magnitude in effort. If the
key is what would delight the customer, the keys and genus descriptions should
be transcribed and delivered first, with species treatments following, so value
arrives early and the botanist's early review shapes the rest. This inference
is drawn only from the directory name and should be confirmed.

### L4. Cover-to-cover scope breaks the page identifier scheme

Both the tooling and the plan assume every page is a three-digit printed number
in the range 013 to 261.
[build_scan_manifest.py:16-19](../scripts/build_scan_manifest.py#L16-L19)
hardcodes the range and the filename pattern, and rejects anything else.

Cover-to-cover scope introduces pages that scheme cannot express: covers and
endpapers, unnumbered front matter, roman-numeral front matter, unnumbered
plate pages, and any unnumbered leaves in the back. Before the re-shoot, define
a page identifier that covers all of them — a sequence number for physical
position, plus a separate printed-label field holding the number as printed,
empty where there is none. Physical sequence is what establishes reading order;
the printed label is what cross-references resolve against.

Deciding this before the shoot is what keeps it cheap. Deciding it afterward
means renaming several hundred files.

## Method gaps that still stand

### M1. Two-column layout is the dominant case and is unaddressed

The Phase 4 region list is: running head and page number, body text, headings,
keys and indented lists, figure, caption, footnote. There is no column region
and no reading-order rule. Columns appear once in the whole plan, as a passing
mention of TEI `<cb>` in Phase 5.

Every body page in this book is two-column, and figure pages mix full-width
figure and full-width caption with two-column body above or below. Column
detection and column-aware reading order are the largest source of catastrophic
OCR failure on this material — not character errors, but interleaved text that
is expensive to detect and expensive to repair after the fact.

Phase 4 needs an explicit column model: detect the column separator, assign
each region a column span, and define reading order as full-width regions in
vertical order with two-column bands read left column fully, then right column.
The benchmark must measure column assignment and reading order on mixed-layout
pages specifically. If the index is set in more than two columns, it needs its
own treatment.

This remains the highest-value methodological fix in the review.

### M2. Filename-to-printed-page verification was already done by hand

**This finding was wrong as originally written, and the correction matters.**
The existing filenames are not naive: every one of the 388 was assigned by the
adjudicated page-mapping pipeline in the Selby repository. See
[P1](#p1-the-page-mapping-is-hand-adjudicated-and-trustworthy). The corpus does
not need this verification pass. It has already had a more thorough one.

The recommendation survives only for the re-shoot, where it applies with full
force: names will be assigned by batch rename from shooting order, so a single
missed or duplicated frame shifts every subsequent name. A narrow pass over the
running-head band — page number and genus name from a small, high-contrast
region, no layout analysis, no dewarping, no frozen parameters, output to a
manifest field and a discrepancy report rather than to transcription — is the
right check.

Set expectations for it honestly, though. That exact pass has been run on this
material once and produced nothing usable; see
[P2](#p2-header-ocr-failed-on-83-percent-of-captures). On a controlled shoot it
should behave far better, but treat a low anchor rate as a signal about capture
quality rather than as a reason to fall back to manual assignment again.

### M3. Running heads are an unused ordering signal

The running heads carry a monotonically increasing genus number and name
(`3 Goodyera` on page 015, `5 Prescottia` on page 018, `72 Jacquiniella` on
page 200). That is a second, independent ordering signal, free to extract in
the same pass as
[M2](#m2-filename-to-printed-page-verification-was-already-done-by-hand).

Use it to validate page order, to detect a transposed or misnamed capture that
a page-number check alone would miss, and to build a genus-to-page index that
later validates key destinations and cross-references. It also bounds any
missing-page problem: a gap in the genus sequence localizes missing content
even where page numbers are illegible.

### M4. No vision-language model is benchmarked

The candidate engines are Tesseract, PaddleOCR, and Kraken. All are classical
recognition pipelines, and their weakest areas map precisely onto this book's
hardest features: italic discrimination, mixed-column reading order, dot
leaders and key structure, diacritics, vulgar fractions, and small capitals.

Benchmark at least one modern vision-language model as a third candidate. Doing
so does not weaken the plan's evidence discipline provided three constraints
are written in:

- The model transcribes one segmented region at a time, never a whole page
  free-form, so every output stays anchored to a region identifier and source
  image.
- The model never supplies text that is not legible in the region. Illegible
  spans are encoded as uncertain exactly as they would be from any other
  engine.
- Output is scored on the same pilot ground truth as the classical engines,
  with attention to invented plausible text — a failure mode classical OCR does
  not have and which the existing metric list does not measure. Add a
  fabrication rate: tokens present in the output with no counterpart in the
  image.

This matters more given [L1](#l1-one-non-botanist-cannot-proofread-nomenclature).
A fabricated but plausible scientific name is precisely the error a
non-botanist proofreader will not catch, which is why the fabrication metric is
not optional and why the authority cross-check is the necessary backstop.

Disagreement between a classical engine and a vision-language model remains a
strong review-priority signal, per the plan's existing rule.

### M5. Ground truth is single-keyed

One transcriber produces the pilot ground truth and a second reviewer compares
it against the images. A reviewer checking existing text is anchored by that
text and will miss errors independent transcription would surface. Everything
downstream is scored against this set, so its own error rate is the floor on
every accuracy claim the project can make.

With one volunteer, double-keying by two people is not available. The workable
substitute is to key the pilot twice, separated by enough time to break recall,
compare mechanically, and reconcile every difference. Report the
pre-reconciliation disagreement rate as the measured human error floor, and
state in the QA report that no pipeline accuracy claim below that floor is
meaningful.

### M6. No accept or reject thresholds anywhere

The benchmark lists six metrics and then says to choose the most accurate
reproducible pipeline, with no floor below which the approach changes. The
final validation requires a character error rate on a stratified sample without
specifying sample size, strata, or confidence interval.

Specify both: a go/no-go threshold on the pilot with a defined response if it
is missed, and a sampling design naming strata (ordinary prose, keys, figure
captions, nomenclature blocks), pages per stratum, characters counted, and the
confidence interval reported alongside the point estimate.

### M7. The hyphenation rule is unsafe for botanical prose

The derived-format rules say to join words split only by a printed line break
and to preserve lexical hyphens. In this book those cases are frequently
indistinguishable: hyphenated compound descriptors are pervasive, and the
inspected pages break inside them repeatedly — `ovate-lanceolate`,
`greenish-white`, `triangular-lanceolate`, and `J. equitanti-folia` all appear
with or adjacent to line breaks.

An automatic join produces `ovatelanceolate`; an automatic retain produces
`equitanti-folia`. Both silently corrupt the printed wording, which principle 4
forbids.

Encode every end-of-line hyphen in the TEI layer with its hyphenation status
marked, so the ambiguity is preserved rather than resolved at generation time.
Resolve status during review against a compound-descriptor lexicon built from
the book itself, defaulting to retaining the hyphen when the lexicon has no
entry. Add an automated check listing every joined token that appears nowhere
else in the corpus unhyphenated.

### M8. Italic detection has no strategy, only a metric

Italic accuracy is measured and represented with `<hi rend="italic">`, but no
method is proposed. In a flora italic is semantic — it marks scientific names,
and it also marks organ names in descriptive prose (`Leaves`, `Sepals`,
`Column` on the inspected pages). Font classification on phone captures of
1990s offset print is not reliable enough to carry that load alone.

Detect scientific-name spans structurally — genus and species epithet patterns,
author abbreviation grammar, basionym and synonymy block position — and use
font evidence as corroboration rather than as the primary signal. The authority
cross-check described in [L1](#l1-one-non-botanist-cannot-proofread-nomenclature)
then validates the result.

### M9. Region taxonomy omits real features of this book

Add to the region list: table and table caption, map, plate and plate caption,
thumb-tab or section marker printed in the outer margin, and multi-column index
entry. A `Photographs` thumb-tab is visible in `015.jpg` and would otherwise be
transcribed into the body prose stream. With the index now in scope, its
multi-column structure needs explicit representation.

### M10. Cross-reference integrity is only half checked

Validation covers key couplet destination numbers. The book carries at least
three more reference classes: `Fig. N`, `Photo. N`, and page references in the
text. Extend validation to resolve figure references against transcribed figure
captions, photograph references against the plate inventory — which is now in
scope and therefore checkable — and page references against the page inventory.

### M11. Show-through is not mentioned

Show-through from the reverse of the leaf is visible on all three inspected
pages. It is a common cause of spurious marks after aggressive binarization and
of false low-confidence regions. Name it in the preprocessing steps and in the
review-reason vocabulary alongside `blur`, `glare`, and `shadow`. Backing the
page with black card during the re-shoot reduces it substantially at capture
time, which is cheaper than correcting it afterward.

## Defects in the current tooling

The committed scripts implement the manifest and a contact-sheet report. Both
are clean, dependency-free, deterministic, and tested. The following are
specific defects rather than style observations. Items 1 through 3 should be
fixed before the re-shoot, because they affect how the new corpus is ingested.

1. **Stale acceptance decisions survive a file replacement.**
   [build_scan_manifest.py:216-224](../scripts/build_scan_manifest.py#L216-L224)
   carries review fields forward when the candidate *filename* list is
   unchanged. Replacing an image in place — re-exporting, rotating,
   recompressing — preserves an `accepted` decision made against different
   pixels. Key the carry-forward on the SHA-256 list, which the manifest
   already records, and reset any page whose checksums changed to `unreviewed`
   with a remark naming the superseded digest.

2. **Reviewer edits to `pages.csv` are silently discarded.** `write_csv`
   regenerates the CSV from the JSON, and
   [build_scan_manifest.py:304-309](../scripts/build_scan_manifest.py#L304-L309)
   reads only `pages.json` as previous state. The plan describes `pages.csv` as
   "Human-readable page and source selection," which invites a reviewer to edit
   it; the next build overwrites their work with no warning. Either declare the
   CSV generated-only and say so in the file, or add an ingest path. Do not
   leave it ambiguous — this is the defect most likely to destroy real work.

3. **The page range and filename pattern are hardcoded.**
   [build_scan_manifest.py:16-19](../scripts/build_scan_manifest.py#L16-L19)
   fixes pages 013 to 261 and the `NNN[-scanN].jpg` pattern, and
   [build_scan_manifest.py:180-186](../scripts/build_scan_manifest.py#L180-L186)
   raises `ValueError` on anything else, so one stray `IMG_1234.jpg` makes the
   manifest unbuildable. Cover-to-cover scope requires the identifier scheme in
   [L4](#l4-cover-to-cover-scope-breaks-the-page-identifier-scheme) instead, and
   unmatched files should be recorded as an anomaly list rather than aborting
   the build.

4. **The audit report shows contradictory dimensions.**
   [build_scan_manifest.py:143-148](../scripts/build_scan_manifest.py#L143-L148)
   returns encoded `width` and `height` while `display_orientation` accounts for
   EXIF rotation. For `224.jpg`, the only rotated file in the corpus, the report
   renders `4032 x 3024 pixels; portrait`. Add and render display dimensions.

5. **No personal-information field exists.** Screening the old corpus per
   [R3](#r3-personal-information-becomes-a-disposal-task) needs somewhere to
   record the result. Add a boolean flag and a remark, and add a filter to the
   audit report so screening can be done in one pass over the contact sheets.

6. **The manifest cannot answer the plan's own question about capture
   conditions.** EXIF `DateTimeOriginal`, camera model, and exposure settings
   are present in the files and are not extracted; only orientation is. Add
   capture timestamp and camera model, and group the audit report by session.
   After a controlled re-shoot this becomes a useful drift check: a session
   boundary in the middle of a chapter is worth knowing about.

7. **None of the specified automated quality indicators exist.**
   [build_audit_report.py:150-158](../scripts/build_audit_report.py#L150-L158)
   categorizes pages by capture count alone. Focus, clipping, perspective, edge
   coverage, and near-duplicate detection are all absent. Under the re-shoot
   recommendation most of these become unnecessary, which is a further argument
   for it — but keep a simple focus score and an edge-margin check as a
   per-frame sanity check during shooting, so a bad frame is caught while the
   book is still open rather than months later.

8. **The audit report has no path from looking to deciding.** It is read-only
   HTML; the reviewer must switch to the CSV or JSON and keep the two in sync by
   hand. With a single volunteer making several hundred screening and
   acceptance decisions, per-page controls that emit a paste-able record are
   worth the modest effort.

9. **Image links break silently if `--output` moves.**
   [build_audit_report.py:164](../scripts/build_audit_report.py#L164) hardcodes
   `../../page-scans/`, correct only for the default output path. Compute the
   relative path from the actual output location.

10. **No `.gitignore`, and `page-scans/.DS_Store` is present.** Fix before
    initializing the repository per
    [R4](#r4-version-control-has-a-defined-destination).

11. **The plan's project layout omits `test/`, which already exists.** Add it,
    state how the suite is run, and require that manifest-affecting changes ship
    with tests.

## Quick win: pages 016 and 017 are one missed page turn

The plan and the manifest both treat this gap as unresolved. The captures
resolve it.

Page 015 is a recto — its page number sits at the top right. Page 018 is a
verso — its number sits at the top left. Pages 016 and 017 are therefore the
verso and recto of a single opening: exactly what is visible one turn past the
014-015 spread. The gap is one skipped page turn, not a missing leaf, not an
unnumbered insert, and not an out-of-scope plate.

Content confirms it. Page 015 carries running head `3 Goodyera`; page 018
carries `5 Prescottia`. Genus 4, and the start of genus 5, fall entirely on the
two missing pages.

Under the re-shoot recommendation this resolves itself. It is recorded here
because it demonstrates the value of the recto-verso and genus-sequence checks
in [M3](#m3-running-heads-are-an-unused-ordering-signal) as general tools, and
because the manifest remarks for both pages should be updated to record the
reasoning rather than leaving the gap described as unexplained.

## Revised execution order

1. Confirm the deliverable with the botanist — full-book transcription,
   structured species data, the keys, or a staged combination. See
   [L3](#l3-the-deliverable-is-not-tei-and-is-possibly-not-the-whole-book).
   Everything downstream is sized by this answer.
2. Initialize a repository in place; commit scripts, manifests, and documents.
   Decide image storage: outside the repository with checksums, or Git LFS.
3. Record the rights assumption and, after the shoot, the title-page
   bibliographic details.
4. Screen the existing 388 captures for personal information; flag in the
   manifest. Do not delete yet.
5. Define the page identifier scheme for cover-to-cover scope, including
   unnumbered and roman-numeral pages and plates.
6. Fix tooling defects 1 through 3 so the new corpus ingests correctly.
7. Build the capture setup; shoot and inspect a test spread at full
   magnification before proceeding.
8. Shoot the book cover to cover in page order, checking frames as you go.
9. Build the manifest for the new corpus; run the running-head pass to verify
   naming, page order, and the genus sequence.
10. Verify completeness against the printed page sequence and the contents
    page. Only then delete the old captures flagged for personal information.
11. Select a pilot spanning ordinary prose, a genus opening, a dense key, a
    figure page with a full-width caption, a plate, and an index page.
12. Key the pilot ground truth twice with separation in time; reconcile; report
    the human error floor.
13. Benchmark OCR and layout pipelines including a vision-language model;
    measure column assignment and reading order explicitly; apply the go/no-go
    threshold.
14. Freeze preprocessing, segmentation, and OCR versions and parameters by
    container image digest.
15. Process the corpus in page order.
16. Proofread with machine assistance; run boundary, structure, and
    cross-reference checks continuously; accumulate the authority-check flag
    list rather than resolving taxonomic questions alone.
17. Hold botanist milestone reviews against the batched flag list, organized by
    genus.
18. Generate the botanist-facing deliverables from reviewed TEI.
19. Deliver the QA report: scope, rights position, missing material, marked
    uncertainties, human error floor, measured sample accuracy with confidence
    interval, and exact tool versions.

## Residual questions

1. Is the deliverable the full book, or primarily the key to genera implied by
   the destination repository name? This sizes the whole project and should be
   settled with the botanist before the pilot.
2. How much botanist review time is available, and what constitutes a
   milestone?
3. Is the index set in two columns or more? It affects the column model.
4. Does the book contain tables, maps, or distribution charts? None appeared in
   the three pages inspected, but the region taxonomy should be settled before
   segmentation is frozen.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Opus 5
generator-model-token: claude-opus-5
generator-provider: Anthropic
generation-date: 2026-07-27
generator-responsibility: review
```

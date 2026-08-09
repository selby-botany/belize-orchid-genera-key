# Prototype 04, Phase 2: implementation and test plan

- [Prototype 04, Phase 2: implementation and test plan](#prototype-04-phase-2-implementation-and-test-plan)
  - [Purpose](#purpose)
  - [1. Commit sequence](#1-commit-sequence)
  - [2. Test plan](#2-test-plan)
    - [2.1 Convention](#2-1-convention)
    - [2.2 `test_build_character_matrix.py`](#2-2-test_build_character_matrixpy)
    - [2.3 `test_generate_key.py`](#2-3-test_generate_keypy)
    - [2.4 `test_validate_key.py`](#2-4-test_validate_keypy)
    - [2.5 `test_export_review_queue.py`](#2-5-test_export_review_queuepy)
  - [3. Pilot gate](#3-pilot-gate)
  - [4. Full-run acceptance checklist](#4-full-run-acceptance-checklist)
  - [Metadata](#metadata)

## Purpose

The commit-by-commit build order, the test plan for each new module, the
pilot gate (named genera, not just criteria), and the full-run acceptance
checklist — the same four things prototype 03's implementation plan
covers, one phase further along.

## 1. Commit sequence

Subjects follow this repository's own convention, same as prototype 03's
implementation plan states for itself.

| # | Subject | Gist |
| --- | --- | --- |
| 1 | `docs(prototype-04): add problem overview and motivation` | Doc 1 |
| 2 | `docs(prototype-04): add requirements` | Doc 2 |
| 3 | `docs(prototype-04): add architecture and design overview` | Doc 3 |
| 4 | `docs(prototype-04): add data formats and relationships` | Doc 4 |
| 5 | `docs(prototype-04): add detailed module design` | Doc 5 |
| 6 | `docs(prototype-04): add implementation and test plan` | Doc 6 (this document) |
| 7 | `docs(prototype-04): add prototype README` | Navigation stub, document index |
| 8 | `data(prototype-04): add character vocabulary` | `data/character_vocabulary.json` — hand-curated, Stage A |
| 9 | `feat(prototype-04): add character extraction proposals` | `analysis/character_proposals.jsonl` — agent-authored, Stage B (detailed design, §2) |
| 10 | `feat(prototype-04): add matrix assembly and quote verification` | `bin/build_character_matrix.py` + tests, Stage C |
| 11 | `feat(prototype-04): add key generation` | `bin/generate_key.py` + tests, Stage D |
| 12 | `feat(prototype-04): add validation analytics` | `bin/validate_key.py` + tests, Stage E |
| 13 | `feat(prototype-04): add review queue export` | `bin/export_review_queue.py` + tests, Stage F |
| 14 | `feat(prototype-04): add pipeline orchestrator` | `bin/run_pipeline`, `--pilot` and full-range modes |
| 15 | `feat(prototype-04): run pilot key generation over a representative sample` | Pilot output + a short pilot report (§3) |
| 16 | `feat(prototype-04): run key generation over all 69 genera` | Full-run output, only after the pilot gate passes |
| 17 | `docs(prototype-04): add results summary for botanist review` | Coverage, self-consistency, ambiguous leaves — plain language |

## 2. Test plan

### 2.1 Convention

Identical to prototype 03's own (its implementation plan, §2.1):
`unittest` via `../bin/python3`, module under test loaded by file path
(`importlib.util.spec_from_file_location`), no pytest, no package
structure. Every fixture is small and synthetic — hand-written matrix
rows and vocabulary entries, never a dependency on the real 69-genus
corpus at test time, for the same reason prototype 03's tests never
depend on real Vision OCR output: a test has to be a pure function of the
commit under test (this project's own stated non-negotiable — see the
project's global instructions on test determinism). The real corpus is
exercised only by the pilot and full runs themselves (§3, §4), which are
commits with recorded, reviewed output.

### 2.2 `test_build_character_matrix.py`

- `verify_quote` returns `True` when the quote is an exact substring of
  the named field's text, and `False` both when it isn't present at all
  and when it's a near-miss (paraphrased, reordered, or trailing
  whitespace/punctuation-only difference) — the boundary has to be exact
  substring match, not fuzzy, per design principle 2's "mechanically
  confirm," not "plausibly resemble."
- `build_matrix_row` fills a character with `not_stated` when no verified
  proposal exists for it, for every character in the vocabulary — a
  regression test asserting the returned row's key set equals the
  vocabulary's character set exactly, not just a subset.
- An unverified proposal (quote doesn't check out) does not appear in the
  resulting row and is reported for Stage F, not silently dropped —
  direct analogue of prototype 03's `ambiguous_genus_boundary` "surface
  the gap, don't drop it" test pattern.

### 2.3 `test_generate_key.py`

- `split_score` scores a character with zero `not_stated` rows higher
  than an otherwise-equal character with some `not_stated` rows, on a
  synthetic matrix built to isolate exactly that difference.
- `choose_best_split` never re-selects a character already used earlier
  on the same path (synthetic matrix with two useful characters, tree
  built two levels deep, second-level split differs from the first).
- `build_tree` produces a single-genus leaf when a synthetic matrix's
  characters fully separate two genera, and a multi-genus (ambiguous)
  leaf when two synthetic genera share every character's state — the
  direct test that requirements §2's "ambiguous leaf is an allowed,
  honestly reported outcome" is actually implemented as designed, not
  just described.
- `render_key_markdown` produces numbered couplets in the documented
  style (data document, §5) from a small synthetic tree.

### 2.4 `test_validate_key.py`

- `walk_tree` reaches the correct leaf for a matrix row built to match
  one specific path through a small synthetic tree.
- `self_consistency_report` reports zero failures for a tree built
  directly from the same rows it's tested against (the expected case),
  and — the direct regression test for requirements §2's acceptance
  floor — correctly reports a non-zero `failed` count when given a
  deliberately-inconsistent synthetic tree/row pairing, so the check
  itself is proven to fire, not just assumed to.
- `find_ambiguous_leaves` reports the correct shared-state dict for a
  synthetic multi-genus leaf, not just the genus list.

### 2.5 `test_export_review_queue.py`

- `queue_from_matrix` produces one row for a dropped/unverified proposal
  and one row for an all-`not_stated` genus row, each with the documented
  columns, from small synthetic input.
- `queue_from_validation` produces one row per ambiguous leaf, naming
  every member genus and the shared states.
- `merge_with_previous`: copied test-for-test from
  `prototype-03/test/test_export_review_queue.py`'s own
  `MergeWithPreviousTest` (detailed design, §8, item "copied, not
  reimplemented") — the same fixture shape, run against this phase's
  `merge_with_previous`, since it's the same function.

## 3. Pilot gate

Before the full 69-genus matrix/key/validation run (commit 16), the
pipeline runs once over a small sample chosen to be telling, not
representative — architecture document, §5's criteria, applied to real
genus records identified by inspecting the corrected Phase 1 output
directly (not guessed at in the abstract):

| Genus | Why it's in the pilot |
| --- | --- |
| `Psilochilus` | Rich, complete field coverage (10 fields, including `Roots`, `Leaves`, `Column`, `Lip`, `ETYMOLOGY`) — the happy path: proves a well-described genus produces a sensible, mostly-non-`not_stated` matrix row |
| `Corymborkis` | Its only Phase 1 field is `SUMMARY`, and even after the furniture-filter fix (`prototype-03` commit `df6139f`) that field still carries a residual, honestly-documented fragment rather than real diagnostic prose — the genuine, current thin-data/no-usable-evidence case, not a synthetic stand-in for one |
| `Sacoila` + `Sarcoglottis` | Both Spiranthinae genera whose only Phase 1 field is `SUMMARY`, both consisting largely of plate-caption/figure-reference fragments rather than substantive diagnostic text (same residual class as `Corymborkis`) — a real, plausible pair to end up sharing every extractable character state, making an ambiguous leaf a realistic outcome to test for rather than a hypothetical one |

**Pass condition:** `Psilochilus` and `Corymborkis` each produce a matrix
row with correct provenance on every non-`not_stated` cell (`Corymborkis`
is expected to be mostly or entirely `not_stated`, and that is a pass, not
a failure — requirements, §1.5). The tree built over just these four
genera is self-consistent for all four (requirements §2's floor still
applies to a four-genus pilot tree exactly as it does to the full one).
`Sacoila` and `Sarcoglottis` either separate cleanly (if the vocabulary
and their residual text turn out to support it) or land together in an
ambiguous leaf that Stage F reports by name with the shared states that
caused it — either outcome passes; a crash, a silent merge, or a silently
dropped genus does not.

**On failure:** the specific gap is fixed and the pilot re-run before
scaling — identical discipline to prototype 03's pilot gate (its
implementation plan, §3), for the identical reason.

## 4. Full-run acceptance checklist

Before Phase 2 is called complete:

1. Every genus in `prototype-03/analysis/genera.jsonl` has exactly one row
   in `analysis/character_matrix.jsonl` — never silently absent
   (requirements, §1.1).
2. `manifest/review_queue.csv` contains only genuine residual items, each
   with a legible reason.
3. Every non-`not_stated` cell in `analysis/character_matrix.jsonl` carries
   full provenance (`quote`, `source_field`, `source_image`).
4. `analysis/genus_key.md` reads as a plausible, usable dichotomous key on
   a manual spot check — not just schema-valid — and its couplet style is
   recognizably the same convention as McLeish's own key (data document,
   §5).
5. `analysis/validation_report.json`'s `self_consistency.failed` is `0`
   (requirements, §2's acceptance floor) — a non-zero value here is not a
   number to report and move past, per the module design's own note
   (detailed design, §7) that it would indicate a Stage D defect, not a
   data limitation.
6. The results-summary document (commit 17) states coverage honestly: how
   many of the 69 genera the key resolves cleanly, how many share an
   ambiguous leaf (named), what fraction of the matrix is `not_stated`,
   and — matching requirements §1.1's "no implied completeness" — that
   this key covers only the 69 genera in Phase 1's captured page range,
   nothing more.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

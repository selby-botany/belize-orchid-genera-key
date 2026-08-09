# Prototype 04, Phase 2: detailed module design

Engineer audience. Assumes the architecture document's six stages and the
data document's file schemas.

- [Prototype 04, Phase 2: detailed module design](#prototype-04-phase-2-detailed-module-design)
  - [Purpose](#purpose)
  - [1. Module map](#1-module-map)
  - [2. A clarification: what "Stage B" actually is](#2-a-clarification-what-stage-b-actually-is)
  - [3. `data/character_vocabulary.json` (Stage A)](#3-datacharacter_vocabularyjson-stage-a)
  - [4. `analysis/character_proposals.jsonl` (Stage B)](#4-analysischaracter_proposalsjsonl-stage-b)
  - [5. `bin/build_character_matrix.py` (Stage C)](#5-binbuild_character_matrixpy-stage-c)
  - [6. `bin/generate_key.py` (Stage D)](#6-bingenerate_keypy-stage-d)
  - [7. `bin/validate_key.py` (Stage E)](#7-binvalidate_keypy-stage-e)
  - [8. `bin/export_review_queue.py` (Stage F)](#8-binexport_review_queuepy-stage-f)
  - [9. `bin/run_pipeline` (orchestrator)](#9-binrun_pipeline-orchestrator)
  - [10. Principles carried from Phase 1, and where each is implemented](#10-principles-carried-from-phase-1-and-where-each-is-implemented)
  - [Metadata](#metadata)

## Purpose

Script-by-script design: inputs, outputs, main functions, and how each of
Phase 1's carried-forward principles (architecture document, §1) is
actually implemented here.

## 1. Module map

| Artifact | Stage | Kind | Notes |
| --- | --- | --- | --- |
| `data/character_vocabulary.json` | A | Hand-curated data file | No script writes it |
| `analysis/character_proposals.jsonl` | B | Semi-curated data file | See §2 — not a rerunnable script's output |
| `bin/build_character_matrix.py` | C | Python, via `../bin/python3` | Pure, deterministic, fully tested |
| `bin/generate_key.py` | D | Python, via `../bin/python3` | Pure, deterministic |
| `bin/validate_key.py` | E | Python, via `../bin/python3` | Pure, deterministic |
| `bin/export_review_queue.py` | F | Python, via `../bin/python3` | Shape modeled directly on `prototype-03/bin/export_review_queue.py` |
| `bin/run_pipeline` | orchestration | bash | Runs Stages C-F only — see §2 |

All Python scripts follow prototype-03's own test convention exactly:
pure functions importable via `importlib.util.spec_from_file_location`,
no package structure, no third-party test framework.

## 2. A clarification: what "Stage B" actually is

The architecture document's §3.3/§3.4 recommends model-assisted
classification for qualitative characters, verified by quote-checking.
This repository has no live, on-demand model API integration, and adding
one would conflict with this whole project's "no unsourced network
dependency" convention (requirements, §3) — a running pipeline script
that calls out to an API at execution time would make Stage C's output a
function of whatever the model returns *that run*, not of the committed
inputs, which breaks the reproducibility requirement outright.

The resolution: **Stage B is an authoring activity, not a runtime pipeline
stage.** `analysis/character_proposals.jsonl` is produced once (and
revised when the vocabulary changes or new evidence is found) by whoever
is doing the extraction work — in practice, so far, an AI coding agent
reading each genus's Phase 1 field text directly and recording a proposed
state with its supporting quote, the same way this document set itself
was written. The output is a committed, versioned, human-reviewable file,
not a live computation. Everything from Stage C onward is a pure,
deterministic script, rerunnable from that committed file with no network
access at all — which is exactly what makes the reproducibility
requirement satisfiable: the *proposals* are curated like the vocabulary
is; the *verification and assembly* are code, tested like any other stage
in this project.

## 3. `data/character_vocabulary.json` (Stage A)

Hand-curated per the data document, §2. Worth a small structural-validation
script (`bin/validate_vocabulary.py`, or a check inside Stage C's own
loading step) that confirms every character has a `not_stated` state and
every `state_id` is unique within its character — a self-validating check
in the same spirit as prototype 03's "self-validating test helpers"
convention (its detailed design's carried-forward-defects section), not a
generator.

## 4. `analysis/character_proposals.jsonl` (Stage B)

One JSON object per proposed assignment:

```text
{genus_id, character_id, state_id, quote, source_field, source_image}
```

No `confidence` field here — confidence belongs to Phase 1's OCR
provenance, already carried on the field the quote was read from; Stage C
looks that up rather than duplicating it. A proposal is just a claim; it
is not yet trusted (design principle 2).

## 5. `bin/build_character_matrix.py` (Stage C)

Reads `analysis/character_proposals.jsonl`, `data/character_vocabulary.json`,
and `prototype-03/analysis/genera.jsonl`; writes
`analysis/character_matrix.jsonl`.

```text
verify_quote(genus_record: GenusRecord, source_field: str, quote: str) -> bool
    # exact substring check: is `quote` actually present in
    # genus_record["fields"][source_field]["text"]? The one function this
    # whole stage exists to run before anything else is trusted
    # (architecture document, design principle 2).

build_matrix_row(genus_id: str, proposals: list[Proposal], vocabulary: Vocabulary,
                  genera_by_id: dict) -> MatrixRow
    # for every character in the vocabulary: find a verified proposal for
    # this genus, or fall back to the character's own `not_stated` state
    # (requirements, §1.5) — never an omitted key

main() -> None
    # loads all three inputs, verifies every proposal (unverified ones are
    # dropped from the matrix and queued for review, not silently
    # discarded — architecture document §4.6), builds one row per genus in
    # genera.jsonl (every genus gets a row, per requirements §1.1, even
    # one entirely `not_stated`), writes character_matrix.jsonl
```

## 6. `bin/generate_key.py` (Stage D)

Reads `analysis/character_matrix.jsonl` and `data/character_vocabulary.json`;
writes `analysis/genus_key.json` and `analysis/genus_key.md`.

```text
split_score(character_id: str, rows: list[MatrixRow]) -> float
    # information-gain-style score for splitting `rows` on this
    # character, penalized by the fraction of rows whose value for it is
    # `not_stated` (architecture document, §4.4) — a character nobody's
    # data supports isn't a good split candidate even if, on the rows
    # that do have it, it would separate them well

choose_best_split(candidates: list[str], rows: list[MatrixRow]) -> str | None
    # greedy: highest split_score among characters not already used on
    # this path to the current node (no character asked twice in one
    # couplet chain); None when no candidate usefully separates `rows`

build_tree(rows: list[MatrixRow], vocabulary: Vocabulary,
           used_characters: set[str] = frozenset()) -> KeyNode
    # recursive: a `rows` set of size 1, or one where no candidate
    # usefully splits it further, becomes a leaf (ambiguous if size > 1);
    # otherwise splits on choose_best_split's pick and recurses per branch

render_key_markdown(tree: KeyNode, vocabulary: Vocabulary) -> str
    # numbered-couplet rendering, McLeish's own key's own style (data
    # document, §5) — "1a. <lead for state group>" / "1b. <lead for the
    # other>", each pointing to the next couplet number or a genus name

main() -> None
```

## 7. `bin/validate_key.py` (Stage E)

Reads `analysis/character_matrix.jsonl` and `analysis/genus_key.json`;
writes `analysis/validation_report.json` and `.md`.

```text
walk_tree(tree: KeyNode, row: MatrixRow) -> list[str]
    # follows `row`'s own character values down the tree to a leaf,
    # returns that leaf's genus_ids (>1 means the genus landed in an
    # ambiguous leaf, per requirements §2 — not a walk failure)

self_consistency_report(tree: KeyNode, rows: list[MatrixRow]) -> SelfConsistencyReport
    # for every row, walk_tree and check its own genus_id is among the
    # returned genus_ids; a row whose own genus_id is *not* in the leaf
    # it reaches is a hard failure (requirements §2's acceptance floor) —
    # this should not be structurally possible if build_tree only ever
    # splits on the rows it's given, and a non-empty `failed` list here
    # means Stage D has a real defect, not just a data limitation

tree_depth_stats(tree: KeyNode) -> DepthStats
character_usage(tree: KeyNode) -> dict[str, int]
find_ambiguous_leaves(tree: KeyNode, vocabulary: Vocabulary) -> list[AmbiguousLeaf]
    # for each multi-genus leaf, the states every member genus shares —
    # not just that they're tied, but specifically why (requirements §2:
    # "reported explicitly ... with the shared states that caused it")

main() -> None
```

## 8. `bin/export_review_queue.py` (Stage F)

Reads `analysis/character_matrix.jsonl` (for unverified/dropped proposals
and all-`not_stated` rows — both need to be threaded through from Stage C,
either via a side-channel file or by Stage C recording them directly in
the matrix records' own `review_flags`, per the data document, §3, rather
than inventing a second output file) and `analysis/validation_report.json`
(for ambiguous leaves and any split worth a human sanity check); writes
`manifest/review_queue.csv`.

```text
queue_from_matrix(records: list[MatrixRow]) -> list[Row]
    # one row per dropped (quote-verification-failed) proposal, one row
    # per genus whose entire record is `not_stated`

queue_from_validation(report: ValidationReport) -> list[Row]
    # one row per ambiguous leaf, naming every genus in it and the shared
    # states that caused the tie

merge_with_previous(new_rows: list[Row], previous_path: Path) -> list[Row]
    # identical carry-forward-by-item_id logic to
    # prototype-03/bin/export_review_queue.py's own function — copied,
    # not reimplemented, since the problem and the correct fix are
    # already solved there

main() -> None
```

## 9. `bin/run_pipeline` (orchestrator)

Runs Stages C through F only, in order — Stage A (vocabulary) and Stage B
(proposals) are committed, curated inputs, not steps a rerun regenerates
(§2, and directly parallel to prototype 03's own decision to exclude its
Stage B preprocessing from its runtime `run_pipeline`, for a related
reason: a one-time, already-recorded conclusion doesn't need re-deriving
on every run). Supports a `--pilot GENUS_ID...` mode identical in spirit
to prototype 03's `--pilot FILE...`: restricts Stages C-E to the named
genera's rows while Stage F's review queue still reflects the full
current state of every stage's output on disk, matching prototype 03's
own reasoning for why the review queue is never pilot-scoped.

## 10. Principles carried from Phase 1, and where each is implemented

| Principle (architecture document, §1) | Where it's implemented |
| --- | --- |
| Never invent a state | `verify_quote` (Stage C) is the sole gate; nothing downstream of it can see an unverified proposal |
| A quote is not evidence until it's checked | Same — `verify_quote` runs before `build_matrix_row` accepts anything |
| Provenance travels with every fact | `MatrixRow` carries `source_field`/`source_image` through unchanged from the proposal; a `not_stated` cell has no provenance because it has no claim to back |
| Generated and hand-curated files are never ambiguous | §1's module map column "Kind" states it per file; `data/character_vocabulary.json` and `analysis/character_proposals.jsonl` are the only two hand/agent-curated artifacts, everything else is `bin/run_pipeline` output |
| Prove the approach, then scale it | `run_pipeline --pilot`, identical mechanism to prototype 03's |

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

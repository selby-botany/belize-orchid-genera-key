# Pilot run report

Ran `bin/run_pipeline --pilot psilochilus corymborkis sacoila sarcoglottis`
over the sample named in the implementation plan document, §3:
`Psilochilus` (rich, complete Phase 1 field coverage), `Corymborkis`
(thin/residual data even after prototype-03's furniture-filter fix), and
`Sacoila`/`Sarcoglottis` (a pair plausible enough to end up sharing every
extractable character state). This is a deliberately telling, not
representative, sample -- chosen to exercise the `not_stated` path and
the ambiguous-leaf path against real data, not just a synthetic fixture.

## Pass condition (implementation plan document, §3)

> `Psilochilus` and `Corymborkis` each produce a matrix row with correct
> provenance on every non-`not_stated` cell (`Corymborkis` is expected to
> be mostly or entirely `not_stated`, and that is a pass, not a failure).
> The tree built over just these four genera is self-consistent for all
> four. `Sacoila` and `Sarcoglottis` either separate cleanly or land
> together in an ambiguous leaf that Stage F reports by name with the
> shared states that caused it -- either outcome passes; a crash, a
> silent merge, or a silently dropped genus does not.

**Met.**

- `Psilochilus`: 7 of 17 characters verified (plant habit, leaf texture,
  inflorescence position and flower count, lip lobing and attachment,
  pollinia count), each with a real quote and source image from
  `prototype-03/analysis/genera.jsonl`. No review flags.
- `Corymborkis`, `Sacoila`, `Sarcoglottis`: entirely `not_stated`,
  each flagged `all_not_stated` -- their only Phase 1 field (`SUMMARY`)
  is residual caption/citation fragment text even after prototype-03's
  furniture-filter fix (`df6139f`), not usable morphological
  description. Correctly not guessed at.
- The generated tree over these four genera: one split on `plant_habit`,
  separating `Psilochilus` cleanly from the other three, who share the
  `not_stated` state on every character and so land together in one
  ambiguous leaf.
- Self-consistency: **0 failed**, out of 4 -- `Psilochilus` reaches its
  own clean leaf, the other three each reach the leaf containing
  themselves (as part of the shared three-genus ambiguous group).
- The review queue correctly lists all four items: three
  `all_not_stated` rows (one per thin genus) and one `ambiguous_leaf` row
  naming all three genera and the shared state (`plant_habit =
  not_stated`) that caused the tie.

Nothing crashed. Nothing disappeared without a trace: every pilot genus
is accounted for in `character_matrix.jsonl`, and the two genuinely
uncertain outcomes (three all-`not_stated` genera, one ambiguous leaf)
are both in `review_queue.csv` with a legible reason each.

## What this means for the full run

- The `not_stated`/ambiguous-leaf machinery worked exactly as designed
  on its first real exercise, not just in the synthetic test suite --
  a genuine, if small, validation that the pilot gate's purpose (prove
  the approach before scaling) delivered real signal here, the same way
  Phase 1's own pilot did.
- Three of four pilot genera being effectively data-free is a real
  consequence of choosing a deliberately hard sample, not a preview of
  the full run's typical genus. Most of the 69 genus records have
  meaningfully more field content than these three (prototype-03's
  results summary: 59 of 69 are "complete" records with several
  populated fields) -- the full run is expected to produce far more
  characters per genus on average than this pilot's 7-out-of-17-for-one-
  genus-and-nothing-for-three shows.
- The character vocabulary (17 characters) was not adjusted on the
  strength of this one pilot. If the full run's coverage turns out
  systematically thin across many genera, that is the point to revisit
  it with real evidence, not now, with four genus records.

## Metadata

```text
generator-name: Claude Code
generator-version: Claude Sonnet 5
generator-model-token: claude-sonnet-5
generator-provider: Anthropic
generation-date: 2026-08-08
generator-responsibility: implementation
```

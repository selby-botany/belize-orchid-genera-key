# A vegetative-first character system and feature → taxa index for the orchid genera of Belize

**Date:** 2026-08-07
**Status:** _Exploratory research_; **Only** use for further analysis.
**Scope:** 104 orchid genera recorded for Belize and the adjacent
Yucatán–Petén–Caribbean-slope region.
**Rank of analysis:** genus (species records are used only to estimate
within-genus state frequencies).
**Purpose:** specify an atomic, vegetative-first character space for the
orchid flora of Belize; publish the inverted `feature → taxa` index over it
with per-line confidence codes; define the observation model, encoding,
distance, clustering, pattern-mining, and Bayesian key-construction
pipeline that consumes it; and state the data-acquisition plan, readiness
status, and the decisions that require botanical governance.
**Summary:** Consolidated specification and working
index, prepared for botanical review. Every morphological index line in §8
is a confidence-coded hypothesis awaiting primary-source verification, not
an established datum; §8.1 and §20 state exactly what is and is not data.

---

## Introduction

This document serves as an exploration of the potential key construction features (character), their data types, and potential analytic treatments.

The document’s construction process involved a common prompt processed by seven distinct commercial large language models (LLMs) and subsequently synthesized into a final document by another LLM. The document explicitly states the sources available online that were utilized as source material. Additionally, several significant sources are identified that are not publicly accessible.

It is important to note that the prompt itself is quite leading, so the “exploration space” beyond the prompt is not considered.

Furthermore, the choice was made to employ the language and analytic treatments of [Jost](https://www.researchgate.net/profile/Lou-Jost). The botanical statements and treatments are subject to review by a botanist and are “above the pay grade” of the volunteer.

### What the document is:

- An **exploratory** attempt to identify the feature space of the problem.
- The product of a retired software engineer volunteer with **no training in botany**, but decades of experience with machine learning.
- A **very preliminary** exploration of analytic treatments that are believed to be relevant.

### What this document is NOT

- It is NOT a **normative** feature construction
- It is NOT a software **specification**:
    - It is NOT a **requirements** specification
    - It is NOT a **use case** specification
    - It is NOT a **design** specification
    - It is NOT a **implementation** specification

---

## Contents

- [A vegetative-first character system and feature → taxa index for the orchid genera of Belize](#a-vegetative-first-character-system-and-feature→-taxa-index-for-the-orchid-genera-of-belize)
  - [Introduction](#introduction)
    - [What the document is:](#what-the-document-is)
    - [What this document is NOT](#what-this-document-is-not)
  - [Contents](#contents)
  - [1. The field problem and product constraints](#1-the-field-problem-and-product-constraints)
    - [1.1 Why vegetative-first](#1-1-why-vegetative-first)
    - [1.2 The non-negotiable product constraint](#1-2-the-non-negotiable-product-constraint)
    - [1.3 Evidence layers](#1-3-evidence-layers)
    - [1.4 Three products, not one artifact](#1-4-three-products-not-one-artifact)
  - [2. Scope](#2-scope)
    - [2.1 Operational geographic scopes](#2-1-operational-geographic-scopes)
    - [2.2 Taxon concepts, not name strings](#2-2-taxon-concepts-not-name-strings)
    - [2.3 The working genus list and its known problems](#2-3-the-working-genus-list-and-its-known-problems)
  - [3. Observation model](#3-observation-model)
    - [3.1 Five levels](#3-1-five-levels)
    - [3.2 The atomic observation record](#3-2-the-atomic-observation-record)
    - [3.3 Variable classes](#3-3-variable-classes)
    - [3.4 Observation status: the facts a null value hides](#3-4-observation-status-the-facts-a-null-value-hides)
    - [3.5 Applicability is a directed acyclic graph](#3-5-applicability-is-a-directed-acyclic-graph)
    - [3.6 A genus is a hierarchical distribution, not a value](#3-6-a-genus-is-a-hierarchical-distribution-not-a-value)
    - [3.7 Observation burden is a vector](#3-7-observation-burden-is-a-vector)
    - [3.8 Uncertainty types](#3-8-uncertainty-types)
  - [4. Design principles for an atomic character space](#4-design-principles-for-an-atomic-character-space)
    - [4.1 The atomicity test](#4-1-the-atomicity-test)
    - [4.2 Entity–quality decomposition](#4-2-entity–quality-decomposition)
    - [4.3 Redundancy is a feature to be measured, not avoided](#4-3-redundancy-is-a-feature-to-be-measured-not-avoided)
    - [4.4 Identification and classification are different objectives](#4-4-identification-and-classification-are-different-objectives)
  - [5. The character dictionary: 218 characters in 12 facets](#5-the-character-dictionary-218-characters-in-12-facets)
    - [5.1 Facet ARCH — growth architecture and shoot organization](#5-1-facet-arch—-growth-architecture-and-shoot-organization)
    - [5.2 Facet STEM — stem and pseudobulb](#5-2-facet-stem—-stem-and-pseudobulb)
    - [5.3 Facet SHTH — sheaths, cataphylls, and bracts](#5-3-facet-shth—-sheaths-cataphylls-and-bracts)
    - [5.4 Facet LARR — leaf arrangement and attachment](#5-4-facet-larr—-leaf-arrangement-and-attachment)
    - [5.5 Facet LFRM — leaf blade form and geometry](#5-5-facet-lfrm—-leaf-blade-form-and-geometry)
    - [5.6 Facet LSUR — leaf surface, texture, indumentum, colour](#5-6-facet-lsur—-leaf-surface-texture-indumentum-colour)
    - [5.7 Facet ROOT — roots and underground organs](#5-7-facet-root—-roots-and-underground-organs)
    - [5.8 Facet SIZE — whole-plant size and allometry](#5-8-facet-size—-whole-plant-size-and-allometry)
    - [5.9 Facet REMN — persistent reproductive remains (layer R)](#5-9-facet-remn—-persistent-reproductive-remains-layer-r)
    - [5.10 Facet ECOL — habitat, substrate, and behaviour](#5-10-facet-ecol—-habitat-substrate-and-behaviour)
    - [5.11 Facet MICR — micromorphology and anatomy (layer L)](#5-11-facet-micr—-micromorphology-and-anatomy-layer-l)
    - [5.12 Facet FLOR — floral refinement layer (layer F)](#5-12-facet-flor—-floral-refinement-layer-layer-f)
    - [5.13 Facet totals](#5-13-facet-totals)
  - [6. Subatomic field-measurement layer](#6-subatomic-field-measurement-layer)
    - [6.1 Purpose and naming](#6-1-purpose-and-naming)
    - [6.2 Completeness target](#6-2-completeness-target)
    - [6.3 The field-measurable minimum set](#6-3-the-field-measurable-minimum-set)
      - [Growth and renewal (`S-GRO`, `S-RHZ`)](#growth-and-renewal-s-gro-s-rhz)
      - [Pseudobulb (`S-PBL`)](#pseudobulb-s-pbl)
      - [Cane and ramicaul (`S-CAN`)](#cane-and-ramicaul-s-can)
      - [Sheaths (`S-SHT`) — the Pleurothallidinae signal lives here](#sheaths-s-sht—-the-pleurothallidinae-signal-lives-here)
      - [Leaf insertion and abscission (`S-LAT`)](#leaf-insertion-and-abscission-s-lat)
      - [Blade geometry (`S-LGE`)](#blade-geometry-s-lge)
      - [Blade surface and mechanics (`S-LSF`)](#blade-surface-and-mechanics-s-lsf)
      - [Roots and underground organs (`S-ROT`, `S-UND`)](#roots-and-underground-organs-s-rot-s-und)
      - [Size, remains, ecology, context](#size-remains-ecology-context)
    - [6.4 Scale of the space](#6-4-scale-of-the-space)
    - [6.5 Mapping between layers (selected)](#6-5-mapping-between-layers-selected)
  - [7. Measurement protocols for high-value organs](#7-measurement-protocols-for-high-value-organs)
    - [7.1 General rules](#7-1-general-rules)
    - [7.2 Pseudobulb geometry](#7-2-pseudobulb-geometry)
    - [7.3 Lepanthiform sheath (×10 lens)](#7-3-lepanthiform-sheath×-10-lens)
    - [7.4 Blade shape without shape words](#7-4-blade-shape-without-shape-words)
    - [7.5 Texture and fracture](#7-5-texture-and-fracture)
    - [7.6 Rosette terrestrials (the Cranichideae attack)](#7-6-rosette-terrestrials-the-cranichideae-attack)
    - [7.7 Persistent inflorescence scars](#7-7-persistent-inflorescence-scars)
  - [8. Inverted index: feature → genera](#8-inverted-index-feature→-genera)
    - [8.1 How to read this section](#8-1-how-to-read-this-section)
    - [8.2 Group names used in this index](#8-2-group-names-used-in-this-index)
    - [8.3 ARCH-01 — Growth form](#8-3-arch-01—-growth-form)
    - [8.4 STEM-01 — Principal stem type](#8-4-stem-01—-principal-stem-type)
    - [8.5 STEM-14 — Pseudobulb arrangement](#8-5-stem-14—-pseudobulb-arrangement)
    - [8.6 STEM-10 / STEM-11 — Hollow pseudobulb and ant occupancy](#8-6-stem-10-stem-11—-hollow-pseudobulb-and-ant-occupancy)
    - [8.7 STEM-13 — Pseudobulb clothing at maturity](#8-7-stem-13—-pseudobulb-clothing-at-maturity)
    - [8.8 STEM-05 — Pseudobulb outline (partial; derived from S-PBL geometry)](#8-8-stem-05—-pseudobulb-outline-partial-derived-from-s-pbl-geometry)
    - [8.9 LARR-01 — Leaves per mature shoot](#8-9-larr-01—-leaves-per-mature-shoot)
    - [8.10 LFRM-02 — Ptyxis (vernation)](#8-10-lfrm-02—-ptyxis-vernation)
    - [8.11 LARR-04 — Leaf articulation with the sheath](#8-11-larr-04—-leaf-articulation-with-the-sheath)
    - [8.12 LFRM-03 — Blade cross-section](#8-12-lfrm-03—-blade-cross-section)
    - [8.13 LARR-03 — Phyllotaxy](#8-13-larr-03—-phyllotaxy)
    - [8.14 SHTH-01 — Stem and ramicaul sheath type](#8-14-shth-01—-stem-and-ramicaul-sheath-type)
    - [8.15 SHTH-14 — Persistent sheath ladder](#8-15-shth-14—-persistent-sheath-ladder)
    - [8.16 LSUR-01 — Blade texture, broad classes](#8-16-lsur-01—-blade-texture-broad-classes)
    - [8.17 LSUR-04 / LSUR-05 — Leaf and stem indumentum](#8-17-lsur-04-lsur-05—-leaf-and-stem-indumentum)
    - [8.18 LSUR-10 — Leaf variegation](#8-18-lsur-10—-leaf-variegation)
    - [8.19 LSUR-02 — Adaxial lustre](#8-19-lsur-02—-adaxial-lustre)
    - [8.20 LFRM-12 — Venation pattern](#8-20-lfrm-12—-venation-pattern)
    - [8.21 LFRM-08 — Apex minutely tridenticulate](#8-21-lfrm-08—-apex-minutely-tridenticulate)
    - [8.22 ROOT-12 / ROOT-13 — Root and underground storage organs](#8-22-root-12-root-13—-root-and-underground-storage-organs)
    - [8.23 Remaining inversions](#8-23-remaining-inversions)
      - [ARCH-05 — shoot spacing](#arch-05—-shoot-spacing)
      - [LARR-05 — leaf duration](#larr-05—-leaf-duration)
      - [ECOL-01 — substrate](#ecol-01—-substrate)
      - [REMN-02 — position of the inflorescence scar](#remn-02—-position-of-the-inflorescence-scar)
      - [REMN-04 — old rachis architecture (partial)](#remn-04—-old-rachis-architecture-partial)
      - [SIZE-01 — mature plant height](#size-01—-mature-plant-height)
      - [ECOL-11 — forest formation, specialists only](#ecol-11—-forest-formation-specialists-only)
    - [8.24 Residual-attack lines (subatomic layer)](#8-24-residual-attack-lines-subatomic-layer)
      - [S-LAT-05 — abscission geometry](#s-lat-05—-abscission-geometry)
      - [S-RPR-01 — scar position refinements](#s-rpr-01—-scar-position-refinements)
      - [S-ECO — host and formation priors](#s-eco—-host-and-formation-priors)
      - [S-CAN-07 — ramicaul annulus](#s-can-07—-ramicaul-annulus)
    - [8.25 Assertions queued for early verification](#8-25-assertions-queued-for-early-verification)
    - [8.26 Coverage of this index](#8-26-coverage-of-this-index)
  - [9. Measured genus-level elevation envelopes](#9-measured-genus-level-elevation-envelopes)
    - [9.1 Method](#9-1-method)
    - [9.2 Caveats that govern use](#9-2-caveats-that-govern-use)
    - [9.3 The envelopes](#9-3-the-envelopes)
  - [10. Demonstration: a hand-built vegetative group key](#10-demonstration-a-hand-built-vegetative-group-key)
    - [10.1 Ground rules](#10-1-ground-rules)
    - [10.2 The key](#10-2-the-key)
    - [10.3 Group register](#10-3-group-register)
    - [10.4 What the demonstration shows, in effective numbers](#10-4-what-the-demonstration-shows-in-effective-numbers)
    - [10.5 Residual budget: where effort buys α reduction](#10-5-residual-budget-where-effort-buysα-reduction)
  - [11. Smallest volumes, diagnostic bundles, and vegetative terminal units](#11-smallest-volumes-diagnostic-bundles-and-vegetative-terminal-units)
    - [11.1 What "smallest volume" means here](#11-1-what-smallest-volume-means-here)
    - [11.2 Worked diagnostic bundles](#11-2-worked-diagnostic-bundles)
    - [11.3 Minimum-cost diagnoses as hitting sets](#11-3-minimum-cost-diagnoses-as-hitting-sets)
    - [11.4 VTU declaration is governance-gated](#11-4-vtu-declaration-is-governance-gated)
    - [11.5 The hardest group, named in advance](#11-5-the-hardest-group-named-in-advance)
  - [12. Encoding, provenance, and the prototype-03 data contract](#12-encoding-provenance-and-the-prototype-03-data-contract)
    - [12.1 The source of truth is long-form](#12-1-the-source-of-truth-is-long-form)
    - [12.2 Provenance minimum on every morphological assertion](#12-2-provenance-minimum-on-every-morphological-assertion)
    - [12.3 The term lexicon](#12-3-the-term-lexicon)
    - [12.4 Quantitative storage](#12-4-quantitative-storage)
    - [12.5 File contract for prototype-03](#12-5-file-contract-for-prototype-03)
  - [13. Distance measures](#13-distance-measures)
    - [13.1 There is no single "orchid distance"](#13-1-there-is-no-single-orchid-distance)
    - [13.2 Block-balanced mixed dissimilarity](#13-2-block-balanced-mixed-dissimilarity)
    - [13.3 Per-variable dissimilarities](#13-3-per-variable-dissimilarities)
    - [13.4 Inapplicability algebra (non-negotiable)](#13-4-inapplicability-algebra-non-negotiable)
    - [13.5 Two weight families that never mix](#13-5-two-weight-families-that-never-mix)
    - [13.6 The shape plane](#13-6-the-shape-plane)
    - [13.7 Validating a distance measure](#13-7-validating-a-distance-measure)
  - [14. Clustering and structure discovery](#14-clustering-and-structure-discovery)
    - [14.1 What clustering is for](#14-1-what-clustering-is-for)
    - [14.2 Sequence](#14-2-sequence)
    - [14.3 Evaluation](#14-3-evaluation)
    - [14.4 Supervised companions](#14-4-supervised-companions)
  - [15. Frequent sets, closed sets, and diagnoses](#15-frequent-sets-closed-sets-and-diagnoses)
    - [15.1 Multiple formal contexts](#15-1-multiple-formal-contexts)
    - [15.2 Formal concept analysis](#15-2-formal-concept-analysis)
    - [15.3 Stability filters before acceptance](#15-3-stability-filters-before-acceptance)
    - [15.4 Implications as a data-quality instrument](#15-4-implications-as-a-data-quality-instrument)
  - [16. Bayesian adaptive key in effective-number currency](#16-bayesian-adaptive-key-in-effective-number-currency)
    - [16.1 Generative model](#16-1-generative-model)
    - [16.2 Dependence](#16-2-dependence)
    - [16.3 Priors](#16-3-priors)
    - [16.4 Observer model](#16-4-observer-model)
    - [16.5 Residual uncertainty as effective numbers](#16-5-residual-uncertainty-as-effective-numbers)
    - [16.6 Question selection as multiplicative diversity partitioning](#16-6-question-selection-as-multiplicative-diversity-partitioning)
    - [16.7 Policy graph, constraints, robustness](#16-7-policy-graph-constraints-robustness)
    - [16.8 Stopping, abstention, and the printable export](#16-8-stopping-abstention-and-the-printable-export)
    - [16.9 The q-profile requirement](#16-9-the-q-profile-requirement)
  - [17. Validation](#17-validation)
    - [17.1 Leakage-resistant test units](#17-1-leakage-resistant-test-units)
    - [17.2 Reference set](#17-2-reference-set)
    - [17.3 Metrics](#17-3-metrics)
    - [17.4 Comparative baselines](#17-4-comparative-baselines)
    - [17.5 Deterministic and auditable analysis](#17-5-deterministic-and-auditable-analysis)
  - [18. Source register and governance](#18-source-register-and-governance)
    - [18.1 Register](#18-1-register)
      - [Tier A — generic circumscription (authoritative for genus-level states)](#tier-a—-generic-circumscription-authoritative-for-genus-level-states)
      - [Tier A-R — regional literature (substantially Spanish)](#tier-a-r—-regional-literature-substantially-spanish)
      - [Tier B — anatomy and micromorphology](#tier-b—-anatomy-and-micromorphology)
      - [Tier C — nomenclature and distribution only](#tier-c—-nomenclature-and-distribution-only)
      - [Tier D — aggregators and leads (verify before use)](#tier-d—-aggregators-and-leads-verify-before-use)
    - [18.2 Claim-specific authority](#18-2-claim-specific-authority)
    - [18.3 The institutional advantage](#18-3-the-institutional-advantage)
    - [18.4 Language coverage as a data-quality signal](#18-4-language-coverage-as-a-data-quality-signal)
  - [19. Data acquisition and implementation path](#19-data-acquisition-and-implementation-path)
    - [19.1 Order of work](#19-1-order-of-work)
    - [19.2 Scoring protocol](#19-2-scoring-protocol)
    - [19.3 Phases](#19-3-phases)
    - [19.4 Week-1 executable package](#19-4-week-1-executable-package)
  - [20. Readiness scorecard](#20-readiness-scorecard)
  - [21. Risks, open questions, and governance inputs](#21-risks-open-questions-and-governance-inputs)
    - [21.1 Risks](#21-1-risks)
    - [21.2 Open questions for the botanist](#21-2-open-questions-for-the-botanist)
    - [21.3 Governance inputs algorithms must not invent](#21-3-governance-inputs-algorithms-must-not-invent)
    - [21.4 Evidence boundaries](#21-4-evidence-boundaries)
  - [22. References](#22-references)
  - [Prompt](#prompt)
  - [Metadata](#metadata)
    - [Reseach](#reseach)
    - [Synthesis](#synthesis)

---

## 1. The field problem and product constraints

### 1.1 Why vegetative-first

Orchid generic taxonomy is built almost entirely on flowers. Field
encounters are not. In any given month most individuals of most species
are sterile, and a key that requires anthesis is therefore unusable for
most plants most of the time. Regional experience makes the point
concrete: Dressler's field guide for the adjacent Costa Rican and
Panamanian flora was written explicitly around features "readily seen with
the naked eye or a hand lens" because that is what an encounter actually
offers (Dressler 1993b).

The product is a genus-level identification system for Belize and
surrounding areas that:

1. prefers vegetative morphology;
2. uses persistent reproductive remains only when they are actually
   present on the plant;
3. treats floral and laboratory characters as optional refinements; and
4. returns honest multi-genus answers when vegetative evidence cannot
   support a single genus.

### 1.2 The non-negotiable product constraint

> Every *required* path through the primary key must terminate using only
> evidence available on a living, non-flowering plant (layer V), or on
> persistent reproductive remains *actually present* on that plant
> (layer R). Flowers (layer F) and laboratory anatomy (layer L) may refine
> a result; they may never be required to obtain the best defensible
> vegetative identification.

"Terminate" includes honest multi-genus answers. Forcing a single genus
where vegetative evidence cannot support one makes the key more decisive
and less correct. The honest terminal objects are:

| Terminal object | Meaning |
| --- | --- |
| Single genus | Calibrated posterior and confirmatory blocks support one concept |
| Vegetative terminal unit (VTU) | An adequately sampled vegetative model cannot separate the members (§11.4) |
| Temporary candidate set | Missing observations prevent resolution; more questions remain |
| Out of scope | All modeled genera fit poorly; rejection, not forced assignment |

### 1.3 Evidence layers

| Layer | Content | Required in the primary key? |
| --- | --- | --- |
| V | Living vegetative organs and growth architecture | Yes |
| R | Persistent reproductive traces: old axes, scars, bracts, capsules | Only when the trace is actually present |
| F | Current flowers or fresh inflorescences | No; optional refinement |
| L | Destructive, microscopic, chemical, or laboratory observations | No; research and difficult-case refinement |

Persistent old inflorescences are valuable out-of-bloom evidence — a dried
rachis persists for months or years, and its emergence point, branching,
and bract arrangement are generically diagnostic — but they are
reproductive evidence, not vegetative morphology. Keeping layer R separate
prevents an "out-of-bloom" key from quietly requiring an old rachis that a
juvenile or recently damaged plant lacks.

The character tables in §5 also carry a **default field profile** (Tier 1:
naked-eye, non-destructive; Tier 2: ×10 lens, handling, or a season's
observation; Tier 3: floral, anatomical, or laboratory). The tier is a
one-dimensional summary of the observation-burden vector of §3.7, kept
because it is convenient in print; the vector, not the tier, is what the
question policy consumes.

### 1.4 Three products, not one artifact

| Product | Role |
| --- | --- |
| Interactive adaptive key (policy graph) | Primary product; any order, skips, uncertainty, images, context |
| Printable single-access key | Constrained export; stable wording, minimal equipment, controlled duplication |
| Diagnostic cards | Short redundant bundles for confirming a proposed genus, with confusers and optional floral refinements |

A printable couplet tree is an export of the system, not the system.

---

## 2. Scope

### 2.1 Operational geographic scopes

"Belize and surrounding areas" needs a reproducible boundary. Three nested
scopes are stored rather than one informal region:

| Scope ID | Boundary | Purpose |
| --- | --- | --- |
| `BZ` | Belize political boundary | Primary field product and occurrence prior |
| `YPBP` | Yucatán Peninsula Biotic Province (Carnevali et al. 2001) | Principal biogeographic expansion; includes Belize and the Petén |
| `MESO` | Southern Mexico through adjacent Caribbean-slope Central America | Edge taxa and misleading-endemism checks |

Every occurrence record carries coordinates, coordinate uncertainty,
source, date, and the scope calculation used. A taxon is not deleted
because it is outside one boundary; its prior changes with the user's
location.

Belize elevation consequence: the country's highest point (Doyle's
Delight, Maya Mountains) is ≈1,124 m. Inside `BZ` the elevation band
`>1400 m` is structurally empty and `900–1400 m` is rare (Maya Mountains
summits only). Regional matrices keep the higher bands for the Guatemalan
and Chiapan margins of `YPBP` and `MESO`.

### 2.2 Taxon concepts, not name strings

Generic circumscriptions have changed substantially in Pleurothallidinae,
Maxillariinae, Oncidiinae, and other groups. Each modeled genus therefore
requires: accepted name and author; a stable taxon identifier where
available; an `accordingTo` source defining the concept; included regional
species; excluded or ambiguous species; synonyms with sources; the date of
reconciliation; and the classification release against which the key was
built. A key version identifies taxon concepts, not bare labels:
reassigning one species can change a genus's state distribution and must
trigger a matrix rebuild. Name resolution uses a dated WCVP/IPNI bulk
snapshot, not an unversioned web query.

### 2.3 The working genus list and its known problems

The working list contains 104 genera. It has not yet been taxonomically
reconciled, and one problem is already known: the species recorded in the
project's survey under *Andreettaea* do not match that genus's usual
circumscription, which suggests transfers recorded under the wrong genus.
Reconciliation against Flora Mesoamericana vol. 7(2) and the Yucatán
synopsis (Carnevali et al. 2001) is a hard gate before scoring begins
(§19, Phase 0). A key to the wrong genera is worse than no key.

The classification baseline proposed for release 1 is Chase et al. (2015),
with Flora Mesoamericana overrides logged; whether that or a traditional
broader circumscription should govern is an open question for the botanist
(§21.2, question 1), and it changes *Pleurothallis* and *Maxillaria*
substantially — and with them, the answer to "how many genera are there."

---

## 3. Observation model

### 3.1 Five levels

"Atomic" is not one thing. The system distinguishes five levels, and the
distinction is what prevents the same measurement from being counted
several times under different names:

| Level | Name | Definition | Example |
| --- | --- | --- | --- |
| L−1 | Landmark / signal | Coordinate, pixel region, or instrument sample on one organ at one time | Caliper reading at 50% blade length; sheath-margin photo region |
| L0 | Subatomic measurement | One protocolized instrument reading or coded elementary state | `S-LGE-02` blade width at widest point (mm) |
| L1 | Atomic observation | One entity × one quality × one method (may be a controlled judgment) | `leaf blade × cross-section × naked-eye = terete` |
| L2 | Character (matrix variable) | Versioned, gated variable used in models and keys; raw or derived | `LFRM-03` blade cross-section; `LFRM-05` length÷width |
| L3 | Question | User-facing wording, diagrams, answer map, and burden for a user class | "Is the leaf round in cross-section like a pencil, or flattened?" |

Rules (the anti-pseudoreplication law):

1. L−1/L0/L1 are the evidence store. L2 is a model view. L3 is an
   interface view.
2. Derived L2 variables never enter a distance or likelihood beside their
   parents as independent evidence.
3. Changing L3 wording does not create a new character; changing an L2
   definition invalidates affected scores and forces a version bump.
4. Outline labels (lanceolate, ovoid, fusiform, …) are **derived** from
   geometry, never free-scored for analysis.
5. Syndromes (e.g., the lepanthiform sheath) are derived from component
   scores, not scored as opaque binaries.
6. An L1 judgment without a written protocol is not yet a character.

### 3.2 The atomic observation record

```text
O = (organism, entity, quality, value, method, context, evidence, status)
```

A record must pass all of: one organism or explicitly defined aggregate;
one anatomical entity; one quality or measurement; one method and unit;
one developmental and environmental context; one value representation;
evidence that can be found again; and an observation status (§3.4).

"Leaves leathery and lanceolate" fails: it combines a texture judgment and
an outline label, and it names no organ measurements. The passing record
set is blade length, width, widest-point position, thickness, bending
response, and the source's own wording preserved verbatim.

### 3.3 Variable classes

| Code | Meaning | Analysis rule |
| --- | --- | --- |
| R | Raw observation or measurement | Primary data |
| D | Derived deterministically from raw parents | Compute once; never score independently |
| J | Controlled human judgment with a scoring protocol | Model observer disagreement |
| C | Encounter context (place, host, date) | Conditions priors and availability, not inherited morphology |
| L | Laboratory or microscopic | Layer L only |
| F | Floral refinement | Layer F only |
| Q | Question object | Versioned separately from the biology |

### 3.4 Observation status: the facts a null value hides

One overloaded null is unacceptable. A cell carries exactly one status:

| Status | Meaning |
| --- | --- |
| `scored` | A value or probability distribution was recorded under protocol |
| `absent` | The structure is genuinely absent, and that absence is itself the state ("pseudobulb: absent") |
| `inapplicable` | The parent structure does not exist, so the question is meaningless (pseudobulb shape in *Stelis*); computed from gates, not asserted by hand |
| `not_examined` | Could have been observed but was not checked |
| `not_visible` | Present or possibly present but hidden in the current view |
| `obscured` | Substrate, damage, epiphyte load, decay, or overlap prevents scoring |
| `temporarily_unavailable` | Seasonal or developmental absence |
| `method_unavailable` | Required equipment, handling, or permission is absent |
| `conflicting` | Sources or repeated observations disagree and remain unresolved |
| `unknown` | Evidence insufficient to choose a more specific status |
| `variable` | Explicit polymorphism at the stated rank; store the distribution, never a single pick |
| `legacy_unverified` | Imported hypothesis awaiting source adjudication (§8.1) |

Inapplicable ≠ missing ≠ absent ≠ variable. Collapsing any pair is a data
defect of the same rank as a wrong state. The distinction is standard in
morphological systematics (Maddison 1993; Strong & Lipscomb 1999; Brazeau
et al. 2019) and matters here for a practical reason: a key that asks "is
the pseudobulb ribbed?" of a plant with no pseudobulb has wasted the
user's most expensive resource, their patience.

Only `scored` (and `absent`, where absence is a declared state of a
presence character) contributes a morphological value. The availability
statuses inform the question policy and the coverage report.

### 3.5 Applicability is a directed acyclic graph

Characters have gates, not a single parent string. A character may require
the entity to exist, the entity to be mature, a preceding state, a minimum
observation method, a suitable season or hydration state, or permission
for manipulation. Gates are Boolean expressions over prior observations;
validation rejects cycles and any child state reachable when its entity is
absent.

**Presence characters are always separate from property characters.**
STEM-02 asks whether a pseudobulb exists; STEM-05 asks its outline and is
applicable only when STEM-02 is `present`. Merging them into one character
with an "absent" state destroys the applicability structure and inflates
distances between pseudobulbless taxa and everything else.

### 3.6 A genus is a hierarchical distribution, not a value

At genus rank most characters are polymorphic. Representing *Epidendrum* —
some 1,500 species spanning reed-stems, pseudobulbs, terete leaves and
flat ones — by a single modal state throws away the fact that the genus is
*diagnostically* variable. Evidence is kept at the level collected:

```text
observation → individual → population → species → taxon concept
```

with source, geography, season, developmental stage, and cultivated/wild
status as cross-cutting fields. Genus-level cells are posterior summaries
over that hierarchy, not hand-entered adjectives. Estimators, in priority
order:

| Estimator | When |
| --- | --- |
| hierarchical posterior | Specimen or species data exist |
| `species-proportion` | Regional species scored, no abundance model |
| `abundance-weighted` | Only with a separately audited encounter prior |
| `expert-uniform` | A monograph gives a range without frequencies — **flagged**: "leaves 1–3" is not necessarily equally often 1, 2, and 3 |
| `monomorphic` | Source and specimens agree on one state |

The hierarchy preserves the difference between one unusual individual
photographed many times, a polymorphic species, several species with
different fixed states, and a source that says "variable" without counts.
Occurrence frequency must never be used both as a state-likelihood weight
and as the genus prior; that counts prevalence twice.

Three consequences, all wanted: distances become distributional (§13);
the key becomes Bayesian (§16) — observing "cane stem" raises the
posterior on *Epidendrum* without excluding it when a pseudobulb is seen;
and a genus may legitimately appear at more than one leaf of a printed
key (§16.8).

### 3.7 Observation burden is a vector

A single "easy/hard" tier cannot represent the difference between a
flower (easy but usually unavailable) and root anatomy (persistent but
difficult). Each character carries:

| Field | Values |
| --- | --- |
| `equipment` | none / ruler / ×10 lens / macro camera / microscope / laboratory |
| `manipulation` | none / reorient / detach dead material / remove living tissue |
| `damage` | none / reversible / minor / destructive |
| `time_seconds` | measured distribution, not "easy/hard" |
| `expertise` | novice / naturalist / orchid specialist / anatomist |
| `availability` | empirical P(observable on a random field encounter) |
| `persistence` | days / season / years / permanent on mature growth |
| `repeatability` | within- and between-observer agreement |
| `access` | ground / reachable trunk / canopy or hazardous |
| `lighting_sensitivity` | none / moderate / standardized light required |
| `hydration_sensitivity` | none / affects state / valid only when hydrated |
| `source_fillability` | fraction of taxa scoreable from admissible published evidence |
| `taxon_reliability` | reliability of this character in this particular taxon |

Question cost is user- and situation-specific:

```text
C(q, u, z) = time + equipment + expertise + access + damage + error risk
```

where `u` is the user profile and `z` the field context. The key must not
ask a novice to assess velamen anatomy merely because the observation is
persistent. `source_fillability` is not a field cost: a laboratory
character can be unusable on a live key path yet nearly complete in
published comparative data, making it useful for structure discovery.
Per-(taxon, character) reliability is needed because the same question can
be obvious in one genus and ambiguous in another — a capability already
recognized in the DELTA system (Dallwitz 1980).

### 3.8 Uncertainty types

| Type | Encoding |
| --- | --- |
| State uncertainty | The observer cannot distinguish `acute` from `acuminate`: a distribution or allowed set over states |
| Parameter uncertainty | Only two species examined: retain the posterior around the genus frequency |
| Source uncertainty | A secondary site paraphrases a protologue: record source class and verification state, not a fabricated probability |
| Taxon uncertainty | The voucher identification is itself uncertain: do not train as though the label were certain |
| Observer uncertainty | P(report \| truth, method, user class), estimated from trials (§16.4) |

---

## 4. Design principles for an atomic character space

### 4.1 The atomicity test

A character is atomic when it satisfies all four conditions:

1. **Single entity.** It describes exactly one anatomical structure.
   "Leaf or pseudobulb oblong" fails.
2. **Single quality.** It describes exactly one property of that
   structure — one of shape, size, texture, colour, count, orientation,
   surface, or position. "Coriaceous and lanceolate" fails; that is two
   characters.
3. **Exhaustive, mutually exclusive states.** Every taxon to which the
   character applies takes at least one state, and states do not overlap.
   A taxon may take several states only through polymorphism (§3.6),
   never through ambiguity in the state definitions.
4. **Independently observable.** Scoring it does not require having
   already scored another character, except through a declared
   applicability gate (§3.5).

A flat bag of adjectives — `coriaceous`, `oblong`, `erect`, `terete` —
fails all four at once, because the organ each adjective belongs to has
been discarded: `oblong` may describe the pseudobulb or the leaf, and
without the entity the assertion cannot be checked against anything.

### 4.2 Entity–quality decomposition

Each character is written as an entity–quality (EQ) pair, following the
annotation pattern used for plant phenotypes (Phenoscape; Hoehndorf et al.
2016): the **entity** is an anatomical structure, ideally a Plant Ontology
term; the **quality** a property, ideally a PATO term. The entity is part
of the character's identity.

| Facet | Principal entity | Example EQ |
| --- | --- | --- |
| ARCH | shoot system, rhizome | `rhizome` × `internode length` |
| STEM | stem, pseudobulb | `pseudobulb` × `number of internodes` |
| SHTH | cataphyll, sheath, bract | `stem sheath` × `ornamentation` |
| LARR | leaf, phyllotaxy | `leaf` × `arrangement along stem` |
| LFRM | leaf blade | `leaf blade` × `ptyxis` |
| LSUR | leaf epidermis | `leaf epidermis` × `trichome density` |
| ROOT | root, tuberoid | `root` × `velamen presence` |
| SIZE | whole plant | `whole plant` × `height` |
| REMN | inflorescence axis, fruit | `inflorescence axis` × `persistence` |
| ECOL | whole plant, habitat | `whole plant` × `substrate` |
| MICR | tissue, cell | `leaf mesophyll` × `silica body presence` |
| FLOR | flower parts | deferred; layer F |

Ontology term identifiers are deferred but the character IDs are stable,
so `po_term` / `pato_term` columns can be added without renumbering.
Ontology annotation buys interoperability and lexicon alignment; it does
not automatically provide a numerical distance (§13.3).

### 4.3 Redundancy is a feature to be measured, not avoided

Vegetative characters are heavily correlated — pseudobulb presence, leaf
count, leaf texture, and habit all covary. Correlated characters inflate
distances (the same signal counted several times) but *stabilize*
identification (a user who misreads one still routes correctly on the
others). The pipeline measures redundancy explicitly — conditional
association between characters, and attribute implications from the
concept lattice (§15.4) — rather than pruning it away. Structure discovery
uses redundancy-corrected weighting; the key generator does not, and
deliberately retains redundant confirmatory characters at high-risk nodes
(§16.7).

### 4.4 Identification and classification are different objectives

A character can be excellent for *identification* and useless for
*classification*: growth habit is wildly homoplastic across the family yet
superb for keying, because it is consistent within most genera and visible
from three meters away. Conversely, phylogenetically clean characters can
be unscoreable in the field. Two weight families therefore exist and must
never mix (§13.5): discovery weights (organ balance, optional phylogenetic
signal) for clustering, and cost/reliability weights for the key. A
vegetative key is not obliged to mirror the classification, and a
clustering that fails to recover some subtribes is reporting vegetative
homoplasy, not necessarily a bug (§14.3).

---

## 5. The character dictionary: 218 characters in 12 facets

Column key: **Type** — `bin` binary, `nom` nominal, `ord` ordinal, `qnt`
quantitative, `set` multistate set. **T** — default field profile (tier,
§1.3). **O/P/C** — observability (3 naked eye at arm's length … 0
laboratory), persistence (3 year-round on any mature plant … 0 brief),
scoring cost (1 free … 3 destructive or laboratory); these three are the
print summary of the burden vector of §3.7. **App** — applicability gate:
the named character must be in the named state for this one to apply.

Two derived scoring axes exist per character but are not printed here
because they are outputs of the first analysis pass, not assignments:
within-genus stability (1 − normalized entropy of the state distribution,
averaged over genera) and phylogenetic reliability (from ancestral-state
reconstruction where available, e.g. Bogarín et al. 2019). They feed the
two weight families of §13.5.

Sources given per facet apply to the character concepts and terminology;
per-cell sources for state assignments are recorded separately (§12).

Quantitative characters are stored as log₁₀ mm intervals with a typical
value (§12.4); the bands printed here are key-export conveniences.

### 5.1 Facet ARCH — growth architecture and shoot organization

Concept sources: Dressler 1993a, 1993b; Karremans 2016; Bogarín et al.
2019; Watson & Dallwitz (DELTA).

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARCH-01 | Growth form | bin | sympodial / monopodial | 1 | 3 | 3 | 1 | — |
| ARCH-02 | Shoot determinacy | bin | determinate / indeterminate | 1 | 3 | 3 | 1 | — |
| ARCH-03 | Rhizome development | nom | not evident / short / elongate | 1 | 3 | 3 | 1 | ARCH-01 sympodial |
| ARCH-04 | Rhizome internode length ÷ shoot diameter | ord | <1 / 1–3 / >3 | 1 | 2 | 3 | 1 | ARCH-03 ≠ not evident |
| ARCH-05 | Shoot spacing | nom | caespitose / shortly repent / long-repent | 1 | 3 | 3 | 1 | ARCH-01 sympodial |
| ARCH-06 | Rhizome orientation | nom | appressed-creeping / ascending / pendent | 1 | 3 | 3 | 1 | ARCH-03 ≠ not evident |
| ARCH-07 | Rhizome cross-section | nom | terete / flattened / angled | 2 | 2 | 3 | 1 | ARCH-03 ≠ not evident |
| ARCH-08 | Rhizome covering | nom | naked / scarious sheaths / fibrous net | 2 | 2 | 3 | 1 | ARCH-03 ≠ not evident |
| ARCH-09 | New shoot origin | nom | base of previous shoot / apex of previous pseudobulb / mid-stem node | 1 | 2 | 3 | 1 | ARCH-01 sympodial |
| ARCH-10 | Shoot branching above the base | bin | absent / present | 1 | 3 | 3 | 1 | — |
| ARCH-11 | Plant attitude | nom | erect / spreading / arcuate / pendent / scandent | 1 | 3 | 3 | 1 | — |
| ARCH-12 | Climbing mechanism | nom | none / adventitious clasping roots / scrambling | 1 | 3 | 3 | 1 | — |
| ARCH-13 | Growth periodicity | bin | continuous / seasonally arrested | 2 | 1 | 1 | 2 | — |
| ARCH-14 | Clone architecture | nom | compact clump / diffuse mat / straggling | 1 | 3 | 3 | 1 | — |
| ARCH-15 | Active growths per rhizome apex | ord | 1 / >1 | 2 | 2 | 2 | 1 | ARCH-01 sympodial |
| ARCH-16 | Shoot base swelling | bin | absent / present | 2 | 2 | 3 | 1 | — |
| ARCH-17 | Ramicaul present (Pleurothallidinae sense) | bin | absent / present | 1 | 3 | 3 | 1 | — |
| ARCH-18 | Annulus on ramicaul | bin | absent / present | 2 | 1 | 3 | 2 | ARCH-17 present |
| ARCH-19 | Shoot cross-section | nom | terete / laterally compressed / ancipitous / angled | 1 | 2 | 3 | 1 | — |
| ARCH-20 | Shoot surface relief | nom | smooth / sulcate / ridged / verrucose | 2 | 2 | 3 | 1 | — |
| ARCH-21 | Stolons or runners bearing distant shoots | bin | absent / present | 2 | 3 | 3 | 1 | — |
| ARCH-22 | Vegetative plantlets (keikis) on stems | bin | absent / present | 2 | 3 | 2 | 1 | — |
| ARCH-23 | Basal equitant fan organization | bin | absent / present | 1 | 3 | 3 | 1 | — |
| ARCH-24 | Whole-plant symmetry | nom | radial rosette / bilateral fan / linear distichous shoot / irregular clump | 1 | 3 | 3 | 1 | — |

### 5.2 Facet STEM — stem and pseudobulb

Concept sources: Pridgeon et al. (*Genera Orchidacearum*); Dressler 1993a,
1993b; Watson & Dallwitz.

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| STEM-01 | Principal stem type | nom | pseudobulb / cane / ramicaul / rosette (no aerial stem) / leaf fan / underground corm or tuber | 1 | 3 | 3 | 1 | ARCH-01 sympodial |
| STEM-02 | Pseudobulb present | bin | absent / present | 1 | 3 | 3 | 1 | — |
| STEM-03 | Pseudobulb internode number | nom | 1 (heteroblastic) / 2–3 / >3 (homoblastic) | 1 | 2 | 3 | 1 | STEM-02 present |
| STEM-04 | Visible node or sheath scars on pseudobulb | ord | 0 / 1–2 / >2 | 2 | 2 | 3 | 1 | STEM-02 present |
| STEM-05 | Pseudobulb outline (derived from S-PBL geometry) | nom | globose / ovoid / pyriform / conical / cylindric / fusiform / clavate / discoid | 1 | 3 | 3 | 1 | STEM-02 present |
| STEM-06 | Pseudobulb cross-section | nom | terete / laterally compressed / 4-angled / ancipitous | 1 | 2 | 3 | 1 | STEM-02 present |
| STEM-07 | Pseudobulb ribbing | nom | smooth / sulcate only when dehydrated / permanently ribbed | 1 | 2 | 3 | 1 | STEM-02 present |
| STEM-08 | Pseudobulb surface lustre | nom | matte / glossy / glaucous-pruinose | 2 | 2 | 3 | 1 | STEM-02 present |
| STEM-09 | Pseudobulb consistency | ord | hard-woody / firm-fleshy / soft-fleshy | 2 | 1 | 3 | 1 | STEM-02 present |
| STEM-10 | Pseudobulb interior | bin | solid / hollow | 1 | 1 | 3 | 2 | STEM-02 present |
| STEM-11 | Ant occupancy of hollow stem | bin | absent / present | 1 | 3 | 3 | 1 | STEM-10 hollow |
| STEM-12 | Basal ostium (ant entrance) | bin | absent / present | 2 | 2 | 3 | 1 | STEM-10 hollow |
| STEM-13 | Pseudobulb clothing at maturity | nom | naked / persistent papery sheaths / fibrous sheath net / spiny persistent leaf bases | 1 | 3 | 3 | 1 | STEM-02 present |
| STEM-14 | Pseudobulb arrangement | nom | clustered / spaced on rhizome / superposed | 1 | 3 | 3 | 1 | STEM-02 present |
| STEM-15 | Pseudobulb orientation | nom | erect / spreading / pendent | 1 | 3 | 3 | 1 | STEM-02 present |
| STEM-16 | Pseudobulb length ÷ width | qnt | continuous, banded 1–2 / 2–4 / 4–8 / >8 | 1 | 2 | 3 | 1 | STEM-02 present |
| STEM-17 | Pseudobulb length | qnt | mm, banded | 1 | 2 | 3 | 1 | STEM-02 present |
| STEM-18 | Pseudobulb apex | nom | leaf-bearing / naked / beaked | 2 | 2 | 2 | 1 | STEM-02 present |
| STEM-19 | Cane rigidity | nom | rigid-woody / firm / flexible-herbaceous | 2 | 1 | 3 | 1 | STEM-01 cane |
| STEM-20 | Cane thickening profile | nom | uniform / basal / median (fusiform) / apical | 1 | 2 | 3 | 1 | STEM-01 cane |
| STEM-21 | Cane node count | ord | <5 / 5–15 / >15 | 2 | 2 | 3 | 1 | STEM-01 cane |
| STEM-22 | Cane internode swelling at nodes | bin | absent / present | 2 | 2 | 3 | 1 | STEM-01 cane |
| STEM-23 | Underground storage organ | nom | none / corm / tuberoid / thickened rhizome only | 1 | 1 | 3 | 3 | — |
| STEM-24 | Depth of underground organ | nom | at surface / buried | 2 | 1 | 3 | 3 | STEM-23 ≠ none |
| STEM-25 | Stem pigmentation | nom | green / purple-suffused / spotted | 2 | 3 | 2 | 1 | — |
| STEM-26 | Stem indumentum | nom | glabrous / papillose / pubescent / hispid | 2 | 2 | 3 | 1 | — |
| STEM-27 | Exudate on cutting | nom | watery / mucilaginous | 3 | 1 | 3 | 3 | — |
| STEM-28 | Old pseudobulb persistence | nom | persistent several years / shrivels within a year | 2 | 2 | 2 | 1 | STEM-02 present |

Scoring rules for STEM-01:

- **Perennating-organ rule.** Score STEM-01 by the organ that persists
  through the unfavorable season, not the most conspicuous organ at
  anthesis. Consequently *Habenaria*, *Bletia*, and *Eulophia* — all
  terrestrial geophytes whose leafy aerial shoot is seasonal — score
  `underground corm or tuber`; the seasonal leafy shoot is captured by
  ARCH and LARR characters, not STEM-01.
- **Monopodial plants are `inapplicable`.** A monopodial plant has no
  "principal stem type" among sympodial alternatives; its stem is
  described by ARCH and LARR characters. The gate makes both
  *Campylocentrum* and *Vanilla* structurally `inapplicable`; *Vanilla*'s
  climbing habit is carried by ARCH-01 monopodial + ARCH-11 scandent +
  ARCH-12 clasping roots, which already isolate it in two observations
  (§11.2). A former `climbing stem` state, reachable only by *Vanilla*,
  is dropped as unreachable under the gate.
- The `leaf fan` state covers genera whose shoot is an equitant or
  imbricating fan without a pseudobulb; the boundary between
  `underground corm or tuber` and a corm-like pseudobulb at the soil
  surface (*Liparis*, *Malaxis*) must be written into the state
  definitions when Flora Mesoamericana is read (§8.25).

### 5.3 Facet SHTH — sheaths, cataphylls, and bracts

Concept sources: Karremans 2016; Bogarín et al. 2019 (ramicaul bract
states); Dressler 1993b.

This facet carries far more generic signal in Pleurothallidinae than its
size suggests. Bogarín et al. (2019) found ramicaul bract ornamentation
phylogenetically informative in the *Lepanthes* clade while several floral
characters were homoplastic — a direct counterexample to the assumption
that floral characters are always the better ones.

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SHTH-01 | Stem/ramicaul sheath type (lepanthiform is derived from S-SHT components) | nom | absent / plain tubular / lepanthiform / spathaceous / foliaceous | 1 | 2 | 3 | 1 | — |
| SHTH-02 | Lepanthiform ostium margin | nom | entire / ciliate / dilated and thickened | 2 | 1 | 3 | 2 | SHTH-01 lepanthiform |
| SHTH-03 | Sheath ribbing | bin | smooth / longitudinally ribbed | 2 | 1 | 3 | 2 | SHTH-01 ≠ absent |
| SHTH-04 | Sheath surface | nom | glabrous / papillose / muricate / hirsute | 2 | 1 | 3 | 2 | SHTH-01 ≠ absent |
| SHTH-05 | Sheaths per shoot | ord | 1 / 2–3 / >3 | 2 | 2 | 3 | 1 | SHTH-01 ≠ absent |
| SHTH-06 | Sheath persistence | nom | caducous / persistent papery / persistent fibrous | 1 | 3 | 3 | 1 | SHTH-01 ≠ absent |
| SHTH-07 | Sheath imbrication | bin | separated / imbricating | 2 | 2 | 3 | 1 | SHTH-01 ≠ absent |
| SHTH-08 | Sheath texture | nom | scarious / chartaceous / foliaceous | 2 | 2 | 3 | 1 | SHTH-01 ≠ absent |
| SHTH-09 | Sheath colour | nom | hyaline / straw / brown / purple-spotted | 2 | 2 | 2 | 1 | SHTH-01 ≠ absent |
| SHTH-10 | Cataphylls at shoot base | ord | 0 / 1–2 / >2 | 2 | 2 | 3 | 1 | — |
| SHTH-11 | Spathe subtending inflorescence | nom | absent / one / several | 2 | 2 | 2 | 1 | — |
| SHTH-12 | Spathe persistence when dry | bin | caducous / persistent | 2 | 2 | 2 | 1 | SHTH-11 ≠ absent |
| SHTH-13 | Leaf sheath closure | bin | open / closed (tubular) | 2 | 1 | 3 | 2 | — |
| SHTH-14 | Leaf-sheath persistence after leaf fall | bin | absent / persistent as a ladder of sheaths | 1 | 3 | 3 | 1 | — |
| SHTH-15 | Sheath margin fimbriate | bin | absent / present | 2 | 1 | 3 | 2 | SHTH-01 ≠ absent |
| SHTH-16 | Sheath keel | bin | absent / carinate | 2 | 1 | 3 | 2 | SHTH-01 ≠ absent |

### 5.4 Facet LARR — leaf arrangement and attachment

Concept sources: Watson & Dallwitz (arrangement, articulation); Dressler
1993a, 1993b.

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LARR-01 | Leaves per mature shoot | ord | 0 / 1 / 2 / 3–5 / >5 | 1 | 3 | 3 | 1 | — |
| LARR-02 | Leaf insertion | nom | apical / along the stem / basal rosette | 1 | 3 | 3 | 1 | LARR-01 ≠ 0 |
| LARR-03 | Phyllotaxy | nom | distichous / spiral / equitant / rosulate | 1 | 3 | 3 | 1 | LARR-01 ≠ 0 |
| LARR-04 | Leaf articulation with sheath | bin | articulated / not articulated | 1 | 2 | 3 | 1 | LARR-01 ≠ 0 |
| LARR-05 | Leaf duration | bin | evergreen / seasonally deciduous | 1 | 2 | 1 | 1 | LARR-01 ≠ 0 |
| LARR-06 | Leaf base | nom | sessile / petiolate / conduplicate-petiolate / sheathing | 1 | 2 | 3 | 1 | LARR-01 ≠ 0 |
| LARR-07 | Petiole length ÷ blade length | qnt | continuous, banded | 2 | 2 | 3 | 1 | LARR-06 petiolate |
| LARR-08 | Petiole channelled | bin | flat / conduplicate-channelled | 2 | 2 | 3 | 1 | LARR-06 petiolate |
| LARR-09 | Leaf attitude | nom | erect / spreading / arcuate / pendent / reflexed | 1 | 3 | 3 | 1 | LARR-01 ≠ 0 |
| LARR-10 | Leaf base overlap | bin | free / imbricating | 1 | 3 | 3 | 1 | LARR-01 ≥ 2 |
| LARR-11 | Blade borne edgewise to the stem | bin | no / yes (unifacial) | 1 | 3 | 3 | 1 | LARR-01 ≠ 0 |
| LARR-12 | Blade twisted at the base | bin | absent / present | 2 | 2 | 3 | 1 | LARR-01 ≠ 0 |
| LARR-13 | Internode length ÷ blade length | qnt | continuous, banded | 2 | 2 | 3 | 1 | LARR-02 along stem |
| LARR-14 | Abscission scar visible on sheath | bin | absent / present | 2 | 1 | 3 | 2 | LARR-04 articulated |
| LARR-15 | Leaf distribution along stem | nom | evenly spaced / clustered at apex / clustered at base | 1 | 3 | 3 | 1 | LARR-02 along stem |
| LARR-16 | Opposite or subopposite leaf pairs | bin | absent / present | 2 | 3 | 3 | 1 | LARR-01 ≥ 2 |

### 5.5 Facet LFRM — leaf blade form and geometry

Concept sources: Watson & Dallwitz (vernation, venation); Systematics
Association Committee (1962) shape grid; Dressler 1993b; Karremans 2016.

LFRM-05 and LFRM-06 together define the shape-space embedding of §13.4.
LFRM-04 is retained as a human-readable label but is *derived* from them
and must never be scored independently.

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LFRM-01 | Blade present | bin | absent / present | 1 | 3 | 3 | 1 | — |
| LFRM-02 | Ptyxis (vernation) | nom | conduplicate / plicate / convolute | 1 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-03 | Blade cross-section | nom | flat / channelled / V-folded / terete / subterete / laterally compressed / dorsiventrally thickened | 1 | 3 | 3 | 1 | LFRM-01 present |
| LFRM-04 | Blade outline label (derived) | nom | linear / ligulate / lanceolate / oblanceolate / elliptic / oblong / ovate / obovate / orbicular / subulate | 1 | 3 | 3 | 1 | LFRM-01 present |
| LFRM-05 | Blade length ÷ width | qnt | continuous, log-scaled | 1 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-06 | Position of widest point (fraction from base) | qnt | 0–1 continuous | 1 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-07 | Blade apex | nom | acute / acuminate / obtuse / rounded / emarginate / bilobed / tridenticulate / mucronate / aristate | 1 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-08 | Apex tridenticulate (derived from S-LGE-08 components) | bin | absent / present | 1 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-09 | Blade margin | nom | entire / undulate / crenulate / serrulate / ciliate / revolute | 2 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-10 | Blade base | nom | cuneate / attenuate / rounded / cordate / auriculate / clasping | 2 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-11 | Blade symmetry | bin | symmetric / oblique or falcate | 2 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-12 | Venation pattern | nom | obscure / midvein only / few prominent parallel veins / many parallel veins / reticulate | 1 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-13 | Primary vein count | ord | 1 / 3–5 / 6–10 / >10 | 2 | 2 | 3 | 1 | LFRM-12 ≠ obscure |
| LFRM-14 | Midvein prominence abaxially | nom | flush / raised / keeled | 2 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-15 | Cross-venules visible | bin | absent / present | 3 | 1 | 3 | 2 | LFRM-01 present |
| LFRM-16 | Blade thickness | qnt | mm, banded | 1 | 1 | 3 | 1 | LFRM-01 present |
| LFRM-17 | Blade length | qnt | mm, banded | 1 | 3 | 3 | 1 | LFRM-01 present |
| LFRM-18 | Blade width | qnt | mm, banded | 1 | 3 | 3 | 1 | LFRM-01 present |
| LFRM-19 | Blade curvature | nom | flat / falcate / sigmoid / recurved | 2 | 3 | 3 | 1 | LFRM-01 present |
| LFRM-20 | Blade twisted along its axis | bin | absent / present | 2 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-21 | Blade carinate (keeled) | bin | absent / present | 2 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-22 | Blade transversely rugose | bin | absent / present | 2 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-23 | Fleshiness index (thickness ÷ width) | qnt | derived from LFRM-16, LFRM-18 | 2 | 1 | 3 | 1 | LFRM-01 present |
| LFRM-24 | Blade rigidity | ord | rigid / firm / flexible / limp | 2 | 1 | 3 | 1 | LFRM-01 present |
| LFRM-25 | Blade constricted below apex | bin | absent / present | 2 | 2 | 3 | 1 | LFRM-01 present |
| LFRM-26 | Blade dimorphism between shoots | bin | absent / present | 3 | 2 | 2 | 2 | LFRM-01 present |

### 5.6 Facet LSUR — leaf surface, texture, indumentum, colour

Concept sources: Watson & Dallwitz (texture states); Karremans 2016;
Pleurothallidinae anatomical literature.

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LSUR-01 | Blade texture (pair with LFRM-16 thickness and S-LSF-09 fracture) | ord | membranaceous / chartaceous / herbaceous / coriaceous / carnose / rigid-succulent | 1 | 2 | 3 | 1 | LFRM-01 present |
| LSUR-02 | Adaxial lustre | nom | matte / glossy / glaucous-pruinose | 1 | 3 | 3 | 1 | LFRM-01 present |
| LSUR-03 | Bloom removable by rubbing | bin | no / yes | 2 | 1 | 3 | 1 | LSUR-02 glaucous |
| LSUR-04 | Adaxial indumentum | nom | glabrous / papillose / pubescent / hirsute / scurfy | 1 | 2 | 3 | 1 | LFRM-01 present |
| LSUR-05 | Abaxial indumentum | nom | glabrous / papillose / pubescent / hirsute / scurfy | 1 | 2 | 3 | 1 | LFRM-01 present |
| LSUR-06 | Marginal cilia | bin | absent / present | 2 | 1 | 3 | 2 | LFRM-01 present |
| LSUR-07 | Surface verruculose or muricate | bin | absent / present | 2 | 1 | 3 | 2 | LFRM-01 present |
| LSUR-08 | Adaxial colour | nom | mid green / dark green / yellow-green / blue-green / purple-suffused | 2 | 3 | 2 | 1 | LFRM-01 present |
| LSUR-09 | Abaxial colour | nom | concolorous / purple / maroon-spotted | 1 | 2 | 2 | 1 | LFRM-01 present |
| LSUR-10 | Variegation pattern | nom | absent / silver-reticulate / median stripe / marbled / spotted | 1 | 3 | 3 | 1 | LFRM-01 present |
| LSUR-11 | Colour pattern durability | bin | ontogenetic / durable | 2 | 2 | 2 | 1 | LSUR-10 ≠ absent |
| LSUR-12 | Adaxial purple spotting | bin | absent / present | 2 | 3 | 2 | 1 | LFRM-01 present |
| LSUR-13 | Translucent margin | bin | absent / present | 2 | 1 | 3 | 2 | LFRM-01 present |
| LSUR-14 | Transverse wrinkling when dehydrated | bin | absent / present | 2 | 2 | 1 | 1 | LFRM-01 present |
| LSUR-15 | Extrafloral nectaries or pearl glands | bin | absent / present | 2 | 1 | 2 | 2 | LFRM-01 present |
| LSUR-16 | Stomata visible at ×10 | bin | no / yes | 3 | 0 | 3 | 2 | LFRM-01 present |
| LSUR-17 | Papillae in longitudinal rows | bin | absent / present | 3 | 0 | 3 | 2 | LFRM-01 present |
| LSUR-18 | Anthocyanin flush in exposed plants | bin | absent / present | 2 | 3 | 1 | 1 | LFRM-01 present |
| LSUR-19 | Blade brittle when bent | bin | pliable / brittle | 2 | 1 | 3 | 2 | LFRM-01 present |
| LSUR-20 | Odour of crushed tissue | nom | none / grassy / resinous / fetid | 3 | 1 | 3 | 3 | LFRM-01 present |

### 5.7 Facet ROOT — roots and underground organs

Concept sources: Porembski & Barthlott 1988 (velamen syndromes,
tilosomes); Watson & Dallwitz (velamen presence); Dressler 1993a.

Roots are the most under-used vegetative organ in orchid keys, and often
highly informative — but they are **not** always available. Roots may be
invisible, lost, reduced, obscured by substrate, or subterranean only.
Root visibility is therefore scored first (S-ROT-01, §6), and root
characters are treated as high-value when visible, never as universal.

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ROOT-01 | Root habit | nom | aerial clinging / free-hanging / in humus / subterranean | 1 | 3 | 3 | 1 | roots visible |
| ROOT-02 | Velamen | bin | absent / present | 1 | 2 | 3 | 1 | roots visible |
| ROOT-03 | Velamen thickness | ord | thin / moderate / thick | 3 | 0 | 3 | 3 | ROOT-02 present |
| ROOT-04 | Root diameter | qnt | mm, banded | 1 | 2 | 3 | 1 | roots visible |
| ROOT-05 | Root cross-section | nom | terete / flattened where appressed | 1 | 2 | 3 | 1 | roots visible |
| ROOT-06 | Root branching | ord | unbranched / sparse / dense | 1 | 2 | 3 | 1 | roots visible |
| ROOT-07 | Root surface | nom | smooth / hairy / warty | 1 | 2 | 3 | 1 | roots visible |
| ROOT-08 | Root apex colour | nom | green / white / purple | 2 | 2 | 2 | 1 | roots visible |
| ROOT-09 | Roots photosynthetic | bin | no / yes | 1 | 3 | 3 | 1 | roots visible |
| ROOT-10 | Roots the dominant photosynthetic organ | bin | no / yes (shootless habit) | 1 | 3 | 3 | 1 | LFRM-01 absent |
| ROOT-11 | Root origin | nom | rhizome only / pseudobulb base / stem nodes / along whole stem | 1 | 3 | 3 | 1 | roots visible |
| ROOT-12 | Fleshy fascicled tuberous roots | bin | absent / present | 1 | 2 | 3 | 2 | — |
| ROOT-13 | Tuberoid | bin | absent / present | 1 | 1 | 2 | 3 | — |
| ROOT-14 | Tuberoid shape | nom | ovoid / fusiform / digitate | 2 | 1 | 2 | 3 | ROOT-13 present |
| ROOT-15 | Dense root hairs (felted) | bin | absent / present | 2 | 1 | 3 | 2 | roots visible |
| ROOT-16 | Mycorrhizal pelotons in section | bin | absent / present | 3 | 0 | 3 | 3 | — |
| ROOT-17 | Velamen syndrome sensu Porembski & Barthlott | nom | 12 named types | 3 | 0 | 3 | 3 | ROOT-02 present |
| ROOT-18 | Tilosomes | nom | absent / lamellate / spongy / discoid / other | 3 | 0 | 3 | 3 | ROOT-02 present |
| ROOT-19 | Adherence to substrate | ord | free / loosely attached / tightly appressed | 1 | 3 | 3 | 1 | roots visible |
| ROOT-20 | Inflorescences borne on roots | bin | absent / present | 2 | 2 | 1 | 1 | roots visible |

### 5.8 Facet SIZE — whole-plant size and allometry

Concept sources: Dressler 1993b; horticultural size classes given explicit
numeric bounds so they stop being a matter of opinion.

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SIZE-01 | Mature plant height | ord | mini-miniature <3 cm / miniature 3–10 / small 10–25 / medium 25–60 / large 60–150 / giant >150 | 1 | 3 | 3 | 1 | ARCH-11 ≠ scandent |
| SIZE-02 | Blade length ÷ shoot length | qnt | continuous | 1 | 2 | 3 | 1 | LFRM-01 present |
| SIZE-03 | Blade area | qnt | cm², log-scaled | 2 | 2 | 3 | 1 | LFRM-01 present |
| SIZE-04 | Shoot diameter | qnt | mm, banded | 2 | 2 | 3 | 1 | — |
| SIZE-05 | Clump diameter | qnt | cm, banded | 2 | 3 | 2 | 1 | — |
| SIZE-06 | Within-genus size variability | ord | narrow / moderate / wide | 2 | 1 | 3 | 1 | — |
| SIZE-07 | Blade length vs shoot length allometric slope | qnt | derived | 3 | 0 | 3 | 1 | — |
| SIZE-08 | Pseudobulb length ÷ blade length | qnt | continuous | 1 | 2 | 3 | 1 | STEM-02 present |

The SIZE-01 gate makes scandent plants structurally `inapplicable`:
*Vanilla* vines run many meters and "mature plant height" has no stable
value there. Its size is carried by SIZE-04 shoot diameter and LFRM-17
blade length, which are stable.

### 5.9 Facet REMN — persistent reproductive remains (layer R)

Concept sources: Dressler 1993b; Karremans 2016; Bogarín et al. 2019
(inflorescence position; successive vs simultaneous flowering).

This entire facet is **layer R**: scoreable only when remains are actually
present, and never silently required on a key path. When present, a dried
inflorescence axis is among the most diagnostic evidence a sterile plant
offers — where it emerges, whether it passed through a spathe, whether the
rachis zig-zags from successive flowering, whether floral bracts are
conspicuous and distichous.

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REMN-01 | Old inflorescence axis persistence | nom | not persistent / one season / several seasons | 1 | 3 | 2 | 1 | remains present |
| REMN-02 | Position of inflorescence scar | nom | terminal on shoot / apex of pseudobulb / base of pseudobulb / stem node / leaf axil / rhizome | 1 | 2 | 2 | 1 | remains present |
| REMN-03 | Inflorescence emerges through a spathe | bin | no / yes | 1 | 2 | 2 | 1 | remains present |
| REMN-04 | Old rachis architecture | nom | single-flowered pedicel / fascicle / unbranched raceme / spike with imbricating bracts / panicle | 1 | 2 | 2 | 1 | REMN-01 ≠ not persistent |
| REMN-05 | Rachis zig-zag (successive flowering) | bin | absent / present | 1 | 2 | 2 | 1 | REMN-01 ≠ not persistent |
| REMN-06 | Persistent floral bracts | nom | minute / conspicuous / foliaceous | 1 | 2 | 2 | 1 | REMN-01 ≠ not persistent |
| REMN-07 | Bract arrangement | nom | distichous / spiral | 2 | 2 | 2 | 1 | REMN-06 ≠ minute |
| REMN-08 | Rachis length ÷ leaf length | qnt | continuous | 1 | 2 | 2 | 1 | REMN-01 ≠ not persistent |
| REMN-09 | Peduncle covering | nom | naked / bracteate / sheathed | 2 | 2 | 2 | 1 | REMN-01 ≠ not persistent |
| REMN-10 | Capsule shape and ribbing | nom | ellipsoid smooth / ellipsoid ribbed / fusiform / elongate-cylindric | 2 | 2 | 1 | 1 | capsule present |
| REMN-11 | Capsule persistence | bin | dehisces and falls / persists | 2 | 2 | 1 | 1 | capsule present |
| REMN-12 | Old inflorescence scars per shoot | ord | 0 / 1 / >1 (repeat-flowering) | 1 | 2 | 2 | 1 | remains present |

Absence of remains is never evidence: it must not be read as "flowers
basally" or "does not repeat-flower." The status is `not_visible` or
`temporarily_unavailable`, not a state.

### 5.10 Facet ECOL — habitat, substrate, and behaviour

Concept sources: Watson & Dallwitz (C3/CAM, epiphytic habit); occurrence
portals for the frequency prior.

ECOL-20 is not a morphological character; it is the **prior** in §16.3.
Without it a key spends decisions separating a genus of forty common
species from a genus known from one collection. Ecological states enter
the likelihood as distributions — never as hard filters that zero out a
genus.

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ECOL-01 | Substrate | nom | epiphyte / lithophyte / terrestrial / mycoheterotroph / climber on trees | 1 | 3 | 3 | 1 | — |
| ECOL-02 | Substrate breadth | ord | obligate / facultative / broad | 1 | 2 | 3 | 1 | — |
| ECOL-03 | Host bark texture preference | nom | none / smooth / rough / fissured | 2 | 2 | 3 | 1 | ECOL-01 epiphyte |
| ECOL-04 | Host taxon association | nom | none / oak / pine / mangrove / other | 2 | 2 | 3 | 1 | ECOL-01 epiphyte |
| ECOL-05 | Position on host | nom | trunk / major branch / outer twig | 1 | 3 | 3 | 1 | ECOL-01 epiphyte |
| ECOL-06 | Canopy stratum | nom | understory / midstory / exposed canopy | 1 | 3 | 3 | 1 | ECOL-01 epiphyte |
| ECOL-07 | Exposure | ord | deep shade / filtered / full sun | 1 | 3 | 3 | 1 | — |
| ECOL-08 | Moisture regime | ord | seasonally dry / mesic / everwet | 1 | 2 | 3 | 1 | — |
| ECOL-09 | Ant association | bin | absent / present | 1 | 3 | 3 | 1 | — |
| ECOL-10 | Elevation band | ord | 0–150 / 150–500 / 500–900 / 900–1400 / >1400 m | 1 | 3 | 3 | 1 | — |
| ECOL-11 | Forest formation | set | lowland broadleaf / submontane / montane / elfin / pine savanna / mangrove / karst scrub / riparian | 1 | 3 | 3 | 1 | — |
| ECOL-12 | Habitat seasonality | ord | strongly seasonal / intermediate / aseasonal | 1 | 2 | 3 | 1 | — |
| ECOL-13 | Photosynthetic pathway | bin | C3 / CAM | 3 | 0 | 3 | 3 | — |
| ECOL-14 | Colony habit | nom | solitary / small clumps / extensive mats | 1 | 3 | 3 | 1 | — |
| ECOL-15 | Association with substrate moss | bin | absent / usual | 1 | 3 | 3 | 1 | — |
| ECOL-16 | Fire tolerance | bin | intolerant / tolerant | 2 | 1 | 3 | 2 | — |
| ECOL-17 | Limestone or karst affinity | bin | indifferent / karst-associated | 1 | 2 | 3 | 1 | — |
| ECOL-18 | Riparian affinity | bin | indifferent / riparian | 1 | 2 | 3 | 1 | — |
| ECOL-19 | Disturbance tolerance | ord | intolerant / tolerant / weedy | 1 | 2 | 3 | 1 | — |
| ECOL-20 | Local frequency (Belize) | ord | very rare / rare / occasional / frequent / abundant | 1 | 1 | 3 | 2 | — |

ECOL-10 band rule for in-country use: inside Belize, `>1400 m` is
structurally empty and `900–1400 m` is rare (§2.1). The five bands stand
for the regional matrix.

### 5.11 Facet MICR — micromorphology and anatomy (layer L)

Concept sources: Porembski & Barthlott 1988; Watson & Dallwitz (stegmata,
silica bodies, raphides, stomatal type); Stern 2014; Pleurothallidinae and
*Bulbophyllum* anatomical exemplars.

Layer L throughout. These characters are the correct resolution for the
residual groups that vegetative macro-morphology cannot split (§11.4), and
the natural target for a later herbarium-based refinement pass. They are
never offered to a field user.

| ID | Character | Type | States | T | O | P | C | App |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MICR-01 | Stegmata (silica bodies) | nom | absent / conical / spherical / other | 3 | 0 | 3 | 3 | — |
| MICR-02 | Stomatal type | nom | anomocytic / paracytic / tetracytic | 3 | 0 | 3 | 3 | — |
| MICR-03 | Epidermal cell wall thickening | ord | thin / moderate / thick | 3 | 0 | 3 | 3 | — |
| MICR-04 | Hypodermis | bin | absent / present | 3 | 0 | 3 | 3 | — |
| MICR-05 | Water-storage tissue | bin | absent / present | 3 | 0 | 3 | 3 | — |
| MICR-06 | Fibre bundle distribution | nom | none / subepidermal / scattered | 3 | 0 | 3 | 3 | — |
| MICR-07 | Raphide idioblasts | bin | absent / present | 3 | 0 | 3 | 3 | — |
| MICR-08 | Spiral thickenings in mesophyll | bin | absent / present | 3 | 0 | 3 | 3 | — |
| MICR-09 | Cuticle thickness | ord | thin / moderate / thick | 3 | 0 | 3 | 3 | — |
| MICR-10 | Exodermis pattern | nom | uniform / dimorphic / with thickened cells | 3 | 0 | 3 | 3 | — |
| MICR-11 | Tracheoidal cortex | bin | absent / present | 3 | 0 | 3 | 3 | — |
| MICR-12 | Velamen cell wall ornamentation | nom | smooth / reticulate / spiral / other | 3 | 0 | 3 | 3 | ROOT-02 present |
| MICR-13 | Trichome type | nom | absent / unicellular / uniseriate / branched | 3 | 0 | 3 | 3 | — |
| MICR-14 | Crystal type | nom | none / raphides / styloids / druses | 3 | 0 | 3 | 3 | — |

### 5.12 Facet FLOR — floral refinement layer (layer F)

Concept sources: Pridgeon et al.; Karremans 2016; Bogarín et al. 2019.

Layer F by construction. These characters exist in the matrix so that
(a) the key can offer an optional refinement when a flower happens to be
present, and (b) the analysis can *quantify how much is lost* by excluding
them — the information difference between the vegetative-only and full
character spaces is the honest measure of what a vegetative key costs.
They never appear on a required path.

| ID | Character | Type | T |
| --- | --- | --- | --- |
| FLOR-01 | Inflorescence architecture | nom | 3 |
| FLOR-02 | Flower size | qnt | 3 |
| FLOR-03 | Resupination | bin | 3 |
| FLOR-04 | Lateral sepals connate into a synsepal | bin | 3 |
| FLOR-05 | Column foot | bin | 3 |
| FLOR-06 | Pollinium number | ord | 3 |
| FLOR-07 | Lip mobile on a hinge | bin | 3 |
| FLOR-08 | Spur or mentum | nom | 3 |
| FLOR-09 | Lip callus form | nom | 3 |
| FLOR-10 | Anther position | nom | 3 |
| FLOR-11 | Stipe and viscidium form | nom | 3 |
| FLOR-12 | Flower colour | nom | 3 |
| FLOR-13 | Fragrance | nom | 3 |
| FLOR-14 | Flowering season | set | 3 |

### 5.13 Facet totals

| Facet | Characters | Tier 1 | Tier 2 | Tier 3 |
| --- | ---: | ---: | ---: | ---: |
| ARCH | 24 | 15 | 9 | 0 |
| STEM | 28 | 15 | 12 | 1 |
| SHTH | 16 | 3 | 13 | 0 |
| LARR | 16 | 10 | 6 | 0 |
| LFRM | 26 | 12 | 12 | 2 |
| LSUR | 20 | 6 | 11 | 3 |
| ROOT | 20 | 12 | 4 | 4 |
| SIZE | 8 | 3 | 4 | 1 |
| REMN | 12 | 8 | 4 | 0 |
| ECOL | 20 | 16 | 3 | 1 |
| MICR | 14 | 0 | 0 | 14 |
| FLOR | 14 | 0 | 0 | 14 |
| **Total** | **218** | **100** | **78** | **40** |

100 Tier 1 characters against 104 genera is an appropriate ratio: enough
signal to separate genera many times over, few enough that a botanist can
review every one. For comparison, the character study closest to this
problem (Bogarín et al. 2019) scored 18 macro-morphological characters, of
which five were vegetative.

---

## 6. Subatomic field-measurement layer

### 6.1 Purpose and naming

The dictionary of §5 is the L2 model layer. Several of its characters are
still judgments that pack multiple independently measurable facts —
"blade texture," "apex tridenticulate," "pseudobulb fusiform." The `S-*`
variables below are the L0/L1 measurement layer that grounds them: every
row is executable in the field with ruler and ×10 lens, with no
living-tissue damage unless marked `damage=minor` and permitted. Outline
labels and syndromes are then **derived**, which is what makes observer
disagreement measurable instead of merely verbal.

| Prefix | Domain | Parent facets |
| --- | --- | --- |
| `S-GRO` | Growth architecture landmarks | ARCH |
| `S-RHZ` | Rhizome geometry | ARCH |
| `S-PBL` | Pseudobulb geometry and surface | STEM |
| `S-CAN` | Cane / ramicaul geometry | STEM, ARCH |
| `S-SHT` | Sheath and cataphyll field micromorphology | SHTH |
| `S-LAT` | Leaf insertion and abscission | LARR |
| `S-LGE` | Blade geometry landmarks | LFRM |
| `S-LSF` | Blade surface and mechanics | LSUR |
| `S-ROT` | Root macromorphology | ROOT |
| `S-UND` | Underground storage organs | STEM, ROOT |
| `S-SIZ` | Whole-plant metrics | SIZE |
| `S-RPR` | Persistent reproductive remains | REMN |
| `S-ECO` | Substrate and placement | ECOL |
| `S-CTX` | Season, damage, development | (new) |

Each `S-*` ID is an L0/L1 variable; mapping tables bind them to L2
characters (many-to-one, §6.5). An `S-*` variable never silently reuses an
L2 ID with a new meaning. Beyond this field minimum (~120 variables), a
wider pool of candidate variables exists for the same organ domains; new
candidates enter only through the versioned ontology process of §12, after
definition review, source-availability review, inter-observer testing, and
redundancy analysis.

### 6.2 Completeness target

A vegetative feature space adequate to this flora must cover every organ a
sterile plant can present: (1) clone architecture and renewal; (2) rhizome
and connectors; (3) aerial storage stem or its absence; (4) cane, ramicaul,
or rosette axis; (5) sheaths, cataphylls, spathes; (6) leaf number,
insertion, abscission; (7) blade geometry, venation, mechanics; (8)
surface, indumentum, colour pattern; (9) roots and velamen at field scale;
(10) underground storage when terrestrial; (11) size and allometry; (12)
persistent reproductive scars and axes; (13) substrate, host position,
hydrology; (14) developmental and damage context. A multi-genus residue
may not be declared irreducible (§11.4) until the variables below have
been attempted or gated for its members.

### 6.3 The field-measurable minimum set

Class codes R/D/J as in §3.3.

#### Growth and renewal (`S-GRO`, `S-RHZ`)

| ID | Class | Measurement / state | Unit or states | Gate |
| --- | --- | --- | --- | --- |
| S-GRO-01 | R | Attachment mode | epiphyte-attached / terrestrial-rooted / lithophyte / vine-climbing | plant visible |
| S-GRO-02 | R | Principal axis determinacy | determinate modules / indeterminate axis | ≥2 growth ages |
| S-GRO-03 | R | Renewal origin | basal / apical on prior module / nodal / root-borne | renewal visible |
| S-GRO-04 | R | Inter-shoot distance | mm between consecutive mature shoot bases | sympodial |
| S-GRO-05 | R | Active apices per clone front | count | clone visible |
| S-GRO-06 | R | Superposed renewal | absent / present | multiple ages |
| S-GRO-07 | R | Support dependence | self-supporting / scrambling / root-climbing / twining | plant visible |
| S-GRO-08 | R | Leafless photosynthetic habit | absent / present | mature plant |
| S-RHZ-01 | R | Rhizome mean internode length | mm | rhizome visible |
| S-RHZ-02 | R | Rhizome diameter | mm | rhizome visible |
| S-RHZ-03 | R | Rhizome cross-section class | terete / compressed / angled | rhizome visible |
| S-RHZ-04 | J | Rhizome covering | naked / scarious sheaths / fibrous net | rhizome visible |
| S-RHZ-05 | R | Rhizome attitude | appressed / ascending / pendent / subterranean | rhizome visible |

#### Pseudobulb (`S-PBL`)

| ID | Class | Measurement / state | Unit or states | Gate |
| --- | --- | --- | --- | --- |
| S-PBL-01 | R | Pseudobulb presence | absent / present | shoot mature |
| S-PBL-02 | R | Length | mm | present |
| S-PBL-03 | R | Maximum width | mm | present |
| S-PBL-04 | R | Width at 25%, 50%, 75% length | mm triple | present |
| S-PBL-05 | D | Length ÷ width; taper indices from S-PBL-04 | — | present |
| S-PBL-06 | R | Internode count (visible nodes / sheath scars) | count | present |
| S-PBL-07 | R | Cross-section class | terete / laterally compressed / 4-angled / ancipitous | present |
| S-PBL-08 | R | Ribbing | smooth / sulcate when dry / permanently ribbed | present |
| S-PBL-09 | J | Consistency | hard-woody / firm-fleshy / soft-fleshy | present; gentle compression |
| S-PBL-10 | R | Interior | solid / hollow (basal ostium or naturally broken old bulb only) | present; dead material preferred |
| S-PBL-11 | R | Basal ostium | absent / present | hollow or ant-plants |
| S-PBL-12 | R | Clothing at maturity | naked / papery sheaths / fibrous net / spiny leaf-base stubs | present |
| S-PBL-13 | R | Arrangement | clustered / rhizome-spaced / superposed | present |
| S-PBL-14 | R | Orientation | erect / spreading / pendent | present |
| S-PBL-15 | R | Apex condition | leaf-bearing / naked / beaked | present |

Outline labels (globose, ovoid, fusiform, clavate, …) are **derived** from
S-PBL-04/05, not free-scored for analysis.

#### Cane and ramicaul (`S-CAN`)

| ID | Class | Measurement / state | Unit or states | Gate |
| --- | --- | --- | --- | --- |
| S-CAN-01 | R | Axis type | none / cane / ramicaul / rosette axis / vine stem | shoot mature |
| S-CAN-02 | R | Axis length | mm | axis present |
| S-CAN-03 | R | Axis diameter at mid-length | mm | axis present |
| S-CAN-04 | R | Node count | count | cane/ramicaul |
| S-CAN-05 | R | Cross-section | terete / compressed / ancipitous / angled | axis present |
| S-CAN-06 | R | Surface relief | smooth / sulcate / ridged / verrucose | axis present |
| S-CAN-07 | R | Annulus on ramicaul | absent / present | ramicaul |
| S-CAN-08 | R | Thickening profile | uniform / basal / median / apical | cane |
| S-CAN-09 | J | Rigidity | woody / firm / flexible | cane |
| S-CAN-10 | R | Branching above base | absent / present | axis present |

#### Sheaths (`S-SHT`) — the Pleurothallidinae signal lives here

| ID | Class | Measurement / state | Unit or states | Gate |
| --- | --- | --- | --- | --- |
| S-SHT-01 | R | Sheaths per axis | count | axis present |
| S-SHT-02 | R | Sheath length | mm (mid-axis sheath) | sheath present |
| S-SHT-03 | R | Ostium diameter | mm | tubular sheath |
| S-SHT-04 | R | Ostium dilated relative to tube | no / yes | tubular sheath |
| S-SHT-05 | R | Longitudinal ribs | count at ×10 | sheath present |
| S-SHT-06 | J | Ostium margin | entire / ciliate / thickened-ciliate | ×10 |
| S-SHT-07 | J | Sheath surface | glabrous / papillose / muricate / hirsute | ×10 |
| S-SHT-08 | R | Imbrication | separated / imbricating | ≥2 sheaths |
| S-SHT-09 | R | Persistence after blade fall | caducous / papery persistent / fibrous / ladder | old axes |
| S-SHT-10 | R | Keel | absent / present | sheath present |
| S-SHT-11 | J | Texture class | scarious / chartaceous / foliaceous | sheath present |
| S-SHT-12 | D | Lepanthiform syndrome | absent / present — derived bundle of S-SHT-04..08 | components scored |

`S-SHT-12 = present` operationalizes `SHTH-01 = lepanthiform`: dilated
ostium + ribs + imbrication, with thickened/ciliate margin raising
confidence. Score the components; derive the syndrome.

#### Leaf insertion and abscission (`S-LAT`)

| ID | Class | Measurement / state | Unit or states | Gate |
| --- | --- | --- | --- | --- |
| S-LAT-01 | R | Leaves on mature shoot | count | shoot mature |
| S-LAT-02 | R | Insertion zone | apical / cauline / basal rosette | leaves ≥1 |
| S-LAT-03 | R | Phyllotaxy | distichous / spiral / equitant / rosulate | leaves ≥2 or equitant |
| S-LAT-04 | R | Abscission line present | no / yes | leaf or scar |
| S-LAT-05 | R | Distance sheath apex → abscission line | mm | articulated |
| S-LAT-06 | R | Petiole length | mm | petiole present |
| S-LAT-07 | R | Petiole channelled | no / yes | petiole present |
| S-LAT-08 | R | Leaf attitude | erect / spreading / arcuate / pendent / reflexed | leaf present |
| S-LAT-09 | R | Unifacial / edgewise blade | no / yes | leaf present |
| S-LAT-10 | R | Base twist | degrees, estimated 0 / 90 / 180 | leaf present |
| S-LAT-11 | R | Seasonal leaf loss | evergreen / deciduous | multi-season or sheath evidence |

#### Blade geometry (`S-LGE`)

Landmarks on a mature, undamaged blade: **B0** blade–petiole or
blade–sheath junction; **B1** widest point; **B2** apex (excluding a
freely articulated hair-point); **M** midvein track.

| ID | Class | Measurement | Notes |
| --- | --- | --- | --- |
| S-LGE-01 | R | Blade length B0–B2 | mm |
| S-LGE-02 | R | Blade width at B1 | mm |
| S-LGE-03 | R | Position of B1 as fraction of B0–B2 | 0–1 |
| S-LGE-04 | R | Width at 10%, 25%, 75%, 90% length | mm; shape without shape words |
| S-LGE-05 | R | Thickness at mid-blade | mm; calipers or comparator card |
| S-LGE-06 | R | Cross-section class | flat / channelled / V / terete / subterete / laterally compressed / dorsiventrally thickened |
| S-LGE-07 | R | Ptyxis on young leaf | conduplicate / plicate / convolute |
| S-LGE-08 | R | Apex components | sinus depth mm; mucro length mm; lobe/tooth count |
| S-LGE-09 | R | Margin class | entire / undulate / crenulate / serrulate / ciliate / revolute |
| S-LGE-10 | R | Base class | cuneate / attenuate / rounded / cordate / auriculate / clasping |
| S-LGE-11 | R | Primary vein count visible | count |
| S-LGE-12 | R | Venation pattern class | obscure / midvein / few-parallel / many-parallel / reticulate |
| S-LGE-13 | R | Midvein abaxial relief | flush / raised / keeled |
| S-LGE-14 | R | Falcation | straight / curved; sagitta mm optional |
| S-LGE-15 | D | Aspect ratio, fleshiness index, outline label | from S-LGE-01..05 |

"Tridenticulate apex" (LFRM-08) becomes three apical points with measured
central mucro and lateral tooth lengths under S-LGE-08, not an opaque
binary.

#### Blade surface and mechanics (`S-LSF`)

| ID | Class | Measurement / protocol | States or unit |
| --- | --- | --- | --- |
| S-LSF-01 | J | Texture ladder with bend test | membranaceous / chartaceous / herbaceous / coriaceous / carnose / rigid-succulent |
| S-LSF-02 | R | Adaxial lustre | matte / glossy / glaucous |
| S-LSF-03 | R | Glaucous bloom rubs off | no / yes |
| S-LSF-04 | R | Adaxial indumentum | glabrous / papillose / pubescent / hirsute / scurfy |
| S-LSF-05 | R | Abaxial indumentum | same states |
| S-LSF-06 | R | Indumentum density at ×10 | sparse / moderate / dense |
| S-LSF-07 | R | Variegation | absent / silver-reticulate / median stripe / marbled / spotted |
| S-LSF-08 | R | Abaxial anthocyanin | concolorous / purple / maroon-spotted |
| S-LSF-09 | J | Bend-fracture test | pliable / creases / snaps |
| S-LSF-10 | R | Transverse wrinkling when dry | absent / present |

Texture is a judgment: always pair S-LSF-01 with thickness S-LGE-05 and
fracture S-LSF-09 so the label can be audited.

#### Roots and underground organs (`S-ROT`, `S-UND`)

| ID | Class | Measurement | Gate |
| --- | --- | --- | --- |
| S-ROT-01 | R | Root visibility class | none visible / aerial clinging / free-hanging / in humus / subterranean only |
| S-ROT-02 | R | Mean root diameter 10 mm behind apex | mm; when visible |
| S-ROT-03 | R | Velamen apparent | no / yes (silvery sheath) |
| S-ROT-04 | R | Branching density | unbranched / sparse / dense |
| S-ROT-05 | R | Surface | smooth / hairy / warty |
| S-ROT-06 | R | Photosynthetic roots dominant | no / yes (shootless) |
| S-ROT-07 | R | Root origin | rhizome / bulb base / stem nodes / whole stem |
| S-ROT-08 | R | Adherence | free / loose / tight |
| S-UND-01 | R | Underground storage | none / corm / tuberoid / fleshy fascicled roots / thick rhizome |
| S-UND-02 | R | Storage depth | at surface / buried |
| S-UND-03 | R | Tuberoid shape | ovoid / fusiform / digitate |
| S-UND-04 | R | Fascicled root fleshiness | absent / present |

Destructive confirmation of hollow bulbs or buried tuberoids is optional
refinement, never a required path.

#### Size, remains, ecology, context

| ID range | Domain | Core measurements |
| --- | --- | --- |
| S-SIZ-01..06 | Size | plant height (`inapplicable` if scandent); clump diameter; shoot diameter; blade-area proxy; pseudobulb ÷ blade |
| S-RPR-01..08 | Remains | scar position (shoot apex / pseudobulb apex / pseudobulb base / rhizome / axillary); old rachis attitude; successive vs simultaneous scars; bract persistence; capsule presence |
| S-ECO-01..08 | Ecology | substrate; host organ (twig / branch / trunk / rock / soil); light class; hydrology; forest formation; elevation band |
| S-CTX-01..06 | Context | life stage; damage; epiphyte load; hydration; cultivated/wild; date |

### 6.4 Scale of the space

| Layer | Approximate count | Status |
| --- | --- | --- |
| Subatomic field minimum (§6.3) | ~120 variables | Normative pilot targets |
| Character dictionary (§5) | 218 | Baseline L2 namespace |
| Candidate expansion pool | several hundred | Intake-gated (§6.1); research superset |
| User-facing questions (L3) | far fewer than L2 | Selected by utility × availability |

The key never asks 120 questions. The space must be large so that (a)
clustering and pattern mining can discover which conjunctions actually
diagnose, and (b) hard residual groups have unused measurements left to
try before surrender.

### 6.5 Mapping between layers (selected)

| L2 character | Built from |
| --- | --- |
| ARCH-01 | S-GRO-02 + S-GRO-03 pattern |
| ARCH-05 | S-GRO-04 thresholds |
| STEM-01 | S-PBL-01, S-CAN-01, S-UND-01 with the perennating-organ rule (§5.2) |
| STEM-05 | derived from S-PBL-04/05 |
| STEM-10/11/12 | S-PBL-10/11 |
| STEM-13 | S-PBL-12 |
| STEM-14 | S-PBL-13 |
| SHTH-01 | S-SHT-12 syndrome from components |
| SHTH-14 | S-SHT-09 ladder state |
| LARR-01..05 | S-LAT-01..05, S-LAT-11 |
| LFRM-02..08, 12, 16–18 | S-LGE-* |
| LSUR-01..05, 10 | S-LSF-* |
| ROOT-12/13 | S-UND-01/03/04 |
| REMN-02 | S-RPR-01 |
| SIZE-01 | S-SIZ-01 with the scandent gate |
| ECOL-01, 10, 11 | S-ECO-* |

---

## 7. Measurement protocols for high-value organs

Protocols exist so that disagreement is about the plant, not about the
wording. Each protocol is mandatory before the linked character enters a
published key.

### 7.1 General rules

1. Prefer a mature, undamaged module from the current or previous season.
2. Record hydration (turgid / intermediate / shrivelled); many
   cross-section and ribbing states change with water.
3. Photograph a scale bar with every quantitative set used in validation.
4. If the organ is missing, score status `not_visible` or
   `temporarily_unavailable`, never a morphological state.
5. Spanish and English protocol sheets are dual-maintained; the original
   source wording stays in the evidence record even when the protocol is
   English.

### 7.2 Pseudobulb geometry

1. Select the newest fully hardened pseudobulb.
2. Measure length along the curvature midline (S-PBL-02).
3. Measure maximum width perpendicular to the midline (S-PBL-03).
4. Measure widths at 25/50/75% length (S-PBL-04).
5. Count visible nodes or persistent sheath scars (S-PBL-06).
6. Score cross-section at mid-length without squeezing (S-PBL-07).
7. Score clothing only on mature bulbs, not on sheathed new growth
   (S-PBL-12).
8. Hollow interior: prefer a natural basal ostium or a naturally broken
   old bulb; do not cut live tissue.

### 7.3 Lepanthiform sheath (×10 lens)

1. Use a mid-ramicaul sheath, not the basal cataphyll.
2. Count longitudinal ribs (S-SHT-05).
3. Compare ostium diameter to the tube diameter below (S-SHT-03/04).
4. At ×10, score margin cilia and thickening (S-SHT-06).
5. Score surface trichomes without scraping (S-SHT-07).
6. Derive the lepanthiform syndrome (S-SHT-12) only if dilated ostium AND
   ribs AND imbrication are present; margin thickening or cilia raise
   confidence.

### 7.4 Blade shape without shape words

1. Lay the blade flat; if terete or compressed, measure major/minor
   diameters instead of width.
2. Record S-LGE-01..04 before any outline label.
3. Apex: measure mucro and sinus; do not argue "acute vs acuminate"
   without numbers when the key depends on it.
4. Ptyxis: score only on an expanding leaf; never infer plicate from
   mature corrugation alone without a protocol note.

### 7.5 Texture and fracture

1. Thickness first (S-LGE-05).
2. Gentle fold at mid-blade away from the midvein (S-LSF-09): pliable /
   creases / snaps.
3. Assign S-LSF-01 from the joint rule table printed on the field card,
   not from free recollection of "coriaceous."

### 7.6 Rosette terrestrials (the Cranichideae attack)

1. Confirm absence of aerial pseudobulb and cane (S-PBL-01, S-CAN-01).
2. Count living leaves; measure petiole and blade separately.
3. Score variegation under standardized shade (S-LSF-07); photograph.
4. Without digging when possible: note root fleshiness at the soil
   interface (S-UND-04). Tuberoid confirmation is optional and
   destructive.
5. Record substrate, light, and season — ecological priors matter more
   here than in epiphyte groups.

### 7.7 Persistent inflorescence scars

1. Score only if a scar or old axis is actually present.
2. Locate emergence relative to pseudobulb apex, base, sheath axil, or
   rhizome (S-RPR-01).
3. Note whether the old rachis is erect, arcuate, or descends into the
   substrate.
4. Never treat absence of remains as evidence of basal vs apical
   flowering.

---

## 8. Inverted index: feature → genera

### 8.1 How to read this section

This is the `feature → taxa` inversion at genus rank over the Tier 1/2
characters, plus the residual-attack lines of §8.24. Each entry gives a
character, then one line per state listing the genera that carry it.

**Confidence codes**, applied per state line:

| Code | Meaning |
| --- | --- |
| `[A]` | Established generic circumscription; expected to survive verification against the primary monographs unchanged |
| `[B]` | Supported by strong secondary sources or the project corpus; verify |
| `[C]` | Provisional; recorded so that it can be checked, not so that it can be used |

**Every line in this section is a hypothesis with a confidence code, not a
datum.** No cell here has yet been read out of Flora Mesoamericana
vol. 7(2) or *Genera Orchidacearum*, and no morphological cell yet exists
in a machine-readable store with primary-monograph provenance. The value
of publishing the index in this state is that verification against Ames &
Correll (open access, §18) and Flora Mesoamericana becomes a mechanical
checking exercise over an enumerated list rather than an open-ended
reading project, and disagreements get recorded rather than absorbed.
When imported into the data store, every line below enters with status
`legacy_unverified` (§3.4), never `scored`.

Where a state cannot responsibly be assigned across the whole genus set,
the entry says **Unscored** and names the resolving source. Unscored means
unscored, not absent: guessing cells to make a table look complete is how
morphological indexes come to assert thousands of facts with no checkable
citation behind them.

Genera are given in lexical order within each state line. Group names
resolve in §8.2.

### 8.2 Group names used in this index

The nine rows partition the 104 genera exactly (verified by set
comparison: no duplicates, no gaps). Placements follow Chase et al. (2015)
and are themselves `[B]` pending Flora Mesoamericana.

| Group | *n* | Genera |
| --- | ---: | --- |
| Pleurothallidinae | 20 | *Acianthera*, *Anathallis*, *Andreettaea*, *Dresslerella*, *Dryadella*, *Echinosepala*, *Karma*, *Lankesteriana*, *Lepanthes*, *Lepanthopsis*, *Masdevallia*, *Myoxanthus*, *Octomeria*, *Phloeophila*, *Platystele*, *Pleurothallis*, *Restrepiella*, *Specklinia*, *Stelis*, *Trichosalpinx* |
| Laeliinae | 18 | *Arpophyllum*, *Brassavola*, *Caularthron*, *Dimerandra*, *Dinema*, *Encyclia*, *Epidendrum*, *Guarianthe*, *Isochilus*, *Jacquiniella*, *Laelia*, *Myrmecophila*, *Nemaconia*, *Nidema*, *Oestlundia*, *Prosthechea*, *Rhyncholaelia*, *Scaphyglottis* |
| Oncidiinae | 14 | *Brassia*, *Comparettia*, *Cryptarrhena*, *Erycina*, *Ionopsis*, *Leochilus*, *Lockhartia*, *Macradenia*, *Macroclinium*, *Notylia*, *Oncidium*, *Ornithocephalus*, *Trichocentrum*, *Trichopilia* |
| Rosette Cranichideae | 15 | *Beloglottis*, *Cranichis*, *Cyclopogon*, *Eurystyles*, *Goodyera*, *Lyroglossa*, *Mesadenella*, *Mesadenus*, *Microchilus*, *Pelexia*, *Prescottia*, *Pseudogoodyera*, *Sacoila*, *Sarcoglottis*, *Spiranthes* |
| Stanhopeinae | 5 | *Coryanthes*, *Gongora*, *Kegeliella*, *Lacaena*, *Stanhopea* |
| Catasetinae | 4 | *Catasetum*, *Clowesia*, *Cycnoches*, *Mormodes* |
| Zygopetalinae | 4 | *Cochleanthes*, *Galeottia*, *Huntleya*, *Koellensteinia* |
| Maxillariinae | 2 | *Maxillaria*, *Xylobium* |
| Unassigned to a group name here | 22 | *Bifrenaria*, *Bletia*, *Bulbophyllum*, *Campylocentrum*, *Chysis*, *Coelia*, *Corymborkis*, *Cyrtopodium*, *Dichaea*, *Elleanthus*, *Epistephium*, *Eriopsis*, *Eulophia*, *Galeandra*, *Habenaria*, *Liparis*, *Lycaste*, *Malaxis*, *Polystachya*, *Psilochilus*, *Sobralia*, *Vanilla* |

### 8.3 ARCH-01 — Growth form

- **monopodial** `[A]` — *Campylocentrum*, *Vanilla*
- **sympodial** `[A]` — the other 102 genera

A single decision that costs nothing and removes two genera; useful mainly
because it pairs with ARCH-12 and LFRM-01 to isolate *Vanilla* in one
step.

### 8.4 STEM-01 — Principal stem type

The highest-value single vegetative character in the flora. Under the
perennating-organ rule of §5.2 it partitions the 102 sympodial genera into
six classes; the two monopodial genera (*Campylocentrum*, *Vanilla*) are
structurally `inapplicable` and are resolved by ARCH-01 and ARCH-12
instead.

- **pseudobulb** `[A]` — *Bifrenaria*, *Brassia*, *Bulbophyllum*,
  *Catasetum*, *Caularthron*, *Chysis*, *Clowesia*, *Coelia*,
  *Comparettia*, *Coryanthes*, *Cycnoches*, *Cyrtopodium*, *Dinema*,
  *Encyclia*, *Eriopsis*, *Galeandra*, *Galeottia*, *Gongora*,
  *Guarianthe*, *Ionopsis*, *Kegeliella*, *Koellensteinia*, *Lacaena*,
  *Laelia*, *Leochilus*, *Lycaste*, *Macradenia*, *Maxillaria*,
  *Mormodes*, *Myrmecophila*, *Nidema*, *Notylia*, *Oestlundia*,
  *Oncidium*, *Polystachya*, *Prosthechea*, *Rhyncholaelia*,
  *Scaphyglottis*, *Stanhopea*, *Trichocentrum*, *Trichopilia*, *Xylobium*
- **pseudobulb, corm-like, at or just below ground level** `[C]` —
  *Liparis*, *Malaxis* (boundary against the geophyte state to be fixed
  from Flora Mesoamericana; §8.25 queue)
- **cane or reed-like leafy stem, not conspicuously thickened** `[A]` —
  *Arpophyllum*, *Brassavola*, *Corymborkis*, *Dichaea*, *Dimerandra*,
  *Elleanthus*, *Epidendrum*, *Epistephium*, *Isochilus*, *Jacquiniella*,
  *Nemaconia*, *Psilochilus*, *Sobralia*
- **ramicaul (Pleurothallidinae)** `[A]` — the 20 Pleurothallidinae
- **basal rosette, no aerial stem** `[A]` — the 15 rosette Cranichideae
- **leaf fan, pseudobulb absent or vestigial** `[A]` — *Cochleanthes*,
  *Cryptarrhena*, *Erycina*, *Huntleya*, *Lockhartia*, *Macroclinium*,
  *Ornithocephalus*
- **underground corm or tuber (geophytes)** `[B]` — *Bletia*, *Eulophia*,
  *Habenaria*
- **Inapplicable** — *Campylocentrum*, *Vanilla* (monopodial; resolved by
  ARCH-01, ARCH-11, ARCH-12)

*Epidendrum* is polymorphic here and is the clearest case for the
distributional coding of §3.6: most species are cane-stemmed, a
substantial minority pseudobulbous. It is entered under **cane** with a
distribution, not moved.

### 8.5 STEM-14 — Pseudobulb arrangement

- **superposed (each new pseudobulb arising from the apex of the last)**
  `[A]` — *Scaphyglottis*; `[B]` — *Polystachya* (part)
- **spaced along a visible creeping rhizome** `[A]` — *Bulbophyllum*,
  *Dinema*; `[B]` — *Maxillaria* (part), *Nidema*
- **clustered** `[A]` — the remaining pseudobulbous genera
- **Not applicable** — the genera without pseudobulbs

Superposed pseudobulbs are close to a singleton diagnosis (§11.2).

### 8.6 STEM-10 / STEM-11 — Hollow pseudobulb and ant occupancy

- **hollow, ant-inhabited** `[A]` — *Caularthron*, *Myrmecophila*
- **solid** `[A]` — all other pseudobulbous genera

Two genera out of 104 identified by a character visible from several
meters away, at any season, on any mature plant.

### 8.7 STEM-13 — Pseudobulb clothing at maturity

- **spiny persistent leaf bases after leaf fall** `[A]` — *Catasetum*,
  *Clowesia*, *Cycnoches*, *Mormodes*
- **fibrous sheath net** `[B]` — *Cyrtopodium*; `[C]` — *Eulophia*
- **persistent papery sheaths** `[B]` — *Encyclia*, *Guarianthe*,
  *Laelia*, *Prosthechea*
- **naked** `[B]` — *Bulbophyllum*, *Maxillaria*, *Oncidium*, *Stanhopea*,
  and most other pseudobulbous genera
- **Unscored** — the remaining pseudobulbous genera; resolve from Flora
  Mesoamericana

The first state is the key to Catasetinae out of season: after the plicate
leaves drop, the bare fusiform pseudobulb retains a ring of stiff,
spine-like leaf-base remnants — diagnostic of a four-genus group, and
scoreable precisely when the plant is least identifiable by any other
means.

### 8.8 STEM-05 — Pseudobulb outline (partial; derived from S-PBL geometry)

Only the states that carry group-level signal are asserted; the rounded
middle of the shape space needs measurement, not recollection.

- **fusiform (spindle-shaped, several internodes)** `[B]` — *Catasetum*,
  *Clowesia*, *Cycnoches*, *Mormodes*; `[C]` — *Cyrtopodium*, *Galeandra*
- **clavate, pendent** `[C]` — *Chysis*
- **ovoid to globose, strongly flattened or not** — the pseudobulbous
  majority; **Unscored** at state level pending Flora Mesoamericana
- **Not applicable** — the genera without pseudobulbs

The fusiform line pairs with STEM-13 (spiny stubs) and LARR-05
(deciduous): three mutually confirming Tier 1 characters that all point at
Catasetinae plus its lookalikes — exactly the confirmatory redundancy the
key wants at high-risk nodes (§16.7).

### 8.9 LARR-01 — Leaves per mature shoot

- **0 (leafless at maturity, at least in part)** `[B]` — *Campylocentrum*
  (part)
- **1** `[A]` — *Acianthera*, *Anathallis*, *Andreettaea*, *Arpophyllum*,
  *Brassavola*, *Bulbophyllum*, *Comparettia*, *Coryanthes*,
  *Dresslerella*, *Dryadella*, *Echinosepala*, *Karma*, *Lankesteriana*,
  *Leochilus*, *Lepanthes*, *Lepanthopsis*, *Macradenia*, *Masdevallia*,
  *Maxillaria*, *Myoxanthus*, *Notylia*, *Octomeria*, *Phloeophila*,
  *Platystele*, *Pleurothallis*, *Restrepiella*, *Rhyncholaelia*,
  *Specklinia*, *Stanhopea*, *Stelis*, *Trichocentrum*, *Trichopilia*,
  *Trichosalpinx*
- **2** `[A]` — *Guarianthe*, *Laelia* (1–2); `[B]` — *Bifrenaria*,
  *Caularthron*, *Dinema*, *Lacaena*, *Nidema*, *Scaphyglottis*
- **3–5** `[B]` — *Brassia*, *Coelia*, *Encyclia*, *Eriopsis*, *Gongora*,
  *Lycaste*, *Myrmecophila*, *Oncidium*, *Polystachya*, *Prosthechea*,
  *Xylobium*; `[C]` — *Cryptarrhena*, *Galeottia*, *Ionopsis*,
  *Kegeliella*, *Koellensteinia*, *Oestlundia*
- **>5, borne along the stem** `[A]` — *Campylocentrum*, *Catasetum*,
  *Chysis*, *Clowesia*, *Corymborkis*, *Cycnoches*, *Cyrtopodium*,
  *Dichaea*, *Dimerandra*, *Elleanthus*, *Epidendrum*, *Epistephium*,
  *Galeandra*, *Habenaria*, *Isochilus*, *Jacquiniella*, *Lockhartia*,
  *Mormodes*, *Sobralia*, *Vanilla*; `[B]` — *Bletia*, *Cochleanthes*,
  *Erycina*, *Eulophia*, *Huntleya*, *Liparis*, *Macroclinium*,
  *Malaxis*, *Nemaconia*, *Ornithocephalus*, *Psilochilus*
- **rosette** `[A]` — the 15 rosette Cranichideae

### 8.10 LFRM-02 — Ptyxis (vernation)

- **plicate (longitudinally pleated, thin, several strong veins)** `[A]` —
  *Bletia*, *Catasetum*, *Chysis*, *Clowesia*, *Corymborkis*,
  *Coryanthes*, *Cycnoches*, *Cyrtopodium*, *Eulophia*, *Galeandra*,
  *Gongora*, *Lycaste*, *Mormodes*, *Sobralia*, *Stanhopea*, *Xylobium*;
  `[B]` — *Bifrenaria*, *Coelia*, *Elleanthus*, *Eriopsis*, *Galeottia*,
  *Kegeliella*, *Koellensteinia*, *Lacaena*, *Liparis*, *Malaxis*,
  *Psilochilus*
- **convolute, soft, not plicate** `[B]` — the 15 rosette Cranichideae,
  plus *Habenaria*; `[C]` — *Epistephium*
- **conduplicate** `[A]` — the remaining ~60 genera, comprising
  Pleurothallidinae, Laeliinae, most Oncidiinae, *Bulbophyllum*,
  *Dichaea*, *Maxillaria*, *Polystachya*, *Campylocentrum*,
  *Cochleanthes*, *Huntleya*, and *Vanilla*

Plicate versus conduplicate is one of the strongest and cheapest
vegetative characters in the family, separating roughly a quarter of the
flora from the rest on a property visible at a glance and present
year-round on evergreen taxa.

### 8.11 LARR-04 — Leaf articulation with the sheath

- **not articulated** `[A]` — *Corymborkis*, *Elleanthus*, *Epistephium*,
  *Habenaria*, *Liparis*, *Malaxis*, *Psilochilus*, *Sobralia*, *Vanilla*,
  and the 15 rosette Cranichideae
- **articulated** `[A]` — Pleurothallidinae (20), Laeliinae (18),
  Oncidiinae (14), *Bifrenaria*, *Bulbophyllum*, *Campylocentrum*,
  *Catasetum*, *Chysis*, *Clowesia*, *Coryanthes*, *Cycnoches*,
  *Cyrtopodium*, *Dichaea*, *Eriopsis*, *Galeandra*, *Gongora*,
  *Kegeliella*, *Lacaena*, *Lycaste*, *Maxillaria*, *Mormodes*,
  *Polystachya*, *Stanhopea*, *Xylobium*
- **Unscored** `[C]` — *Bletia*, *Cochleanthes*, *Coelia*, *Eulophia*,
  *Galeottia*, *Huntleya*, *Koellensteinia*; resolve from Flora
  Mesoamericana or Dressler 1993a

Articulation is scored by looking for a clean transverse abscission line
where the blade meets the sheath — on a plant that has already shed a
leaf, the scar is unambiguous. It correlates strongly with subfamily and
tribe, which makes it excellent for clustering validation and a good early
node.

### 8.12 LFRM-03 — Blade cross-section

- **terete or subterete** `[A]` — *Brassavola*; `[B]` — *Campylocentrum*
  (part), *Epidendrum* (part), *Jacquiniella* (part); `[C]` — *Vanilla*
  (part)
- **laterally compressed, equitant (borne edgewise)** `[A]` — *Erycina*,
  *Lockhartia*, *Macroclinium*, *Ornithocephalus*; `[B]` — *Arpophyllum*,
  *Cryptarrhena*
- **dorsiventrally thickened, fleshy** `[A]` — *Trichocentrum*; `[B]` —
  *Acianthera* (part), *Maxillaria* (part)
- **flat** `[A]` — the large remainder

### 8.13 LARR-03 — Phyllotaxy

- **equitant fan** `[A]` — *Cryptarrhena*, *Erycina*, *Lockhartia*,
  *Macroclinium*, *Ornithocephalus*; `[B]` — *Cochleanthes*, *Huntleya*
  (imbricating fan, not strictly equitant)
- **distichous along an elongate stem** `[A]` — *Arpophyllum*,
  *Campylocentrum*, *Dichaea*, *Dimerandra*, *Elleanthus*, *Epidendrum*,
  *Isochilus*, *Jacquiniella*, *Nemaconia*, *Sobralia*, *Vanilla*;
  `[B]` — *Polystachya*
- **rosulate** `[A]` — the 15 rosette Cranichideae
- **spiral** `[B]` — *Catasetum*, *Chysis*, *Clowesia*, *Corymborkis*,
  *Cycnoches*, *Cyrtopodium*, *Galeandra*, *Habenaria*, *Mormodes*
- **Not applicable** — genera with a single leaf per shoot (§8.9)

### 8.14 SHTH-01 — Stem and ramicaul sheath type

- **lepanthiform (tubular, ribbed, imbricating, with a dilated ostium)**
  `[A]` — *Lepanthes*, *Trichosalpinx*; `[B]` — *Karma*, *Lepanthopsis*;
  `[C]` — *Andreettaea*
- **plain tubular** `[A]` — the remaining Pleurothallidinae, most
  Laeliinae
- **spathaceous (a conduplicate bract subtending the inflorescence)**
  `[B]` — *Acianthera* (part), *Caularthron*, *Encyclia*, *Guarianthe*,
  *Laelia*, *Prosthechea*
- **foliaceous** `[B]` — *Elleanthus*, *Isochilus*, *Sobralia*
- **absent or not evident** `[B]` — the rosette Cranichideae, *Habenaria*

The lepanthiform sheath is the textbook example of an atomic vegetative
character with generic weight. Scoring it needs a ×10 lens and ten
seconds; §7.3 gives the component protocol.

### 8.15 SHTH-14 — Persistent sheath ladder

Leaf sheaths that persist after blade fall, clothing the stem in a
distichous ladder — scoreable on old, even moribund stems.

- **present** `[B]` — *Dichaea*, *Isochilus*, *Jacquiniella*; `[C]` —
  *Dimerandra*, *Elleanthus* (part)
- **absent** `[B]` — the great majority
- **Unscored** — cane genera not named above; resolve from Ames & Correll
  plates and Flora Mesoamericana

Combined with LARR-03 distichous and LFRM-17 short blades, `present` is
close to a three-genus diagnosis among the cane-stemmed epiphytes.

### 8.16 LSUR-01 — Blade texture, broad classes

Asserted at class level only; the six-state ordinal fine structure needs
sources.

- **thin (membranaceous–chartaceous)** `[B]` — every plicate-leaved genus
  of §8.10; the 15 rosette Cranichideae; *Liparis*, *Malaxis*
- **coriaceous** `[B]` — most Laeliinae, most Oncidiinae, most
  Pleurothallidinae, *Bulbophyllum*, *Maxillaria* (part)
- **carnose to rigid-succulent** `[B]` — *Brassavola*, *Jacquiniella*,
  *Trichocentrum*; `[C]` — *Acianthera* (part), *Dichaea* (part),
  *Myrmecophila*
- **Unscored** — remainder

Note the near-implication `LFRM-02 = plicate → LSUR-01 = thin`. When the
matrix is populated this should surface in the implication basis (§15.4);
if it holds with zero exceptions, one of the two characters is free
information after the other, and if it has exactly one exception, that
cell is where a scoring error is most likely hiding. It is written down
now so the implication check has a stated expectation to test.

### 8.17 LSUR-04 / LSUR-05 — Leaf and stem indumentum

- **leaves densely pubescent over the whole blade** `[A]` —
  *Dresslerella*
- **ramicaul or sheaths pubescent, hirsute, or ciliate** `[A]` —
  *Myoxanthus*, *Trichosalpinx*; `[B]` — *Echinosepala*, *Acianthera*
  (part), *Lepanthes* (part)
- **glabrous** `[A]` — the great majority of the flora

*Dresslerella* is a one-character genus out of bloom, and the character is
free to score.

### 8.18 LSUR-10 — Leaf variegation

- **silver-reticulate or marbled** `[A]` — *Goodyera*, *Microchilus*,
  *Sarcoglottis*; `[B]` — *Cyclopogon*, *Pelexia* (part)
- **absent** `[A]` — the great majority

Within the fifteen rosette Cranichideae — otherwise the hardest group in
the flora to separate vegetatively — variegation carries most of the
available signal. Genus-level monomorphy must not be invented from one
illustrated species: several of these genera are polymorphic for
variegation at species level, so the states enter as distributions.

### 8.19 LSUR-02 — Adaxial lustre

- **glaucous-pruinose** `[A]` — *Rhyncholaelia*; `[B]` — *Brassavola*
  (part), *Dichaea* (part); `[C]` — *Encyclia* (part)
- **matte or glossy** — the remainder

### 8.20 LFRM-12 — Venation pattern

- **reticulate (net-veined)** `[A]` — *Epistephium*
- **many prominent parallel veins** — the plicate-leaved genera of §8.10
- **midvein only, or obscure** `[B]` — *Brassavola*, *Campylocentrum*,
  *Jacquiniella*, *Vanilla*, and most fleshy-leaved Pleurothallidinae
- **few prominent parallel veins** `[B]` — the remainder

Reticulate venation is a Vanilloideae marker and isolates *Epistephium* in
one observation.

### 8.21 LFRM-08 — Apex minutely tridenticulate

- **present** `[B]` — *Stelis*; `[C]` — *Anathallis* (part), *Platystele*
  (part), *Specklinia* (part)
- **absent or not recorded** — remainder; resolve within Pleurothallidinae
  from Karremans 2016 and the *Lankesteriana* literature

Kept despite its `[C]`-heavy state line because it is one of the few ×10
lens characters that works *inside* the core-Pleurothallidinae residue
(§10.3, group G5), where the flora is hardest. Measured components
(S-LGE-08) replace the binary as data arrive.

### 8.22 ROOT-12 / ROOT-13 — Root and underground storage organs

- **tuberoid (a fleshy root-stem tuber)** `[A]` — *Habenaria*
- **fascicled fleshy tuberous roots** `[A]` — *Beloglottis*, *Cyclopogon*,
  *Lyroglossa*, *Mesadenella*, *Mesadenus*, *Pelexia*, *Prescottia*,
  *Sacoila*, *Sarcoglottis*, *Spiranthes*; `[B]` — *Cranichis*,
  *Pseudogoodyera*
- **creeping fleshy rhizome, roots at the nodes** `[A]` — *Goodyera*,
  *Microchilus*
- **fleshy roots, epiphytic rosette** `[B]` — *Eurystyles*
- **velamentous aerial roots** `[A]` — the epiphytic majority
- **subterranean corm** `[B]` — *Bletia*, *Eulophia*

*Habenaria* is the only tuberoid-bearing genus in the flora, so one dig
resolves it — but the dig is destructive (cost 3). The key generator
prefers LFRM-02 and LARR-04, which reach the same answer for free, and
offers ROOT-13 only as confirmation.

### 8.23 Remaining inversions

#### ARCH-05 — shoot spacing

- **long-repent (shoots well spaced on an elongate rhizome)** `[B]` —
  *Bulbophyllum*, *Dichaea*, *Dinema*, *Goodyera*, *Microchilus*,
  *Nidema*, *Phloeophila*, *Acianthera* (part), *Maxillaria* (part)
- **shortly repent** `[B]` — *Scaphyglottis*, *Stelis* (part), many
  Pleurothallidinae
- **caespitose** `[A]` — the majority

ARCH-04 expresses the same quantity scale-free as a ratio to shoot
diameter, removing the confound between a large plant with short
internodes and a small plant with long ones.

#### LARR-05 — leaf duration

- **seasonally deciduous** `[A]` — *Catasetum*, *Chysis*, *Clowesia*,
  *Cycnoches*, *Cyrtopodium*, *Galeandra*, *Mormodes*; `[B]` — *Bletia*,
  *Eulophia*, *Lycaste* (part)
- **evergreen** `[A]` — the remainder

This character has persistence 1: it is precisely the character a
season-independent key must be cautious with, because a Catasetinae plant
in leaf and the same plant out of leaf present differently. The Bayesian
formulation conditions on season when the user supplies a date and
marginalizes over it when they do not (§16.6).

#### ECOL-01 — substrate

- **terrestrial (predominantly)** `[A]` — *Beloglottis*, *Bletia*,
  *Corymborkis*, *Cranichis*, *Cyclopogon*, *Epistephium*, *Eulophia*,
  *Goodyera*, *Habenaria*, *Lyroglossa*, *Mesadenella*, *Mesadenus*,
  *Microchilus*, *Pelexia*, *Prescottia*, *Pseudogoodyera*, *Psilochilus*,
  *Sacoila*, *Sarcoglottis*, *Sobralia*, *Spiranthes*
- **frequently lithophytic** `[B]` — *Acianthera* (part), *Bletia*,
  *Cyrtopodium*, *Encyclia*, *Laelia*, *Prosthechea*
- **climber on trees** `[A]` — *Vanilla*
- **epiphytic (predominantly)** `[A]` — the remaining ~80 genera,
  including the epiphytic rosette of *Eurystyles*

#### REMN-02 — position of the inflorescence scar

Layer R; scoreable from a dried peduncle base months after flowering.

- **terminal at the shoot apex** `[A]` — the 20 Pleurothallidinae,
  *Arpophyllum*, *Dimerandra*, *Elleanthus*, *Epidendrum*, *Isochilus*,
  *Sobralia*
- **from the apex of the pseudobulb** `[B]` — *Caularthron*, *Encyclia*,
  *Guarianthe*, *Laelia*, *Myrmecophila*, *Polystachya*, *Prosthechea*;
  `[C]` — *Rhyncholaelia* (queued for verification, §8.25)
- **from the base of the pseudobulb** `[A]` — *Bifrenaria*, *Brassia*,
  *Comparettia*, *Eriopsis*, *Ionopsis*, *Kegeliella*, *Lacaena*,
  *Leochilus*, *Lycaste*, *Macradenia*, *Maxillaria*, *Notylia*,
  *Oncidium*, *Trichopilia*, *Xylobium*
- **from the pseudobulb base and descending through the substrate**
  `[A]` — *Coryanthes*, *Gongora*, *Stanhopea*
- **from the rhizome, away from the pseudobulb** `[A]` — *Bulbophyllum*
- **from stem nodes or leaf axils** `[A]` — *Campylocentrum*, *Dichaea*,
  *Lockhartia*, *Vanilla*
- **Unscored** — the remainder, including the *Dinema* – *Nidema* –
  *Oestlundia* – *Trichocentrum* residue; resolve from Flora Mesoamericana

The pendent, substrate-piercing inflorescence of the Stanhopeinae core is
a three-genus diagnosis available from a dried stalk — it is why those
plants are grown in baskets, a mnemonic worth putting in the user-facing
key.

#### REMN-04 — old rachis architecture (partial)

Layer R; scoreable from dried remains months after anthesis.

- **dense bracteate spike** `[B]` — *Arpophyllum*, *Elleanthus*
- **fascicles of single-flowered pedicels** `[B]` — *Maxillaria* (part),
  *Scaphyglottis*; `[C]` — *Octomeria*
- **single-flowered scape** `[B]` — *Bifrenaria*, *Cochleanthes*,
  *Huntleya*, *Lycaste*, *Rhyncholaelia*; `[C]` — *Trichopilia* (1–3)
- **large panicle** `[B]` — *Cyrtopodium*, *Oncidium* (part); `[C]` —
  *Epidendrum* (part)
- **Unscored** — remainder

#### SIZE-01 — mature plant height

Extremes only; the middle of the range needs measurement, not
recollection.

- **mini-miniature to miniature (<10 cm)** `[B]` — *Andreettaea*,
  *Dryadella*, *Erycina*, *Lankesteriana*, *Lepanthopsis*, *Macroclinium*,
  *Ornithocephalus*, *Platystele*; `[C]` — *Leochilus*, *Phloeophila*
- **giant (>150 cm)** `[B]` — *Corymborkis*, *Cyrtopodium*,
  *Myrmecophila*, *Sobralia*; `[C]` — *Epistephium*
- **Not applicable** — *Vanilla* (scandent)
- **Unscored** — the remainder; populate from Flora Mesoamericana
  measurements

#### ECOL-11 — forest formation, specialists only

Belize's pine savannas and mangrove cays are the two formations where the
candidate set collapses fastest; a user standing in either has discarded
most of the flora before the first morphological question.

- **pine savanna (regular)** `[B]` — *Bletia* (part, incl. *B. purpurea*),
  *Cyrtopodium* (part), *Encyclia* (part), *Eulophia*, *Habenaria* (part),
  *Myrmecophila* (part)
- **mangrove and coastal cays (regular)** `[B]` — *Brassavola* (part),
  *Myrmecophila* (part); `[C]` — *Prosthechea* (part)
- **Unscored** — all other genus–formation pairs

Every line here is `part`: these genera also occur elsewhere, so ECOL-11
enters the likelihood as a distribution, never as a filter. The codes rest
on regional habitat notes and must be re-derived from Belize-specific
occurrence records during matrix fill.

### 8.24 Residual-attack lines (subatomic layer)

Hypotheses aimed at the groups the demonstration key leaves large
(§10.3). These are the first rows to verify against Ames & Correll plates
and Flora Mesoamericana.

#### S-LAT-05 — abscission geometry

Within articulated taxa only.

- **abscission flush at the sheath mouth** `[B]` — most articulated
  Laeliinae and Oncidiinae
- **abscission with a measurable petiole above the sheath** `[B]` — many
  Maxillariinae, some Pleurothallidinae; verify the Cranichideae and
  *Liparis*/*Malaxis* petiole condition against sources

#### S-RPR-01 — scar position refinements

- **axillary from upper cane nodes** `[C]` — *Epidendrum* (part); verify
  species-proportion
- **terminal or near-terminal on the superposed stem** `[B]` —
  *Scaphyglottis*; verify

#### S-ECO — host and formation priors

Never required; they improve priors only.

- **outer-twig / small-branch bias** `[C]` — *Comparettia*, *Erycina*,
  *Ionopsis*, *Leochilus* (part), *Macroclinium* (part), *Notylia*,
  *Ornithocephalus* (part)
- **open terrestrial / savanna bias** `[B]` — *Bletia* (part),
  *Eulophia*, *Habenaria* (part), *Spiranthes*
- **deep-shade forest floor** `[B]` — many rosette Cranichideae,
  *Corymborkis*

#### S-CAN-07 — ramicaul annulus

- **present** `[B]` — a subset of Pleurothallidinae ramicauls; per-genus
  frequencies needed from the Pleurothallidinae literature. Useful inside
  the core-Pleurothallidinae residue, not at the top of the flora.

### 8.25 Assertions queued for early verification

Lines most likely to move when checked, listed so the first reading
session starts here:

1. *Corymborkis* under spiral phyllotaxy (§8.13) — Tropidieae stem leaves
   are often described as distichous or subdistichous.
2. *Psilochilus* under plicate `[B]` (§8.10) — Triphoreae blades are thin
   and few-veined but only weakly, if at all, plicate.
3. *Liparis*/*Malaxis* corm-like placement (§8.4) — correct in substance,
   but the boundary against the geophyte state needs writing when Flora
   Mesoamericana is read.
4. *Andreettaea* group membership (§8.14 and G4 in §10.3) — blocked on the
   circumscription problem of §2.3.
5. *Rhyncholaelia* pseudobulb-apex scar `[C]` (§8.23).
6. *Epidendrum* (part) axillary scars; *Scaphyglottis* terminal scars
   (§8.24).

### 8.26 Coverage of this index

| Metric | Value |
| --- | --- |
| Genera in scope | 104 |
| Tier 1/2 characters defined (§5) | 178 |
| Characters with at least one inverted state line (§8.3–§8.24) | 30 |
| Explicit genus-state assertions | ~660 |
| Further assertions carried by group names (§8.2) | ~485 |
| Genera with a measured elevation envelope (§9) | 52 |
| Morphological cells sourced from a primary monograph | 0 |

The last row is the honest headline. This index is a well-structured
hypothesis suite awaiting its primary sources; §19 is the plan for getting
them, and the elevation block of §9 is the one facet whose content is
already measured rather than recalled.

---

## 9. Measured genus-level elevation envelopes

### 9.1 Method

Species-level elevation limits were aggregated to genus rank from Plants
of the World Online records for the regional species — a distribution
fact, for which a nomenclatural/distributional database is a legitimate
authority (§18.2):

- genus minimum = min over that genus's species minima;
- genus maximum = max over that genus's species maxima;
- `n` = number of species records contributing;
- bands = the ECOL-10 bands the envelope intersects.

The aggregation is a small script over the recorded species values; rerun
it to reproduce the table exactly.

### 9.2 Caveats that govern use

1. **These are range-wide envelopes, not Belize occupancy.** A genus
   reaching 2,500 m in Chiapas tops out below 1,124 m inside Belize
   (§2.1). Envelopes are an upper bound on in-country breadth.
2. **Sampling is thin.** Median contribution is one species per genus;
   only *Epidendrum* (13), *Maxillaria* (8), and *Habenaria* (6) have
   more than four. Treat every envelope as `expert-uniform` quality until
   cleaned Belize occurrence records replace it.
3. **The species sample reflects aggregator coverage, not the flora.**
   Envelopes are provisional priors, not measurements of the genus.

Encoding: each row becomes an ECOL-10 cell with `source_type: aggregator`,
`estimator: species-proportion`, confidence `B` (n ≥ 4) or `C` (n < 4).

### 9.3 The envelopes

52 of 104 genera have at least one record. Elevations in meters.

| Genus | Min | Max | n | ECOL-10 bands intersected |
| --- | ---: | ---: | ---: | --- |
| *Acianthera* | 100 | 2450 | 4 | all five |
| *Arpophyllum* | 800 | 2400 | 2 | 500–900, 900–1400, >1400 |
| *Beloglottis* | 50 | 1100 | 1 | 0–150, 150–500, 500–900, 900–1400 |
| *Bletia* | 2000 | 2000 | 1 | >1400 |
| *Brassavola* | 500 | 500 | 1 | (point record at a band edge) |
| *Bulbophyllum* | 550 | 1500 | 1 | 500–900, 900–1400, >1400 |
| *Chysis* | 800 | 1500 | 1 | 500–900, 900–1400, >1400 |
| *Cochleanthes* | 250 | 1200 | 1 | 150–500, 500–900, 900–1400 |
| *Coryanthes* | 100 | 600 | 1 | 0–150, 150–500, 500–900 |
| *Cranichis* | 200 | 2950 | 1 | 150–500 through >1400 |
| *Cyclopogon* | 750 | 1800 | 1 | 500–900, 900–1400, >1400 |
| *Dichaea* | 500 | 2400 | 2 | 500–900, 900–1400, >1400 |
| *Dimerandra* | 800 | 800 | 1 | 500–900 |
| *Dryadella* | 650 | 650 | 1 | 500–900 |
| *Elleanthus* | 200 | 1350 | 1 | 150–500, 500–900, 900–1400 |
| *Epidendrum* | 20 | 2500 | 13 | all five |
| *Epistephium* | 600 | 1100 | 1 | 500–900, 900–1400 |
| *Eriopsis* | 500 | 2000 | 1 | 500–900, 900–1400, >1400 |
| *Gongora* | 180 | 850 | 1 | 150–500, 500–900 |
| *Goodyera* | 1180 | 1200 | 1 | 900–1400 |
| *Habenaria* | 80 | 3000 | 6 | all five |
| *Huntleya* | 400 | 1200 | 1 | 150–500, 500–900, 900–1400 |
| *Jacquiniella* | 60 | 2000 | 2 | all five |
| *Kegeliella* | 370 | 1200 | 1 | 150–500, 500–900, 900–1400 |
| *Koellensteinia* | 500 | 1200 | 1 | 500–900, 900–1400 |
| *Lacaena* | 1100 | 2400 | 1 | 900–1400, >1400 |
| *Leochilus* | 220 | 1300 | 1 | 150–500, 500–900, 900–1400 |
| *Lepanthes* | 350 | 2200 | 3 | 150–500 through >1400 |
| *Lyroglossa* | 1000 | 1300 | 1 | 900–1400 |
| *Masdevallia* | 400 | 1500 | 1 | 150–500 through >1400 |
| *Maxillaria* | 50 | 2500 | 8 | all five |
| *Mesadenus* | 320 | 2350 | 1 | 150–500 through >1400 |
| *Microchilus* | 50 | 1900 | 1 | all five |
| *Mormodes* | 500 | 1100 | 2 | 500–900, 900–1400 |
| *Myoxanthus* | 200 | 1300 | 1 | 150–500, 500–900, 900–1400 |
| *Octomeria* | 100 | 1400 | 1 | 0–150 through 900–1400 |
| *Oestlundia* | 900 | 1350 | 1 | 900–1400 |
| *Oncidium* | 1000 | 2000 | 2 | 900–1400, >1400 |
| *Pelexia* | 300 | 1500 | 2 | 150–500 through >1400 |
| *Platystele* | 2 | 2500 | 2 | all five |
| *Pleurothallis* | 40 | 2300 | 2 | all five |
| *Polystachya* | 100 | 1400 | 1 | 0–150 through 900–1400 |
| *Psilochilus* | 500 | 2200 | 1 | 500–900, 900–1400, >1400 |
| *Restrepiella* | 40 | 1600 | 1 | all five |
| *Rhyncholaelia* | 700 | 1600 | 1 | 500–900, 900–1400, >1400 |
| *Scaphyglottis* | 700 | 2300 | 1 | 500–900, 900–1400, >1400 |
| *Sobralia* | 50 | 1700 | 1 | all five |
| *Stanhopea* | 300 | 1500 | 1 | 150–500 through >1400 |
| *Stelis* | 350 | 1500 | 4 | 150–500 through >1400 |
| *Trichopilia* | 70 | 1500 | 1 | all five |
| *Trichosalpinx* | 200 | 2500 | 1 | 150–500 through >1400 |
| *Vanilla* | 50 | 900 | 1 | 0–150, 150–500, 500–900 |

Two rows illustrate the caveats deliberately: *Bletia* at a single
2,000 m record contradicts its well-known presence in Belizean lowland
pine savanna — the one sampled species is simply a montane one — and
*Brassavola* has a single point record. Rows like these are why the
`expert-uniform` downgrade of §9.2 exists. The table's value is not its
individual rows but that ECOL-10 moves from 0% to 50% genus coverage with
honest provenance, and that the aggregation pattern (species → genus
envelope, estimator recorded) is exercised end to end before the same
pattern is applied to the morphological characters read from the
monographs.

---

## 10. Demonstration: a hand-built vegetative group key

### 10.1 Ground rules

- Only Tier 1 characters from §5, using only state assignments published
  in §8. No new facts enter here; this section is a *rearrangement* of the
  published assertions into key form.
- Confidence is inherited: a lead resting on a `[B]`/`[C]` line is only as
  good as that line, and the verification pass will move members between
  groups.
- This key is illustrative. The generated key (§16) will differ — it will
  order questions by measured effectiveness per cost, condition on season
  and locality, and handle polymorphism probabilistically. The point is
  that even a naive hand arrangement of the existing assertions already
  resolves the flora into workable groups.

### 10.2 The key

```text
1a. Growth monopodial, without repeated sympodial units ............... 2
1b. Growth sympodial .................................................. 3

2a. Robust climbing vine; stout green stems rooting at the nodes
    ......................................................... G1 Vanilla
2b. Short-stemmed epiphyte, leafy or a leafless tuft of
    grey-green photosynthetic roots; not climbing ..... G2 Campylocentrum

3a. Terrestrial basal rosette; no aerial stem, no pseudobulb;
    roots fleshy, fascicled ................. G3 Rosette Cranichideae (15)
3b. Not as above ...................................................... 4

4a. Shoots ramicauls: slender, single-leaved, clothed in tubular
    sheaths; pseudobulbs absent ....................................... 5
4b. Shoots otherwise .................................................. 6

5a. Sheaths lepanthiform: ribbed, imbricating, the ostium dilated,
    its margin thickened-ciliate at ×10 ........... G4 Lepanthes group (5)
5b. Sheaths plain tubular ............... G5 core Pleurothallidinae (15)
    (within G5: blade densely pubescent → Dresslerella; sheaths
     hispid → Myoxanthus, Echinosepala; apex tridenticulate → cf.
     Stelis, §8.21)

6a. Terrestrial; perennating organ subterranean or at the soil
    surface; leafy shoot seasonal ..................................... 7
6b. Perennating organ an aerial pseudobulb or persistent leafy
    stem .............................................................. 8

7a. Perennating organ a tuberoid; one dig resolves it .... G6 Habenaria
7b. Perennating organ a corm or corm-like pseudobulb at the
    surface ......... G7 Terrestrial geophytes: Bletia, Eulophia,
                       Liparis, Malaxis (4)

8a. Pseudobulbs present ............................................... 9
8b. Pseudobulbs absent: canes, fans, or short leafy stems ............ 14

9a. Pseudobulb hollow, ant-inhabited (basal ostium)
    .......................... G8 Caularthron, Myrmecophila (2)
9b. Pseudobulb solid ................................................. 10

10a. Pseudobulbs superposed, each new one from the apex of the
     last ............................................ G9 Scaphyglottis
10b. Pseudobulbs clustered or spaced along a rhizome ................. 11

11a. Leaves plicate, thin ............................................ 12
11b. Leaves conduplicate, mostly coriaceous .......................... 13

12a. Pseudobulb fusiform, crowned after leaf fall with spiny
     leaf-base stubs; leaves deciduous ......... G10 Catasetinae (4)
     (giant fusiform Cyrtopodium may key here if its old sheaths
      read as spiny; it is >150 cm, Catasetinae are not)
12b. Old inflorescence stalk emerging at the pseudobulb base and
     descending through the substrate ... G11 Coryanthes, Gongora,
                                          Stanhopea (3)
12c. Neither ......... G12 Plicate-bulb residue (12): Bifrenaria,
     Chysis, Coelia, Cyrtopodium, Eriopsis, Galeandra, Galeottia,
     Kegeliella, Koellensteinia, Lacaena, Lycaste, Xylobium

13a. Old inflorescence scar at the pseudobulb apex ... G13 Encyclia,
     Guarianthe, Laelia, Polystachya, Prosthechea, Rhyncholaelia (6)
13b. Scar at the pseudobulb base ......... G14 Brassia, Comparettia,
     Ionopsis, Leochilus, Macradenia, Maxillaria, Notylia, Oncidium,
     Trichopilia (9)
13c. Scar on the rhizome, away from the pseudobulb
     ........................................... G15 Bulbophyllum
13d. Scar position not yet scored ......... G16 residue (4): Dinema,
     Nidema, Oestlundia, Trichocentrum
     (within G16: blade thick-carnose, pseudobulb vestigial →
      Trichocentrum)

14a. Leaves laterally flattened, equitant, in a fan or along the
     stem .......... G17 Fan genera (7): Cryptarrhena, Erycina,
     Lockhartia, Macroclinium, Ornithocephalus; plus the loose
     (not strictly equitant) fans of Cochleanthes and Huntleya
14b. Leaf solitary, terete, on a short stem .......... G18 Brassavola
14c. Canes with thin plicate non-articulate leaves ... G19 Plicate
     canes (5): Corymborkis, Elleanthus, Epistephium, Psilochilus,
     Sobralia
     (within G19: venation reticulate → Epistephium, one look)
14d. Canes or short stems with conduplicate, mostly articulate
     leaves .......... G20 Conduplicate canes (7): Arpophyllum,
     Dichaea, Dimerandra, Epidendrum, Isochilus, Jacquiniella,
     Nemaconia
     (within G20: persistent distichous sheath ladder → Dichaea,
      Isochilus, Jacquiniella, §8.15)
```

Group G13 includes *Rhyncholaelia* on the `[C]` apex-scar line of §8.23;
that placement moves if verification moves the line.

### 10.3 Group register

| Group | n | Members or pointer | Sharpest next split |
| --- | ---: | --- | --- |
| G1 | 1 | *Vanilla* | — |
| G2 | 1 | *Campylocentrum* | — |
| G3 | 15 | rosette Cranichideae (§8.2) | LSUR-10 variegation; then the hardest residue in the flora (§11.5) |
| G4 | 5 | *Andreettaea*?, *Karma*, *Lepanthes*, *Lepanthopsis*, *Trichosalpinx* | SHTH-02 ostium detail; SIZE-01 |
| G5 | 15 | core Pleurothallidinae | LSUR-04/05 indumentum; LFRM-08; S-CAN-07; Karremans 2016 needed |
| G6 | 1 | *Habenaria* | — |
| G7 | 4 | *Bletia*, *Eulophia*, *Liparis*, *Malaxis* | LFRM-02 ptyxis; SIZE-01; ECOL-11 savanna |
| G8 | 2 | *Caularthron*, *Myrmecophila* | SIZE-01 giant → *Myrmecophila* `[C]` |
| G9 | 1 | *Scaphyglottis* | — |
| G10 | 4 | Catasetinae | vegetative terminal unit expected; floral refinement only |
| G11 | 3 | *Coryanthes*, *Gongora*, *Stanhopea* | near-VTU vegetatively |
| G12 | 12 | plicate-bulb residue | REMN-04; STEM-05 taper; SIZE-01 |
| G13 | 6 | apex-scar Laeliinae | SHTH-11 spathe; STEM-13 clothing |
| G14 | 9 | base-scar conduplicate | REMN-04; LARR-01 leaf count |
| G15 | 1 | *Bulbophyllum* | — |
| G16 | 4 | REMN-02 unscored residue | LFRM-03 carnose → *Trichocentrum*; rest needs Flora Mesoamericana |
| G17 | 7 | fans | ARCH-05; SIZE-01 miniature |
| G18 | 1 | *Brassavola* | — |
| G19 | 5 | plicate canes | LFRM-12 reticulate → *Epistephium* |
| G20 | 7 | conduplicate canes | SHTH-14 ladder; STEM-01 polymorphism note for *Epidendrum* |

### 10.4 What the demonstration shows, in effective numbers

Scored with the machinery of §16.5 under a uniform prior (a deliberate
worst-case choice — no abundance data is used):

| Quantity | Value |
| --- | --- |
| γ, effective genera before the key | 104 |
| Terminal groups (⁰D of the partition) | 20 |
| β, effective number of terminal groups (¹D) | 14.31 |
| α, mean effective genera per group (¹D) | 7.27 |
| Check: α × β | 104.00 exactly |
| Single-genus groups | 6 |
| Largest groups | 15, 15, 12 |
| Maximum decisions to a terminal group | 9 |

Reading: nine cheap observations — most answerable from three meters
away — reduce 104 genera to effectively 14.3 distinct groups, leaving on
average 7.3 effective genera of residual ambiguity, and the partition
identity α × β = γ holds exactly, which is the invariant of §16.5 doing
its job on real numbers. The gap between β = 14.31 and ⁰D = 20 measures
how unbalanced the hand-built groups are (three groups hold 40% of the
genera).

What it proves: even sparse Tier 1 assertions already carve the flora into
field-usable piles without flowers. What it does not prove: correctness of
any `[C]` membership; species-level separability; or that α can be driven
near 1 for G3, G5, and G12 without new subatomic data and monograph
scoring.

### 10.5 Residual budget: where effort buys α reduction

| Group | n | First subatomic questions | Expected path |
| --- | ---: | --- | --- |
| G3 rosette Cranichideae | 15 | S-LSF-07 variegation; S-LGE morphometrics; S-LAT petiole; S-ECO formation | partial splits; a residual multi-genus VTU is likely and acceptable |
| G5 core Pleurothallidinae | ~15 | S-SHT components; S-LSF indumentum; S-LGE-08 apex; S-CAN-07 annulus; S-SIZ miniature thresholds | several singletons + small VTUs |
| G12 plicate-bulb residue | ~12 | S-PBL taper and clothing; S-RPR-01 scar position; S-SIZ giants; S-LAT-11 deciduousness | Catasetinae and Stanhopeinae cores peel off; middle needs monograph scoring |
| G14 base-scar conduplicate | ~9 | S-RPR-01; S-LAT-01 leaf count; S-LGE-05 thickness; twig-ecology priors | needs monograph |
| G20 conduplicate canes | ~7 | S-SHT-09 ladder; branching; articulation; blade fleshiness; nodal rooting | *Epidendrum* is a mixture model, not a VTU |

Work order for α reduction: G3 → G5 → G12 → G14/G20 → polymorphic giants
→ roots and anatomy last. *Epidendrum* and broad *Maxillaria* concepts are
**mixture models**, not VTUs: they require species-level regional scoring
and hierarchical posteriors, and the printable key will duplicate them
under several leads (§16.8).

---

## 11. Smallest volumes, diagnostic bundles, and vegetative terminal units

### 11.1 What "smallest volume" means here

The project's aim is to partition the feature space into the smallest
volumes. Mixed categorical data do not occupy ordinary Euclidean volume,
so three related objects make the aim precise:

**A morphological cell** is a conjunction of admissible predicates with
non-empty extent:

```text
cell = ∧_k (variable_k ∈ allowed_set_k)
extent(cell) = { organisms or taxon mass satisfying the cell }
```

Reported per cell: `n_extent` (organisms or species in the cell);
`⁰D_taxa` (genus concepts with positive mass); `¹D_taxa` (Hill effective
number of genera, §16.5); `support` (stability across bootstrap and
source draws); and `cost` (minimum observation cost to place a plant in
the cell). A useful diagnosis is a **low-cost cell with small `¹D_taxa`
and high support**, not merely a rare conjunction.

**The posterior residual volume** after evidence is the Hill profile of
the posterior over genera (§16.5): how many genera effectively remain.

**A formal concept** `(extent, intent)` is a closed cell: no attribute
can be added without shrinking the extent (§15.2). Smaller extent means a
more specific diagnosis; smaller intent means fewer observations to get
there. The two are in tension, and the object worth optimizing is the
pair.

### 11.2 Worked diagnostic bundles

Each of the following reads directly off §8, and each is expressed only
in Tier 1 vegetative characters. A bundle of size *k* with a one-genus
extent is a *k*-character diagnosis.

| Bundle | Extent | Size |
| --- | --- | --- |
| `ARCH-01 = monopodial` ∧ `ARCH-12 = clasping roots` | *Vanilla* | 2 |
| `ARCH-01 = monopodial` ∧ `ARCH-12 = none` | *Campylocentrum* | 2 |
| `STEM-14 = superposed` | *Scaphyglottis* (+ *Polystachya* part) | 1 |
| `STEM-10 = hollow` ∧ `STEM-11 = ants` | *Caularthron*, *Myrmecophila* | 2 |
| `LSUR-04 = pubescent over whole blade` ∧ `ARCH-17 = ramicaul` | *Dresslerella* | 2 |
| `LFRM-12 = reticulate` | *Epistephium* | 1 |
| `ROOT-13 = tuberoid` | *Habenaria* | 1 |
| `SHTH-01 = lepanthiform` | *Lepanthes*, *Lepanthopsis*, *Trichosalpinx*, *Karma* (+ *Andreettaea*?) | 1 |
| `STEM-13 = spiny persistent leaf bases` ∧ `LFRM-02 = plicate` | Catasetinae: *Catasetum*, *Clowesia*, *Cycnoches*, *Mormodes* | 2 |
| `LARR-03 = equitant fan` ∧ `STEM-02 = absent` | *Cryptarrhena*, *Erycina*, *Lockhartia*, *Macroclinium*, *Ornithocephalus* | 2 |
| `REMN-02 = descends through substrate` ∧ `LFRM-02 = plicate` | *Coryanthes*, *Gongora*, *Stanhopea* | 2 |

Eleven bundles, none longer than two characters, none requiring a flower,
none requiring more than a hand lens, together resolving or nearly
resolving 20 of 104 genera. This is the concrete demonstration that a
vegetative-first key is feasible rather than merely desirable — subject,
like everything in §8, to primary-source verification.

### 11.3 Minimum-cost diagnoses as hitting sets

For genus *g*, each admissible observation-state eliminates a set of
rival genera. A diagnosis is a low-cost cover of all rivals:

```text
minimize  Σ_k c_k z_k
s.t.      every rival eliminated by some selected observation;
          gates satisfied; methods allowed; layers ∈ {V, R-if-present}
```

Minimal generators of singleton formal concepts (§15.2) are the special
case where elimination is deterministic. Diagnoses are ranked by total
observation cost, not cardinality — a two-character diagnosis requiring a
dissection is worse than a three-character one visible at arm's length —
and near-optimal alternatives are always kept for field use, because the
optimal bundle's organ may be missing on the plant at hand.

### 11.4 VTU declaration is governance-gated

| Term | Definition |
| --- | --- |
| Temporary residue | Group still large because measurements or sources are missing |
| Vegetative terminal unit (VTU) | After adequate sampling and protocols, no admissible V/R character separates the members at target confidence |

A multi-genus set may be declared a VTU only when all of the following
hold: every member has completed the source-complete genus foundation
(§19, Phase 2); within-genus variation is modeled for polymorphic members
(Phase 3); all pilot-mandatory subatomic variables have been attempted or
gated; no admissible unused V/R character has expected discriminating
power above threshold at acceptable cost; a botanist's sign-off is
recorded; and the optional floral refinements are listed on the VTU card.
Until then it is a temporary residue. VTUs are first-class outputs, not
failures: the count and size distribution of VTUs is *the* headline
quality metric for a vegetative key, and each VTU card names the floral
character that would resolve it as an optional layer F refinement.

### 11.5 The hardest group, named in advance

The fifteen rosette Cranichideae share: no aerial stem, no pseudobulb, a
basal rosette of thin convolute petiolate leaves, non-articulate leaves,
fleshy fascicled roots, terrestrial habit. Six Tier 1 characters, one
state each, all shared. Vegetative separation rests almost entirely on
variegation (§8.18), blade morphometrics (S-LGE), petiole geometry,
indumentum at ×10, and ecology.

Naming this in advance sets expectations for review, and it tells the
acquisition plan where the marginal hour of reading is worth most: the
Spanish-language Cranichideae literature — Salazar's treatments in Flora
Mesoamericana and the *Lankesteriana* corpus — is where resolution for
this group will come from, if it exists at all. A residual multi-genus
VTU here is a likely and acceptable outcome.

---

## 12. Encoding, provenance, and the prototype-03 data contract

### 12.1 The source of truth is long-form

A wide genus × character spreadsheet is an **export**, never the store.

| Table | Grain |
| --- | --- |
| `taxon_concept` | accepted concept + accordingTo + included species |
| `organism` | voucher or living individual |
| `observation_event` | time, place, observer, method set |
| `character` | versioned L2 definition + gates + burden vector |
| `subatomic_variable` | L0/L1 definitions + maps to characters |
| `state` | multilingual controlled vocabulary |
| `assertion` | organism/taxon × variable value + status + evidence |
| `source` | bibliographic object + language + claim fitness |
| `evidence_fragment` | quotation, page, image, measurement file |
| `question` | L3 interface object |
| `genus_model` | generated posterior summaries only |

JSON serves interchange and review; a normalized relational store is
safer for many-to-many evidence and versioning; columnar analytical files
are generated products, never the only provenance store.

### 12.2 Provenance minimum on every morphological assertion

Nothing enters the matrix without a provenance record, and the pipeline
rejects cells that lack one.

```json
{
  "assertion_id": "urn:uuid:...",
  "taxon_concept_id": "Epidendrum@chase2015",
  "variable_id": "S-LGE-02",
  "character_id": "LFRM-18",
  "value": {"kind": "interval", "min": 12.0, "max": 45.0, "unit": "mm"},
  "status": "scored",
  "basis": "explicit",
  "source_id": "SRC-19a",
  "locator": {"work": "Fieldiana 26", "page": "…", "bhl_page": "…"},
  "verbatim": "…",
  "language": "en",
  "translation": "…",
  "confidence": "B",
  "original_name": "Epidendrum …",
  "mapped_name": "Epidendrum",
  "estimator": "species-proportion",
  "asserted_by": "…",
  "asserted_on": "2026-08-07"
}
```

- `basis ∈ {explicit, measured, coded_from_image, derived, inferred}`.
  An inference never masquerades as a quotation.
- `verbatim` preserves the source's own wording in its own language;
  translation is separate and attributed.
- Assertions read from pre-modern nomenclature always store both the
  original and the mapped name (§19, risk 9).
- Where sources disagree, both readings are recorded as a conflict and
  surfaced in a report; the pipeline never silently chooses.

### 12.3 The term lexicon

The controlled vocabulary is what replaces regex extraction over prose.
Each canonical term carries its definition, its synonyms, the
misspellings actually observed in working corpora, and — critically — the
organs it may attach to:

```json
{
  "term": "compressed",
  "quality": "cross-sectional form",
  "definition": "Flattened, usually laterally.",
  "synonyms": ["flattened", "comprimido"],
  "observed_misspellings": ["compessed"],
  "valid_entities": ["pseudobulb", "ramicaul", "stem", "leaf blade", "root"]
}
```

`valid_entities` is what makes extraction sound: a term is accepted only
once attached to a permitted organ, because `terete` on a ramicaul and
`terete` on a leaf blade are different facts. Spanish terms belong in the
lexicon from the start (*pseudobulbo*, *coriáceo*, *envainador*,
*ramicaule*, *equitante*, *conduplicado*, *plicado*, *caespitoso*), with
author-specific false friends noted; Portuguese terms are added for
wide-ranging genera when Brazilian revisions are the best source.
Historical Latin and English equivalents, definitions with diagrams, and
mappings to Plant Ontology / PATO / FLOPO complete the record. Observed
misspellings are recorded rather than corrected in place — the corpus is
evidence, and evidence is not edited; the lexicon absorbs the noise.

### 12.4 Quantitative storage

Orchid dimensions span three orders of magnitude, from a 5 mm
*Platystele* leaf to a 2 m *Sobralia* cane. Every length, width, and area
is stored as a log₁₀ mm interval with a typical value, never a point
estimate. Bands are key-export conveniences, not evidence. Ratios live
beside their parents in one derivation block (§3.1, rule 2). Continuous
traits are normalized with **biological** ranges, not sample min/max that
shift when one giant *Sobralia* is added.

### 12.5 File contract for prototype-03

`prototype-03/` is the implementation target. Required layout:

| Path | Hand-edited | Content |
| --- | --- | --- |
| `prototype-03/data/taxa.json` | yes | 104 concepts + synonymy map, historical names → modern |
| `prototype-03/data/sources.json` | yes | source register with language and claim fitness (§18) |
| `prototype-03/data/characters.json` | yes | the L2 dictionary of §5 |
| `prototype-03/data/subatomic.json` | yes | the S-* register of §6 |
| `prototype-03/data/states.json` | yes | EN/ES lexicon + valid entities |
| `prototype-03/data/gates.json` | yes | applicability DAG |
| `prototype-03/data/scores.jsonl` | yes | assertions (§12.2) |
| `prototype-03/data/questions.json` | yes | L3 question bank |
| `prototype-03/derived/*` | no | matrix, distances, lattices, keys — rebuilt from data on every run |
| `prototype-03/snapshots/*` | no | frozen portal pulls, WCVP dumps |

Validation rejects: any scored cell without provenance; any cycle in the
gate graph; any derived variable scored without its parents; and any
declared applicability rule that does not surface as an implication in
the populated matrix (§15.4). Derived artifacts are never hand-edited.
The dictionary is DELTA-compatible and exportable to the TDWG SDD
standard, so the matrix can be driven through IKey+ or Xper3 for
cross-checking against the project's own key generator — agreeing with an
independent implementation is cheap validation.

---

## 13. Distance measures

### 13.1 There is no single "orchid distance"

Different tasks compare different objects:

| Task | Objects | Tool |
| --- | --- | --- |
| Structure discovery | taxon state-distributions | block-balanced mixed dissimilarity (§13.2) |
| Identification | specimen reports vs taxon model | predictive log-score / Bayes risk (§16) |
| Character redundancy | variables | conditional association, observer co-error |
| Source audit | score sets | agreement and conflict rates |
| Shape-only comparison | landmark or outline configurations | Procrustes / elliptic Fourier, after a declared scaling policy |

Gower's general coefficient for mixed data is the correct starting point
for the first row and only the first row; identification is a prediction
problem, not a symmetric distance between two taxa.

### 13.2 Block-balanced mixed dissimilarity

For taxa *i*, *j*, organ blocks *b* (architecture, rhizome, pseudobulb,
cane/ramicaul, sheath, leaf insertion, blade geometry, blade surface,
roots/underground, size, remains, ecology), and variables *k*:

```text
D(i,j) = Σ_b W_b A_ijb D_ijb  /  Σ_b W_b A_ijb

D_ijb  = Σ_{k∈b} w_k a_ijk d_ijk  /  Σ_{k∈b} w_k a_ijk
```

- `a_ijk` = 1 only when the pair is comparable for variable *k* (§13.4);
- `A_ijb` = 1 only when block *b* meets a minimum coverage for the pair;
- `W_b` prevents a facet with many near-duplicate mm measurements from
  dominating the total;
- ecology is down-weighted or held out of a pure-morphology `D`.

Call `D` a **dissimilarity**; test the triangle inequality and inspect
PCoA negative eigenvalues before making metric claims. Report the
pairwise-coverage matrix alongside the distance matrix: with per-pair
denominators, two genera can appear similar merely by both being poorly
known, and a distance matrix with unreported coverage is not
interpretable. Pairs below a pre-registered coverage threshold are
declared incomparable rather than given a number.

### 13.3 Per-variable dissimilarities

| Type | `d_ijk` |
| --- | --- |
| Symmetric binary | mismatch |
| Asymmetric binary | Jaccard-style on presence where shared absence is uninformative (shared absence of a spur is not evidence of kinship) |
| Nominal, distribution-valued | Hellinger distance between state distributions (preferred; a true metric, bounded, degrades exactly to the matching coefficient when both taxa are monomorphic) or total variation |
| Ordinal, distribution-valued | 1-D Wasserstein on scored ranks |
| Continuous / interval | Wasserstein or energy distance after robust scaling on log values |
| Landmark shape | Procrustes under a declared scaling policy |
| Outline | elliptic Fourier distance, validated against human sorts |

Ontology semantic distances (Resnik, Lin, Jiang–Conrath over PATO)
organize meanings; they do not automatically encode morphometric or
perceptual distance. Use them for lexicon alignment, never as a drop-in
`d_ijk` on field measurements.

### 13.4 Inapplicability algebra (non-negotiable)

1. Unexamined for either taxon → exclude the variable; reduce coverage.
2. Inapplicable in both → **not** similarity; exclude.
3. Entity present in one, absent in the other → compare the presence
   character **once**.
4. Do **not** also compare the gated child characters as extra absences —
   that counts the same absence many times, and the inflation correlates
   with the taxon's own morphology (28 pseudobulb characters against the
   60 genera without pseudobulbs), biasing the distance rather than
   merely adding noise.
5. `variable` cells compare as distributions, not as modal states.

### 13.5 Two weight families that never mix

| Family | Use |
| --- | --- |
| Discovery weights | balance organs; optionally report phylogenetic signal; redundancy-corrected |
| Key costs and reliabilities | time, equipment, damage, observer error, availability |

Using key weights for clustering produces clusters of convenience rather
than of biology; using discovery weights for the key produces a key that
asks about velamen syndromes. The pipeline stores both and requires the
caller to name which one it wants.

### 13.6 The shape plane

Simple symmetrical plane outlines are located by two continuous
quantities — the length:width ratio and the position of the widest point
(Systematics Association Committee 1962). LFRM-04's labels are derived
from LFRM-05/06 coordinates, so `linear` and `lanceolate` become near
neighbours, `linear` and `orbicular` maximally distant, and a taxon
recorded only as "lanceolate" enters the analysis as the centroid of the
lanceolate cell with an uncertainty radius — vague prose becomes vague
data rather than a false point. The same ladder treatment applies to any
quality with an intrinsic order written down as words: texture, rigidity,
consistency, exposure.

### 13.7 Validating a distance measure

A distance measure is a modelling choice and must be tested: coverage
sensitivity (re-mask 10% of scored cells; large movement means the
measure reports coverage, not morphology); stability across posterior
draws of polymorphic cells; source leave-one-out; weight perturbation
(±25%, rank correlation of resulting matrices); and an expert spot-check
— twenty genus pairs, half predicted near and half far, put to a botanist
blind. The last is the only test that can detect a measure that is
internally consistent and biologically wrong. Recovery of the subtribal
classification is a descriptive diagnostic, not a pass/fail oracle:
vegetative characters can be useful and homoplastic at the same time.

---

## 14. Clustering and structure discovery

### 14.1 What clustering is for

Clustering audits structure and errors; it does **not** build the key.
Uses: finding the natural field-recognition groups a user-facing key
should be organized around; exposing scoring errors as taxa that land in
implausible places; mapping convergence and vegetative homoplasy; showing
where organ blocks disagree; and nominating residue targets for focused
data collection.

### 14.2 Sequence

1. Freeze a taxon-concept and matrix version.
2. Drop variables failing definition, coverage, or inter-observer
   agreement thresholds.
3. Keep one representation per derivation family (§3.1, rule 2).
4. Build block-balanced `D` across posterior or imputation draws.
5. Run PAM/k-medoids (medoids are real genera, which makes clusters
   explainable to a botanist) and average-linkage hierarchical clustering
   as interpretable baselines.
6. Use PCoA or NMDS for visualization, with explicit non-Euclidean
   diagnostics. Ward linkage is not valid directly on an arbitrary
   Gower-like dissimilarity, and a Euclidean correction applied for
   ordination does not automatically make a Ward tree meaningful.
7. Produce a consensus co-clustering matrix across draws.
8. Review high-instability taxa and blocks before interpreting anything.

### 14.3 Evaluation

Report silhouette and medoid distances; stability under observation,
species, and source resampling (cluster-wise bootstrap recovery below 0.5
is dissolution; 0.6–0.75 unstable; above 0.75 defensible); consensus
membership probabilities; sensitivity to block weights `W_b`; and
enrichment by tribe, subtribe, habit, and evidence coverage — as
description, with chance-corrected indices. A cluster that vanishes when
one source is withheld is a source imprint, not a morphological
discovery. In a matrix this size, the commonest cause of a badly placed
genus is a mis-scored cell, not an interesting biological fact — outliers
get their scores re-read first.

### 14.4 Supervised companions

Under species-level holdout (§17.1): regularized multinomial models;
shallow cost-sensitive trees; calibrated nearest-distribution
classifiers. Feature importance is unstable under correlated predictors —
report grouped permutation importance, not one ranked list of individual
variables.

---

## 15. Frequent sets, closed sets, and diagnoses

### 15.1 Multiple formal contexts

A single Boolean incidence matrix cannot honestly represent polymorphism,
uncertainty, and missing data at once. Build several:

| Context | Incidence rule |
| --- | --- |
| Certain | state strongly supported for the taxon |
| Possible | state still plausible for the taxon |
| Specimen | rows are individuals, not taxa |
| Bootstrap | incidence drawn from the posterior state distributions |

Missing and inapplicable cells are never ordinary `false`; they are
excluded from support counting.

### 15.2 Formal concept analysis

With genera as objects and (character, state) pairs as attributes, a
formal concept `(A, B)` pairs an extent `A` (the genera) with a closed
intent `B` (exactly the attributes shared by all of `A`). This is
precisely the "smallest volume" object of §11.1, and the **minimal
generators** of a concept — the minimal attribute subsets whose closure
is the full intent — are exactly the shortest diagnoses: the minimal
generators of the concept whose extent is {*Scaphyglottis*} are the
shortest observation sets that identify *Scaphyglottis*.

The parameterization is counter-intuitive and easy to get wrong:
**diagnosis needs rare itemsets, not frequent ones.** An itemset
supported by 60 genera describes Orchidaceae; one supported by a single
genus is a diagnosis. Enumeration therefore runs at `min_support = 1`
with tractability bought by capping intent size — but support-1
enumeration is a license to *enumerate*, never to *accept*: a one-record
pattern is also the pattern most vulnerable to error.

### 15.3 Stability filters before acceptance

A candidate diagnosis is promoted only when it survives bootstrap
resampling of polymorphic cells (retain patterns present in ≥90% of
draws), source withholding, and observer-agreement thresholds on its
member characters; depends on no unresolved taxon identifications; and,
when many patterns are screened, validates on held-out species. Certain
and possible lattices are compared before promotion.

### 15.4 Implications as a data-quality instrument

The implication basis of the certain context (Duquenne–Guigues) serves
three audits: real biological implications (`hollow pseudobulb →
ant-occupied`) reveal redundancy — if exceptionless, one character is
free information after the other; **near**-exceptionless implications are
audit leads — often a scoring error in the one exception, though
biological exceptions are common enough that the lead is investigated,
never auto-corrected; and every declared applicability rule should
surface as an implication — one that does not was mis-declared. This is
the cheapest automated proofreading available for a matrix of this size,
and it needs no ground truth.

---

## 16. Bayesian adaptive key in effective-number currency

### 16.1 Generative model

```text
P(g, s, x, y | z, m) = P(g | z) · P(s | g, z) · P(x | s, z) · P(y | x, m)
```

for genus *g*, species *s*, true states *x*, reported observations *y*,
encounter context *z*, and method *m*. Species and true states are
integrated out for genus identification; parameter uncertainty is
propagated, not collapsed.

### 16.2 Dependence

Vegetative characters are correlated, so naive Bayes with ad-hoc
mutual-information discounts is not a coherent likelihood and is not the
shipped model. The starting model is **block likelihoods** — joint models
within each organ block (architecture, pseudobulb, sheath, leaf geometry,
leaf surface, roots, remains), independence across blocks — upgraded to
tree-augmented or latent-factor structure only when calibration data
exist to support it.

### 16.3 Priors

| Mode | Use |
| --- | --- |
| Regional neutral | equal mass on in-scope genera — for evaluating pure morphology |
| Field encounter | coordinates, elevation, habitat, audited detection (ECOL-20 and §9 envelopes) |
| Herbarium | models the collection process |
| User checklist | an explicit local list |

The interface shows the user when location changed the prior. A genus is
never set to zero probability merely because an occurrence portal is
empty nearby, and abundance is never multiplied into both the character
likelihood and the genus prior (§3.6).

### 16.4 Observer model

The likelihood includes `P(report | truth, method, user class)` — the
per-character confusion structure, including "unsure" and "not visible"
responses. It is diagonal-heavy for sympodial/monopodial and distinctly
not for acute-versus-acuminate. Until user trials estimate it (§17.2),
uncertainty is widened and outputs are labeled uncalibrated; the `O`
observability scores of §5 are a stand-in, not a confusion matrix.

### 16.5 Residual uncertainty as effective numbers

For the posterior `p` over genera, the Hill number

```text
qD(p) = ( Σ_g p_g^q )^(1/(1−q)) ,    ¹D(p) = exp( −Σ_g p_g ln p_g )
```

is the **effective number of remaining candidate genera** (Jost 2006).
The key starts (uniform prior) at ¹D = 104 and every observation drives
it down.

| Order | Meaning in the key |
| --- | --- |
| ⁰D | count of genera with nonzero support — worst-case logic of a classical key |
| ¹D | effective number of plausible genera — the default currency |
| ²D | inverse concentration on the leading candidates |
| ∞D | 1 / max posterior |

Effective numbers are the reporting currency throughout because they are
directly interpretable — "effectively 6.3 genera remain" means something
to a user mid-key; nats do not — and because the framework's consistency
conditions become free invariant checks on the implementation (§16.6).

### 16.6 Question selection as multiplicative diversity partitioning

Observing character *k* at a node splits the posterior into answer
branches *e* with probabilities P(e). Set

```text
γ_k = ¹D(p)                       (effective genera before the question)
α_k = exp( Σ_e P(e) · H(p | e) )  (effective genera remaining per branch,
                                   averaged)
β_k = γ_k / α_k                   (effective number of distinct branches
                                   the question creates)
```

This is exactly the multiplicative partition γ = α × β (Jost 2007), with
key branches in the role of communities. `β_k` answers, in plain terms:
*into how many genuinely distinct groups does this question divide the
remaining candidates?* A binary character with balanced, non-overlapping
branches has β = 2; one whose states are confounded by polymorphism has
β ≈ 1 and is not worth asking. Node selection maximizes answerability ×
utility per burden:

```text
k* = argmax  A_k · u(ΔR_k) / C_k
```

where `A_k` is the probability the user can answer, `C_k` the burden
(§3.7), and `ΔR_k` the expected drop in ¹D or in an explicit
misidentification loss. With entropy utility this reproduces classical
expected-information-gain ranking at every node — but the implementation
gains an invariant: **α_k × β_k = γ_k must hold to numerical precision at
every node**, and a violation is a bug in the posterior update. The
multiplicative partition is the only one in which α and β are
independent, which is what licenses comparing β across nodes with very
different numbers of remaining genera. Branch leakage — a polymorphic
genus putting mass on several branches — is reported per node as the
overlap among branch-conditional posteriors (the C_qN
multiple-community overlap family at q = 2; Jost, Chao & Chazdon 2011):
0 means the branches partition cleanly; values near 1 mean the question
sorts almost nobody.

### 16.7 Policy graph, constraints, robustness

The primary product is a policy graph, not a binary tree: skipped
questions and converging evidence reach the same posterior state by
different paths. It supports multistate answers; skip (posterior
unchanged, next-best question offered — the main argument for the
multi-access interface); unsure and not-visible answers; deliberate
confirmatory redundancy near ties (§4.3); recovery suggestions; and
out-of-scope rejection.

Hard constraints on required paths: no layer F or L question; no layer R
question unless the trace is visible; no question whose gate is
unsatisfied; no destructive act without permission; no question below the
tested agreement threshold for the user class; no raw + derived double
counting; and no zero-probability elimination from a single ordinary
field observation unless the state is structurally impossible and
verified.

Seasonality is handled by conditioning: given a date, persistence-1
characters like leaf duration are conditioned on it; without one, the
likelihood marginalizes over season, which correctly widens the posterior
rather than silently assuming leaves are present. When evidence becomes
internally inconsistent, the policy computes posterior predictive checks
by block, identifies the observation whose retraction most reduces
conflict, offers a clearer protocol or an independent confirmatory
character, preserves the original answer in the audit trail, and allows
an out-of-scope result rather than forcing a revision.

### 16.8 Stopping, abstention, and the printable export

Stop with a single genus only when pre-registered conditions jointly
hold: calibrated posterior above target; posterior odds over the runner-up
above target; stability under model and source uncertainty; support from
at least two independent organ blocks; and expected value of the next
admissible question below its cost. A ¹D threshold guards against
declaring victory on max-posterior alone while three genera still share
the mass. Otherwise the key returns the smallest calibrated candidate set
meeting the coverage target, with probabilities, supporting and
contradicting observations, the next useful vegetative question if any,
and optional layer R/F/L refinements. Where exchangeability is credible,
conformal calibration turns held-out scores into candidate sets with
explicit marginal coverage; coverage on habitat, genus, and rare-taxon
strata is audited separately.

The printable dichotomous key is generated as a constrained export:
restricted binary wording, explicit "not seen" exits, a maximum
observation burden, no hidden dependence on prior answers, and controlled
taxon duplication — a genus appears under several leads when its minority
state mass exceeds 0.15, and total leaf count ÷ genera is reported as a
quality metric, since unbounded duplication is how automated keys become
unreadable. Optimal cost-sensitive trees are NP-hard, so construction is
greedy expected utility with bounded look-ahead and beam search over the
first levels, cross-checked against IKey+/Xper3-style exports.

### 16.9 The q-profile requirement

A key tuned only at q = 1 with an abundance prior is efficient for common
plants and slow or wrong precisely for the rare genera a botanist most
wants flagged — the same rare-species sensitivity argument that governs
diversity measurement in conservation. Every headline metric is therefore
reported at q ∈ {0, 1, 2} — the **q-profile** — and a key whose q = 0 and
q = 2 profiles diverge sharply is trading worst-case coverage for
average-case speed. That trade must be a reviewed decision, not an
artifact.

Terminal-partition metrics in the same currency: resolution = β of the
terminal partition at q ∈ {0, 1, 2}; residual ambiguity = α of the
terminal partition (1.0 is perfect; the cost of vegetative-only relative
to a full key is `α_veg / α_full`); VTU severity = each VTU's ⁰D (genus
count) and its ¹D under the local prior — a four-genus VTU where one
genus holds 90% of the mass is mild, and the register should say so.

---

## 17. Validation

### 17.1 Leakage-resistant test units

Randomly splitting rows from the same species or the same photographed
individual between training and test produces optimistic results.
Progressively harder holdouts:

| Test | What is held out |
| --- | --- |
| Repeat-observation | one observation event from a known individual |
| Individual | entire individuals |
| Population | entire localities |
| Species | all evidence for one regional species, retaining its genus |
| Source | one flora, monograph, website, or image contributor |
| Time | observations collected after the model freeze |

Species holdout is mandatory: the key must identify a genus from
variation, not memorize descriptions of the species used to build the
profile.

### 17.2 Reference set

A vouchered validation collection of non-flowering plants or documented
image sets: representative genera and all expected VTUs; multiple species
for the polymorphic giants; juveniles and mature plants; wet and dry
condition; intact and damaged examples; field backgrounds and controlled
views; and difficult non-orchid lookalikes plus out-of-scope orchids.
Reference identifications are established independently (flowers,
vouchers, DNA where appropriate) and those channels stay excluded from
the vegetative input. The disagreements between a botanist and a novice
keying the same specimens are not merely quality assurance — they are the
training data for the observer model of §16.4.

### 17.3 Metrics

Top-1 accuracy with confidence intervals on resolvable/unresolvable
strata; calibrated-set coverage; candidate-set size with ¹D and ²D;
abstention and out-of-scope accuracy; expected questions and measured
elapsed time; damage and equipment burden; per-question observer
agreement; reliability curves with Brier and log scores; source
sensitivity; VTU size distribution; printable duplication ratio.

Thresholds are set after a pilot establishes realistic baselines — a
target selected before any vouchered trial is a design aspiration, not
evidence. Initial working aspirations, to be re-set at the pilot:
expected decisions ≤ 10 under the encounter prior; 95th-percentile path
length ≤ 16; top-3 accuracy ≥ 0.95 at a 10% per-character observation
error; duplication ≤ 1.5.

### 17.4 Comparative baselines

(1) morphology only, layer V; (2) V plus visible layer R; (3) V plus
optional floral F; (4) the coarse-character representation without the
subatomic layer; (5) a conventional human-authored regional key where
accessible; (6) simple nearest-neighbour and shallow-tree baselines.
These quantify the marginal value of old inflorescences, flowers,
atomization, and the Bayesian policy separately.

### 17.5 Deterministic and auditable analysis

Every analysis is a pure function of its inputs. Pinned: taxon-concept
release; source snapshots with retrieval dates; character and question
versions; random seeds; software environments; train/test partitions; and
input hashes for every generated artifact. Occurrence-portal results are
captured as versioned snapshots before use. A key that changes because a
portal changed yesterday is not reproducible.

---

## 18. Source register and governance

### 18.1 Register

Each source carries a stable ID, a declared **scope of authority** — what
it may legitimately be cited *for* — a language, and a verification
status (`verified`: bibliographic details confirmed against the publisher
or the resource itself; `unverified`: recorded from reference knowledge,
confirm before external citation; `not-consulted`: required but not yet
available).

#### Tier A — generic circumscription (authoritative for genus-level states)

| ID | Source | Scope of authority | Status |
| --- | --- | --- | --- |
| SRC-01 | Pridgeon, A.M., Cribb, P.J., Chase, M.W. & Rasmussen, F.N. (eds). *Genera Orchidacearum*, vols 1–6. Oxford University Press, 1999–2014. | Genus-level descriptions of vegetative and floral organs; the global standard | not-consulted |
| SRC-02 | Chase, M.W. et al. (2015). An updated classification of Orchidaceae. *Botanical Journal of the Linnean Society* 177(2): 151–174. doi:10.1111/boj.12234 | Subfamily/tribe/subtribe placement; the external partition for §14.3 | verified |
| SRC-03 | Dressler, R.L. (1993a). *Phylogeny and Classification of the Orchid Family*. Dioscorides Press. | Comparative vegetative morphology of the family | unverified |
| SRC-04 | Dressler, R.L. (1993b). *Field Guide to the Orchids of Costa Rica and Panama*. Cornell University Press. | Generic keys for an adjacent flora built on naked-eye and hand-lens features; the closest published prior art | verified |
| SRC-05 | Karremans, A.P. (2016). Genera Pleurothallidinarum. *Lankesteriana* 16(2): 219–241. | Generic delimitation of the 20 Pleurothallidinae genera in scope | unverified |
| SRC-06 | Bogarín, D. et al. (2019). Phylogenetic comparative methods improve the selection of characters for generic delimitations in a hyperdiverse Neotropical orchid clade. *Scientific Reports* 9: 15098. doi:10.1038/s41598-019-51360-0 | Character-selection methodology; scored vegetative states for the *Lepanthes* clade | verified |
| SRC-07 | McLeish, I., Pearce, N.R. & Adams, B.R. (1995). *Native Orchids of Belize*. A.A. Balkema. | The in-scope flora; the Belize-specific check (not the first monograph pass — it does not describe genera at facet-SHTH resolution) | unverified |
| SRC-08 | Ackerman, J.D. Orchidaceae. Smithsonian National Museum of Natural History (PDF). | Neotropical generic treatment | verified |
| SRC-09 | Balick, M.J., Nee, M.H. & Atha, D.E. (2000). *Checklist of the Vascular Plants of Belize*. Mem. New York Botanical Garden 85. | Regional taxon list | unverified |

#### Tier A-R — regional literature (substantially Spanish)

The working language of Neotropical orchid systematics is Spanish. **A
source list for Central American orchids that is entirely in English is
prima facie incomplete** (§18.4).

| ID | Source | Lang | Scope of authority | Status |
| --- | --- | --- | --- | --- |
| SRC-14 | *Flora Mesoamericana*, Vol. 7(2): Orchidaceae (2023). Missouri Botanical Garden Press. 842 pp. ISBN 978-1-935641-29-2. Prepared by C. Ulloa Ulloa, H.M. Hernández, G. Davidse, F.R. Barrie, S. Knapp & R. Dressler; 270 genera, 2,336 species. | es | **The** authoritative regional flora, covering Belize entire; first source for every morphological cell | verified (publisher page) |
| SRC-15 | Carnevali, G. et al. (2001). A synopsis of the orchid flora of the Mexican Yucatán Peninsula… *Harvard Papers in Botany* 5: 383–466. | en/es | The one published checklist whose biogeographic scope (Yucatán Peninsula Biotic Province) matches this project's | verified |
| SRC-16 | Carnevali, G. et al. (eds) (2010). *Flora ilustrada de la Península de Yucatán: Listado florístico*. CICY. | es | Regional floristic list; its bibliography is a route to further Spanish sources | verified |
| SRC-17 | Hágsater, E. & Santiago, E. (eds) (1990– ). *Icones Orchidacearum*. Herbario AMO. | es/en | The standard monographic series for *Epidendrum*, the largest and most polymorphic genus in scope | verified |
| SRC-18 | *Lankesteriana*, Jardín Botánico Lankester, Universidad de Costa Rica. Open access. | es/en | Principal serial for Neotropical orchid systematics; Pleurothallidinae generic literature | verified |
| SRC-19 | Ossenbach, C. (2009). Orchids and orchidology in Central America: 500 years of history. *Lankesteriana* 9(1–2). | en | Bibliographic history; fastest route to pre-modern sources | verified |
| SRC-19a | Ames, O. & Correll, D.S. (1952–53). Orchids of Guatemala. *Fieldiana: Botany* 26(1–2). | en | Classic regional monograph, 527 species in 89 genera; includes what was then British Honduras. **Open access in full on the Biodiversity Heritage Library** (bibliography 2380; doi:10.5962/bhl.title.2380) | verified, open access |
| SRC-19c | Ames, O. & Correll, D.S. (1965). Supplement to Orchids of Guatemala, and British Honduras. *Fieldiana: Botany* 31(7). | en | **The only monographic treatment whose title names this flora.** Open access on BHL (bibliography 4816; doi:10.5962/bhl.title.4816) | verified, open access |
| SRC-19d | Ames, O. & Correll, D.S. (1985). *Orchids of Guatemala and Belize*. Dover reprint of the above, ISBN 0-486-24834-8. | en | One-volume desk convenience; content identical to the originals | verified |
| SRC-19b | Dix, M.A. & Dix, M.W. *Orquídeas de Guatemala*. Universidad del Valle de Guatemala. | es | Annotated checklist for the adjacent flora | unverified |
| SRC-23 | Hamer, F. (1982–85). Orchids of Nicaragua. *Icones Plantarum Tropicarum*, fasc. 7–13, plates 601–1300. Marie Selby Botanical Gardens. | en | Adjacent-flora treatment; one full-page line drawing per species showing habit, pseudobulbs, and leaves — directly scoreable for vegetative states. **Published by the project's host institution** | verified |
| SRC-24 | Hamer, F. (1974, 1981). *Las orquídeas de El Salvador*, 3 vols. | es/en | Bilingual adjacent-flora treatment, same illustrated format | unverified |
| SRC-25 | *Selbyana*, Marie Selby Botanical Gardens (1975–2016). ISSN 0361-185X. | en | Epiphyte biology and Neotropical orchid systematics; in-house archive | unverified |
| SRC-26 | Epidendra digital botanical database, Jardín Botánico Lankester. | es/en | Digitized protologues, types, and illustrations; availability intermittent — confirm before relying on it | unverified |

Spanish-language holdings to check before the register is considered
closed: the AMO *Orquídeas de México* series and Soto Arenas' treatments;
Espejo-Serna & López-Ferrari, *Las monocotiledóneas mexicanas*; the CICY
bibliography in full; the *Lankesteriana* back catalogue filtered to
Belize, Guatemala, and Chiapas; and the AMO, CICY, BIGU, and USCG
herbarium databases. Portuguese-language literature matters for the
wide-ranging genera (*Bulbophyllum*, *Epidendrum*, *Maxillaria*,
Pleurothallidinae) at lower priority.

#### Tier B — anatomy and micromorphology

| ID | Source | Scope of authority | Status |
| --- | --- | --- | --- |
| SRC-10 | Porembski, S. & Barthlott, W. (1988). Velamen radicum micromorphology and classification of Orchidaceae. *Nordic Journal of Botany* 8: 117–137. | The 12 velamen syndromes; tilosomes; sole authority for ROOT-17/18 | verified |
| SRC-11 | Watson, L. & Dallwitz, M.J. The families of flowering plants: Orchidaceae. DELTA. | Family-level character-state inventory: habit, velamen, leaf arrangement/texture/venation/articulation, stegmata, raphides, stomata, C3/CAM | verified |
| SRC-12 | Stern, W.L. (2014). *Anatomy of the Monocotyledons X: Orchidaceae*. Oxford University Press. | Comparative anatomy of the family | unverified |
| SRC-13 | Exemplar vegetative-anatomy studies: *Pabstiella* (Pleurothallidinae), *Flora* 2024; *Bulbophyllum sterile*, *Lankesteriana* 18(1). | Scoring-method exemplars for facet MICR | verified |

#### Tier C — nomenclature and distribution only

Not admissible as morphological authorities; citing them for a
morphological state is a validation error.

| ID | Source | Scope of authority | Status |
| --- | --- | --- | --- |
| SRC-20 | Plants of the World Online (POWO), Kew. | Accepted names, synonymy, native range, elevation records (§9) | verified |
| SRC-21 | World Checklist of Vascular Plants (WCVP), Kew. | Accepted names; distribution at TDWG level 3; dated bulk snapshots | verified |
| SRC-22 | International Plant Names Index (IPNI). | Nomenclatural acts, authorship, protologue citation | verified |
| SRC-27 | Tropicos, Missouri Botanical Garden. | Names, specimens, bibliography — not characters without a voucher or cited treatment | verified |

#### Tier D — aggregators and leads (verify before use)

| ID | Source | Scope of authority | Status |
| --- | --- | --- | --- |
| SRC-30 | OrchidSpecies.com (J. Pfahl). | Lead generation only; frequently reproduces protologue wording, which makes it valuable, but unrefereed and noisy — every state must be confirmed against Tier A or the protologue | verified |
| SRC-31 | Biodiversity Heritage Library. | Protologue and monograph retrieval; cite the contained work, not BHL as author | verified |
| SRC-32 | American Orchid Society. | Terminology, photographs, education — not regional circumscription | verified |
| SRC-33 | GBIF and iNaturalist. | Occurrence hypotheses, phenology, licensed images for the encounter prior — never unfiltered absences, identifications, or abundance | unverified |

Method and tooling references (Gower; Podani; Hyafil & Rivest; Payne &
Preece; Ganter & Wille; closed-itemset mining; IKey+; Xper3; DELTA; SDD;
FLOPO; Phenoscape; inapplicable-data coding; the shape grid; Jost's
diversity papers) appear in §22.

### 18.2 Claim-specific authority

Source fitness is assigned per claim, not as one global tier:

| Claim | Preferred evidence |
| --- | --- |
| Accepted name / synonym | Kew WCVP/POWO + taxonomic revision |
| Regional presence | flora/checklist, then vouchered herbarium record, then curated portal |
| Generic morphology | revision, monograph, regional flora genus description |
| Within-genus variation | species treatments, vouchers, population field scores |
| Anatomy | peer-reviewed anatomy tied to vouchers |
| Ecology | labels and plots; observation kept separate from generalization |
| Character usability | blind repeated scoring on real specimens |
| Local prior | audited occupancy/detection, not raw portal counts |
| Elevation | distribution databases are legitimate here (§9) |

### 18.3 The institutional advantage

The project runs at Marie Selby Botanical Gardens, whose research library
exists precisely for this literature and which published SRC-23 and
SRC-25. Flora Mesoamericana 7(2) and *Genera Orchidacearum* should be
requested through the Selby library before any purchase; the *Icones
Plantarum Tropicarum* fascicles are in-house, and Hamer's plates are a
fast visual cross-check whenever a written description is ambiguous about
habit or pseudobulb form. Source acquisition is a library-request path,
not a generic internet problem.

### 18.4 Language coverage as a data-quality signal

Every source and every provenance record carries a language. A
per-character report gives the proportion of cells whose evidence is
English-only, and **a character or genus whose morphological evidence is
100% English is flagged for review** — not because the English sources
are wrong, but because the Spanish-language regional literature, where
the primary descriptions of Mesoamerican taxa mostly live, has not been
reached, so the evidence base is untested rather than confirmed. The flag
is a search-gap indicator, with two symmetrical cautions: English-only is
not proof a score is wrong, and citing a Spanish source does not by
itself make a score correct.

---

## 19. Data acquisition and implementation path

### 19.1 Order of work

1. **Immediately: score vegetative states for all genera from Ames &
   Correll (SRC-19a + SRC-19c) via the Biodiversity Heritage Library.**
   Zero cost, zero delay, explicit Belize coverage, genus descriptions
   with keys. Priced-in caveat: the nomenclature is 1952/1965 — much of
   what it treats as *Epidendrum*, *Pleurothallis*, or *Oncidium* has
   since been split — so every extracted state passes through a committed
   synonymy map (POWO/WCVP, a legitimate Tier C use) from the name Ames &
   Correll used to the accepted genus. The map is a reviewed, reusable
   artifact, and every such cell stores both names (§12.2).
2. **In parallel: obtain Flora Mesoamericana 7(2) through the Selby
   library** (purchase only if that fails). On arrival it becomes the
   arbiter wherever it and Ames & Correll disagree; both readings are
   kept under the conflict protocol.
3. **Cross-check residual disagreements against *Genera Orchidacearum***
   (SRC-01), also via the Selby library.
4. **Take *Epidendrum* from *Icones Orchidacearum* (SRC-17) and
   Pleurothallidinae from SRC-05/SRC-18** — the twenty hardest genera
   rest exactly on the sheath and ramicaul characters of facets SHTH and
   S-SHT.
5. **Replace the §9 elevation envelopes with cleaned Belize-specific
   occurrence records** (SRC-33) and build the ECOL-20 encounter prior
   from the same pull — as separate artifacts, so prevalence is not
   counted twice.
6. **Verify the §8 index**, starting with the §8.25 queue (the
   assertions already suspected of being wrong). Each line has three
   outcomes: confirmed (upgrade with the new source), corrected (record
   the correction and source), or unresolvable (record as a conflict).
   The corrected fraction, broken down by original confidence code, is a
   direct measurement of how far generic reasoning can be trusted in this
   flora.
7. **McLeish (SRC-07) as the Belize-specific check** on the regional
   sources.
8. **Anatomy last, and only for surviving VTUs.** There is no point
   sectioning roots for genera already resolved.
9. **Run the §7 protocols on vouchered living material** for the G3, G5,
   and G12 residues.

Step 1 is unblocked today.

### 19.2 Scoring protocol

Score at genus rank from a genus description into the assertion store
with full provenance; never score a genus from one species. Where a
source gives a range ("leaves 1–3"), record the range and the
`expert-uniform` estimator, not a midpoint. Where sources disagree,
record both under `conflict`; resolution is a botanist's decision, made
once, recorded with a rationale. Two independent scorers work a 20-genus
overlap sample, with agreement (Cohen's κ) reported per character —
characters below κ = 0.6 have a definition problem, not a scorer problem,
and the definition gets rewritten. Every cell carries a language (§18.4).

### 19.3 Phases

| Phase | Content | Exit criterion |
| --- | --- | --- |
| 0 — Concepts and names | Freeze the three geographic scopes; reconcile the 104 genera to a classification release (proposal: Chase et al. 2015 with Flora Mesoamericana overrides logged); resolve *Andreettaea*; commit `taxa.json` | No modeled genus without a concept and an included regional species list |
| 1 — Ontology pilot | Load characters, gates, subatomic register; write bilingual protocols for ~80–130 high-availability layer V variables; pilot-score 10 morphologically diverse genera plus confusers from Ames & Correll plates | No cyclic gates; no raw/derived double scoring; κ plan defined |
| 2 — Source-complete genus foundation | Full SRC-19a/19c pass; SRC-14 pass; conflict log; import all §8 lines as `legacy_unverified` and adjudicate; coverage report by genus × facet × language | Every genus linked to ≥1 authoritative regional morphological source |
| 3 — Within-genus variation | Species-level scoring for *Epidendrum*, *Maxillaria* concepts, Pleurothallidinae, rosette Cranichideae, and the α-dominating residues; hierarchical posteriors replace `expert-uniform` wherever data exist | — |
| 4 — Discovery | Freeze a matrix release; distances, consensus clustering, certain/possible/bootstrap concept analysis; diagnosis register with stability reports | — |
| 5 — Adaptive key pilot | Block-likelihood policy graph; novice and specialist timing and confusion studies on vouchered sterile material; dichotomous export; pre-registered calibration and coverage targets met | — |
| 6 — Expand by value of information | Spend new scoring only where it reduces documented residual ambiguity: G3 → G5 → G12 → polymorphic giants → roots/anatomy last | — |
| 7 — Reproducibility discipline | Analyses as pure functions of pinned inputs (§17.5); portal pulls snapshotted before use | — |

### 19.4 Week-1 executable package

| Day | Deliverable |
| --- | --- |
| 1 | Create the `prototype-03/data/` skeleton (§12.5) with empty valid schemas |
| 1 | Commit draft `taxa.json` from the 104-genus working list with the *Andreettaea* flag open |
| 2 | Build the historical-name synonymy map stub; link BHL bibliography IDs for SRC-19a/19c |
| 2–3 | Encode the §8.2 group partition and the §8 backbone as `legacy_unverified` assertions |
| 3 | Encode the §6.3 subatomic register and the presence-character gates |
| 4 | Score 10 pilot genera from Ames & Correll plates and descriptions through the map |
| 5 | Coverage-report script: genus × facet × status, with language flags |
| 5 | Regenerate the §20 readiness scorecard from data files, not prose |

No clustering, no key generation, no floral work in week 1.

---

## 20. Readiness scorecard

Claims about readiness are measured against committed project artifacts,
not prose ambition.

| Dimension | Target for the key pilot | Current state | Status |
| --- | --- | --- | --- |
| Taxon concepts reconciled | 100% of modeled genera | 104 working names; *Andreettaea* open; no `taxa.json` | **Fail** |
| Geographic scopes coded | 3 scopes with polygon or rule | Described in prose only | **Fail** |
| Character ontology versioned | ≥80 pilot layer V variables with gates, machine-readable | 218 characters defined in this document; no machine file | **Partial** |
| Subatomic variables with protocols | ≥120 field minimum | Specified (§6–§7); not encoded | **Partial** |
| Morphological cells from a primary monograph | ≥1 authoritative regional source per genus | 0 cells in any machine store | **Fail** |
| Index assertions imported for adjudication | All §8 lines as `legacy_unverified` | Prose only | **Fail** |
| Elevation / encounter priors | Belize-specific cleaned occurrences | 52 range-wide genus envelopes (§9), provisional | **Partial** |
| Bilingual lexicon | EN/ES core vegetative terms | Fragments only | **Fail** |
| Historical-name synonymy map | Complete for Ames & Correll names | Not started | **Fail** |
| Observer confusion matrices | Pilot user classes | None | **Fail** |
| Adaptive policy implementation | Runnable on a frozen matrix | None | **Fail** |
| Feasibility demonstration | Group lattice from published assertions | §10: 104 → 20 groups, α = 7.27 | **Pass (demonstration only)** |

Reading: the architecture and the feasibility *argument* are strong; the
*data and software* are not. The correct next move is Phase 0–2
acquisition, not further character invention without sources.

---

## 21. Risks, open questions, and governance inputs

### 21.1 Risks

| # | Risk | Mitigation |
| --- | --- | --- |
| 1 | Primary sources hard to obtain | Downgraded: Ames & Correll open on BHL; Flora Mesoamericana in print (2023) and the Selby library is the natural route (§18.3) |
| 2 | Genus-level scoring hides species variation | Hierarchical distributions (§3.6); controlled duplication in the export (§16.8) |
| 3 | Vegetative homoplasy vs the classification | Expected, not a defect; two weight families (§13.5); subtribal recovery is descriptive only |
| 4 | Rosette Cranichideae may not resolve vegetatively | Named in advance (§11.5); the honest output is a VTU, not a forced split |
| 5 | Observer error unknown until trials | Confusion matrices from §17.2; outputs labeled uncalibrated until then |
| 6 | Taxon-list errors (*Andreettaea*) | Phase 0 reconciliation is a hard gate |
| 7 | Scope creep from genus to species | Hold at genus; the species key is a different problem with a different data requirement |
| 8 | `[C]` assertions mistaken for data | Confidence codes; `legacy_unverified` import; the §19.1 step 6 verification |
| 9 | 1952 nomenclature silently mis-mapped to modern genera | The synonymy map is a committed, reviewed artifact; both names stored per cell |
| 10 | Range-wide elevation used as Belize occupancy | §9.2 caveats; §2.1 band truncation; replacement by local records (§19.1 step 5) |
| 11 | Abundance-tuned key degrades rare-genus performance | The q-profile requirement (§16.9) makes the trade visible |
| 12 | Pseudo-replication of derived traits | The level hierarchy and derivation blocks (§3.1) |
| 13 | A required path quietly needs an old inflorescence | Layer R separation (§1.3) |
| 14 | Store fills without provenance | §12 validation rejects |
| 15 | Design continues without data | The scorecard (§20) and the week-1 package (§19.4) |
| 16 | English-only literature search | The language flag (§18.4) |

### 21.2 Open questions for the botanist

1. Which generic circumscription defines release 1 — Chase et al. (2015),
   Flora Mesoamericana, or traditional broader genera? This changes
   *Pleurothallis* and *Maxillaria* substantially, and with them the
   genus count.
2. What terminates the key: a calibrated posterior threshold (0.90?
   0.95?), a ¹D threshold, a fixed top-k list, or the joint rule of
   §16.8?
3. Should the working region be the Yucatán Peninsula Biotic Province,
   defined biogeographically, rather than a political boundary? The
   project's framing implies yes.
4. Is destructive scoring (tuberoid digs, cutting a pseudobulb)
   acceptable anywhere in the field product, or layer L regardless of
   information content?
5. Which herbaria and living collections can supply vouchered
   non-flowering validation material (§17.2)?
6. Is the effective-number (Hill number) framing the preferred review
   currency, and at which orders should headline numbers be quoted?
   ({0, 1, 2} proposed.)
7. Should the encounter prior come from cleaned GBIF/iNaturalist counts
   (auditable, roadside-biased), expert abundance classes (calibrated,
   unauditable), or both with disagreements displayed?
8. Does the Selby library hold Flora Mesoamericana 7(2), *Genera
   Orchidacearum*, and the *Icones Plantarum Tropicarum* fascicles, and
   can the fascicles be scanned for project use?
9. Which user profiles are v1 products: household observer, field
   botanist, orchid specialist, herbarium worker?
10. Are some misidentifications costlier than others (conservation
    consequences, false commonness), so that the stopping rule should
    carry an explicit loss?
11. What sampling thresholds and sign-off should the VTU declaration
    rule (§11.4) require?
12. Which source conflicts deserve formal taxonomic adjudication rather
    than coexistence in the evidence store?

### 21.3 Governance inputs algorithms must not invent

Classification release; geographic boundary; damage policy;
living-versus-herbarium scoring rules; calibrated coverage targets
(90/95/99%); VTU declaration thresholds; conflict adjudication authority;
user-profile set; validation collection access; misidentification loss.
These are versioned inputs, decided by people and recorded, never
defaults chosen implicitly by code.

### 21.4 Evidence boundaries

| Class | Content |
| --- | --- |
| Sourced foundations | The regional source scope; family-level vegetative vocabulary; ontology roles; the named methods (Gower, FCA, Hill numbers, block likelihoods, conformal calibration) |
| Project proposals requiring botanical validation | The character and subatomic registers; state partitions; gates; protocols; burden vector; organ blocks; VTU rule; acquisition phases |
| Unverified empirical claims | Genus membership details in §8; per-genus state distributions; expected VTUs; observer matrices; local priors; attainable accuracy |

No source validates the complete register or proves that a vegetative
genus-level key is possible for every taxon. That conclusion can come
only from the populated matrix and held-out vouchered evaluation.

---

## 22. References

Regional morphology and checklists:

- Ames, O. & Correll, D.S. (1952–53). Orchids of Guatemala. *Fieldiana:
  Botany* 26(1–2). Open access:
  [BHL bibliography 2380](https://www.biodiversitylibrary.org/bibliography/2380);
  [doi:10.5962/bhl.title.2380](https://doi.org/10.5962/bhl.title.2380)
- Ames, O. & Correll, D.S. (1965). Supplement to Orchids of Guatemala,
  and British Honduras. *Fieldiana: Botany* 31(7). Open access:
  [BHL bibliography 4816](https://www.biodiversitylibrary.org/bibliography/4816);
  [doi:10.5962/bhl.title.4816](https://doi.org/10.5962/bhl.title.4816)
- Ames, O. & Correll, D.S. (1985). *Orchids of Guatemala and Belize*.
  Dover. ISBN 0-486-24834-8.
- Balick, M.J., Nee, M.H. & Atha, D.E. (2000). *Checklist of the Vascular
  Plants of Belize*. Memoirs of the New York Botanical Garden 85.
- Carnevali, G., Tapia-Muñoz, J.L., Jiménez-Machorro, R., Sánchez
  Saldaña, L., Ibarra-González, L., Ramírez, I.M. & Gómez, M.P. (2001).
  Notes on the flora of the Yucatán Peninsula II: a synopsis of the
  orchid flora of the Mexican Yucatán Peninsula and a tentative checklist
  of the Orchidaceae of the Yucatán Peninsula Biotic Province. *Harvard
  Papers in Botany* 5: 383–466.
- Carnevali, G., Tapia-Muñoz, J.L., Duno de Stefano, R. & Ramírez
  Morillo, I.M. (eds) (2010). *Flora ilustrada de la Península de
  Yucatán: Listado florístico*. CICY.
- *Flora Mesoamericana*, Volumen 7, Parte 2: Orchidaceae (2023). Missouri
  Botanical Garden Press. 842 pp. ISBN 978-1-935641-29-2.
  [MBG Press](https://www.mbgpress.org/product-p/9781935641292.htm)
- Hágsater, E. & Santiago, E. (eds) (1990– ). *Icones Orchidacearum*.
  Herbario AMO, Mexico City. [herbarioamo.org](https://herbarioamo.org/)
- Hamer, F. (1982–85). Orchids of Nicaragua. *Icones Plantarum
  Tropicarum*, fascicles 7–13. Marie Selby Botanical Gardens.
- McLeish, I., Pearce, N.R. & Adams, B.R. (1995). *Native Orchids of
  Belize*. A.A. Balkema.
- Ossenbach, C. (2009). Orchids and orchidology in Central America: 500
  years of history. *Lankesteriana* 9(1–2).

Classification, genera, and character systems:

- Bogarín, D., Pérez-Escobar, O.A., Karremans, A.P., Fernández, M.,
  Kruizinga, J., Pupulin, F., Smets, E. & Gravendeel, B. (2019).
  Phylogenetic comparative methods improve the selection of characters
  for generic delimitations in a hyperdiverse Neotropical orchid clade.
  *Scientific Reports* 9: 15098.
  [doi:10.1038/s41598-019-51360-0](https://doi.org/10.1038/s41598-019-51360-0)
- Chase, M.W., Cameron, K.M., Freudenstein, J.V., Pridgeon, A.M.,
  Salazar, G., van den Berg, C. & Schuiteman, A. (2015). An updated
  classification of Orchidaceae. *Botanical Journal of the Linnean
  Society* 177(2): 151–174.
  [doi:10.1111/boj.12234](https://doi.org/10.1111/boj.12234)
- Dressler, R.L. (1993a). *Phylogeny and Classification of the Orchid
  Family*. Dioscorides Press.
- Dressler, R.L. (1993b). *Field Guide to the Orchids of Costa Rica and
  Panama*. Cornell University Press.
- Karremans, A.P. (2016). Genera Pleurothallidinarum: an updated
  phylogenetic overview of Pleurothallidinae. *Lankesteriana* 16(2):
  219–241.
- Pridgeon, A.M., Cribb, P.J., Chase, M.W. & Rasmussen, F.N. (eds)
  (1999–2014). *Genera Orchidacearum*, vols 1–6. Oxford University Press.

Anatomy and micromorphology:

- Porembski, S. & Barthlott, W. (1988). Velamen radicum micromorphology
  and classification of Orchidaceae. *Nordic Journal of Botany* 8:
  117–137.
  [doi:10.1111/j.1756-1051.1988.tb00491.x](https://doi.org/10.1111/j.1756-1051.1988.tb00491.x)
- Stern, W.L. (2014). *Anatomy of the Monocotyledons X: Orchidaceae*.
  Oxford University Press.
- Watson, L. & Dallwitz, M.J. The families of flowering plants:
  Orchidaceae. DELTA.
  [delta-intkey.com](https://www.delta-intkey.com/angio/www/orchidac.htm)

Descriptive-data standards and ontologies:

- Dallwitz, M.J. (1980). A general system for coding taxonomic
  descriptions. *Taxon* 29: 41–46.
- Hoehndorf, R. et al. (2016). The Flora Phenotype Ontology (FLOPO).
  *Journal of Biomedical Semantics* 7: 15.
  [doi:10.1186/s13326-016-0107-8](https://doi.org/10.1186/s13326-016-0107-8)
- Phenoscape. Guide to character annotation.
  [wiki.phenoscape.org](https://wiki.phenoscape.org/wiki/Guide_to_Character_Annotation)
- Systematics Association Committee for Descriptive Biological
  Terminology (1962). Terminology of simple symmetrical plane shapes.
  *Taxon* 11: 145–156.
- TDWG Structured Descriptive Data (SDD) standard.

Inapplicable data and character coding:

- Brazeau, M.D., Guillerme, T. & Smith, M.R. (2019). An algorithm for
  morphological phylogenetic analysis with inapplicable data. *Systematic
  Biology* 68(4): 619–631.
- Maddison, W.P. (1993). Missing data versus missing characters in
  phylogenetic analysis. *Systematic Biology* 42: 576–581.
- Strong, E.E. & Lipscomb, D. (1999). Character coding and inapplicable
  data. *Cladistics* 15: 363–371.

Distances, diversity, patterns, and keys:

- Burguière, T., Causse, F., Ung, V. & Vignes-Lebbe, R. (2013). IKey+: a
  new single-access key generation web service. *Systematic Biology*
  62(1): 157–161.
  [doi:10.1093/sysbio/sys069](https://doi.org/10.1093/sysbio/sys069)
- Ganter, B. & Wille, R. (1999). *Formal Concept Analysis: Mathematical
  Foundations*. Springer.
- Gower, J.C. (1971). A general coefficient of similarity and some of its
  properties. *Biometrics* 27: 857–871.
- Hyafil, L. & Rivest, R.L. (1976). Constructing optimal binary decision
  trees is NP-complete. *Information Processing Letters* 5(1): 15–17.
- Jost, L. (2006). Entropy and diversity. *Oikos* 113(2): 363–375.
- Jost, L. (2007). Partitioning diversity into independent alpha and beta
  components. *Ecology* 88(10): 2427–2439.
- Jost, L., Chao, A. & Chazdon, R.L. (2011). Compositional similarity and
  beta diversity. In: Magurran, A.E. & McGill, B.J. (eds), *Biological
  Diversity: Frontiers in Measurement and Assessment*. Oxford University
  Press.
- Pasquier, N., Bastide, Y., Taouil, R. & Lakhal, L. (1999). Discovering
  frequent closed itemsets for association rules. *ICDT 1999*.
- Payne, R.W. & Preece, D.A. (1980). Identification keys and diagnostic
  tables: a review. *Journal of the Royal Statistical Society A* 143(3):
  253–292.
- Podani, J. (1999). Extending Gower's general coefficient of similarity
  to ordinal characters. *Taxon* 48: 331–340.
- Stumme, G., Taouil, R., Bastide, Y., Pasquier, N. & Lakhal, L. (2002).
  Computing iceberg concept lattices with Titanic. *Data & Knowledge
  Engineering* 42(2): 189–222.
- Uno, T., Kiyomi, M. & Arimura, H. (2004). LCM ver. 2: efficient mining
  algorithms for frequent/closed/maximal itemsets. *FIMI 2004*.
- Xper3 reference guide for taxonomists. *European Journal of Taxonomy*
  (2025). [Zenodo 15245479](https://zenodo.org/records/15245479)

Websites (discovery and nomenclature; not automatic morphology
authority): [powo.science.kew.org](https://powo.science.kew.org/),
[wcvp.science.kew.org](https://wcvp.science.kew.org/),
[ipni.org](https://www.ipni.org/),
[tropicos.org](https://www.tropicos.org/),
[biodiversitylibrary.org](https://www.biodiversitylibrary.org/),
[orchidspecies.com](http://www.orchidspecies.com/),
[aos.org](https://www.aos.org/), [gbif.org](https://www.gbif.org/),
[inaturalist.org](https://www.inaturalist.org/),
[lankesteriana.org](https://www.lankesteriana.org/),
[herbarioamo.org](https://herbarioamo.org/).

Sources whose register status is `unverified` (§18.1) were recorded from
reference knowledge; confirm bibliographic details before citing them
outside this project.

---

## Prompt

**Focus:**

* **Repository:** .../selby/belize-orchid-genera-key
* **Documentation:** Examine doc/*.md

**Document Enhancement:**

* **Objective:** Improve on the documents *-belize-orchid-characteristic-of-taxa.md by creating a new document <date>-<model-id>-belize-orchid-characteristic-of-taxa.md.

**Botanical Key Development:**

* **Primary Focus:** Vegetative morphology of the Orchidaceae of Belize and surrounding areas.
* **Secondary Focus:** Floral morphology (as an “afterthought” or “refinement”).
* **Reason:** Orchids are rarely in bloom, and orchid taxonomy is predominantly based on floral morphology. The goal is to create a key that classifies plants to the genus level based solely on vegetative characteristics, which are typically the only ones available.

**Elemental Characteristics:**

* **Detail and Scope:** Require significantly more detail and broader scope, potentially described as “atomic” or “subatomic” characteristics.

**Plan of Attack:**

* **Feature Space Mapping:** Identify a large feature space, prioritizing vegetative characteristics.
* **Distance Measures:** Define distance measures over the feature set.
* **Clustering Algorithms:** Partition the feature space into the smallest volumes (more specific to a feature set).
* **Frequent Set Analyses:** Conduct frequent set analyses.
* **Bayesian Tree Creation:** Develop a botanical key (bayesian tree) that efficiently partitions the decision space, minimizing the number of “decisions” (node traversed) to reliably arrive at the most probable leaf node.

**Additional Resources:**

In addition to the local documents, several websites are referenced. These may provide additional information or overlooked sources.

---

## Metadata

### Reseach

```text
generator-name: Claude Code
generator-version: Claude Opus 5
generator-model-token: claude-opus-5
generator-provider: Anthropic
generation-date: 2026-08-06
generator-responsibility: research
```
---

```text
generator-name: Copilot
generator-version: Kimi K2.7 Code
generator-model-token: kimi-k2-7-code
generator-provider: Moonshot AI
generation-date: 2026-08-06
generator-responsibility: research
```

---

```text
generator-name: Claude Code
generator-version: Claude Fable 5
generator-model-token: claude-fable-5
generator-provider: Anthropic
generation-date: 2026-08-07
generator-responsibility: research
```

---

```text
generator-name: GitHub Copilot CLI
generator-version: GPT-5.4
generator-model-token: gpt-5-4
generator-provider: OpenAI via GitHub Copilot
generation-date: 2026-08-07
generator-responsibility: research
```

---

```text
generator-name: GitHub Copilot
generator-version: GPT-5.6 Sol
generator-model-token: gpt-5-6-sol
generator-provider: OpenAI
generation-date: 2026-08-07
generator-responsibility: research
```

---

```text
generator-name: GitHub Copilot CLI
generator-version: Grok 4.5
generator-model-token: grok-4-5
generator-provider: xAI via GitHub Copilot
generation-date: 2026-08-07
generator-responsibility: research
```

---

```text
generator-name: Copilot CLI
generator-version: mai-code-1-flash
generator-model-token: mai-code-1-flash
generator-provider: Microsoft 
generation-date: 2026-08-07
generator-responsibility: research
```

### Synthesis

```text
generator-name: Claude Code
generator-version: Claude Fable 5
generator-model-token: claude-fable-5
generator-provider: Anthropic
generation-date: 2026-08-07
generator-responsibility: synthesis
```


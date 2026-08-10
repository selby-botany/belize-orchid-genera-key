#!/usr/bin/env python3
"""Parse genus and species treatments out of OCR'd page text (Stage D).

Reads `analysis/page_ocr.jsonl` (Stage C) and `manifest/scan_inventory.json`
(Stage A, for page numbers -- Stage C's own output only knows filenames,
not page identity), writes `analysis/genera.jsonl` (machine-readable) and
`analysis/mcleish.genera.md` (the document a botanist actually reads).

This is the core new logic in this project -- neither prior prototype
parsed genus-level structure out of OCR text. Everything here was designed
against, and tested against, the real OCR of `page-050.jpeg` (Psilochilus,
Epistephium), not an assumed idealization of the book's layout. Three
findings from that real page shaped the design directly:

1. Field labels (`ETYMOLOGY`, `NOTE`, ...) are set in small caps in the
   book, and Vision's OCR renders small caps with inconsistent letter
   case ("EtymoLogY", "ETymoLoGY", "NoTE" all appear on one page for the
   same two labels). Matching them case-sensitively would silently miss
   most instances. `_normalize_label` upper-cases before comparing.
2. The running head ("18 Psilochilus" -- genus number and name, no
   trailing period) sits in its own geometric column, at the same page-top
   `mid_y` band as a bare page-number running head ("50"). Reading order
   (sorted by column, then `mid_y`) places it in the middle of the line
   sequence, not at the start -- so it is found by scanning for lines in
   the top `mid_y` band, not by taking the first N lines of the page.
   Critically, it has no period after the number, which is exactly what
   distinguishes it from a real genus header ("18. Psilochilus Barb.
   Rodr.") -- that period is load-bearing, not incidental.
3. Organ-lead words (`Roots`, `Leaves`, `Column`, ...) are not on their
   own lines or in their own paragraphs -- they are ordinary
   sentence-initial capitalized words inside one continuous diagnostic
   paragraph, and OCR line breaks fall mid-sentence and mid-word
   (hyphenated). Finding them requires dehyphenating and rejoining the
   paragraph, then splitting on sentence boundaries, not scanning lines.
4. A running head is not always one OCR line. On the real pilot page 66,
   Vision split "28 Clowesia" into two separate line observations ("28"
   and "Clowesia"), which defeats a pattern matched against one line's
   full text. When that happens there is no continuity signal at all --
   this is treated as a fact to surface (`ambiguous_genus_boundary`), not
   as silent-continue territory, because the first version of this code
   did silently continue and a real synonymy block for Clowesia vanished
   from the pilot run with no trace anywhere.
5. The book's dichotomous key to genera (pages 9-12) is typeset as
   "<number>. <Capitalized word> <descriptive prose>" -- structurally
   identical to a genus header. The full 190-page run (which the pilot's
   sample didn't happen to include) produced 481 "genus" records for 108
   real genera before this was caught; see `_PROSE_WORD_PATTERN`. A second
   pass on the same defect class found two residual cases even after that
   fix: a terse comparative couplet answer with no prose word at all
   ("24. Pollinia 2"; see `_AUTHOR_CAPITAL_PATTERN`), and a large genus
   (Epidendrum) that numbers its own internal species list with the full
   genus name repeated, which is genuinely citation-shaped text and so
   passes both header discriminators -- caught instead by checking
   whether the "new" genus name is the one already open (`build_genus_
   records`).
6. The running head is not always at the page top. Investigating why
   Epidendrum's numbered-species-list continuation pages (183, 185, 187,
   189) were flagged `ambiguous_genus_boundary` despite genuinely
   continuing the same genus found that those specific pages print the
   folio number and running head at the page *bottom*
   (`mid_y` ~0.964-0.965) instead -- the even-numbered pages in the same
   run (182, 184, ...) still print it at the top. `cross_check_running_
   head` and `_is_page_furniture` now check both bands (see
   `BOTTOM_BAND_MID_Y`).
   **This reading of the evidence was wrong, and finding 11 corrects it.**
   The book does not typeset those pages differently; they were scanned
   upside down, which is why the split fell exactly on page parity. The
   two-band check is kept because a chapter-opening page really does
   print a drop folio at the page foot, but it is no longer load-bearing
   for the pages named here.
7. A plate/photo page's caption block and photo-index sidebar have no
   per-line furniture signature -- unlike a folio number or running head,
   their lines read as ordinary sentences ("Figure 25. Eriopsis biloba.
   A: habit, x 2/3; ... Drawn by Beverley Mears from living material in
   Belize.", or a "Photographs" heading followed by a numbered list of
   unrelated species). Undetected, this content fell into whichever
   genus happened to be open at that point in reading order, landing in
   its `SUMMARY` field as if it were diagnostic prose. Found while
   grounding Phase 2's pilot-genus selection in real data: 36 of the 65
   genus records carrying a `SUMMARY` field (55%) contained caption or
   photo-index text, not McLeish's own genus description. A related
   symptom -- bare plate/photo numbers printed outside the running-head
   band ("42", "41", "43", "45"; or several run together with no
   separator, "111112 113114 115") -- is the same root problem: numeric
   sidebar content this parser didn't yet know how to recognize as not
   being body text. Fixed in `_is_page_furniture` (any bare-digit line,
   not just ones in the running-head band, and a lone stray capital
   letter -- a caption panel label split off from its own description by
   OCR) and `_filter_furniture` (a `Figure <N>.` or `Photographs` trigger
   line truncates everything from that point to the end of the given
   span, since both kinds are always trailing content on a plate page in
   this book's layout).
8. A genus header printed alone in its own narrow "tab" column can sit
   physically *after* the next genus's real diagnostic paragraph in plain
   (column, mid_y) reading order, silently attaching that paragraph to
   the *wrong* genus -- not missing data, but a different genus's real
   facts under the current genus's name. Found while extracting Phase 2
   characters from real field text: `Cranichis`'s record contained
   Habenaria's own genus-level description verbatim ("the flowers of
   Habenaria are rather complex..."; its ETYMOLOGY explained "habena
   (reins)", Habenaria's name, not Cranichis's) -- page 40 carries both
   headers, with Habenaria's real paragraph in a column that sorts before
   Habenaria's own header column. The same layout produced the page-142
   Epidendrum-list case already handled (finding 5) and, on inspection,
   likely misattributes part of Trichopilia/Bletia's own boundary the
   same way. Both confirmed real instances share one narrow, specific
   signature: the misattributed content's column is exactly the *next*
   header's column minus one, and it contains a TRIBE/SUBTRIBE heading
   line (finding on `TRIBE_HEADING_PATTERN`, page-050). An automatic fix
   that reliably re-splices only the misattributed lines (not a
   preceding genus's own legitimate trailing content mixed in the same
   column) is a bigger, riskier change than this pass takes on; instead
   `_has_embedded_tribe_heading_before_next_header` detects the exact
   signature and flags the affected record `possible_cross_genus_
   content` -- stopping the silent trust violation (a `complete` record
   with zero flags containing objectively wrong facts) without guessing
   at a repair the evidence doesn't fully support.
9. Large, species-rich genera number their species list instead of
   repeating the bare genus name ("1. Epidendrum acuñae Dressler in Am.
   Orch. Soc. Bull. ...", "10. Habenaria quinqueseta (Michx.) Sw., Adnot.
   Bot.: 46 (1829)."; confirmed on real full-run text for Dichaea,
   Epidendrum, and Habenaria). `find_species_entries` previously only
   matched the bare form; the numbered form fell through entirely, and
   for Epidendrum specifically it also collided with the genus-header
   pattern (finding 5's `_PROSE_WORD_PATTERN`/`_AUTHOR_CAPITAL_PATTERN`
   fix only suppresses that false hit, it doesn't parse the list).
   `_numbered_species_header_pattern` matches it directly, searched
   alongside the bare pattern. A key couplet's abbreviated answer ("7. D.
   panamensis", "9. H. novemfida") never repeats the full genus name, so
   it doesn't collide with this; requiring text after the epithet also
   rejects a bare, citation-less OCR artifact ("156. Epidendrum acuqae",
   page 182 -- a typo'd duplicate of species 1 with nothing following it
   on the line, not a genuine 156th entry). Testing against that real
   text also surfaced a second, silent bug in the *existing* bare
   pattern: Epidendrum's own species 1, "Epidendrum acuñae", has an
   epithet containing ñ, which a plain `[a-z]` class does not match --
   the whole header line failed to match at all, with no error, just a
   quietly unrecognized species. `_LOWERCASE_EPITHET_CHARS` broadens
   both patterns' epithet class to the accented Latin-1 lowercase range;
   Latinized epithets honoring a collector's name (as "acuñae" does, for
   Galé Acuña) are a real, unavoidable source of diacritics here, not a
   one-off worth special-casing instead of fixing at the character-class
   level. `find_genus_headers`/`_PROSE_WORD_PATTERN` are unaffected --
   they never depended on this class.
   Species detection is also, separately, now run on every continuation
   page of a genus's treatment (`build_genus_records`), not only the
   page carrying its own header -- previously `find_species_entries` was
   never even called past the first page, so a species list spanning
   many pages (Epidendrum's own, 181-190) had no chance to be split
   regardless of pattern coverage. A continuation page's content now
   attaches to whichever species is currently open (tracked across
   pages), or to the genus's own fields if none is open yet -- the same
   "species-level facts belong to the species" rule finding 3 already
   established for a single page, extended across a multi-page span.
10. Finding 8's detector only catches the tab-column collision by its
   layout signature, which on the real full run turns out to be a
   minority of the cross-genus swaps actually present. A record's own
   ETYMOLOGY field is a far better witness, and needs no layout evidence
   at all: an etymology *states the word its genus was coined from*, so
   an etymology filed under the wrong genus convicts itself. Erythrodes'
   record derived "corymbos (a corymb)" -- Corymborkis, whose real
   species citations ("Corymborkis forcipigera") sat in the same record;
   Coryanthes' derived "trigonos (three-)" (Trigonidium); Clowesia's
   derived "kata (down)" plus a seta gloss (Catasetum, whose "Catasetum
   integerrimum" citation was likewise present); Coelia's derived "harpe
   (sickle)" (Arpophyllum); Malaxis' derived "liparos (greasy)"
   (Liparis) -- that last one being exactly the page-55 Malaxis/Liparis/
   Vanilla interleaving that finding 8's detector was documented as
   unable to see. `flag_foreign_genus_etymology` runs this as a corpus-
   wide comparison after all records are built, flagging six records
   where the old detector found three, and naming the suspected real
   owner rather than only raising a doubt. Ordinary prose is *not* read
   this way: genus descriptions legitimately name their neighbours
   ("differs from Epidendrum in ..."), and on the real run 33 of the 69
   records mention another captured genus somewhere in their text, so a
   bare mention carries no signal. Two deliberate limits: the owner
   match must be a leading-edge one (a generic interior element like
   "anthos" fits Spiranthes, Elleanthus and Epidanthus equally and
   identifies none of them), and a self-match of any strength clears the
   record. Of the 43 records carrying an etymology, 10 derive their own
   name, 6 derive another captured genus's (the flags), 1 derives
   nothing, and 26 derive neither. That last group is *not* flagged,
   because it is a different defect and the evidence does not identify
   an owner: most of it is a *species*-level etymology sitting under the
   genus heading ("From the Latin maculatus (spotted)" under
   Platythelys, whose species is P. maculata), which misplaces text
   within a genus rather than across two; a few name a person whose
   eponymous genus is outside the captured range (Barkeria under
   Notylia); and at least one (Eulophia, from eu + lophos) is correctly
   filed and merely falls outside what the self-match recognizes -- a
   recall limit that costs nothing here, since it can only withhold a
   flag, never raise a wrong one.
11. Findings 6, 8 and 10 were all reading the same defect through
   different symptoms, and none of them had the cause: **every
   odd-numbered page in this capture batch was scanned upside down.**
   Vision reads rotated text correctly and reports a flat 1.0 confidence
   either way, so nothing upstream complained; only the geometry is
   wrong, and it makes reading order run up the page with the columns
   mirrored. Fixed in Stage C (`ocr_page.swift`, `pageIsUpsideDown`),
   which is where the orientation is known -- not here, where only its
   consequences are visible. What that one fix did to this stage's own
   output, all of it previously attributed to parsing problems:
   `discontinuity` 8 -> 1, `ambiguous_genus_boundary` 4 -> 0,
   `foreign_genus_etymology` 6 -> 1, records reporting `complete`
   52 -> 62 of 69, species entries 194 -> 214. Erythrodes, Coryanthes,
   Clowesia, Coelia and Malaxis were not holding another genus's text
   through any layout collision; they were reading their neighbour's
   column backwards. Coryanthes now carries its own etymology (korys,
   helmet, + anthos, flower) where it carried Trigonidium's.
   The lesson worth keeping: three rounds of detectors here were built
   against symptoms that a single upstream fact explained. Finding 10's
   detector was *right* about the data being wrong, and still had the
   wrong cause -- a flag that reports a real symptom is not evidence
   that the symptom's cause is where the flag lives.
   Two consequences left standing, deliberately not papered over:
   `possible_cross_genus_content` (finding 8) now fires 6 times with at
   most 1 true positive -- every flagged record was read afterwards, and
   Eulophia, Arpophyllum and Corymborkis carry their own correct
   etymologies; that detector's signature has mostly outlived the defect
   it was built for and wants revisiting. Cranichis is the one genuine
   cross-genus swap left in the corpus, and both detectors still catch
   it.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

# Labels as printed (canonical form), matched case-insensitively against
# OCR text -- see module docstring, finding 1.
FIELD_LABELS: frozenset[str] = frozenset(
    {
        "ETYMOLOGY",
        "GENERAL DISTRIBUTION",
        "DISTRIBUTION IN BELIZE",
        "HABITAT",
        "FLOWERING SEASON",
        "NOTE",
    }
)

# Organ-lead words that open a sentence within the diagnostic paragraph.
# Unlike FIELD_LABELS these appear in ordinary sentence case in the real
# OCR text (not small caps), so they are matched case-sensitively against
# the sentence's first word.
ORGAN_LEADS: frozenset[str] = frozenset(
    {
        "Rhizome",
        "Rhizomes",
        "Roots",
        "Root",
        "Stem",
        "Stems",
        "Leaves",
        "Leaf",
        "Inflorescence",
        "Inflorescences",
        "Flowers",
        "Flower",
        "Sepals",
        "Sepal",
        "Petals",
        "Petal",
        "Lip",
        "Column",
        "Capsule",
    }
)

# Catch-all bucket for diagnostic-paragraph sentences that don't start with
# a recognized organ lead (e.g. "This is a monotypic genus..."). Never
# silently dropped -- requirements document, §1.5.
SUMMARY_FIELD = "SUMMARY"

# A numbered, period-terminated genus header: "18. Psilochilus Barb. Rodr."
# The period after the number is the discriminator against the running
# head "18 Psilochilus", which has no period (finding 2).
GENUS_HEADER_PATTERN = re.compile(r"^(\d+)\.\s+([A-Z][A-Za-z-]+)\s+(.+)$")

# A real author citation ("Barb. Rodr.", "Kunth", "R.O. Williams & Summerh.")
# is a handful of capitalized abbreviations/surnames; a dichotomous-key
# couplet ("1. Anther erect, or nearly so; pollinia soft...") has the same
# leading "<number>. Capitalized-word" shape but is followed by ordinary
# descriptive prose. Found on the real full run: pages 9-10 (the book's
# genus key) produced 373 spurious "genus" records this way, on top of the
# real 108 -- every one of them had a common lowercase word in the author
# position ("erect", "mealy", "terrestrial", ...), which no real author
# citation does. Not airtight (an unusually long author string with a
# stray lowercase word would still be rejected), but effective on every
# false positive actually observed.
_PROSE_WORD_PATTERN = re.compile(r"\b[a-z]{4,}\b")

# A second, independent discriminator against the same key-couplet problem:
# some couplets answer with terse comparative text that has no long
# lowercase word at all ("24. Pollinia 2" / "70. Pollinia 2 or 4", found on
# the real full run on pages 10 and 12 -- both still present after
# _PROSE_WORD_PATTERN alone). A real author citation always contains at
# least one capitalized surname/abbreviation; a couplet's numeric-only
# answer never does. Required in addition to, not instead of,
# _PROSE_WORD_PATTERN -- neither alone catches every case observed.
_AUTHOR_CAPITAL_PATTERN = re.compile(r"[A-Z]")

# The informative running-head variant: "<number> <Genus>", no period.
RUNNING_HEAD_PATTERN = re.compile(r"^(\d+)\s+([A-Z][A-Za-z-]+)$")

# Running heads and folio numbers sit within this fraction of page height
# from the top, discovered on page-050 (~0.042-0.043) with headroom.
TOP_BAND_MID_Y = 0.06

# On most of the book the running head sits at the page top, but the
# numbered-species-list pages within Epidendrum (found on the real full
# run, pages 183/185/187/189) print it at the page *bottom* instead
# ("183" / "70 Epidendrum" both found at mid_y ~0.964-0.965). Symmetric
# headroom to TOP_BAND_MID_Y below the page's bottom edge (mid_y=1.0).
BOTTOM_BAND_MID_Y = 0.94

# Tribe/subtribe heading lines ("TRIBE TRIPHOREAE DRESSLER", "SUBTRIBE
# VANILLINAE LINDL.") are printed in full caps -- an OCR-faithful match,
# unlike FIELD_LABELS' small-caps case garbling. Found on page-050 sitting
# between one genus's last field and the next genus's numbered header;
# left unhandled, one bled into the prior genus's NOTE field.
TRIBE_HEADING_PATTERN = re.compile(r"^(TRIBE|SUBTRIBE)\s+.+$")

# An ETYMOLOGY field names the word a genus name was coined from, and the
# book prints that word immediately before its parenthesized gloss --
# "From the Greek onkos (a pad or mass)", "From the Greek kaulos (stem)
# and arthron (joint)". A "Named after <Person>" etymology carries the
# same information in the eponym instead. Both are the raw material for
# `flag_foreign_genus_etymology` (module docstring, finding 10).
ETYMOLOGY_ROOT_PATTERN = re.compile(r"\b([A-Za-z]{3,})\s*\(")
ETYMOLOGY_EPONYM_PATTERN = re.compile(
    r"[Nn]amed after\s+((?:[A-Z][\w.'-]*\s*){1,4})"
)

# Transliteration equivalences between the Greek/Latin root as the book
# spells it and the genus name coined from it: kyknos -> Cycnoches,
# harpe -> Arpophyllum, stefos -> Epistephium. Applied left to right, so
# digraphs collapse before the single-letter substitutions.
_ROOT_EQUIVALENCES = (
    ("ph", "f"),
    ("th", "t"),
    ("ch", "c"),
    ("k", "c"),
    ("y", "i"),
    ("ae", "e"),
    ("oe", "e"),
)

# How much of a root must coincide with a genus name before that genus is
# named as the etymology's likely real owner. Four characters, or the
# whole root bar a trailing inflection ("harpe"/"Arpophyllum" share only
# "arp"), both hold on every real instance; three characters alone does
# not -- on the real full run it additionally proposes maculatus ->
# Macradenia, plani -> Platythelys, cornutus -> Corymborkis and bractea
# -> Brassia, none of which is a real relationship.
_MIN_OWNER_ROOT_PREFIX = 4

# A lowercase epithet character class covering plain ASCII plus the
# accented Latin-1 lowercase range (à-ö, ø-ÿ -- skips the ÷ division sign
# at U+00F7, the one non-letter in that span). Found necessary on the
# real full run: Epidendrum's own species 1 is "Epidendrum acuñae", and a
# plain `[a-z]` class silently fails to match the ñ, splitting the
# epithet match at "acu" and then requiring whitespace that isn't there
# -- the whole header line fails to match at all. Latinized epithets
# honoring a collector's name (as "acuñae" does, for Galé Acuña) are a
# real, unavoidable source of diacritics in this book, not a one-off.
_LOWERCASE_EPITHET_CHARS = "a-zà-öø-ÿ"

# Species header: the genus name (repeated verbatim from the owning
# genus's header) followed by a lowercase epithet. Matching against the
# specific owning genus name -- not a generic Capitalized-lowercase
# pattern -- avoids false positives on body prose like "Plant terrestrial"
# (requirements, §4 item 6).
def _species_header_pattern(genus_name: str) -> re.Pattern[str]:
    return re.compile(
        rf"^{re.escape(genus_name)}\s+"
        rf"([{_LOWERCASE_EPITHET_CHARS}][{_LOWERCASE_EPITHET_CHARS}-]+)\s+(.+)$"
    )


# A numbered species entry: "1. Epidendrum acuñae Dressler in Am. Orch.
# Soc. Bull. ...", "10. Habenaria quinqueseta (Michx.) Sw., Adnot. Bot.:
# 46 (1829)." -- the shape large, species-rich genera use instead of the
# bare form above (confirmed on real full-run text: Dichaea, Epidendrum,
# Habenaria all number their species this way; module docstring finding
# 9). Requires the genus name in full, which is what already lets
# `find_genus_headers` tell this apart from a dichotomous-key couplet's
# abbreviated answer ("7. D. panamensis", "9. H. novemfida" -- never the
# full name). Requiring text after the epithet also rejects a bare,
# citation-less fragment like the real "156. Epidendrum acuqae" (page
# 182, an isolated OCR artifact duplicating species 1's epithet with a
# typo, not a genuine 156th entry) -- there is nothing on that line past
# the epithet for `(.+)$` to match.
def _numbered_species_header_pattern(genus_name: str) -> re.Pattern[str]:
    return re.compile(
        rf"^\d+\.\s+{re.escape(genus_name)}\s+"
        rf"([{_LOWERCASE_EPITHET_CHARS}][{_LOWERCASE_EPITHET_CHARS}-]+)\s+(.+)$"
    )


# Short abbreviations that precede a "." without ending a sentence, drawn
# from real citations on page-050 ("Barb. Rodr.", "Rchb. f."). Best-effort,
# not exhaustive -- sentence splitting is documented as approximate (see
# `split_into_sentences`).
SENTENCE_ABBREVIATIONS = frozenset(
    {
        "Barb", "Rodr", "Rchb", "Fig", "cm", "mm", "ca", "spp", "sp",
        "var", "subsp", "f", "Sw", "Lindl", "Ames", "Kunth", "Hoehne",
        "Mansf", "Williams", "Summerh",
    }
)


def dehyphenate_join(lines: list[str]) -> str:
    """Rejoin OCR line-wrapped text into a paragraph, undoing hyphenation.

    A trailing hyphen on a line is the original typesetting's line-break
    hyphenation (e.g. "creeping rhi-" / "zomes."), not a semantic hyphen,
    so it is removed and the next line joined without a space. This only
    affects how text is *reflowed for reading*; the raw per-line OCR text
    is preserved unchanged in `page_ocr.jsonl` (requirements, §1.3:
    faithful transcription).

    Args:
        lines: OCR line texts, in reading order.
    Returns:
        One paragraph string.
    """
    if not lines:
        return ""
    pieces: list[str] = [lines[0]]
    for line in lines[1:]:
        previous = pieces[-1]
        if previous.endswith("-") and len(previous) >= 2 and previous[-2].isalpha():
            pieces[-1] = previous[:-1]
            pieces.append(line)
            pieces[-2:] = ["".join(pieces[-2:])]
        else:
            pieces.append(" " + line)
    return "".join(pieces).strip()


def split_into_sentences(paragraph: str) -> list[str]:
    """Split a dehyphenated paragraph into sentences.

    Best-effort, not a general-purpose sentence tokenizer (module
    docstring, finding 3): splits on ". " except where the token before
    the period is a known short abbreviation. Real book abbreviations not
    in `SENTENCE_ABBREVIATIONS` will still cause a false split; this is an
    accepted, documented limitation of a prototype, not a claim of
    correctness.

    Args:
        paragraph: Dehyphenated paragraph text.
    Returns:
        List of sentence strings, whitespace-trimmed, empty ones dropped.
    """
    tokens = re.split(r"(\. )", paragraph)
    sentences: list[str] = []
    current = ""
    for index, token in enumerate(tokens):
        if token == ". " and current:
            last_word = re.split(r"[\s(]", current.strip())[-1]
            if last_word in SENTENCE_ABBREVIATIONS:
                current += token
                continue
            sentences.append(current.strip() + ".")
            current = ""
        else:
            current += token
    if current.strip():
        sentences.append(current.strip())
    return [s for s in sentences if s]


def find_genus_headers(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find numbered genus header lines among a page's OCR lines.

    Excludes dichotomous-key couplets, which share the same
    "<number>. Capitalized-word ..." shape as a real genus header (module
    comments on `_PROSE_WORD_PATTERN` and `_AUTHOR_CAPITAL_PATTERN`) -- a
    match is only kept when the text after the leading word reads like an
    author citation: no long lowercase prose word, and at least one
    capital letter (a couplet's terse numeric answer, e.g. "2 or 4", has
    neither prose nor a capital).

    Args:
        lines: Per-line OCR records (`text`, `confidence`, ...).
    Returns:
        List of matches, each `{index, genus_number, genus_name, author,
        confidence}`, in the order found.
    """
    matches = []
    for index, line in enumerate(lines):
        match = GENUS_HEADER_PATTERN.match(line["text"].strip())
        if not match:
            continue
        author = match.group(3).strip()
        if _PROSE_WORD_PATTERN.search(author):
            continue
        if not _AUTHOR_CAPITAL_PATTERN.search(author):
            continue
        matches.append(
            {
                "index": index,
                "genus_number": match.group(1),
                "genus_name": match.group(2),
                "author": author,
                "confidence": line["confidence"],
            }
        )
    return matches


def cross_check_running_head(lines: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find and parse this page's running head, if it carries genus info.

    Scans for lines in the top or bottom `mid_y` band rather than the
    start of reading order, and only the informative "<number> <Genus>"
    variant is returned -- a bare page-number running head carries no
    continuity signal (module docstring, finding 2). Most of the book
    prints it at the top; Epidendrum's numbered-species-list pages print
    it at the bottom instead (module comment on `BOTTOM_BAND_MID_Y`) --
    both are checked rather than assuming one fixed position.

    Args:
        lines: Per-line OCR records for one page.
    Returns:
        `{genus_number, genus_name}` or None if no informative running
        head is present.
    """
    for line in lines:
        if TOP_BAND_MID_Y < line["mid_y"] < BOTTOM_BAND_MID_Y:
            continue
        match = RUNNING_HEAD_PATTERN.match(line["text"].strip())
        if match:
            return {"genus_number": match.group(1), "genus_name": match.group(2)}
    return None


def _is_page_furniture(line: dict[str, Any]) -> bool:
    """True for a line that is page furniture, not body content.

    Covers six kinds found on the real pages: a bare folio number or a
    plate/photo sidebar number (a real diagnostic sentence is never just
    digits, so this applies regardless of position on the page -- module
    docstring, finding 7); an informative running head (confined to the
    top or bottom `mid_y` band -- see `cross_check_running_head`); a
    tribe/subtribe heading, which can appear anywhere between two genus
    blocks; a lone stray capital letter (a caption panel label, e.g. "B"
    alone on its own line, split off from its own description by OCR --
    finding 7 again); and a caption panel-label fragment ("E: column and
    lip, x 10; F: column from front, x 13;" -- a real diagnostic sentence
    never starts with a single letter and a colon) that survives
    `_filter_furniture`'s trailing-block truncation because its own
    `Figure <N>.` trigger line fell on a different page's span (finding 7,
    residual case).
    """
    text = line["text"].strip()
    if TRIBE_HEADING_PATTERN.match(text):
        return True
    if (
        re.match(r"^\d+$", text)
        or re.match(r"^[A-Z]\.?$", text)
        or re.match(r"^[A-Z]:\s", text)
    ):
        return True
    if TOP_BAND_MID_Y < line["mid_y"] < BOTTOM_BAND_MID_Y:
        return False
    return bool(RUNNING_HEAD_PATTERN.match(text))


# A plate/photo caption ("Figure 25. Eriopsis biloba. A: habit, ...") or a
# photo-index sidebar ("Photographs" followed by a numbered species list)
# has no per-line furniture signature -- its lines read as ordinary
# sentences. Both are always trailing content on a plate/continuation page
# in this book's layout, so once the trigger line is found, everything
# from it to the end of the given span is dropped (module docstring,
# finding 7), not just the trigger line itself.
_CAPTION_BLOCK_START_PATTERN = re.compile(r"^(Figure\s+\d+\.|Photographs?\b)")


def _filter_furniture(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop running heads, folio numbers, tribe/subtribe headings, stray
    plate/photo sidebar numbers and letters, and a trailing caption block.
    """
    trimmed = lines
    for index, line in enumerate(lines):
        if _CAPTION_BLOCK_START_PATTERN.match(line["text"].strip()):
            trimmed = lines[:index]
            break
    return [line for line in trimmed if not _is_page_furniture(line)]


def segment_diagnosis(lines: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Split a genus's leading diagnostic paragraph into organ-lead fields.

    Args:
        lines: The diagnostic-paragraph lines (before the first
            FIELD_LABEL span), excluding the genus header line itself.
    Returns:
        Dict keyed by organ lead (or `SUMMARY_FIELD` for unattributed
        sentences), each value `{text, source_image, confidence, status}`.
    """
    if not lines:
        return {}

    paragraph = dehyphenate_join([line["text"] for line in lines])
    mean_confidence = sum(line["confidence"] for line in lines) / len(lines)
    source_image = lines[0].get("source_image", "")

    fields: dict[str, dict[str, Any]] = {}
    for sentence in split_into_sentences(paragraph):
        first_word = sentence.split(" ", 1)[0].rstrip(",;.")
        label = first_word if first_word in ORGAN_LEADS else SUMMARY_FIELD
        entry = fields.setdefault(
            label,
            {
                "text": "",
                "source_image": source_image,
                "confidence": mean_confidence,
                "status": "scored" if label != SUMMARY_FIELD else "uncertain",
            },
        )
        entry["text"] = (entry["text"] + " " + sentence).strip()

    return fields


def segment_fields(lines: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Assign one content span's lines to field labels or organ leads.

    Takes a single already-selected span -- a genus's own lines up to its
    first species header, or one species' own lines -- and segments it in
    one pass: everything up to the first FIELD_LABEL is the diagnostic
    paragraph (organ-lead territory, `segment_diagnosis`); each FIELD_LABEL
    onward is its own field, running to the next FIELD_LABEL or the end of
    the span. Callers are responsible for choosing the right span in the
    first place (module docstring: field labels after a species'
    description belong to that species, not the enclosing genus, on this
    book's own layout convention -- confirmed on page-050, where
    `GENERAL DISTRIBUTION`/`HABITAT`/etc. describe the single species of a
    monotypic genus, not the genus in the abstract).

    Args:
        lines: Per-line OCR records for exactly one content span.
    Returns:
        Dict keyed by FIELD_LABEL or organ lead (or `SUMMARY_FIELD`),
        each value `{text, source_image, confidence, status}`.
    """
    block = _filter_furniture(lines)

    label_starts: list[tuple[int, str]] = []
    for index, line in enumerate(block):
        text = line["text"].strip()
        normalized = re.sub(r"[.\s]+$", "", text).upper()
        for label in FIELD_LABELS:
            if normalized.startswith(label):
                label_starts.append((index, label))
                break

    diagnosis_end = label_starts[0][0] if label_starts else len(block)
    fields = segment_diagnosis(block[:diagnosis_end])

    for position, (line_index, label) in enumerate(label_starts):
        span_end = (
            label_starts[position + 1][0]
            if position + 1 < len(label_starts)
            else len(block)
        )
        span = block[line_index:span_end]
        text = dehyphenate_join([line["text"] for line in span])
        # Strip the label itself (any case) off the front of the text.
        text = re.sub(rf"^{re.escape(label)}\s*\.?\s*", "", text, flags=re.IGNORECASE)
        confidence = sum(line["confidence"] for line in span) / len(span)
        fields[label] = {
            "text": text.strip(),
            "source_image": span[0].get("source_image", ""),
            "confidence": confidence,
            "status": "scored",
        }

    return fields


def find_species_entries(
    lines: list[dict[str, Any]], genus_name: str, start: int, end: int
) -> tuple[list[dict[str, Any]], int | None]:
    """Find species entries nested under a genus, within a line range.

    A species entry is recognized only when its header line repeats the
    owning genus's name verbatim (module docstring, requirements §4 item
    6) -- this is what distinguishes it from body prose that happens to
    start with a capitalized word ("Plant terrestrial..."). Both the bare
    form ("Psilochilus macrophyllus ...") and the numbered form used by
    large genera ("1. Epidendrum acuñae ...", module docstring finding 9)
    are searched for and merged by position -- a genus can in principle
    use either, and mixing them within one genus is treated as a real
    possibility, not assumed away.

    A species block runs to the next species header (or `end`) -- it is
    *not* cut short at a FIELD_LABEL line. On the real pilot page,
    `GENERAL DISTRIBUTION`/`DISTRIBUTION IN BELIZE`/`HABITAT`/
    `FLOWERING SEASON`/a second `ETYMOLOGY` (for the epithet, not the
    genus name)/`NOTE` all appear *after* the species' own description and
    describe that species specifically -- this book bundles a monotypic
    genus's distribution/habitat/etc. under its one species, not under the
    genus header. Stopping the span early was tried first and produced a
    truncated `DISTRIBUTION IN BELIZE` field and fields misattributed to
    the wrong owner; this is the fix, not the original design.

    `author_and_publication` is left as one raw string rather than split
    into the documented `author`/`publication`/`synonymy` trio (data
    document, §5): reliably separating those from citation punctuation
    alone is not something a regex can do with confidence, and guessing
    would violate the "never guess past the point of confidence"
    requirement (requirements, §1.5) worse than under-structuring does.
    Full synonymy text lands in the species' own `fields[SUMMARY_FIELD]`
    alongside the rest of the unattributed description, not discarded.

    Args:
        lines: Full per-line OCR records.
        genus_name: The owning genus's name, exactly as printed.
        start: Index of the first line to search.
        end: Index one past the last line to search (exclusive).
    Returns:
        Tuple of (species records, with `species_name`,
        `author_and_publication`, `_start`/`_end` line-index bounds for
        the caller to segment and then discard; index of the first species
        header found, or None if there are none -- the boundary where the
        genus's own diagnostic paragraph ends).
    """
    bare_pattern = _species_header_pattern(genus_name)
    numbered_pattern = _numbered_species_header_pattern(genus_name)
    headers = []
    for index in range(start, end):
        text = lines[index]["text"].strip()
        match = bare_pattern.match(text) or numbered_pattern.match(text)
        if match:
            headers.append((index, match.group(1), match.group(2)))
    headers.sort(key=lambda header: header[0])

    if not headers:
        return [], None

    species: list[dict[str, Any]] = []
    for position, (line_index, epithet, rest) in enumerate(headers):
        span_end = headers[position + 1][0] if position + 1 < len(headers) else end
        species.append(
            {
                "species_name": f"{genus_name} {epithet}",
                "author_and_publication": rest,
                "_start": line_index + 1,
                "_end": span_end,
            }
        )

    return species, headers[0][0]


def _has_embedded_tribe_heading_before_next_header(
    lines: list[dict[str, Any]],
    block_start: int,
    block_end: int,
    next_header_column: int | None,
) -> bool:
    """Detect a specific tab-column layout collision (module docstring).

    On at least two real pages (40: Cranichis/Habenaria; 142: Trichopilia/
    Bletia), a genus header is typeset alone in its own narrow "tab"
    column, while the *next* genus's real diagnostic paragraph sits in an
    adjacent body-text column that sorts earlier in plain (column, mid_y)
    reading order -- so it silently lands in the *current* genus's block
    instead of the next one's. Both real instances share one exact,
    narrow signature: the misattributed content's column is the next
    header's own column minus one, and a TRIBE/SUBTRIBE heading line (Bletia's
    own module comment on `TRIBE_HEADING_PATTERN`) appears within it.
    This is deliberately narrow -- a tribe heading anywhere in a block is
    common and usually harmless (already filtered as furniture); only
    this exact column-adjacency combination is flagged, to avoid noising
    up the review queue on the many ordinary single-column pages where a
    tribe heading is not a sign of anything wrong.

    Args:
        lines: Full per-page OCR records.
        block_start: Index of this genus's block start (exclusive of its
            own header line).
        block_end: Index one past this genus's block end.
        next_header_column: The column of the next header found on this
            same page, or None when this is the last header on the page.
    Returns:
        True when the collision signature is present.
    """
    if next_header_column is None:
        return False
    for line in lines[block_start:block_end]:
        if (
            TRIBE_HEADING_PATTERN.match(line["text"].strip())
            and line["column"] == next_header_column - 1
        ):
            return True
    return False


def _etymology_roots(text: str) -> list[str]:
    """Collect the words an ETYMOLOGY field derives a genus name from.

    Args:
        text: An ETYMOLOGY field's text, as segmented.
    Returns:
        Every glossed root word ("onkos" in "onkos (a pad or mass)") and
        every capitalized word of a "Named after ..." eponym, in the
        order they appear. Empty when the field derives nothing.
    """
    roots = [match.group(1) for match in ETYMOLOGY_ROOT_PATTERN.finditer(text)]
    for match in ETYMOLOGY_EPONYM_PATTERN.finditer(text):
        roots.extend(
            word for word in match.group(1).split()
            if len(word) > 2 and word[0].isupper()
        )
    return roots


def _normalize_root(word: str) -> str:
    """Fold a root or genus name to a spelling the two can be compared in.

    Args:
        word: A root word, eponym, or genus name.
    Returns:
        Lowercase letters only, diacritics stripped, a leading silent "h"
        dropped, and `_ROOT_EQUIVALENCES` applied.
    """
    folded = unicodedata.normalize("NFKD", word.lower())
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    folded = re.sub(r"[^a-z]", "", folded)
    if folded.startswith("h"):
        folded = folded[1:]
    for source, replacement in _ROOT_EQUIVALENCES:
        folded = folded.replace(source, replacement)
    return folded


def _root_owner_score(root: str, genus_name: str) -> int:
    """Score a root as evidence that `genus_name` is what it derives.

    Deliberately stricter than `_root_self_score`: this score is what
    names a *different* genus as an etymology's real owner, so it takes
    only a leading-edge coincidence (the position a coined name draws its
    first element from), never an interior one -- "anthos" sits inside
    Spiranthes, Elleanthus and Epidanthus alike and identifies none of
    them.

    Args:
        root: A root word or eponym from an ETYMOLOGY field.
        genus_name: The candidate owning genus name.
    Returns:
        The shared prefix length when it reaches `_MIN_OWNER_ROOT_PREFIX`
        or covers all but a trailing inflection of the root; 0 otherwise.
    """
    folded_root = _normalize_root(root)
    folded_name = _normalize_root(genus_name)
    if len(folded_root) < 4 or len(folded_name) < 3:
        return 0
    shared = _shared_prefix_length(folded_root, folded_name)
    if shared >= _MIN_OWNER_ROOT_PREFIX or shared >= len(folded_root) - 1:
        return shared
    return 0


def _root_self_score(root: str, genus_name: str) -> int:
    """Score a root as evidence that it derives the genus it is filed under.

    Looser than `_root_owner_score` on purpose: a compound name's second
    element sits in the *interior* of the name it helps coin (Eulophia
    from eu + lophos, Psygmorchis from psygma + orchis), and any such
    match is enough to conclude the etymology is already where it belongs
    -- the conservative outcome, since it suppresses a flag rather than
    raising one.

    Args:
        root: A root word or eponym from an ETYMOLOGY field.
        genus_name: The genus whose record the etymology is filed under.
    Returns:
        A positive score when the root plausibly derives `genus_name`;
        0 otherwise.
    """
    folded_root = _normalize_root(root)
    folded_name = _normalize_root(genus_name)
    if len(folded_root) < 3 or len(folded_name) < 3:
        return 0
    shared = _shared_prefix_length(folded_root, folded_name)
    if shared >= 3:
        return shared
    if len(folded_root) >= 4 and folded_root[:4] in folded_name:
        return 4
    return 0


def _shared_prefix_length(first: str, second: str) -> int:
    """Count the characters two strings agree on from their start.

    Args:
        first: Left string.
        second: Right string.
    Returns:
        The length of the common leading run, 0 when they differ at once.
    """
    length = 0
    while length < min(len(first), len(second)) and first[length] == second[length]:
        length += 1
    return length


def flag_foreign_genus_etymology(records: list[dict[str, Any]]) -> None:
    """Flag records whose ETYMOLOGY derives a *different* genus's name.

    A mechanical form of the read-it-and-see scan that originally caught
    Cranichis holding Habenaria's description (module docstring, findings
    8 and 10). An etymology is self-verifying evidence in a way ordinary
    description is not: it states the word its genus was coined from, so
    a record filed under Coryanthes whose etymology derives "trigonos"
    is reporting, in its own text, that the text belongs to Trigonidium.
    Cross-genus reference in ordinary prose ("differs from Epidendrum
    in ...") is common and harmless, which is why only the etymology --
    never a bare mention elsewhere -- is read this way.

    Args:
        records: All genus records for the corpus, mutated in place. The
            whole corpus is needed at once: the evidence is a *comparison*
            against every other genus name captured in this run.
    Returns:
        None. Affected records gain a `foreign_genus_etymology:<image>:
        <suspected owner>` review flag and `needs_review` status.
    """
    genus_names = sorted({record["genus_name"] for record in records})

    for record in records:
        etymology = record["fields"].get("ETYMOLOGY")
        if not etymology:
            continue
        roots = _etymology_roots(etymology["text"])
        if not roots:
            continue

        # How well the etymology accounts for the name it is filed under.
        # Any self-match at all clears the record: the question asked here
        # is only whether some *other* genus explains the text better.
        self_score = max(
            (_root_self_score(root, record["genus_name"]) for root in roots),
            default=0,
        )

        candidates = []
        for candidate in genus_names:
            if candidate == record["genus_name"]:
                continue
            score = max(
                (_root_owner_score(root, candidate) for root in roots),
                default=0,
            )
            if score > self_score:
                candidates.append((score, candidate))
        if not candidates:
            continue

        # Report only the best-supported owner. A weaker runner-up
        # (Cattleya behind Catasetum for "kata") shares a prefix by
        # coincidence and would only dilute the reviewer's lead.
        best_score = max(score for score, _ in candidates)
        owners = sorted(name for score, name in candidates if score == best_score)
        record["extraction_status"] = "needs_review"
        record["review_flags"].append(
            f"foreign_genus_etymology:{etymology.get('source_image', '')}:"
            f"{' or '.join(owners)}"
        )


def _merge_fields(target: dict[str, Any], additions: dict[str, Any]) -> None:
    """Merge freshly segmented fields into an already-open field dict.

    Args:
        target: The field dict being added to, mutated in place.
        additions: Newly segmented fields to merge in -- a label already
            present in `target` has its text concatenated (a continuation
            page's fragment of the same field); a new label is added as-is.
    """
    for label, value in additions.items():
        if label in target:
            target[label]["text"] += " " + value["text"]
        else:
            target[label] = value


def build_genus_records(pages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build genus records by stitching genus headers across pages.

    Args:
        pages: Accepted `PageOCRRecord`s, each augmented with an integer
            `page_number` (joined from the scan inventory), in page order.
    Returns:
        Tuple of (genus records, discontinuity review items). A
        discontinuity -- a continuation page whose running head names a
        different genus than the record currently open -- is reported,
        never silently merged or silently dropped (detailed design, §5).
    """
    records: list[dict[str, Any]] = []
    discontinuities: list[dict[str, Any]] = []
    open_record: dict[str, Any] | None = None
    # Index into open_record["species"] of the species currently being
    # described, or None while still in the genus's own pre-species text.
    # A continuation page's content belongs to whichever of these is open
    # (module docstring, finding on page-050: distribution/habitat/etc.
    # after a species' description belong to that species, not the
    # genus) -- tracked across pages, not reset to the genus by default
    # just because a new page started.
    open_species_index: int | None = None

    for page in pages:
        lines = [dict(line, source_image=page["source_image"]) for line in page["lines"]]
        headers = find_genus_headers(lines)
        running_head = cross_check_running_head(lines)

        # A header-shaped line whose genus name repeats the genus already
        # open is not a new genus -- a book does not redeclare a genus
        # mid-treatment. Found on the real full run: large genera number
        # their own species list ("1. Epidendrum acuñae Dressler in Am.
        # Orch. Soc. Bull. ...", module docstring finding 9), which is
        # genuinely citation-shaped (passes both _PROSE_WORD_PATTERN and
        # _AUTHOR_CAPITAL_PATTERN) because it really is a citation -- just
        # for the species, not the genus. `find_genus_headers` has no
        # continuation state to catch this itself, so it is filtered
        # here, where `open_record` already lives. When no other, real
        # genus header remains on this page, it falls through to the
        # continuation-page logic below, which now parses numbered
        # species entries directly (finding 9) -- `numbered_species_
        # list_unparsed` only fires if that also finds nothing, not
        # unconditionally the way it used to.
        same_genus_header_found = False
        if open_record is not None and headers:
            same_genus = [
                h for h in headers
                if h["genus_name"].lower() == open_record["genus_id"]
            ]
            if same_genus:
                headers = [
                    h for h in headers
                    if h["genus_name"].lower() != open_record["genus_id"]
                ]
                if headers:
                    # A different, real genus header also appears on this
                    # page -- it takes over below, so the suppressed
                    # content is never revisited by the continuation
                    # logic. Flag it here, immediately, rather than
                    # silently losing track of it.
                    open_record["extraction_status"] = "needs_review"
                    open_record["review_flags"].append(
                        f"numbered_species_list_unparsed:{page['source_image']}"
                    )
                else:
                    same_genus_header_found = True

        if headers:
            for position, header in enumerate(headers):
                block_start = header["index"] + 1
                block_end = (
                    headers[position + 1]["index"]
                    if position + 1 < len(headers)
                    else len(lines)
                )
                species, first_species_index = find_species_entries(
                    lines, header["genus_name"], block_start, block_end
                )
                # The genus's own span is everything before its first
                # species header (or the whole block, when it has none) --
                # field labels found there are genus-level (e.g. an
                # ETYMOLOGY explaining the genus name itself).
                genus_span_end = (
                    first_species_index if species else block_end
                )
                fields = segment_fields(lines[block_start:genus_span_end])

                resolved_species = []
                for entry in species:
                    resolved_species.append(
                        {
                            "species_name": entry["species_name"],
                            "author_and_publication": entry["author_and_publication"],
                            "fields": segment_fields(
                                lines[entry["_start"]:entry["_end"]]
                            ),
                        }
                    )

                next_header_column = (
                    lines[headers[position + 1]["index"]]["column"]
                    if position + 1 < len(headers)
                    else None
                )
                collision = _has_embedded_tribe_heading_before_next_header(
                    lines, block_start, block_end, next_header_column
                )

                open_record = {
                    "genus_id": header["genus_name"].lower(),
                    "genus_name": header["genus_name"],
                    "author": header["author"],
                    "genus_number": header["genus_number"],
                    "source_pages": [page["page_number"]],
                    "fields": fields,
                    "species": resolved_species,
                    "extraction_status": "needs_review" if collision else "complete",
                    "review_flags": (
                        [f"possible_cross_genus_content:{page['source_image']}"]
                        if collision
                        else []
                    ),
                }
                open_species_index = (
                    len(resolved_species) - 1 if resolved_species else None
                )
                records.append(open_record)
            continue

        # No header on this page: either a continuation of the open
        # record, or the page has no genus content at all (index pages,
        # illustrations). Only merge as a continuation when the running
        # head actively confirms it.
        if open_record is None:
            continue

        if running_head is None:
            # No informative running head -- found on the real pilot page
            # 66, where Vision split "28 Clowesia" into two separate line
            # observations ("28" and "Clowesia"), neither of which matches
            # the combined "<number> <Genus>" pattern. A page with
            # substantive content and no way to confirm whose treatment it
            # continues is not silently skipped: that produced a genuine
            # data loss during the pilot run (a real synonymy block for
            # Clowesia vanished with no trace anywhere). Flagged with
            # doc4's own anticipated vocabulary term instead.
            if len(_filter_furniture(lines)) >= 3:
                open_record["extraction_status"] = "needs_review"
                open_record["review_flags"].append(
                    f"ambiguous_genus_boundary:{page['source_image']}"
                )
            continue

        if running_head["genus_name"] == open_record["genus_name"]:
            open_record["source_pages"].append(page["page_number"])

            # A continuation page can itself carry one or more species
            # headers -- bare or numbered (finding 9) -- exactly like a
            # header page's own block does. Searching for them here,
            # rather than unconditionally dumping the whole page as
            # genus-level text, is what lets a large genus's species list
            # (which physically spans many continuation pages, e.g.
            # Epidendrum's 181-190) actually get split into per-species
            # records instead of merging into one unsegmented blob.
            species, first_species_index = find_species_entries(
                lines, open_record["genus_name"], 0, len(lines)
            )
            pre_species_end = first_species_index if species else len(lines)
            pre_species_fields = segment_fields(lines[0:pre_species_end])

            _merge_fields(
                open_record["species"][open_species_index]["fields"]
                if open_species_index is not None
                else open_record["fields"],
                pre_species_fields,
            )

            for entry in species:
                open_record["species"].append(
                    {
                        "species_name": entry["species_name"],
                        "author_and_publication": entry["author_and_publication"],
                        "fields": segment_fields(
                            lines[entry["_start"]:entry["_end"]]
                        ),
                    }
                )
                open_species_index = len(open_record["species"]) - 1

            if same_genus_header_found and not species:
                # The suppressed same-genus header really was
                # unparseable here -- species detection, run against the
                # same page, found nothing to attach it to.
                open_record["extraction_status"] = "needs_review"
                open_record["review_flags"].append(
                    f"numbered_species_list_unparsed:{page['source_image']}"
                )
        else:
            discontinuities.append(
                {
                    "page_number": page["page_number"],
                    "source_image": page["source_image"],
                    "expected_genus": open_record["genus_name"],
                    "running_head_genus": running_head["genus_name"],
                }
            )
            open_record["extraction_status"] = "needs_review"
            open_record["review_flags"].append(
                f"discontinuity:{page['source_image']}"
            )

    return records, discontinuities


def render_markdown(records: list[dict[str, Any]]) -> str:
    """Render genus records as a Markdown corpus, prototype-01's style.

    Args:
        records: Genus records, in the order they should appear.
    Returns:
        Full Markdown document text.
    """
    lines = ["# Belize Orchid Genera - Extracted from McLeish Scans", ""]
    lines.append("## Table of Contents")
    for record in records:
        anchor = record["genus_id"]
        lines.append(f"- [{record['genus_name']}](#genus-{anchor})")
    lines.append("")
    lines.append("---")
    lines.append("")

    for record in records:
        pages = ", ".join(f"page-{p:03d}" for p in record["source_pages"])
        lines.append(f"### Genus: {record['genus_name']} {record['author']}")
        lines.append(f"*Source: {pages}*")
        lines.append("")
        # A flagged record reads exactly like a clean one otherwise, and
        # this document -- not the JSONL or the review queue -- is what a
        # botanist actually reads. Presenting a record the parser openly
        # doubts as if it were settled is the same silent trust violation
        # the flags exist to prevent (module docstring, findings 8 and
        # 10), just moved one file downstream.
        for flag in record["review_flags"]:
            reason, _, note = (flag.split(":") + ["", ""])[:3]
            caveat = f"**Needs review** ({reason.replace('_', ' ')}"
            caveat += f", evidence points to {note})" if note else ")"
            lines.append(f"> {caveat}")
            lines.append("")
        for label, field in record["fields"].items():
            if not field["text"]:
                continue
            marker = " (uncertain)" if field["status"] == "uncertain" else ""
            lines.append(f"**{label}{marker}:**")
            lines.append(f"- {field['text']}")
            lines.append("")
        for species in record["species"]:
            lines.append(f"#### Species: {species['species_name']}")
            lines.append(f"*{species['author_and_publication']}*")
            lines.append("")
            for label, field in species["fields"].items():
                if not field["text"]:
                    continue
                lines.append(f"**{label}:**")
                lines.append(f"- {field['text']}")
                lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ocr", type=Path, default=root / "analysis" / "page_ocr.jsonl"
    )
    parser.add_argument(
        "--inventory", type=Path, default=root / "manifest" / "scan_inventory.json"
    )
    parser.add_argument(
        "--genera-out", type=Path, default=root / "analysis" / "genera.jsonl"
    )
    parser.add_argument(
        "--markdown-out", type=Path, default=root / "analysis" / "mcleish.genera.md"
    )
    return parser.parse_args()


def main() -> None:
    """Parse accepted OCR pages into genus records and write both outputs."""
    arguments = parse_args()

    inventory = json.loads(arguments.inventory.read_text(encoding="utf-8"))
    page_number_by_filename = {
        entry["filename"]: entry["claimed_identity"]["page_number"]
        for entry in inventory["entries"]
        if entry["claimed_identity"]["kind"] == "page"
    }

    pages = []
    with arguments.ocr.open(encoding="utf-8") as handle:
        for raw_line in handle:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            record = json.loads(raw_line)
            if record["accept_status"] != "accepted":
                continue
            page_number = page_number_by_filename.get(record["source_image"])
            if page_number is None:
                continue
            pages.append({**record, "page_number": page_number})
    pages.sort(key=lambda page: page["page_number"])

    records, discontinuities = build_genus_records(pages)

    # A corpus-wide pass, not a per-page one: it compares each record's
    # etymology against every other genus name captured in this run.
    flag_foreign_genus_etymology(records)

    arguments.genera_out.parent.mkdir(parents=True, exist_ok=True)
    with arguments.genera_out.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")

    arguments.markdown_out.write_text(render_markdown(records), encoding="utf-8")

    print(
        f"{len(records)} genus records from {len(pages)} accepted pages, "
        f"{len(discontinuities)} discontinuities -> {arguments.genera_out}"
    )


if __name__ == "__main__":
    main()

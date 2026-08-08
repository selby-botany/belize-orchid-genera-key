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
"""

from __future__ import annotations

import argparse
import json
import re
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

# The informative running-head variant: "<number> <Genus>", no period.
RUNNING_HEAD_PATTERN = re.compile(r"^(\d+)\s+([A-Z][A-Za-z-]+)$")

# Running heads and folio numbers sit within this fraction of page height
# from the top, discovered on page-050 (~0.042-0.043) with headroom.
TOP_BAND_MID_Y = 0.06

# Tribe/subtribe heading lines ("TRIBE TRIPHOREAE DRESSLER", "SUBTRIBE
# VANILLINAE LINDL.") are printed in full caps -- an OCR-faithful match,
# unlike FIELD_LABELS' small-caps case garbling. Found on page-050 sitting
# between one genus's last field and the next genus's numbered header;
# left unhandled, one bled into the prior genus's NOTE field.
TRIBE_HEADING_PATTERN = re.compile(r"^(TRIBE|SUBTRIBE)\s+.+$")

# Species header: the genus name (repeated verbatim from the owning
# genus's header) followed by a lowercase epithet. Matching against the
# specific owning genus name -- not a generic Capitalized-lowercase
# pattern -- avoids false positives on body prose like "Plant terrestrial"
# (requirements, §4 item 6).
def _species_header_pattern(genus_name: str) -> re.Pattern[str]:
    return re.compile(rf"^{re.escape(genus_name)}\s+([a-z][a-z-]+)\s+(.+)$")


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
        matches.append(
            {
                "index": index,
                "genus_number": match.group(1),
                "genus_name": match.group(2),
                "author": match.group(3).strip(),
                "confidence": line["confidence"],
            }
        )
    return matches


def cross_check_running_head(lines: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find and parse this page's running head, if it carries genus info.

    Scans for lines in the top `mid_y` band rather than the start of
    reading order, and only the informative "<number> <Genus>" variant is
    returned -- a bare page-number running head carries no continuity
    signal (module docstring, finding 2).

    Args:
        lines: Per-line OCR records for one page.
    Returns:
        `{genus_number, genus_name}` or None if no informative running
        head is present.
    """
    for line in lines:
        if line["mid_y"] > TOP_BAND_MID_Y:
            continue
        match = RUNNING_HEAD_PATTERN.match(line["text"].strip())
        if match:
            return {"genus_number": match.group(1), "genus_name": match.group(2)}
    return None


def _is_page_furniture(line: dict[str, Any]) -> bool:
    """True for a line that is page furniture, not body content.

    Covers three kinds found on the real pilot page: a bare folio number
    or an informative running head (both confined to the top `mid_y`
    band), and a tribe/subtribe heading, which can appear anywhere between
    two genus blocks.
    """
    text = line["text"].strip()
    if TRIBE_HEADING_PATTERN.match(text):
        return True
    if line["mid_y"] > TOP_BAND_MID_Y:
        return False
    return bool(RUNNING_HEAD_PATTERN.match(text) or re.match(r"^\d+$", text))


def _filter_furniture(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop running heads, folio numbers, and tribe/subtribe headings."""
    return [line for line in lines if not _is_page_furniture(line)]


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
    start with a capitalized word ("Plant terrestrial...").

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
    pattern = _species_header_pattern(genus_name)
    headers = []
    for index in range(start, end):
        match = pattern.match(lines[index]["text"].strip())
        if match:
            headers.append((index, match.group(1), match.group(2)))

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

    for page in pages:
        lines = [dict(line, source_image=page["source_image"]) for line in page["lines"]]
        headers = find_genus_headers(lines)
        running_head = cross_check_running_head(lines)

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

                open_record = {
                    "genus_id": header["genus_name"].lower(),
                    "genus_name": header["genus_name"],
                    "author": header["author"],
                    "genus_number": header["genus_number"],
                    "source_pages": [page["page_number"]],
                    "fields": fields,
                    "species": resolved_species,
                    "extraction_status": "complete",
                    "review_flags": [],
                }
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
            continuation_fields = segment_fields(lines)
            for label, value in continuation_fields.items():
                if label in open_record["fields"]:
                    open_record["fields"][label]["text"] += " " + value["text"]
                else:
                    open_record["fields"][label] = value
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

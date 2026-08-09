#!/usr/bin/env python3
"""Verify character proposals and assemble the character matrix (Stage C).

Reads `analysis/character_proposals.jsonl` (Stage B), `data/character_
vocabulary.json` (Stage A), and `prototype-03/analysis/genera.jsonl`
(Phase 1's output, read-only per requirements document, §3); writes
`analysis/character_matrix.jsonl`.

This is the one stage every character state passes through before it is
trusted (architecture document, design principle 2): `verify_quote` is
the sole gate, and nothing downstream of `build_matrix_row` ever sees a
proposal whose quote didn't check out against the genus's own real field
text.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

NOT_STATED = "not_stated"


def verify_quote(genus_record: dict[str, Any], source_field: str, quote: str) -> bool:
    """Mechanically confirm a proposal's quote is real, not just plausible.

    Args:
        genus_record: One genus record from `prototype-03/analysis/genera.jsonl`.
        source_field: The field name the proposal claims the quote came from.
        quote: The literal text the proposal cites as its evidence.
    Returns:
        True only when `source_field` exists on this genus and `quote` is
        an exact substring of that field's `text` -- a near-miss
        (paraphrase, reordering, whitespace-only difference) does not
        count (architecture document, §3.3: "mechanically verify," not
        "plausibly resemble").
    """
    field = genus_record.get("fields", {}).get(source_field)
    if field is None:
        return False
    return quote in field["text"]


def build_matrix_row(
    genus_id: str,
    proposals: list[dict[str, Any]],
    vocabulary: dict[str, Any],
    genera_by_id: dict[str, dict[str, Any]],
    dropped_proposals: list[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Build one genus's matrix row: every vocabulary character, always.

    Args:
        genus_id: The genus this row is for.
        proposals: This genus's own proposals that passed `verify_quote`
            (the caller is responsible for verifying and filtering first
            -- this function does not re-check).
        vocabulary: Parsed `character_vocabulary.json`.
        genera_by_id: Phase 1 genus records, keyed by `genus_id` --
            used only for `genus_name`.
        dropped_proposals: This genus's proposals that failed `verify_
            quote` -- recorded as review flags here, on the matrix row
            itself, rather than in a second output file only Stage C
            ever reads (detailed design, §8: "recording them directly in
            the matrix records' own review_flags").
    Returns:
        `{genus_id, genus_name, characters, review_flags}` -- `characters`
        has exactly one entry per character in the vocabulary, never more,
        never fewer (requirements, §1.1/§1.5): a character with no
        verified proposal for this genus gets the vocabulary's own
        `not_stated` state, not an omitted key.
    """
    verified_by_character = {p["character_id"]: p for p in proposals}

    characters: dict[str, Any] = {}
    for character in vocabulary["characters"]:
        character_id = character["character_id"]
        proposal = verified_by_character.get(character_id)
        if proposal is not None:
            characters[character_id] = {
                "state_id": proposal["state_id"],
                "quote": proposal["quote"],
                "source_field": proposal["source_field"],
                "source_image": proposal["source_image"],
                "status": "verified",
            }
        else:
            characters[character_id] = {
                "state_id": NOT_STATED,
                "quote": None,
                "source_field": None,
                "source_image": None,
                "status": NOT_STATED,
            }

    review_flags: list[str] = [
        f"unverified_proposal:{p['character_id']}" for p in dropped_proposals
    ]
    if all(entry["status"] == NOT_STATED for entry in characters.values()):
        review_flags.append("all_not_stated")

    return {
        "genus_id": genus_id,
        "genus_name": genera_by_id[genus_id]["genus_name"],
        "characters": characters,
        "review_flags": review_flags,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--genera",
        type=Path,
        default=root.parent / "prototype-03" / "analysis" / "genera.jsonl",
    )
    parser.add_argument(
        "--vocabulary", type=Path, default=root / "data" / "character_vocabulary.json"
    )
    parser.add_argument(
        "--proposals", type=Path, default=root / "analysis" / "character_proposals.jsonl"
    )
    parser.add_argument(
        "--output", type=Path, default=root / "analysis" / "character_matrix.jsonl"
    )
    return parser.parse_args()


def main() -> None:
    """Verify every proposal, assemble one row per genus, write the matrix."""
    arguments = parse_args()

    genera_by_id: dict[str, dict[str, Any]] = {}
    with arguments.genera.open(encoding="utf-8") as handle:
        for raw_line in handle:
            raw_line = raw_line.strip()
            if raw_line:
                record = json.loads(raw_line)
                genera_by_id[record["genus_id"]] = record

    vocabulary = json.loads(arguments.vocabulary.read_text(encoding="utf-8"))

    # Every genus in Phase 1's output gets a row, even one with no
    # proposals at all (requirements, §1.1) -- proposals are grouped by
    # genus_id first so a genus absent from character_proposals.jsonl
    # still produces an all-not_stated row rather than being skipped.
    proposals_by_genus: dict[str, list[dict[str, Any]]] = {
        genus_id: [] for genus_id in genera_by_id
    }
    dropped_by_genus: dict[str, list[dict[str, Any]]] = {
        genus_id: [] for genus_id in genera_by_id
    }
    if arguments.proposals.exists():
        with arguments.proposals.open(encoding="utf-8") as handle:
            for raw_line in handle:
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                proposal = json.loads(raw_line)
                genus_record = genera_by_id.get(proposal["genus_id"])
                if genus_record is not None and verify_quote(
                    genus_record, proposal["source_field"], proposal["quote"]
                ):
                    proposals_by_genus[proposal["genus_id"]].append(proposal)
                elif genus_record is not None:
                    dropped_by_genus[proposal["genus_id"]].append(proposal)

    rows = [
        build_matrix_row(
            genus_id, proposals, vocabulary, genera_by_id, dropped_by_genus[genus_id]
        )
        for genus_id, proposals in proposals_by_genus.items()
    ]

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with arguments.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")

    all_not_stated = sum(1 for row in rows if "all_not_stated" in row["review_flags"])
    dropped_total = sum(len(items) for items in dropped_by_genus.values())
    print(
        f"{len(rows)} genus rows ({all_not_stated} all-not_stated, "
        f"{dropped_total} dropped proposal(s)) -> {arguments.output}"
    )


if __name__ == "__main__":
    main()

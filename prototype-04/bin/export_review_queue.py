#!/usr/bin/env python3
"""Export a human review queue from every stage's flagged items (Stage F).

Reads `analysis/character_matrix.jsonl` (Stage C's own review_flags --
dropped proposals and all-not_stated genera) and `analysis/validation_
report.json` (Stage E's ambiguous leaves); writes `manifest/review_
queue.csv` -- one row per item a person needs to look at, each with a
legible reason.

`merge_with_previous` is copied, not reimplemented, from
`prototype-03/bin/export_review_queue.py`'s own function (detailed
design, §8) -- the carry-forward-by-`item_id` problem and its correct
fix already exist there; this is the same function against this phase's
own column shape.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

CSV_COLUMNS = [
    "item_id",
    "kind",
    "genus_id",
    "reason",
    "detail",
    "status",
    "resolution",
    "resolved_by",
    "resolved_date",
]


def _new_row(item_id: str, kind: str, genus_id: str, reason: str, detail: str) -> dict[str, Any]:
    """Build one queue row with the carry-forward fields at their defaults.

    Args:
        item_id: Stable identifier for this row.
        kind: `unverified_proposal`, `all_not_stated`, or `ambiguous_leaf`.
        genus_id: Genus (or comma-joined genera) this row concerns.
        reason: Short classifier matching `kind` (kept separate from
            `detail` so a reader can filter on it without parsing text).
        detail: Free text, enough to act on without opening the matrix.
    Returns:
        A row dict with every CSV_COLUMNS key present.
    """
    return {
        "item_id": item_id,
        "kind": kind,
        "genus_id": genus_id,
        "reason": reason,
        "detail": detail,
        "status": "open",
        "resolution": "",
        "resolved_by": "",
        "resolved_date": "",
    }


def queue_from_matrix(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build queue rows from Stage C's own review_flags.

    Args:
        records: Matrix rows, as written to `character_matrix.jsonl`.
    Returns:
        List of queue rows -- one per flag, not per genus, since a genus
        can carry more than one (several dropped proposals at once).
    """
    rows = []
    for record in records:
        genus_id = record["genus_id"]
        genus_name = record["genus_name"]
        for flag in record.get("review_flags", []):
            reason, _, extra = flag.partition(":")
            if reason == "unverified_proposal":
                detail = (
                    f"{genus_name}: a proposed state for '{extra}' did not "
                    "verify against its cited source text"
                )
            elif reason == "all_not_stated":
                detail = (
                    f"{genus_name}: no character could be confidently "
                    "extracted from its Phase 1 field text"
                )
            else:
                detail = f"{genus_name}: flagged during matrix assembly"
            rows.append(
                _new_row(
                    item_id=f"matrix:{genus_id}:{flag}",
                    kind=reason,
                    genus_id=genus_id,
                    reason=reason,
                    detail=detail,
                )
            )
    return rows


def queue_from_validation(
    report: dict[str, Any], genus_names: dict[str, str]
) -> list[dict[str, Any]]:
    """Build queue rows from Stage E's ambiguous leaves.

    Args:
        report: Parsed `validation_report.json`.
        genus_names: `genus_id` -> `genus_name`, for a readable detail.
    Returns:
        One row per ambiguous leaf, naming every member genus and the
        states that caused the tie (requirements, §2).
    """
    rows = []
    for leaf in report.get("ambiguous_leaves", []):
        genus_ids = sorted(leaf["genus_ids"])
        names = ", ".join(genus_names.get(g, g) for g in genus_ids)
        shared = "; ".join(f"{k}={v}" for k, v in leaf["shared_states"].items())
        rows.append(
            _new_row(
                item_id="ambiguous_leaf:" + ",".join(genus_ids),
                kind="ambiguous_leaf",
                genus_id=",".join(genus_ids),
                reason="ambiguous_leaf",
                detail=(
                    f"{names} cannot be distinguished by the extracted "
                    f"characters (shared: {shared or 'none -- both entirely not_stated'})"
                ),
            )
        )
    return rows


def merge_with_previous(
    new_rows: list[dict[str, Any]], previous_path: Path
) -> list[dict[str, Any]]:
    """Carry forward a reviewer's resolution across a regeneration.

    Copied from `prototype-03/bin/export_review_queue.py`'s own function
    (detailed design, §8) -- identical logic, this phase's column shape.

    Args:
        new_rows: Freshly generated rows for this run.
        previous_path: Path to a previously written `review_queue.csv`.
    Returns:
        `new_rows`, with `status`/`resolution`/`resolved_by`/
        `resolved_date` overwritten from the previous file wherever
        `item_id` recurs.
    """
    if not previous_path.exists():
        return new_rows

    carried: dict[str, dict[str, str]] = {}
    with previous_path.open(newline="", encoding="utf-8") as handle:
        for old_row in csv.DictReader(handle):
            carried[old_row["item_id"]] = {
                "status": old_row["status"],
                "resolution": old_row["resolution"],
                "resolved_by": old_row["resolved_by"],
                "resolved_date": old_row["resolved_date"],
            }

    merged = []
    for row in new_rows:
        previous_state = carried.get(row["item_id"])
        merged.append({**row, **previous_state} if previous_state else row)
    return merged


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    """Write queue rows to a CSV file, columns in the documented order.

    Args:
        rows: Queue rows.
        path: Output file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix", type=Path, default=root / "analysis" / "character_matrix.jsonl"
    )
    parser.add_argument(
        "--validation",
        type=Path,
        default=root / "analysis" / "validation_report.json",
    )
    parser.add_argument(
        "--output", type=Path, default=root / "manifest" / "review_queue.csv"
    )
    return parser.parse_args()


def main() -> None:
    """Build the review queue from every stage's flagged items and write it."""
    arguments = parse_args()

    rows: list[dict[str, Any]] = []
    genus_names: dict[str, str] = {}

    records = []
    if arguments.matrix.exists():
        with arguments.matrix.open(encoding="utf-8") as handle:
            for raw_line in handle:
                raw_line = raw_line.strip()
                if raw_line:
                    records.append(json.loads(raw_line))
        genus_names = {r["genus_id"]: r["genus_name"] for r in records}
        rows.extend(queue_from_matrix(records))

    if arguments.validation.exists():
        report = json.loads(arguments.validation.read_text(encoding="utf-8"))
        rows.extend(queue_from_validation(report, genus_names))

    rows = merge_with_previous(rows, arguments.output)
    write_csv(rows, arguments.output)

    open_count = sum(1 for row in rows if row["status"] == "open")
    print(f"{len(rows)} queue rows ({open_count} open) -> {arguments.output}")


if __name__ == "__main__":
    main()

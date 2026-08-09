#!/usr/bin/env python3
"""Export a human review queue from every stage's flagged items (Stage E).

Reads `manifest/scan_inventory.json` (Stage A anomalies),
`analysis/page_ocr.jsonl` (Stage C rejections), and `analysis/genera.jsonl`
(Stage D discontinuities and uncertain fields), and writes
`manifest/review_queue.csv` -- one row per item a person needs to look at,
each with a legible reason and enough detail to act without opening the
source file first (data document, §3).

`merge_with_previous` is the direct fix for prototype-02's documented
defect #2 (detailed design, §8): a reviewer's `status`/`resolution`/
`resolved_by`/`resolved_date` on a row is carried forward by `item_id`
across regenerations, never silently discarded because the pipeline ran
again.
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
    "source_image",
    "page_number",
    "reason",
    "detail",
    "status",
    "resolution",
    "resolved_by",
    "resolved_date",
]


def _new_row(
    item_id: str,
    kind: str,
    source_image: str,
    reason: str,
    detail: str,
    page_number: int | None = None,
) -> dict[str, Any]:
    """Build one queue row with the carry-forward fields at their defaults.

    Args:
        item_id: Stable identifier for this row (see module docstring).
        kind: `image_anomaly`, `ocr_reject`, or `parse_ambiguous`.
        source_image: Filename this row concerns.
        reason: Short classifier from the fixed vocabulary (data document,
            §3) -- the specific detail goes in `detail`, not here.
        detail: Free text, enough to act on without opening the source.
        page_number: Page number, when known; None otherwise.
    Returns:
        A row dict with every CSV_COLUMNS key present.
    """
    return {
        "item_id": item_id,
        "kind": kind,
        "source_image": source_image,
        "page_number": page_number,
        "reason": reason,
        "detail": detail,
        "status": "open",
        "resolution": "",
        "resolved_by": "",
        "resolved_date": "",
    }


def queue_from_inventory(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    """Build queue rows from Stage A's per-file anomalies.

    One row per anomaly, not per file -- a file can carry more than one
    (e.g. `too_small` and `unparseable_filename` together), and each needs
    its own reviewable, resolvable identity.

    Args:
        inventory: Parsed `scan_inventory.json`.
    Returns:
        List of queue rows.
    """
    rows = []
    for entry in inventory.get("entries", []):
        filename = entry["filename"]
        page_number = entry["claimed_identity"].get("page_number")
        for anomaly in entry.get("anomalies", []):
            reason, _, extra = anomaly.partition(":")
            detail = f"{reason.replace('_', ' ')}: {extra}" if extra else reason.replace(
                "_", " "
            )
            rows.append(
                _new_row(
                    item_id=f"image_anomaly:{filename}:{anomaly}",
                    kind="image_anomaly",
                    source_image=filename,
                    reason=reason,
                    detail=detail,
                    page_number=page_number,
                )
            )
    return rows


def queue_from_ocr(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build queue rows from Stage C's rejected pages.

    One row per reject reason, not per page -- a page can fail more than
    one acceptance check at once.

    Args:
        pages: `PageOCRRecord`s, accepted and rejected alike (only
            `rejected` ones produce rows).
    Returns:
        List of queue rows.
    """
    rows = []
    for page in pages:
        if page.get("accept_status") != "rejected":
            continue
        source_image = page["source_image"]
        for reason in page.get("reject_reasons", []):
            rows.append(
                _new_row(
                    item_id=f"ocr_reject:{source_image}:{reason}",
                    kind="ocr_reject",
                    source_image=source_image,
                    reason=reason,
                    detail=(
                        f"mean_confidence={page.get('mean_confidence')} "
                        f"low_confidence_count={page.get('low_confidence_count')} "
                        f"line_count={page.get('line_count')}"
                    ),
                )
            )
    return rows


def queue_from_genera(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build queue rows from Stage D's discontinuities and uncertain fields.

    Args:
        records: Genus records, as written to `genera.jsonl`.
    Returns:
        List of queue rows.
    """
    rows = []
    for record in records:
        genus_id = record["genus_id"]
        source_image = record["fields"].get("SUMMARY", {}).get("source_image", "")

        review_flag_details = {
            "discontinuity": "running head named a different genus than expected",
            "ambiguous_genus_boundary": (
                "no genus header and no readable running head -- can't "
                "confirm which genus's treatment this page continues"
            ),
            "numbered_species_list_unparsed": (
                "this genus numbers its own internal species list; the "
                "page's text was captured as unsegmented continuation "
                "prose rather than parsed into individual species"
            ),
            "possible_cross_genus_content": (
                "this genus's text may actually belong to the next genus "
                "on the same page (a genus-header tab-column layout "
                "collision) -- check against the source image before "
                "trusting any field here"
            ),
        }
        for flag in record.get("review_flags", []):
            reason, _, extra = flag.partition(":")
            explanation = review_flag_details.get(reason, "flagged during parsing")
            rows.append(
                _new_row(
                    item_id=f"parse_ambiguous:{genus_id}:{flag}",
                    kind="parse_ambiguous",
                    source_image=extra or source_image,
                    reason=reason,
                    detail=f"{record['genus_name']}: {explanation}",
                )
            )

        for owner_label, owner_name, fields in [
            (genus_id, record["genus_name"], record["fields"]),
            *[
                (f"{genus_id}:{sp['species_name']}", sp["species_name"], sp["fields"])
                for sp in record.get("species", [])
            ],
        ]:
            for label, field in fields.items():
                if field.get("status") != "uncertain":
                    continue
                preview = field["text"][:80]
                rows.append(
                    _new_row(
                        item_id=f"parse_ambiguous:{owner_label}:uncertain_field:{label}",
                        kind="parse_ambiguous",
                        source_image=field.get("source_image", source_image),
                        reason="uncertain_field",
                        detail=f"{owner_name} field {label}: {preview}",
                    )
                )
    return rows


def merge_with_previous(
    new_rows: list[dict[str, Any]], previous_path: Path
) -> list[dict[str, Any]]:
    """Carry forward a reviewer's resolution across a regeneration.

    Args:
        new_rows: Freshly generated rows for this run.
        previous_path: Path to a previously written `review_queue.csv`.
    Returns:
        `new_rows`, with `status`/`resolution`/`resolved_by`/
        `resolved_date` overwritten from the previous file wherever
        `item_id` recurs. Rows whose `item_id` no longer recurs are not
        carried forward -- their underlying condition is gone.
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
        "--inventory", type=Path, default=root / "manifest" / "scan_inventory.json"
    )
    parser.add_argument(
        "--ocr", type=Path, default=root / "analysis" / "page_ocr.jsonl"
    )
    parser.add_argument(
        "--genera", type=Path, default=root / "analysis" / "genera.jsonl"
    )
    parser.add_argument(
        "--output", type=Path, default=root / "manifest" / "review_queue.csv"
    )
    return parser.parse_args()


def main() -> None:
    """Build the review queue from every stage's flagged items and write it."""
    arguments = parse_args()

    rows: list[dict[str, Any]] = []
    page_number_by_filename: dict[str, int] = {}

    if arguments.inventory.exists():
        inventory = json.loads(arguments.inventory.read_text(encoding="utf-8"))
        page_number_by_filename = {
            entry["filename"]: entry["claimed_identity"].get("page_number")
            for entry in inventory["entries"]
        }
        rows.extend(queue_from_inventory(inventory))

    if arguments.ocr.exists():
        pages = []
        with arguments.ocr.open(encoding="utf-8") as handle:
            for raw_line in handle:
                raw_line = raw_line.strip()
                if raw_line:
                    pages.append(json.loads(raw_line))
        ocr_rows = queue_from_ocr(pages)
        for row in ocr_rows:
            row["page_number"] = page_number_by_filename.get(row["source_image"])
        rows.extend(ocr_rows)

    if arguments.genera.exists():
        records = []
        with arguments.genera.open(encoding="utf-8") as handle:
            for raw_line in handle:
                raw_line = raw_line.strip()
                if raw_line:
                    records.append(json.loads(raw_line))
        genera_rows = queue_from_genera(records)
        for row in genera_rows:
            row["page_number"] = page_number_by_filename.get(row["source_image"])
        rows.extend(genera_rows)

    rows = merge_with_previous(rows, arguments.output)
    write_csv(rows, arguments.output)

    open_count = sum(1 for row in rows if row["status"] == "open")
    print(f"{len(rows)} queue rows ({open_count} open) -> {arguments.output}")


if __name__ == "__main__":
    main()

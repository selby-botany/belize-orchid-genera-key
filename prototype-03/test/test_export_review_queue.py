"""Tests for the review queue export (Stage E)."""

from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "bin" / "export_review_queue.py"
SPEC = importlib.util.spec_from_file_location("export_review_queue", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class QueueFromInventoryTest(unittest.TestCase):
    """Rows built from Stage A's per-file anomalies."""

    def test_one_row_per_anomaly_with_documented_columns(self) -> None:
        inventory = {
            "entries": [
                {
                    "filename": "page-065 1.jpeg",
                    "claimed_identity": {"kind": "page", "page_number": 65},
                    "anomalies": ["too_small", "duplicate_of:page-065.jpeg"],
                }
            ]
        }
        rows = MODULE.queue_from_inventory(inventory)
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(set(row.keys()), set(MODULE.CSV_COLUMNS))
            self.assertEqual(row["kind"], "image_anomaly")
            self.assertEqual(row["source_image"], "page-065 1.jpeg")
            self.assertEqual(row["page_number"], 65)
            self.assertEqual(row["status"], "open")

    def test_clean_entry_produces_no_rows(self) -> None:
        inventory = {
            "entries": [
                {
                    "filename": "page-050.jpeg",
                    "claimed_identity": {"kind": "page", "page_number": 50},
                    "anomalies": [],
                }
            ]
        }
        self.assertEqual(MODULE.queue_from_inventory(inventory), [])


class QueueFromOcrTest(unittest.TestCase):
    """Rows built from Stage C's rejected pages."""

    def test_one_row_per_reject_reason(self) -> None:
        pages = [
            {
                "source_image": "page-099.jpeg",
                "accept_status": "rejected",
                "reject_reasons": [
                    "mean_confidence_below_threshold",
                    "line_count_below_band",
                ],
                "mean_confidence": 0.4,
                "low_confidence_count": 10,
                "line_count": 2,
            }
        ]
        rows = MODULE.queue_from_ocr(pages)
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(set(row.keys()), set(MODULE.CSV_COLUMNS))
            self.assertEqual(row["kind"], "ocr_reject")
            self.assertEqual(row["source_image"], "page-099.jpeg")

    def test_accepted_page_produces_no_rows(self) -> None:
        pages = [
            {
                "source_image": "page-050.jpeg",
                "accept_status": "accepted",
                "reject_reasons": [],
            }
        ]
        self.assertEqual(MODULE.queue_from_ocr(pages), [])


class QueueFromGeneraTest(unittest.TestCase):
    """Rows built from Stage D's discontinuities and uncertain fields."""

    def test_discontinuity_review_flag_produces_a_row(self) -> None:
        records = [
            {
                "genus_id": "gamma",
                "genus_name": "Gamma",
                "fields": {},
                "species": [],
                "review_flags": ["discontinuity:page-021.jpeg"],
            }
        ]
        rows = MODULE.queue_from_genera(records)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "parse_ambiguous")
        self.assertEqual(rows[0]["reason"], "discontinuity")
        self.assertEqual(rows[0]["source_image"], "page-021.jpeg")
        self.assertIn("running head named a different genus", rows[0]["detail"])

    def test_ambiguous_genus_boundary_gets_its_own_detail_text(self) -> None:
        # Distinct from discontinuity: no running head was found at all,
        # so the row must not claim one "named a different genus" --
        # found as a real bug during the pilot run, where both cases
        # shared one (wrong, for this one) detail message.
        records = [
            {
                "genus_id": "clowesia",
                "genus_name": "Clowesia",
                "fields": {},
                "species": [],
                "review_flags": ["ambiguous_genus_boundary:page-066.jpeg"],
            }
        ]
        rows = MODULE.queue_from_genera(records)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reason"], "ambiguous_genus_boundary")
        self.assertNotIn("named a different genus", rows[0]["detail"])
        self.assertIn("no genus header", rows[0]["detail"])

    def test_numbered_species_list_unparsed_gets_its_own_detail_text(self) -> None:
        # Distinct from both discontinuity and ambiguous_genus_boundary:
        # a real header line was found, but suppressed because it named
        # the genus already open (module docstring in parse_genus_page.py,
        # finding 5) -- the detail text must say that, not claim a
        # different genus or a missing running head.
        records = [
            {
                "genus_id": "epidendrum",
                "genus_name": "Epidendrum",
                "fields": {},
                "species": [],
                "review_flags": [
                    "numbered_species_list_unparsed:page-182.jpeg"
                ],
            }
        ]
        rows = MODULE.queue_from_genera(records)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reason"], "numbered_species_list_unparsed")
        self.assertNotIn("named a different genus", rows[0]["detail"])
        self.assertNotIn("no genus header", rows[0]["detail"])
        self.assertIn("internal species list", rows[0]["detail"])

    def test_foreign_genus_etymology_row_names_the_suspected_owner(self) -> None:
        # This flag carries a third segment the others don't: the genus
        # the etymology actually derives. That lead is the whole value of
        # the row, so it has to survive into the reviewer's detail text
        # -- and the image must still land in source_image, not be
        # swallowed along with it.
        records = [
            {
                "genus_id": "coryanthes",
                "genus_name": "Coryanthes",
                "fields": {},
                "species": [],
                "review_flags": [
                    "foreign_genus_etymology:page-107.jpeg:Trigonidium"
                ],
            }
        ]
        rows = MODULE.queue_from_genera(records)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reason"], "foreign_genus_etymology")
        self.assertEqual(rows[0]["source_image"], "page-107.jpeg")
        self.assertIn("Trigonidium", rows[0]["detail"])
        self.assertIn("derives a different genus's name", rows[0]["detail"])

    def test_two_segment_flag_still_produces_a_row_without_a_note(self) -> None:
        # Every pre-existing flag is `reason:image` with no third
        # segment; widening the split must not leave them with a
        # dangling, empty "evidence points to" clause.
        records = [
            {
                "genus_id": "galeandra",
                "genus_name": "Galeandra",
                "fields": {},
                "species": [],
                "review_flags": ["discontinuity:page-064.jpeg"],
            }
        ]
        rows = MODULE.queue_from_genera(records)
        self.assertEqual(rows[0]["source_image"], "page-064.jpeg")
        self.assertNotIn("evidence points to", rows[0]["detail"])

    def test_uncertain_field_produces_a_row_scoped_to_its_owner(self) -> None:
        records = [
            {
                "genus_id": "alpha",
                "genus_name": "Alpha",
                "fields": {
                    "SUMMARY": {
                        "text": "unattributed prose",
                        "status": "uncertain",
                        "source_image": "page-010.jpeg",
                    },
                    "Roots": {
                        "text": "adventitious",
                        "status": "scored",
                        "source_image": "page-010.jpeg",
                    },
                },
                "species": [
                    {
                        "species_name": "Alpha minor",
                        "fields": {
                            "SUMMARY": {
                                "text": "species-level unattributed prose",
                                "status": "uncertain",
                                "source_image": "page-010.jpeg",
                            }
                        },
                    }
                ],
                "review_flags": [],
            }
        ]
        rows = MODULE.queue_from_genera(records)
        reasons = [row["reason"] for row in rows]
        self.assertEqual(reasons, ["uncertain_field", "uncertain_field"])
        item_ids = [row["item_id"] for row in rows]
        self.assertIn("parse_ambiguous:alpha:uncertain_field:SUMMARY", item_ids)
        self.assertTrue(
            any("Alpha minor" in row["item_id"] for row in rows)
        )

    def test_complete_record_with_no_uncertain_fields_produces_no_rows(self) -> None:
        records = [
            {
                "genus_id": "beta",
                "genus_name": "Beta",
                "fields": {
                    "Roots": {
                        "text": "adventitious",
                        "status": "scored",
                        "source_image": "page-011.jpeg",
                    }
                },
                "species": [],
                "review_flags": [],
            }
        ]
        self.assertEqual(MODULE.queue_from_genera(records), [])


class MergeWithPreviousTest(unittest.TestCase):
    """The direct regression test for defect #2: resolutions survive a rerun."""

    def test_resolution_carried_forward_for_a_recurring_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous_path = Path(tmp) / "review_queue.csv"
            with previous_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=MODULE.CSV_COLUMNS)
                writer.writeheader()
                writer.writerow(
                    {
                        "item_id": "image_anomaly:page-065 1.jpeg:too_small",
                        "kind": "image_anomaly",
                        "source_image": "page-065 1.jpeg",
                        "page_number": 65,
                        "reason": "too_small",
                        "detail": "too small",
                        "status": "resolved",
                        "resolution": "confirmed corrupt stub, excluded",
                        "resolved_by": "botanist",
                        "resolved_date": "2026-08-01",
                    }
                )

            new_rows = [
                MODULE._new_row(
                    item_id="image_anomaly:page-065 1.jpeg:too_small",
                    kind="image_anomaly",
                    source_image="page-065 1.jpeg",
                    reason="too_small",
                    detail="too small",
                    page_number=65,
                )
            ]
            merged = MODULE.merge_with_previous(new_rows, previous_path)

            self.assertEqual(len(merged), 1)
            self.assertEqual(merged[0]["status"], "resolved")
            self.assertEqual(
                merged[0]["resolution"], "confirmed corrupt stub, excluded"
            )
            self.assertEqual(merged[0]["resolved_by"], "botanist")
            self.assertEqual(merged[0]["resolved_date"], "2026-08-01")

    def test_new_item_not_in_previous_file_is_added_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous_path = Path(tmp) / "review_queue.csv"
            with previous_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=MODULE.CSV_COLUMNS)
                writer.writeheader()

            new_rows = [
                MODULE._new_row(
                    item_id="ocr_reject:page-099.jpeg:line_count_below_band",
                    kind="ocr_reject",
                    source_image="page-099.jpeg",
                    reason="line_count_below_band",
                    detail="line_count=2",
                )
            ]
            merged = MODULE.merge_with_previous(new_rows, previous_path)

            self.assertEqual(len(merged), 1)
            self.assertEqual(merged[0]["status"], "open")
            self.assertEqual(merged[0]["resolution"], "")

    def test_no_previous_file_returns_new_rows_unchanged(self) -> None:
        new_rows = [
            MODULE._new_row(
                item_id="x", kind="image_anomaly", source_image="a.jpeg",
                reason="too_small", detail="too small",
            )
        ]
        result = MODULE.merge_with_previous(new_rows, Path("/nonexistent/path.csv"))
        self.assertEqual(result, new_rows)


class WriteCsvTest(unittest.TestCase):
    """The written file round-trips through the documented column order."""

    def test_round_trips_a_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "review_queue.csv"
            row = MODULE._new_row(
                item_id="x", kind="image_anomaly", source_image="a.jpeg",
                reason="too_small", detail="too small", page_number=1,
            )
            MODULE.write_csv([row], output_path)

            with output_path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, MODULE.CSV_COLUMNS)
                rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["item_id"], "x")


if __name__ == "__main__":
    unittest.main()

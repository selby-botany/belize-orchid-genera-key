"""Tests for the review queue export (Stage F)."""

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


class QueueFromMatrixTest(unittest.TestCase):
    """Rows built from Stage C's own review_flags."""

    def test_one_row_per_unverified_proposal(self) -> None:
        records = [
            {
                "genus_id": "alpha",
                "genus_name": "Alpha",
                "characters": {},
                "review_flags": ["unverified_proposal:lip_lobing"],
            }
        ]
        rows = MODULE.queue_from_matrix(records)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "unverified_proposal")
        self.assertEqual(rows[0]["genus_id"], "alpha")
        self.assertIn("lip_lobing", rows[0]["detail"])

    def test_all_not_stated_gets_its_own_row_and_detail(self) -> None:
        records = [
            {
                "genus_id": "beta",
                "genus_name": "Beta",
                "characters": {},
                "review_flags": ["all_not_stated"],
            }
        ]
        rows = MODULE.queue_from_matrix(records)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "all_not_stated")
        self.assertIn("no character could be confidently extracted", rows[0]["detail"])

    def test_clean_record_produces_no_rows(self) -> None:
        records = [
            {
                "genus_id": "gamma",
                "genus_name": "Gamma",
                "characters": {},
                "review_flags": [],
            }
        ]
        self.assertEqual(MODULE.queue_from_matrix(records), [])


class QueueFromValidationTest(unittest.TestCase):
    """Rows built from Stage E's ambiguous leaves."""

    def test_one_row_per_ambiguous_leaf_naming_every_genus(self) -> None:
        report = {
            "ambiguous_leaves": [
                {
                    "genus_ids": ["sacoila", "sarcoglottis"],
                    "shared_states": {},
                }
            ]
        }
        genus_names = {"sacoila": "Sacoila", "sarcoglottis": "Sarcoglottis"}
        rows = MODULE.queue_from_validation(report, genus_names)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "ambiguous_leaf")
        self.assertIn("Sacoila", rows[0]["detail"])
        self.assertIn("Sarcoglottis", rows[0]["detail"])

    def test_shared_states_appear_in_the_detail(self) -> None:
        report = {
            "ambiguous_leaves": [
                {
                    "genus_ids": ["a", "b"],
                    "shared_states": {"lip_lobing": "entire"},
                }
            ]
        }
        rows = MODULE.queue_from_validation(report, {"a": "Alpha", "b": "Beta"})
        self.assertIn("lip_lobing=entire", rows[0]["detail"])

    def test_no_ambiguous_leaves_produces_no_rows(self) -> None:
        report = {"ambiguous_leaves": []}
        self.assertEqual(MODULE.queue_from_validation(report, {}), [])


class MergeWithPreviousTest(unittest.TestCase):
    """Copied test-for-test from prototype-03's own MergeWithPreviousTest."""

    def test_resolution_carried_forward_for_a_recurring_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous_path = Path(tmp) / "review_queue.csv"
            with previous_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=MODULE.CSV_COLUMNS)
                writer.writeheader()
                writer.writerow(
                    {
                        "item_id": "matrix:corymborkis:all_not_stated",
                        "kind": "all_not_stated",
                        "genus_id": "corymborkis",
                        "reason": "all_not_stated",
                        "detail": "no character could be extracted",
                        "status": "resolved",
                        "resolution": "confirmed, page is a chapter-heading fragment",
                        "resolved_by": "botanist",
                        "resolved_date": "2026-08-08",
                    }
                )

            new_rows = [
                MODULE._new_row(
                    item_id="matrix:corymborkis:all_not_stated",
                    kind="all_not_stated",
                    genus_id="corymborkis",
                    reason="all_not_stated",
                    detail="no character could be extracted",
                )
            ]
            merged = MODULE.merge_with_previous(new_rows, previous_path)

            self.assertEqual(len(merged), 1)
            self.assertEqual(merged[0]["status"], "resolved")
            self.assertEqual(
                merged[0]["resolution"], "confirmed, page is a chapter-heading fragment"
            )

    def test_new_item_not_in_previous_file_is_added_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous_path = Path(tmp) / "review_queue.csv"
            with previous_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=MODULE.CSV_COLUMNS)
                writer.writeheader()

            new_rows = [
                MODULE._new_row(
                    item_id="x", kind="all_not_stated", genus_id="a",
                    reason="all_not_stated", detail="d",
                )
            ]
            merged = MODULE.merge_with_previous(new_rows, previous_path)
            self.assertEqual(merged[0]["status"], "open")
            self.assertEqual(merged[0]["resolution"], "")

    def test_no_previous_file_returns_new_rows_unchanged(self) -> None:
        new_rows = [
            MODULE._new_row(
                item_id="x", kind="all_not_stated", genus_id="a",
                reason="all_not_stated", detail="d",
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
                item_id="x", kind="all_not_stated", genus_id="a",
                reason="all_not_stated", detail="d",
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

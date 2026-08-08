"""Tests for the scan inventory builder (Stage A)."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "bin" / "build_scan_inventory.py"
SPEC = importlib.util.spec_from_file_location("build_scan_inventory", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _write_image(path: Path, size: tuple[int, int], mode: str, fill: int = 0) -> None:
    """Write a tiny synthetic image for a test fixture.

    `fill` varies pixel content between fixtures that would otherwise be
    byte-identical (same size and mode), which would make them collide as
    accidental SHA-256 duplicates.
    """
    Image.new(mode, size, color=fill).save(path)


class Sha256OfTest(unittest.TestCase):
    """sha256_of must be a stable, pure function of file content."""

    def test_stable_across_reads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.jpeg"
            _write_image(path, (600, 800), "L")
            self.assertEqual(MODULE.sha256_of(path), MODULE.sha256_of(path))

    def test_differs_on_different_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "a.jpeg"
            second = Path(tmp) / "b.jpeg"
            _write_image(first, (600, 800), "L")
            _write_image(second, (601, 800), "L")
            self.assertNotEqual(MODULE.sha256_of(first), MODULE.sha256_of(second))


class ParseClaimedIdentityTest(unittest.TestCase):
    """Filename patterns must map to the documented identity kinds."""

    def test_page(self) -> None:
        identity = MODULE.parse_claimed_identity("page-050.jpeg")
        self.assertEqual(identity["kind"], "page")
        self.assertEqual(identity["page_number"], 50)

    def test_plate(self) -> None:
        identity = MODULE.parse_claimed_identity("page-030p1.jpeg")
        self.assertEqual(identity["kind"], "plate")
        self.assertEqual(identity["linked_page"], 30)
        self.assertEqual(identity["plate_index"], 1)

    def test_front_matter(self) -> None:
        identity = MODULE.parse_claimed_identity("titlepage.jpeg")
        self.assertEqual(identity["kind"], "front_matter")
        self.assertEqual(identity["label"], "titlepage")

    def test_unrecognized(self) -> None:
        for filename in ("m276.jpeg", "page-065 1.jpeg"):
            identity = MODULE.parse_claimed_identity(filename)
            self.assertEqual(identity["kind"], "unrecognized", filename)


class DetectAnomaliesTest(unittest.TestCase):
    """Anomaly detection must catch the two problems already found by hand."""

    def test_too_small_flagged(self) -> None:
        entry = {
            "filename": "page-065 1.jpeg",
            "sha256": "aaa",
            "width": 192,
            "height": 152,
            "colorspace": "Gray",
            "claimed_identity": MODULE.parse_claimed_identity("page-065 1.jpeg"),
        }
        anomalies = MODULE.detect_anomalies(entry, [entry])
        self.assertIn("too_small", anomalies)
        self.assertIn("unparseable_filename", anomalies)

    def test_duplicate_content_flagged(self) -> None:
        first = {
            "filename": "page-050.jpeg",
            "sha256": "shared",
            "width": 4350,
            "height": 6450,
            "colorspace": "Gray",
            "claimed_identity": MODULE.parse_claimed_identity("page-050.jpeg"),
        }
        second = {
            "filename": "page-050-copy.jpeg",
            "sha256": "shared",
            "width": 4350,
            "height": 6450,
            "colorspace": "Gray",
            "claimed_identity": MODULE.parse_claimed_identity("page-050-copy.jpeg"),
        }
        all_entries = [first, second]
        anomalies = MODULE.detect_anomalies(second, all_entries)
        self.assertIn("duplicate_of:page-050.jpeg", anomalies)
        # The first-seen entry of a duplicate pair is not flagged against
        # itself -- only the later one records the relationship.
        self.assertNotIn("duplicate_of:page-050.jpeg", MODULE.detect_anomalies(first, all_entries))

    def test_clean_page_has_no_anomalies(self) -> None:
        entry = {
            "filename": "page-050.jpeg",
            "sha256": "unique",
            "width": 4350,
            "height": 6450,
            "colorspace": "Gray",
            "claimed_identity": MODULE.parse_claimed_identity("page-050.jpeg"),
        }
        self.assertEqual(MODULE.detect_anomalies(entry, [entry]), [])

    def test_colorspace_mismatch_flagged(self) -> None:
        entry = {
            "filename": "page-050.jpeg",
            "sha256": "unique2",
            "width": 4350,
            "height": 6450,
            "colorspace": "sRGB",
            "claimed_identity": MODULE.parse_claimed_identity("page-050.jpeg"),
        }
        self.assertIn("colorspace_mismatch", MODULE.detect_anomalies(entry, [entry]))


class ReviewStateCarryForwardTest(unittest.TestCase):
    """Review state follows content, not filename or position (defect #1)."""

    def _previous_inventory(self, tmp: Path) -> Path:
        inventory = {
            "schema_version": 1,
            "generated_at": "then",
            "source_directory": "20260804-page-scans",
            "image_count": 1,
            "entries": [
                {
                    "filename": "page-050.jpeg",
                    "sha256": "original-checksum",
                    "byte_size": 1,
                    "width": 1,
                    "height": 1,
                    "colorspace": "Gray",
                    "claimed_identity": MODULE.parse_claimed_identity("page-050.jpeg"),
                    "anomalies": [],
                    "review_status": "accepted",
                    "review_checksum": "original-checksum",
                    "remarks": "looked fine",
                }
            ],
        }
        path = tmp / "scan_inventory.json"
        path.write_text(json.dumps(inventory), encoding="utf-8")
        return path

    def test_unchanged_content_carries_forward_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous_path = self._previous_inventory(Path(tmp))
            previous = MODULE.load_previous_inventory(previous_path)
            state = MODULE.carry_forward_review_state(
                "page-050.jpeg", "original-checksum", previous
            )
            self.assertEqual(state["review_status"], "accepted")
            self.assertEqual(state["remarks"], "looked fine")

    def test_changed_content_resets_and_names_superseded_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous_path = self._previous_inventory(Path(tmp))
            previous = MODULE.load_previous_inventory(previous_path)
            state = MODULE.carry_forward_review_state(
                "page-050.jpeg", "new-checksum", previous
            )
            self.assertEqual(state["review_status"], "unreviewed")
            self.assertIn("original-checksum", state["remarks"])

    def test_brand_new_file_is_unreviewed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous_path = self._previous_inventory(Path(tmp))
            previous = MODULE.load_previous_inventory(previous_path)
            state = MODULE.carry_forward_review_state(
                "page-999.jpeg", "brand-new", previous
            )
            self.assertEqual(state["review_status"], "unreviewed")
            self.assertEqual(state["remarks"], "")

    def test_no_previous_inventory_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist.json"
            self.assertIsNone(MODULE.load_previous_inventory(missing))


class BuildInventoryTest(unittest.TestCase):
    """End-to-end: a small synthetic scan directory produces a correct inventory."""

    def test_build_inventory_over_synthetic_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "20260804-page-scans"
            source.mkdir()
            _write_image(source / "page-001.jpeg", (4350, 6450), "L", fill=0)
            _write_image(source / "titlepage.jpeg", (4350, 6450), "L", fill=40)
            _write_image(source / "page-002p1.jpeg", (5096, 6600), "RGB", fill=80)
            # Real m276.jpeg is 8812x12944; a smaller stand-in is enough to
            # exercise "unrecognized filename" without tripping PIL's
            # decompression-bomb guard on a synthetic fixture.
            _write_image(source / "m276.jpeg", (2000, 3000), "L", fill=120)
            _write_image(source / "page-065 1.jpeg", (192, 152), "L", fill=160)

            inventory = MODULE.build_inventory(source)

            self.assertEqual(inventory["image_count"], 5)
            by_name = {e["filename"]: e for e in inventory["entries"]}
            self.assertEqual(by_name["page-001.jpeg"]["anomalies"], [])
            self.assertEqual(by_name["titlepage.jpeg"]["anomalies"], [])
            self.assertEqual(by_name["page-002p1.jpeg"]["anomalies"], [])
            self.assertIn("unparseable_filename", by_name["m276.jpeg"]["anomalies"])
            self.assertIn("too_small", by_name["page-065 1.jpeg"]["anomalies"])
            self.assertIn(
                "unparseable_filename", by_name["page-065 1.jpeg"]["anomalies"]
            )


if __name__ == "__main__":
    unittest.main()

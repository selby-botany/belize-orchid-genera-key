"""Tests for the scan manifest generator."""

from __future__ import annotations

import csv
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "build_scan_manifest.py"
SPEC = importlib.util.spec_from_file_location("build_scan_manifest", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BuildScanManifestTest(unittest.TestCase):
    """Validate inventory facts against the source scan corpus."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = MODULE.build_manifest(PROJECT_ROOT / "page-scans")

    def test_corpus_counts_and_missing_pages(self) -> None:
        self.assertEqual(self.manifest["page_count"], 249)
        self.assertEqual(self.manifest["image_count"], 388)

        pages = self.manifest["pages"]
        missing = [page["page_number"] for page in pages if not page["candidates"]]
        self.assertEqual(missing, [16, 17])
        self.assertEqual(
            sum(len(page["candidates"]) == 1 for page in pages),
            129,
        )
        self.assertEqual(
            sum(len(page["candidates"]) > 1 for page in pages),
            118,
        )
        filenames = [
            candidate["filename"]
            for page in pages
            for candidate in page["candidates"]
        ]
        self.assertEqual(sum("-scan" not in name for name in filenames), 247)
        self.assertEqual(sum("-scan" in name for name in filenames), 141)

    def test_candidate_metadata_and_order(self) -> None:
        page_89 = self.manifest["pages"][89 - MODULE.FIRST_PAGE]
        self.assertEqual(
            [candidate["filename"] for candidate in page_89["candidates"]],
            ["089.jpg", *[f"089-scan{number}.jpg" for number in range(2, 8)]],
        )
        for candidate in page_89["candidates"]:
            self.assertGreater(candidate["width"], 0)
            self.assertGreater(candidate["height"], 0)
            self.assertGreater(candidate["byte_size"], 0)
            self.assertRegex(candidate["sha256"], r"^[0-9a-f]{64}$")
            self.assertIn(
                candidate["display_orientation"],
                {"portrait", "landscape", "square"},
            )

    def test_missing_pages_are_flagged_without_source_selection(self) -> None:
        pages = self.manifest["pages"]
        page_16 = pages[16 - MODULE.FIRST_PAGE]
        page_18 = pages[18 - MODULE.FIRST_PAGE]
        self.assertEqual(page_16["status"], "missing")
        self.assertEqual(page_16["review_reasons"], ["incomplete"])
        self.assertEqual(page_18["status"], "unreviewed")
        self.assertIsNone(page_18["primary_image"])

    def test_review_is_preserved_only_for_unchanged_candidates(self) -> None:
        previous = copy.deepcopy(self.manifest)
        page_16 = previous["pages"][16 - MODULE.FIRST_PAGE]
        page_16["reviewer"] = "reviewer"
        page_16["review_date"] = "2026-07-25"
        page_16["remarks"] = "Missing source confirmed."

        page_18 = previous["pages"][18 - MODULE.FIRST_PAGE]
        page_18["status"] = "accepted"
        page_18["primary_image"] = "018.jpg"
        page_18["candidates"][0]["filename"] = "stale-name.jpg"

        rebuilt = MODULE.build_manifest(PROJECT_ROOT / "page-scans", previous)
        rebuilt_page_16 = rebuilt["pages"][16 - MODULE.FIRST_PAGE]
        rebuilt_page_18 = rebuilt["pages"][18 - MODULE.FIRST_PAGE]
        self.assertEqual(rebuilt_page_16["reviewer"], "reviewer")
        self.assertEqual(rebuilt_page_16["remarks"], "Missing source confirmed.")
        self.assertEqual(rebuilt_page_18["status"], "unreviewed")
        self.assertIsNone(rebuilt_page_18["primary_image"])

    def test_json_and_csv_outputs_cover_every_page(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            MODULE.write_manifest(self.manifest, output_directory)

            parsed_json = json.loads(
                (output_directory / "pages.json").read_text(encoding="utf-8")
            )
            self.assertEqual(parsed_json, self.manifest)

            with (output_directory / "pages.csv").open(
                encoding="utf-8", newline=""
            ) as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 249)
            self.assertEqual(rows[0]["page_number"], "13")
            self.assertEqual(rows[-1]["page_number"], "261")


if __name__ == "__main__":
    unittest.main()
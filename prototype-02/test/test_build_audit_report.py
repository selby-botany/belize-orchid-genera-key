"""Tests for the visual scan audit report."""

from __future__ import annotations

import importlib.util
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "build_audit_report.py"
SPEC = importlib.util.spec_from_file_location("build_audit_report", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AuditParser(HTMLParser):
    """Collect page sections and image sources from generated HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.pages: list[tuple[str, str]] = []
        self.image_sources: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = dict(attrs)
        if tag == "section" and "page" in (values.get("class") or "").split():
            self.pages.append((values["data-page"], values["data-category"]))
        if tag == "img":
            self.image_sources.append(values["data-src"])


class BuildAuditReportTest(unittest.TestCase):
    """Validate visual report coverage and source references."""

    @classmethod
    def setUpClass(cls) -> None:
        manifest_path = PROJECT_ROOT / "manifest" / "pages.json"
        cls.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        cls.report = MODULE.build_html(cls.manifest)
        cls.parser = AuditParser()
        cls.parser.feed(cls.report)

    def test_report_covers_every_page_and_image(self) -> None:
        self.assertEqual(len(self.parser.pages), 249)
        self.assertEqual(len(self.parser.image_sources), 388)
        self.assertEqual(self.parser.pages[0], ("13", "single"))
        self.assertEqual(self.parser.pages[-1][0], "261")

    def test_priority_categories_match_corpus(self) -> None:
        categories = [category for _, category in self.parser.pages]
        self.assertEqual(categories.count("missing"), 2)
        self.assertEqual(categories.count("high-duplicate"), 14)
        self.assertEqual(categories.count("multi"), 104)
        self.assertEqual(categories.count("single"), 129)

    def test_every_image_source_resolves(self) -> None:
        report_directory = PROJECT_ROOT / "qa" / "reports"
        for source in self.parser.image_sources:
            self.assertTrue((report_directory / source).resolve().is_file(), source)


if __name__ == "__main__":
    unittest.main()
"""Tests for the preprocessing evidence-gathering module (Stage B)."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "bin" / "preprocess_scan.py"
SPEC = importlib.util.spec_from_file_location("preprocess_scan", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MeasureBackgroundStatsTest(unittest.TestCase):
    """Background statistics on a synthetic, known-flat image."""

    def test_uniform_background_has_near_zero_std(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "flat.jpeg"
            # Uniform paper tone (230) with a few dark "ink" pixels -- the
            # top-40%-brightest proxy should see only the paper.
            array = np.full((200, 200), 230, dtype=np.uint8)
            array[:20, :20] = 30  # a block of "ink"
            Image.fromarray(array, mode="L").save(path, quality=100)

            stats = MODULE.measure_background_stats(path)
            self.assertLess(stats["std"], 3.0)
            self.assertGreater(stats["mean"], 220.0)

    def test_gradient_background_has_higher_std(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gradient.jpeg"
            ramp = np.linspace(150, 250, 200, dtype=np.uint8)
            array = np.tile(ramp, (200, 1))
            Image.fromarray(array, mode="L").save(path, quality=100)

            stats = MODULE.measure_background_stats(path)
            self.assertGreater(stats["std"], MODULE.GRADIENT_STD_THRESHOLD)


class NeedsTransformTest(unittest.TestCase):
    """The accept/reject rule combines both thresholds."""

    def test_clean_page_does_not_need_transform(self) -> None:
        stats = {"mean": 230.0, "std": 3.0, "min": 200.0, "max": 255.0}
        self.assertFalse(MODULE.needs_transform(stats))

    def test_high_gradient_needs_transform(self) -> None:
        stats = {"mean": 230.0, "std": 20.0, "min": 150.0, "max": 255.0}
        self.assertTrue(MODULE.needs_transform(stats))

    def test_dark_background_needs_transform(self) -> None:
        stats = {"mean": 150.0, "std": 3.0, "min": 100.0, "max": 200.0}
        self.assertTrue(MODULE.needs_transform(stats))


class EvaluateInventoryTest(unittest.TestCase):
    """Only clean page/plate entries are measured; the rest are skipped."""

    def test_skips_front_matter_unrecognized_plates_and_anomalous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            array = np.full((200, 200), 230, dtype=np.uint8)
            for name in (
                "page-001.jpeg",
                "titlepage.jpeg",
                "m276.jpeg",
                "page-002.jpeg",
                "page-003p1.jpeg",
            ):
                Image.fromarray(array, mode="L").save(source / name, quality=100)

            inventory = {
                "entries": [
                    {
                        "filename": "page-001.jpeg",
                        "claimed_identity": {"kind": "page"},
                        "anomalies": [],
                    },
                    {
                        "filename": "titlepage.jpeg",
                        "claimed_identity": {"kind": "front_matter"},
                        "anomalies": [],
                    },
                    {
                        "filename": "m276.jpeg",
                        "claimed_identity": {"kind": "unrecognized"},
                        "anomalies": ["unparseable_filename"],
                    },
                    {
                        "filename": "page-002.jpeg",
                        "claimed_identity": {"kind": "page"},
                        "anomalies": ["too_small"],
                    },
                    {
                        "filename": "page-003p1.jpeg",
                        "claimed_identity": {"kind": "plate"},
                        "anomalies": [],
                    },
                ]
            }

            report = MODULE.evaluate_inventory(inventory, source)

            self.assertEqual(report["evaluated_count"], 1)
            self.assertEqual(report["entries"][0]["filename"], "page-001.jpeg")
            self.assertFalse(report["entries"][0]["needs_transform"])


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Decide whether OCR preprocessing is needed, and apply it if so (Stage B).

Whether any image transform runs at all is an evidence-based decision, not a
default (architecture document, §3.2): this capture batch already arrives
classified by colorspace (Stage A found zero `colorspace_mismatch`
anomalies across 242 files), so the question this module actually answers
is narrower than prototype-02's -- not "text or plate", but "does this
image's background show enough illumination gradient or cast to be worth
correcting before OCR."

Measured directly on a sample spanning the capture (page-010, page-050,
page-100, page-150, page-188, titlepage): background brightness (top 40% of
pixels by value, a proxy for paper tone that avoids ink) has a standard
deviation of 2.8-4.0 across every sampled page -- there is essentially no
gradient to remove -- and a mean of 224-236, comfortably above a "needs
whitening" floor. Both thresholds below are set with headroom above those
measured values, so a page that genuinely does have a lighting problem
still trips them.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

# A background standard deviation above this indicates a real illumination
# gradient or vignette (prototype-02's phone captures had exactly this
# problem; this capture batch, measured, does not -- see module docstring).
GRADIENT_STD_THRESHOLD = 8.0

# A background mean below this indicates paper that isn't close enough to
# white to skip whitening.
BACKGROUND_MEAN_FLOOR = 200.0

# Fraction of brightest pixels treated as "background" (paper), excluding
# ink. 0.4 was chosen empirically: text pages in this book are mostly paper
# by area, so the brightest 40% of pixels is reliably paper, not glyphs.
BACKGROUND_SAMPLE_FRACTION = 0.4


def measure_background_stats(path: Path) -> dict[str, float]:
    """Measure paper-tone brightness statistics for one image.

    Args:
        path: Image file.
    Returns:
        Dict with `mean`, `std`, `min`, `max` of the estimated background.
    """
    with Image.open(path) as image:
        gray = np.asarray(image.convert("L"), dtype=np.float32)
    flat = np.sort(gray.flatten())
    background = flat[-int(len(flat) * BACKGROUND_SAMPLE_FRACTION):]
    return {
        "mean": float(background.mean()),
        "std": float(background.std()),
        "min": float(background.min()),
        "max": float(background.max()),
    }


def needs_transform(stats: dict[str, float]) -> bool:
    """Decide, from measured evidence, whether a page needs preprocessing.

    Args:
        stats: Output of `measure_background_stats`.
    Returns:
        True when either threshold indicates a real lighting problem.
    """
    return (
        stats["std"] > GRADIENT_STD_THRESHOLD
        or stats["mean"] < BACKGROUND_MEAN_FLOOR
    )


def transform_text(path: Path, out_path: Path, imagemagick: Path) -> None:
    """Apply prototype-02's flat-field recipe for text and line art.

    Ported unchanged from `prototype-02/doc/20260730-claude-opus-5-image-preprocessing.md`.
    Dormant unless `needs_transform` finds evidence this batch needs it.

    Args:
        path: Source image.
        out_path: Where to write the transformed image.
        imagemagick: Path to the repository's `bin/imagemagick` wrapper.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(imagemagick),
            str(path),
            "-auto-orient",
            "-colorspace", "Gray",
            "(", "+clone", "-blur", "0x60", ")",
            "-compose", "Divide_Src",
            "-composite",
            "-level", "0%,90%",
            "-unsharp", "0x1.2+0.8+0.02",
            "-quality", "95",
            str(out_path),
        ],
        check=True,
    )


def transform_plate(path: Path, out_path: Path, imagemagick: Path) -> None:
    """Apply prototype-02's white-balance-only recipe for colour plates.

    Args:
        path: Source image.
        out_path: Where to write the transformed image.
        imagemagick: Path to the repository's `bin/imagemagick` wrapper.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(imagemagick),
            str(path),
            "-auto-orient",
            "-channel", "RGB",
            "-contrast-stretch", "0.2%x0.05%",
            "+channel",
            "-quality", "95",
            str(out_path),
        ],
        check=True,
    )


def evaluate_inventory(inventory: dict[str, Any], source_dir: Path) -> dict[str, Any]:
    """Measure and decide transform need for every text-page entry.

    Only `kind == "page"` is evaluated. Plates never reach Stage C's OCR in
    Phase 1 (architecture document, §4), so there is nothing to prepare them
    for yet -- and the "background = brightest 40% of pixels" proxy this
    module uses is specific to text-on-paper. Running it against a colour
    plate was tried during design and flagged 22 of 225 entries as needing a
    transform; every one of them was a plate, because a photograph's
    brightest pixels are just the brightest part of the photograph, not a
    paper tone, so the gradient-std heuristic reads normal photographic
    variance as a lighting defect. That is a real result about the proxy's
    scope, not about plate quality, which is why plates are excluded here
    rather than the thresholds being loosened to accommodate them. Front
    matter and unrecognized files are skipped for the same don't-reach-the-
    parser reason (front matter) or because they're a review-queue matter,
    not a preprocessing one (unrecognized).

    Args:
        inventory: Parsed `scan_inventory.json`.
        source_dir: Directory the inventory's filenames live in.
    Returns:
        Report dict: per-file stats/decision, and an overall summary.
    """
    results = []
    for entry in inventory["entries"]:
        kind = entry["claimed_identity"]["kind"]
        if kind != "page":
            continue
        if entry["anomalies"]:
            continue
        stats = measure_background_stats(source_dir / entry["filename"])
        results.append(
            {
                "filename": entry["filename"],
                "kind": kind,
                "stats": stats,
                "needs_transform": needs_transform(stats),
            }
        )

    transform_count = sum(1 for r in results if r["needs_transform"])
    return {
        "evaluated_count": len(results),
        "needs_transform_count": transform_count,
        "thresholds": {
            "gradient_std": GRADIENT_STD_THRESHOLD,
            "background_mean_floor": BACKGROUND_MEAN_FLOOR,
        },
        "entries": results,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inventory", type=Path, default=root / "manifest" / "scan_inventory.json"
    )
    parser.add_argument(
        "--source", type=Path, default=root / "images" / "20260804-page-scans"
    )
    parser.add_argument(
        "--output", type=Path, default=root / "manifest" / "preprocess_report.json"
    )
    return parser.parse_args()


def main() -> None:
    """Evaluate the whole inventory and write the preprocessing report."""
    arguments = parse_args()
    inventory = json.loads(arguments.inventory.read_text(encoding="utf-8"))
    report = evaluate_inventory(inventory, arguments.source)

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")

    if report["needs_transform_count"] == 0:
        print(
            f"{report['evaluated_count']} text pages evaluated: no evidence of "
            f"a lighting problem needing correction -> {arguments.output}"
        )
    else:
        print(
            f"{report['evaluated_count']} text pages evaluated: "
            f"{report['needs_transform_count']} need a transform (run "
            f"transform_text/transform_plate on those) -> {arguments.output}"
        )


if __name__ == "__main__":
    main()

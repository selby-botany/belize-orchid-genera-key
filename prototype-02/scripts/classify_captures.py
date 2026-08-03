#!/usr/bin/env python3
"""Classify captures as colour plates or monochrome text and line art.

Colour pages must keep their colour; text and line-art pages benefit from
grayscale flat-fielding. The captures carry a heavy tungsten cast, so
saturation is only discriminating after a gray-world white balance. The
threshold is chosen from the widest gap in the score distribution rather than
being hardcoded, because the two populations separate cleanly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

SATURATION_CUTOFF = 0.22
SEARCH_BAND = (0.08, 0.35)


def colour_score(path: Path) -> float:
    """Return the fraction of white-balanced pixels that are strongly coloured.

    Args:
        path: Image file to score.
    Returns:
        A value in [0, 1]; text pages score near zero, plates well above it.
    """
    image = Image.open(path)
    image.draft("RGB", (image.width // 12, image.height // 12))
    pixels = np.asarray(
        ImageOps.exif_transpose(image).convert("RGB"), dtype=np.float32
    ) + 1.0

    # Gray-world white balance: without it the tungsten cast saturates
    # every frame equally and the score carries no signal.
    pixels = pixels / pixels.reshape(-1, 3).mean(axis=0) * pixels.mean()

    highest = pixels.max(axis=2)
    lowest = pixels.min(axis=2)
    saturation = (highest - lowest) / np.maximum(highest, 1e-6)
    return float((saturation > SATURATION_CUTOFF).mean())


def choose_threshold(scores: list[float]) -> float:
    """Return the midpoint of the widest gap between the two populations.

    Args:
        scores: All colour scores for the capture set.
    Returns:
        The threshold above which a capture is treated as colour.
    """
    ordered = sorted(scores)
    gaps = [
        (ordered[index + 1] - ordered[index], ordered[index], ordered[index + 1])
        for index in range(len(ordered) - 1)
        if SEARCH_BAND[0] < ordered[index] < SEARCH_BAND[1]
    ]
    if not gaps:
        raise SystemExit("no separable gap found; inspect the score distribution")
    _, below, above = max(gaps)
    return (below + above) / 2.0


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path, default=root / "20260729-page-scans-original"
    )
    parser.add_argument(
        "--output", type=Path, default=root / "manifest" / "capture-classification.json"
    )
    parser.add_argument(
        "--force-colour",
        nargs="*",
        default=[],
        help="filenames to treat as colour regardless of score",
    )
    return parser.parse_args()


def main() -> None:
    """Score every capture and write the classification manifest."""
    arguments = parse_args()
    paths = sorted(
        path
        for path in arguments.source.iterdir()
        if path.suffix.lower() in {".jpg", ".jpeg"}
    )
    scored = {path.name: colour_score(path) for path in paths}
    threshold = choose_threshold(list(scored.values()))

    forced = set(arguments.force_colour)
    colour = sorted(
        name for name, score in scored.items() if score > threshold or name in forced
    )

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(
            {
                "source_directory": arguments.source.name,
                "saturation_cutoff": SATURATION_CUTOFF,
                "threshold": round(threshold, 6),
                "forced_colour": sorted(forced),
                "scores": {name: round(score, 6) for name, score in scored.items()},
                "colour": colour,
            },
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"threshold {threshold:.4f}: {len(colour)} colour, "
        f"{len(scored) - len(colour)} mono -> {arguments.output}"
    )


if __name__ == "__main__":
    main()

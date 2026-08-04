#!/usr/bin/env python3
"""Derive crop and rotation for flatbed scans of book pages.

Flatbed scans have no dark surround to detect a page edge against — the page
and the scanner bed are both white. Cropping to the *printed content* instead
is both more robust and what is actually wanted: the bounding box of all ink,
plus a fixed margin.

Emits one line per input: FILENAME ROTATE WIDTHxHEIGHT+X+Y
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SCALE = 8              # analysis downsample factor
INK_DELTA = 18         # how much darker than local background counts as ink
RUN_FRACTION = 0.08    # projection threshold for counting text lines


def ink_mask(gray: np.ndarray) -> np.ndarray:
    """Return a boolean mask of printed ink.

    Args:
        gray: Grayscale image as a float array.
    Returns:
        Boolean array, True where ink is present.
    """
    background = ndimage.uniform_filter(gray, size=31)
    mask = gray < (background - INK_DELTA)
    return ndimage.binary_opening(mask, np.ones((2, 2)))


def drop_border_components(mask: np.ndarray) -> np.ndarray:
    """Remove components touching the scan border.

    Printed content always sits inside a page margin. Anything reaching the
    edge of the scan is bed shadow, the book's fore-edge, or lid gap.

    Args:
        mask: Ink mask.
    Returns:
        The mask with border-connected components removed.
    """
    labelled, count = ndimage.label(mask)
    if count == 0:
        return mask
    edge = set(labelled[0, :]) | set(labelled[-1, :])
    edge |= set(labelled[:, 0]) | set(labelled[:, -1])
    edge.discard(0)
    if edge:
        mask = mask & ~np.isin(labelled, list(edge))
    return mask


def line_runs(mask: np.ndarray, axis: int) -> int:
    """Count ink bands along a projection.

    Text lines produce many alternations perpendicular to the baseline and
    very few parallel to it, which identifies page orientation reliably even
    on figure pages with only a caption.

    Args:
        mask: Ink mask.
        axis: Axis to sum over.
    Returns:
        Number of distinct ink bands.
    """
    profile = mask.sum(axis=axis).astype(float)
    if profile.max() == 0:
        return 0
    active = profile > (RUN_FRACTION * profile.max())
    return int(np.count_nonzero(active[1:] & ~active[:-1]))


def text_bands(mask: np.ndarray, fraction: float = 0.03) -> list[tuple[int, int]]:
    """Return the vertical extents of horizontal ink bands.

    Args:
        mask: Ink mask.
        fraction: Projection threshold as a fraction of the maximum.
    Returns:
        List of (start, end) row indices, top to bottom.
    """
    profile = mask.sum(axis=1).astype(float)
    if profile.max() == 0:
        return []
    active = profile > (fraction * profile.max())
    changes = np.flatnonzero(active[1:] != active[:-1]) + 1
    edges = np.concatenate(([0], changes, [len(active)]))
    return [
        (start, end)
        for start, end in zip(edges[:-1], edges[1:])
        if active[start] and (end - start) >= 3
    ]


def is_upside_down(mask: np.ndarray) -> bool:
    """Report whether the page is rotated 180 degrees.

    Scanning a bound book naturally alternates page orientation, so half the
    scans arrive inverted. The reliable cue is the running head: it sits alone
    above the body, separated by a gap much larger than any gap between body
    lines. Ascender-versus-descender mass was tried first and is not usable —
    the projection threshold clips ascenders, which inverts the signal.

    Args:
        mask: Ink mask.
    Returns:
        True when the page needs a 180 degree rotation.
    """
    bands = text_bands(mask)
    if len(bands) < 4:
        return False
    gaps = [bands[i + 1][0] - bands[i][1] for i in range(len(bands) - 1)]
    body = float(np.median(gaps))
    return (gaps[-1] - body) > (gaps[0] - body)


def geometry(path: Path, margin_inches: float, dpi: int) -> tuple[int, tuple[int, int, int, int]]:
    """Return the rotation and crop box for one scan.

    Args:
        path: Scan file.
        margin_inches: Margin to leave beyond the printed extrema.
        dpi: Scan resolution, used to convert the margin to pixels.
    Returns:
        (rotation in degrees, (left, top, right, bottom)).
    """
    image = Image.open(path)
    image.draft("L", (image.width // SCALE, image.height // SCALE))
    gray = np.asarray(image.convert("L"), dtype=np.float32)

    mask = drop_border_components(ink_mask(gray))
    rotate = 0 if line_runs(mask, 1) >= line_runs(mask, 0) else 90
    if rotate == 0 and is_upside_down(mask):
        rotate = 180

    # The crop is applied before rotation, so the box must stay in source
    # coordinates. Flipping the mask here would silently crop the wrong region.
    ys, xs = np.where(mask)
    if ys.size == 0:
        width, height = Image.open(path).size
        return rotate, (0, 0, width, height)

    pad = (margin_inches * dpi) / SCALE
    width, height = Image.open(path).size
    box = (
        max(0, int((xs.min() - pad) * SCALE)),
        max(0, int((ys.min() - pad) * SCALE)),
        min(width, int((xs.max() + pad) * SCALE)),
        min(height, int((ys.max() + pad) * SCALE)),
    )
    return rotate, box


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scans", nargs="+", type=Path)
    parser.add_argument("--margin-inches", type=float, default=0.25)
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def header_corner(mask: np.ndarray) -> str:
    """Report where the page number sits in the topmost ink band.

    Page numbers are printed at the outer top corner — left on a verso, right
    on a recto — with the running head centred beside them. This is an
    independent confirmation of orientation and also identifies recto versus
    verso. Returns "left", "right", or "none".

    Args:
        mask: Ink mask, already oriented upright.
    Returns:
        Which outer corner carries an isolated cluster in the top band.
    """
    bands = text_bands(mask)
    if not bands:
        return "none"
    start, end = bands[0]
    columns = mask[start:end].sum(axis=0)
    if columns.max() == 0:
        return "none"
    filled = np.flatnonzero(columns > 0)
    width = mask.shape[1]
    outer = 0.20 * width
    left = filled[0] < outer
    right = filled[-1] > (width - outer)
    if left and not right:
        return "left"
    if right and not left:
        return "right"
    return "none"


def main() -> None:
    """Print crop geometry for every scan given."""
    arguments = parse_args()
    for path in arguments.scans:
        rotate, box = geometry(path, arguments.margin_inches, arguments.dpi)
        left, top, right, bottom = box
        image = Image.open(path)
        image.draft("L", (image.width // SCALE, image.height // SCALE))
        mask = drop_border_components(
            ink_mask(np.asarray(image.convert("L"), dtype=np.float32))
        )
        if rotate == 180:
            mask = mask[::-1, ::-1]
        elif rotate == 90:
            mask = np.rot90(mask, -1)
        corner = header_corner(mask)
        side = {"left": "verso", "right": "recto"}.get(corner, "unknown")
        print(
            f"{path.name} {rotate} {right-left}x{bottom-top}+{left}+{top} {side}"
        )


if __name__ == "__main__":
    main()

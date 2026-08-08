#!/usr/bin/env python3
"""Audit the prototype-03 scan directory (Stage A).

Walks a directory of page captures once and records, per file: a content
checksum, pixel dimensions, colorspace, a parsed "claimed identity" from the
filename, and any anomalies found. Nothing is discarded and nothing aborts
the pass -- a file that doesn't fit any expected pattern is recorded as an
anomaly, not a fatal error (see doc 5, "Carried-forward defects", #3).

Review-state carry-forward is keyed by content checksum (SHA-256), not by
filename or list position, so replacing a file's *content* resets its review
state while renaming or reordering files does not lose one (doc 5, #1).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image

# These are trusted, locally captured scans of a physical book, not
# untrusted uploads -- disable PIL's decompression-bomb guard rather than
# let it warn (or later, at a larger size, refuse to open) a legitimate
# high-resolution capture such as m276.jpeg (8812x12944).
Image.MAX_IMAGE_PIXELS = None

SCHEMA_VERSION = 1

# Minimum size, in pixels, on the smaller dimension, below which a file is
# too small to be a real capture. Real pages are ~4350x6450 px and plates
# ~5096x6600 px; the known corrupt stub (page-065 1.jpeg) is 192x152.
MIN_DIMENSION = 500

# Filename stems (without extension) known to be front matter, established
# by direct inspection of the capture set. Extending this list is a
# one-line change, not a broadening of the page-number pattern.
FRONT_MATTER_LABELS = frozenset(
    {
        "acknowledgments-1",
        "copyrightpage",
        "dedication-page",
        "forward-1",
        "frontis-1",
        "frontis-plate-1",
        "preface-1",
        "preface-2",
        "titlepage",
        "toc-1",
        "toc-2",
        "toc-3",
        "toc-4",
        "toc-5",
    }
)

PAGE_PATTERN = re.compile(r"^page-(\d{3})\.jpeg$")
PLATE_PATTERN = re.compile(r"^page-(\d{3})p([12])\.jpeg$")

# PIL image mode -> the colorspace label recorded in the inventory.
COLORSPACE_BY_MODE = {"L": "Gray", "RGB": "sRGB", "CMYK": "CMYK"}


def sha256_of(path: Path) -> str:
    """Return the hex SHA-256 digest of a file's content.

    Args:
        path: File to hash.
    Returns:
        Lowercase hex digest string.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def identify(path: Path) -> dict[str, Any]:
    """Return pixel dimensions and colorspace for an image.

    Uses PIL directly rather than shelling out to ImageMagick, matching
    prototype-02's classify_captures.py.

    Args:
        path: Image file.
    Returns:
        Dict with `width`, `height`, `colorspace`.
    """
    with Image.open(path) as image:
        width, height = image.size
        colorspace = COLORSPACE_BY_MODE.get(image.mode, image.mode)
    return {"width": width, "height": height, "colorspace": colorspace}


def parse_claimed_identity(filename: str) -> dict[str, Any]:
    """Derive the identity a filename claims for itself.

    Args:
        filename: Base filename, e.g. `page-050.jpeg`.
    Returns:
        Dict with `kind` (page | front_matter | plate | unrecognized) and,
        depending on kind, `page_number`, `label`, `linked_page`,
        `plate_index`.
    """
    identity: dict[str, Any] = {
        "kind": "unrecognized",
        "page_number": None,
        "label": None,
        "linked_page": None,
        "plate_index": None,
    }

    page_match = PAGE_PATTERN.match(filename)
    if page_match:
        identity["kind"] = "page"
        identity["page_number"] = int(page_match.group(1))
        return identity

    plate_match = PLATE_PATTERN.match(filename)
    if plate_match:
        identity["kind"] = "plate"
        identity["linked_page"] = int(plate_match.group(1))
        identity["plate_index"] = int(plate_match.group(2))
        return identity

    stem = Path(filename).stem
    if stem in FRONT_MATTER_LABELS:
        identity["kind"] = "front_matter"
        identity["label"] = stem
        return identity

    return identity


def detect_anomalies(
    entry: dict[str, Any], all_entries: list[dict[str, Any]]
) -> list[str]:
    """Flag problems with one entry, given the whole entry list.

    Args:
        entry: The entry to check.
        all_entries: Every entry built so far (for duplicate detection).
    Returns:
        List of anomaly strings; empty when none are found.
    """
    anomalies: list[str] = []

    if min(entry["width"], entry["height"]) < MIN_DIMENSION:
        anomalies.append("too_small")

    for other in all_entries:
        if other is entry:
            break
        if other["sha256"] == entry["sha256"]:
            anomalies.append(f"duplicate_of:{other['filename']}")
            break

    identity = entry["claimed_identity"]
    if identity["kind"] == "unrecognized":
        anomalies.append("unparseable_filename")
    elif identity["kind"] == "plate" and entry["colorspace"] != "sRGB":
        anomalies.append("colorspace_mismatch")
    elif identity["kind"] == "page" and entry["colorspace"] != "Gray":
        anomalies.append("colorspace_mismatch")

    return anomalies


def load_previous_inventory(path: Path) -> dict[str, Any] | None:
    """Load a prior inventory, if one exists, for review-state carry-forward.

    Args:
        path: Path to a previously generated `scan_inventory.json`.
    Returns:
        A dict with `by_sha256` and `by_filename` lookups, or None if no
        prior inventory exists.
    """
    if not path.exists():
        return None
    previous = json.loads(path.read_text(encoding="utf-8"))
    by_sha256: dict[str, dict[str, Any]] = {}
    by_filename: dict[str, dict[str, Any]] = {}
    for old_entry in previous.get("entries", []):
        review_state = {
            "review_status": old_entry["review_status"],
            "review_checksum": old_entry["review_checksum"],
            "remarks": old_entry["remarks"],
        }
        by_sha256[old_entry["sha256"]] = review_state
        by_filename[old_entry["filename"]] = {
            **review_state,
            "sha256": old_entry["sha256"],
        }
    return {"by_sha256": by_sha256, "by_filename": by_filename}


def carry_forward_review_state(
    filename: str, sha256: str, previous: dict[str, Any] | None
) -> dict[str, Any]:
    """Determine review state for one entry, carrying it forward if safe.

    Args:
        filename: The entry's filename.
        sha256: The entry's current content checksum.
        previous: Output of `load_previous_inventory`, or None.
    Returns:
        Dict with `review_status`, `review_checksum`, `remarks`.
    """
    if previous is None:
        return {"review_status": "unreviewed", "review_checksum": sha256, "remarks": ""}

    matched = previous["by_sha256"].get(sha256)
    if matched is not None:
        return {**matched, "review_checksum": sha256}

    stale = previous["by_filename"].get(filename)
    if stale is not None and stale["sha256"] != sha256:
        return {
            "review_status": "unreviewed",
            "review_checksum": sha256,
            "remarks": f"content changed; supersedes {stale['sha256']}",
        }

    return {"review_status": "unreviewed", "review_checksum": sha256, "remarks": ""}


def build_inventory(
    source_dir: Path, previous: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build the full inventory for a scan directory.

    Args:
        source_dir: Directory of `.jpeg` captures.
        previous: Output of `load_previous_inventory`, or None.
    Returns:
        The inventory dict, matching the `scan_inventory.json` schema.
    """
    entries: list[dict[str, Any]] = []
    paths = sorted(p for p in source_dir.iterdir() if p.suffix.lower() == ".jpeg")

    for path in paths:
        facts = identify(path)
        digest = sha256_of(path)
        review_state = carry_forward_review_state(path.name, digest, previous)
        entry = {
            "filename": path.name,
            "sha256": digest,
            "byte_size": path.stat().st_size,
            "width": facts["width"],
            "height": facts["height"],
            "colorspace": facts["colorspace"],
            "claimed_identity": parse_claimed_identity(path.name),
            "anomalies": [],
            **review_state,
        }
        entries.append(entry)

    for entry in entries:
        entry["anomalies"] = detect_anomalies(entry, entries)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": None,  # filled in by main(); omitted from tests
        "source_directory": source_dir.name,
        "image_count": len(entries),
        "entries": entries,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "images" / "20260804-page-scans",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "manifest" / "scan_inventory.json",
    )
    return parser.parse_args()


def main() -> None:
    """Build and write the scan inventory, carrying forward review state."""
    import datetime

    arguments = parse_args()
    previous = load_previous_inventory(arguments.output)
    inventory = build_inventory(arguments.source, previous)
    inventory["generated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(inventory, indent=1) + "\n", encoding="utf-8"
    )

    anomaly_count = sum(1 for e in inventory["entries"] if e["anomalies"])
    print(
        f"{inventory['image_count']} files, {anomaly_count} with anomalies "
        f"-> {arguments.output}"
    )


if __name__ == "__main__":
    main()

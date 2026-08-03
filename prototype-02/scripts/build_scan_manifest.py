#!/usr/bin/env python3
"""Build deterministic JSON and CSV manifests for the page scan corpus."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import BinaryIO


FIRST_PAGE = 13
LAST_PAGE = 261
MANIFEST_VERSION = 1
SCAN_NAME = re.compile(r"^(?P<page>\d{3})(?:-scan(?P<scan>\d+))?\.jpg$")
REVIEW_FIELDS = (
    "primary_image",
    "supplemental_regions",
    "status",
    "review_reasons",
    "reviewer",
    "review_date",
    "remarks",
)
START_OF_FRAME_MARKERS = {
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC5,
    0xC6,
    0xC7,
    0xC9,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
}


def _exif_orientation(payload: bytes) -> int | None:
    """Return the EXIF orientation from an APP1 payload when present."""
    if not payload.startswith(b"Exif\x00\x00"):
        return None

    tiff = payload[6:]
    if len(tiff) < 8 or tiff[:2] not in {b"II", b"MM"}:
        return None

    byte_order = "<" if tiff[:2] == b"II" else ">"
    if struct.unpack_from(f"{byte_order}H", tiff, 2)[0] != 42:
        return None

    ifd_offset = struct.unpack_from(f"{byte_order}I", tiff, 4)[0]
    if ifd_offset + 2 > len(tiff):
        return None

    entry_count = struct.unpack_from(f"{byte_order}H", tiff, ifd_offset)[0]
    for index in range(entry_count):
        offset = ifd_offset + 2 + index * 12
        if offset + 12 > len(tiff):
            return None
        tag, value_type, count = struct.unpack_from(
            f"{byte_order}HHI", tiff, offset
        )
        if tag == 0x0112 and value_type == 3 and count == 1:
            return struct.unpack_from(f"{byte_order}H", tiff, offset + 8)[0]
    return None


def _read_segment(stream: BinaryIO) -> tuple[int, bytes] | None:
    """Read the next length-prefixed JPEG segment."""
    prefix = stream.read(1)
    while prefix and prefix != b"\xff":
        prefix = stream.read(1)
    if not prefix:
        return None

    marker_byte = stream.read(1)
    while marker_byte == b"\xff":
        marker_byte = stream.read(1)
    if not marker_byte:
        return None

    marker = marker_byte[0]
    if marker in {0x01, *range(0xD0, 0xDA)}:
        return marker, b""

    length_bytes = stream.read(2)
    if len(length_bytes) != 2:
        raise ValueError("truncated JPEG segment length")
    length = struct.unpack(">H", length_bytes)[0]
    if length < 2:
        raise ValueError("invalid JPEG segment length")

    payload = stream.read(length - 2)
    if len(payload) != length - 2:
        raise ValueError("truncated JPEG segment")
    return marker, payload


def jpeg_metadata(path: Path) -> dict[str, int | str | None]:
    """Read dimensions and EXIF orientation without external dependencies."""
    width = None
    height = None
    orientation = None

    with path.open("rb") as stream:
        if stream.read(2) != b"\xff\xd8":
            raise ValueError(f"not a JPEG file: {path}")

        while segment := _read_segment(stream):
            marker, payload = segment
            if marker == 0xE1 and orientation is None:
                orientation = _exif_orientation(payload)
            if marker in START_OF_FRAME_MARKERS:
                if len(payload) < 5:
                    raise ValueError(f"invalid JPEG frame header: {path}")
                height, width = struct.unpack_from(">HH", payload, 1)
            if width is not None and height is not None and orientation is not None:
                break
            if marker in {0xD9, 0xDA}:
                break

    if width is None or height is None:
        raise ValueError(f"JPEG dimensions not found: {path}")

    display_width, display_height = width, height
    if orientation in {5, 6, 7, 8}:
        display_width, display_height = height, width

    display_orientation = "portrait"
    if display_width > display_height:
        display_orientation = "landscape"
    elif display_width == display_height:
        display_orientation = "square"

    return {
        "width": width,
        "height": height,
        "exif_orientation": orientation,
        "display_orientation": display_orientation,
    }


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_sort_key(path: Path) -> tuple[int, int]:
    """Sort a base capture before its numbered alternate captures."""
    match = SCAN_NAME.fullmatch(path.name)
    if match is None:
        raise ValueError(f"unsupported scan filename: {path.name}")
    return int(match.group("page")), int(match.group("scan") or 1)


def build_manifest(
    scan_directory: Path,
    previous_manifest: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build one manifest record for each expected printed page."""
    previous_pages = {
        int(page["page_number"]): page
        for page in (previous_manifest or {}).get("pages", [])
    }
    scans: dict[int, list[Path]] = {}
    for path in scan_directory.iterdir():
        if path.suffix.lower() not in {".jpg", ".jpeg"}:
            continue
        match = SCAN_NAME.fullmatch(path.name)
        if match is None:
            raise ValueError(f"unsupported scan filename: {path.name}")
        page_number = int(match.group("page"))
        if page_number < FIRST_PAGE or page_number > LAST_PAGE:
            raise ValueError(f"scan outside expected page range: {path.name}")
        scans.setdefault(page_number, []).append(path)

    pages = []
    image_count = 0
    for page_number in range(FIRST_PAGE, LAST_PAGE + 1):
        candidates = []
        for path in sorted(scans.get(page_number, []), key=scan_sort_key):
            metadata = jpeg_metadata(path)
            candidates.append(
                {
                    "filename": path.name,
                    "byte_size": path.stat().st_size,
                    "sha256": sha256(path),
                    **metadata,
                }
            )
            image_count += 1

        page = {
            "page_number": page_number,
            "candidates": candidates,
            "primary_image": None,
            "supplemental_regions": [],
            "status": "unreviewed" if candidates else "missing",
            "review_reasons": ["incomplete"] if not candidates else [],
            "reviewer": None,
            "review_date": None,
            "remarks": "",
        }
        previous_page = previous_pages.get(page_number)
        previous_filenames = [
            candidate["filename"]
            for candidate in (previous_page or {}).get("candidates", [])
        ]
        current_filenames = [candidate["filename"] for candidate in candidates]
        if previous_page is not None and previous_filenames == current_filenames:
            for field in REVIEW_FIELDS:
                page[field] = previous_page[field]
        pages.append(page)

    return {
        "manifest_version": MANIFEST_VERSION,
        "source_directory": "page-scans",
        "expected_page_range": {"first": FIRST_PAGE, "last": LAST_PAGE},
        "page_count": len(pages),
        "image_count": image_count,
        "pages": pages,
    }


def write_csv(manifest: dict[str, object], output_path: Path) -> None:
    """Write a human-readable one-row-per-page manifest."""
    fieldnames = [
        "page_number",
        "candidate_count",
        "candidates",
        "primary_image",
        "supplemental_regions",
        "status",
        "review_reasons",
        "reviewer",
        "review_date",
        "remarks",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for page in manifest["pages"]:
            candidate_summary = "; ".join(
                f"{item['filename']}|{item['width']}x{item['height']}|"
                f"{item['byte_size']}|{item['sha256']}"
                for item in page["candidates"]
            )
            writer.writerow(
                {
                    **page,
                    "candidate_count": len(page["candidates"]),
                    "candidates": candidate_summary,
                    "supplemental_regions": json.dumps(
                        page["supplemental_regions"], separators=(",", ":")
                    ),
                    "review_reasons": ";".join(page["review_reasons"]),
                }
            )


def write_manifest(manifest: dict[str, object], output_directory: Path) -> None:
    """Write deterministic JSON and CSV manifest files."""
    output_directory.mkdir(parents=True, exist_ok=True)
    json_path = output_directory / "pages.json"
    json_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_csv(manifest, output_directory / "pages.csv")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    project_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scan-directory",
        type=Path,
        default=project_root / "page-scans",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=project_root / "manifest",
    )
    return parser.parse_args()


def main() -> None:
    """Build and write the scan manifest."""
    arguments = parse_args()
    previous_path = arguments.output_directory / "pages.json"
    previous_manifest = None
    if previous_path.is_file():
        previous_manifest = json.loads(previous_path.read_text(encoding="utf-8"))
    manifest = build_manifest(arguments.scan_directory, previous_manifest)
    write_manifest(manifest, arguments.output_directory)
    print(
        f"Wrote {manifest['page_count']} pages and "
        f"{manifest['image_count']} images to {arguments.output_directory}"
    )


if __name__ == "__main__":
    main()
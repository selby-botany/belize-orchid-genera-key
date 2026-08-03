#!/usr/bin/env python3

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Anchor:
    index: int
    page: int


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manual_overrides(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"manual overrides must be a JSON object: {path}")

    overrides: dict[str, int] = {}
    for image, page in data.items():
        if not isinstance(image, str) or not isinstance(page, int):
            raise SystemExit(f"manual override entries must map image names to integer pages: {path}")
        overrides[image] = page

    return overrides


def collect_anchors(entries: list[dict]) -> list[Anchor]:
    anchors: list[Anchor] = []
    for i, e in enumerate(entries):
        page = e.get("inferred_page")
        if e.get("needs_review") is False and isinstance(page, int):
            anchors.append(Anchor(index=i, page=page))
    return anchors


def enrich_entries(entries: list[dict], anchors: list[Anchor], overrides: dict[str, int]) -> list[dict]:
    out = []
    anchor_lookup = {a.index: a.page for a in anchors}

    # Build strict interpolation windows where index and page deltas match exactly.
    windows: list[tuple[int, int, int]] = []
    for left, right in zip(anchors, anchors[1:]):
        delta_index = right.index - left.index
        delta_page = right.page - left.page
        if delta_index > 1 and delta_page == delta_index:
            windows.append((left.index, right.index, left.page))

    for idx, original in enumerate(entries):
        item = dict(original)
        page = item.get("inferred_page")
        image = str(item.get("image"))

        if image in overrides:
            item["proposed_page"] = overrides[image]
            item["proposed_source"] = "manual_override"
            out.append(item)
            continue

        if idx in anchor_lookup:
            item["proposed_page"] = anchor_lookup[idx]
            item["proposed_source"] = "ocr_anchor"
            out.append(item)
            continue

        proposed = None
        for start, end, start_page in windows:
            if start < idx < end:
                proposed = start_page + (idx - start)
                break

        if proposed is not None:
            item["proposed_page"] = proposed
            item["proposed_source"] = "strict_interpolation"
        elif isinstance(page, int):
            item["proposed_page"] = page
            item["proposed_source"] = "ocr_low_confidence"
        else:
            item["proposed_page"] = None
            item["proposed_source"] = "unresolved"

        out.append(item)

    return out


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    analysis = root / "analysis"
    input_path = analysis / "mcleish_manifest.json"
    output_path = analysis / "mcleish_manifest_postprocessed.json"
    overrides_path = analysis / "mcleish_manual_overrides.json"

    if not input_path.exists():
        raise SystemExit(f"missing input: {input_path}")

    manifest = load_manifest(input_path)
    overrides = load_manual_overrides(overrides_path)
    entries = manifest.get("entries", [])
    anchors = collect_anchors(entries)
    enriched = enrich_entries(entries, anchors, overrides)

    by_source: dict[str, int] = {}
    for e in enriched:
        src = e["proposed_source"]
        by_source[src] = by_source.get(src, 0) + 1

    out = {
        "schema_version": 1,
        "generated_from": "analysis/mcleish_manifest.json",
        "summary": {
            "total_entries": len(enriched),
            "manual_override_entries": by_source.get("manual_override", 0),
            "ocr_anchor_entries": by_source.get("ocr_anchor", 0),
            "strict_interpolation_entries": by_source.get("strict_interpolation", 0),
            "ocr_low_confidence_entries": by_source.get("ocr_low_confidence", 0),
            "unresolved_entries": by_source.get("unresolved", 0),
        },
        "entries": enriched,
    }

    output_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote: {output_path}")
    print(json.dumps(out["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
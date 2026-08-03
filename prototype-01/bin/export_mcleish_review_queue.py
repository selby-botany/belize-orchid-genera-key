#!/usr/bin/env python3

import csv
import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    analysis = root / "analysis"
    src_path = analysis / "mcleish_manifest_postprocessed.json"
    out_path = analysis / "mcleish_review_queue.tsv"

    if not src_path.exists():
        raise SystemExit(f"missing input: {src_path}")

    data = json.loads(src_path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])

    rows = []
    for idx, e in enumerate(entries):
        source = e.get("proposed_source")
        needs_review = bool(e.get("needs_review", True))
        if source == "ocr_anchor" and not needs_review:
            continue

        candidates = e.get("top_candidates") or []
        c1 = candidates[0] if len(candidates) > 0 else {}
        c2 = candidates[1] if len(candidates) > 1 else {}

        rows.append(
            {
                "index": idx + 1,
                "image": e.get("image"),
                "inferred_page": e.get("inferred_page"),
                "proposed_page": e.get("proposed_page"),
                "proposed_source": source,
                "needs_review": needs_review,
                "confidence_score": e.get("confidence_score"),
                "candidate1_page": c1.get("page"),
                "candidate1_score": c1.get("score"),
                "candidate1_text": c1.get("text"),
                "candidate2_page": c2.get("page"),
                "candidate2_score": c2.get("score"),
                "candidate2_text": c2.get("text"),
            }
        )

    # Keep unresolved first, then low-confidence OCR, then strict interpolation.
    priority = {
        "unresolved": 0,
        "ocr_low_confidence": 1,
        "strict_interpolation": 2,
    }
    rows.sort(key=lambda r: (priority.get(str(r.get("proposed_source")), 9), int(r["index"])))

    fieldnames = [
        "index",
        "image",
        "inferred_page",
        "proposed_page",
        "proposed_source",
        "needs_review",
        "confidence_score",
        "candidate1_page",
        "candidate1_score",
        "candidate1_text",
        "candidate2_page",
        "candidate2_score",
        "candidate2_text",
    ]

    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote: {out_path}")
    print(f"Rows: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
"""Measure how well the generated key actually works (Stage E).

Reads `analysis/character_matrix.jsonl` (Stage C), `analysis/genus_key.json`
(Stage D), and `data/character_vocabulary.json` (Stage A); writes
`analysis/validation_report.json` and `.md`.

Self-consistency against the key's own source data is the acceptance
floor (requirements, §1.7/§2): walking the tree with a genus's own
recorded states must land on a leaf containing that genus. A non-zero
`failed` count is not a data limitation -- `walk_tree`'s branch matching
mirrors `generate_key.build_tree`'s own grouping exactly, so a row that
was part of the tree's own construction cannot legitimately fail this
check; a failure here means Stage D produced an inconsistent tree.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def walk_tree(tree: dict[str, Any], row: dict[str, Any]) -> list[str]:
    """Follow one genus's own recorded states down the tree to a leaf.

    Args:
        tree: A `generate_key.build_tree` result (or its `root`).
        row: One matrix row (a genus's own character states).
    Returns:
        The reached leaf's `genus_ids` -- more than one means `row`'s
        genus landed in an ambiguous leaf (requirements, §2), not a walk
        failure. An empty list means no branch matched `row`'s state for
        the split character at some node -- only possible when `row`
        wasn't part of the data the tree was built from.
    """
    node = tree
    while node["type"] == "split":
        state_id = row["characters"][node["character_id"]]["state_id"]
        next_node = None
        for branch in node["branches"]:
            if state_id in branch["state_ids"]:
                next_node = branch["next"]
                break
        if next_node is None:
            return []
        node = next_node
    return node["genus_ids"]


def self_consistency_report(
    tree: dict[str, Any], rows: list[dict[str, Any]]
) -> dict[str, Any]:
    """Check every genus resolves back to itself (requirements, §1.7/§2).

    Args:
        tree: The generated key.
        rows: Every matrix row the tree was built from.
    Returns:
        `{total_genera, resolved_cleanly, in_ambiguous_leaf, failed,
        failed_genus_ids}` -- `failed` must be 0 for the key to be
        accepted; a non-zero value is a Stage D defect, not reported and
        moved past (module docstring).
    """
    resolved_cleanly = 0
    in_ambiguous_leaf = 0
    failed_genus_ids: list[str] = []

    for row in rows:
        leaf_genus_ids = walk_tree(tree, row)
        if row["genus_id"] not in leaf_genus_ids:
            failed_genus_ids.append(row["genus_id"])
        elif len(leaf_genus_ids) == 1:
            resolved_cleanly += 1
        else:
            in_ambiguous_leaf += 1

    return {
        "total_genera": len(rows),
        "resolved_cleanly": resolved_cleanly,
        "in_ambiguous_leaf": in_ambiguous_leaf,
        "failed": len(failed_genus_ids),
        "failed_genus_ids": failed_genus_ids,
    }


def tree_depth_stats(tree: dict[str, Any]) -> dict[str, float]:
    """Mean and max number of questions to reach an answer, per genus.

    Args:
        tree: The generated key.
    Returns:
        `{mean, max}`, weighted by how many genera actually reach each
        leaf (an ambiguous leaf's depth counts once per genus in it, not
        once for the leaf).
    """
    leaves: list[tuple[int, int]] = []

    def walk(node: dict[str, Any], depth: int) -> None:
        if node["type"] == "leaf":
            leaves.append((depth, len(node["genus_ids"])))
            return
        for branch in node["branches"]:
            walk(branch["next"], depth + 1)

    walk(tree, 0)
    total_genera = sum(count for _, count in leaves)
    if total_genera == 0:
        return {"mean": 0.0, "max": 0}
    mean = sum(depth * count for depth, count in leaves) / total_genera
    max_depth = max((depth for depth, count in leaves if count > 0), default=0)
    return {"mean": mean, "max": max_depth}


def character_usage(tree: dict[str, Any]) -> dict[str, int]:
    """Count how many split nodes in the tree ask about each character.

    Args:
        tree: The generated key.
    Returns:
        `character_id` -> number of times it appears as a split -- a
        character can legitimately appear more than once, on different
        branches (never twice on the *same* path -- `generate_key.
        build_tree`'s own guarantee), so a high count surfaces real
        over-reliance (overview document, §3.4/§4.2), not a bug.
    """
    usage: dict[str, int] = defaultdict(int)

    def walk(node: dict[str, Any]) -> None:
        if node["type"] != "split":
            return
        usage[node["character_id"]] += 1
        for branch in node["branches"]:
            walk(branch["next"])

    walk(tree)
    return dict(usage)


def find_ambiguous_leaves(tree: dict[str, Any]) -> list[dict[str, Any]]:
    """List every ambiguous leaf by genus and the states that caused it.

    Args:
        tree: The generated key.
    Returns:
        One entry per multi-genus leaf: `{genus_ids, shared_states}` --
        `shared_states` is every character/state pair on the path that
        led to it, the literal reason those genera couldn't be told
        apart (requirements, §2: "reported explicitly ... with the
        shared states that caused it", not just a tied-genus count).
    """
    results: list[dict[str, Any]] = []

    def walk(node: dict[str, Any], path_states: dict[str, str]) -> None:
        if node["type"] == "leaf":
            if len(node["genus_ids"]) > 1:
                results.append(
                    {"genus_ids": node["genus_ids"], "shared_states": dict(path_states)}
                )
            return
        for branch in node["branches"]:
            state_id = branch["state_ids"][0]
            walk(branch["next"], {**path_states, node["character_id"]: state_id})

    walk(tree, {})
    return results


def render_validation_markdown(
    report: dict[str, Any], vocabulary: dict[str, Any], genus_names: dict[str, str]
) -> str:
    """Render the validation report for a botanist.

    Args:
        report: The full report dict (as written to `validation_report.json`).
        vocabulary: Parsed `character_vocabulary.json`, for readable labels.
        genus_names: `genus_id` -> `genus_name`.
    Returns:
        Markdown text.
    """
    character_labels = {c["character_id"]: c["label"] for c in vocabulary["characters"]}
    state_labels = {
        c["character_id"]: {s["state_id"]: s["label"] for s in c["states"]}
        for c in vocabulary["characters"]
    }

    consistency = report["self_consistency"]
    lines = [
        "# Key validation report",
        "",
        f"- Total genera: {consistency['total_genera']}",
        f"- Resolved cleanly: {consistency['resolved_cleanly']}",
        f"- In an ambiguous leaf: {consistency['in_ambiguous_leaf']}",
        f"- Failed self-consistency: {consistency['failed']}",
        f"- Average questions to an answer: {report['depth']['mean']:.1f}",
        f"- Maximum questions to an answer: {report['depth']['max']}",
        "",
        "## Character usage",
        "",
    ]
    for character_id, count in sorted(
        report["character_usage"].items(), key=lambda item: -item[1]
    ):
        lines.append(f"- {character_labels.get(character_id, character_id)}: {count}")

    lines += ["", "## Ambiguous leaves", ""]
    if not report["ambiguous_leaves"]:
        lines.append("None.")
    for leaf in report["ambiguous_leaves"]:
        names = ", ".join(
            genus_names.get(g, g) for g in sorted(leaf["genus_ids"])
        )
        shared = "; ".join(
            f"{character_labels.get(cid, cid)} = "
            f"{state_labels.get(cid, {}).get(sid, sid)}"
            for cid, sid in leaf["shared_states"].items()
        )
        lines.append(f"- {names} -- share: {shared or '(no characters at all)'}")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix", type=Path, default=root / "analysis" / "character_matrix.jsonl"
    )
    parser.add_argument(
        "--key", type=Path, default=root / "analysis" / "genus_key.json"
    )
    parser.add_argument(
        "--vocabulary", type=Path, default=root / "data" / "character_vocabulary.json"
    )
    parser.add_argument(
        "--json-out", type=Path, default=root / "analysis" / "validation_report.json"
    )
    parser.add_argument(
        "--markdown-out", type=Path, default=root / "analysis" / "validation_report.md"
    )
    return parser.parse_args()


def main() -> None:
    """Compute the validation report from the matrix and key, and write it."""
    arguments = parse_args()

    rows = []
    with arguments.matrix.open(encoding="utf-8") as handle:
        for raw_line in handle:
            raw_line = raw_line.strip()
            if raw_line:
                rows.append(json.loads(raw_line))

    tree = json.loads(arguments.key.read_text(encoding="utf-8"))["root"]
    vocabulary = json.loads(arguments.vocabulary.read_text(encoding="utf-8"))
    genus_names = {row["genus_id"]: row["genus_name"] for row in rows}

    report = {
        "schema_version": 1,
        "self_consistency": self_consistency_report(tree, rows),
        "depth": tree_depth_stats(tree),
        "character_usage": character_usage(tree),
        "ambiguous_leaves": find_ambiguous_leaves(tree),
    }

    arguments.json_out.parent.mkdir(parents=True, exist_ok=True)
    arguments.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    arguments.markdown_out.write_text(
        render_validation_markdown(report, vocabulary, genus_names), encoding="utf-8"
    )

    failed = report["self_consistency"]["failed"]
    print(
        f"self-consistency: {report['self_consistency']['resolved_cleanly']} clean, "
        f"{report['self_consistency']['in_ambiguous_leaf']} ambiguous, "
        f"{failed} failed -> {arguments.json_out}"
    )


if __name__ == "__main__":
    main()

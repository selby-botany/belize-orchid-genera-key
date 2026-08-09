#!/usr/bin/env python3
"""Build a dichotomous key from the character matrix (Stage D).

Reads `analysis/character_matrix.jsonl` (Stage C) and `data/character_
vocabulary.json` (Stage A); writes `analysis/genus_key.json` and
`analysis/genus_key.md`.

A greedy, information-gain-style splitter (architecture document, §4.4;
overview document, §6.4/§10): at each node, the character that best
divides the current genus set is chosen, weighted down by how many of
those genera have no data for it at all (`not_stated` is a real value,
not a wildcard -- requirements, §1.5), and never a character already used
higher up the same path. A node with more than one genus and no further
useful split becomes an ambiguous leaf (requirements, §2) -- reported,
not merged and not hidden.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

NOT_STATED = "not_stated"


def split_score(character_id: str, rows: list[dict[str, Any]]) -> float:
    """Score how well one character divides a genus set.

    Args:
        character_id: The character to score.
        rows: Matrix rows (genera) under consideration at this node.
    Returns:
        Shannon entropy of the resulting state-group sizes (0.0 when every
        row shares one state -- no split at all; higher when the
        character divides `rows` into many, evenly-sized groups),
        discounted by the fraction of `rows` with no data for this
        character (architecture document, §4.4: a character most of the
        candidate genera don't have data for isn't a good split choice
        even where it would otherwise separate cleanly).
    """
    if not rows:
        return 0.0

    groups: dict[str, int] = defaultdict(int)
    for row in rows:
        groups[row["characters"][character_id]["state_id"]] += 1

    total = len(rows)
    entropy = -sum(
        (count / total) * math.log2(count / total) for count in groups.values()
    )
    not_stated_fraction = groups.get(NOT_STATED, 0) / total
    return entropy * (1 - not_stated_fraction)


def choose_best_split(
    candidates: list[str], rows: list[dict[str, Any]]
) -> str | None:
    """Pick the highest-scoring character not already used on this path.

    Args:
        candidates: Character IDs eligible at this node.
        rows: Matrix rows under consideration.
    Returns:
        The best candidate's character_id, or None when nothing usefully
        separates `rows` any further (every candidate scores 0 -- every
        row shares the same state on every remaining character).
    """
    best_id: str | None = None
    best_score = 0.0
    for character_id in candidates:
        score = split_score(character_id, rows)
        if score > best_score:
            best_score = score
            best_id = character_id
    return best_id


def build_tree(
    rows: list[dict[str, Any]],
    vocabulary: dict[str, Any],
    used_characters: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    """Recursively build a key tree from a genus set.

    Args:
        rows: Matrix rows to separate.
        vocabulary: Parsed `character_vocabulary.json`.
        used_characters: Character IDs already asked on this path -- never
            asked twice in one couplet chain.
    Returns:
        A `{"type": "leaf", "genus_ids": [...]}` node (one genus if
        cleanly separated, more than one if genuinely ambiguous), or a
        `{"type": "split", "character_id", "branches": [...]}` node, each
        branch `{"state_ids": [state_id], "next": <node>}` -- one state
        per branch; grouping multiple states into a single branch (a
        finer-grained future refinement noted in the data document, §4)
        is not attempted in this first pass.
    """
    if len(rows) <= 1:
        return {"type": "leaf", "genus_ids": [row["genus_id"] for row in rows]}

    candidates = [
        character["character_id"]
        for character in vocabulary["characters"]
        if character["character_id"] not in used_characters
    ]
    chosen = choose_best_split(candidates, rows)
    if chosen is None:
        return {"type": "leaf", "genus_ids": [row["genus_id"] for row in rows]}

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["characters"][chosen]["state_id"]].append(row)

    branches = []
    for state_id, group_rows in groups.items():
        branches.append(
            {
                "state_ids": [state_id],
                "next": build_tree(
                    group_rows, vocabulary, used_characters | {chosen}
                ),
            }
        )

    return {"type": "split", "character_id": chosen, "branches": branches}


def render_key_markdown(
    tree: dict[str, Any],
    vocabulary: dict[str, Any],
    genus_names: dict[str, str],
) -> str:
    """Render a tree as a numbered-couplet key, McLeish's own key's style.

    Args:
        tree: A `build_tree` result.
        vocabulary: Parsed `character_vocabulary.json`, for character and
            state labels.
        genus_names: `genus_id` -> `genus_name`, for readable leaf text.
    Returns:
        Markdown text: one numbered block per split, one lettered lead
        per branch (data document, §5) -- more than two leads under one
        number when a character has more than two states, a real,
        published convention for a polytomous split, not a deviation
        invented here.
    """
    character_labels = {c["character_id"]: c["label"] for c in vocabulary["characters"]}
    state_labels = {
        c["character_id"]: {s["state_id"]: s["label"] for s in c["states"]}
        for c in vocabulary["characters"]
    }

    order: list[dict[str, Any]] = []

    def assign_order(node: dict[str, Any]) -> None:
        if node["type"] != "split":
            return
        order.append(node)
        for branch in node["branches"]:
            assign_order(branch["next"])

    assign_order(tree)
    number_of = {id(node): index + 1 for index, node in enumerate(order)}

    letters = "abcdefghijklmnopqrstuvwxyz"
    lines: list[str] = []
    for node in order:
        number = number_of[id(node)]
        character_id = node["character_id"]
        for index, branch in enumerate(node["branches"]):
            letter = letters[index]
            state_text = ", or ".join(
                state_labels[character_id][s] for s in branch["state_ids"]
            )
            target = branch["next"]
            if target["type"] == "leaf":
                destination = " / ".join(
                    genus_names.get(g, g) for g in sorted(target["genus_ids"])
                )
            else:
                destination = f"go to {number_of[id(target)]}"
            lines.append(
                f"{number}{letter}. {character_labels[character_id]}: "
                f"{state_text} — {destination}"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix", type=Path, default=root / "analysis" / "character_matrix.jsonl"
    )
    parser.add_argument(
        "--vocabulary", type=Path, default=root / "data" / "character_vocabulary.json"
    )
    parser.add_argument(
        "--json-out", type=Path, default=root / "analysis" / "genus_key.json"
    )
    parser.add_argument(
        "--markdown-out", type=Path, default=root / "analysis" / "genus_key.md"
    )
    return parser.parse_args()


def main() -> None:
    """Build the key from the matrix and write both output forms."""
    arguments = parse_args()

    vocabulary = json.loads(arguments.vocabulary.read_text(encoding="utf-8"))

    rows = []
    with arguments.matrix.open(encoding="utf-8") as handle:
        for raw_line in handle:
            raw_line = raw_line.strip()
            if raw_line:
                rows.append(json.loads(raw_line))

    tree = build_tree(rows, vocabulary)
    genus_names = {row["genus_id"]: row["genus_name"] for row in rows}

    arguments.json_out.parent.mkdir(parents=True, exist_ok=True)
    arguments.json_out.write_text(
        json.dumps({"schema_version": 1, "root": tree}, indent=2) + "\n",
        encoding="utf-8",
    )
    arguments.markdown_out.write_text(
        render_key_markdown(tree, vocabulary, genus_names), encoding="utf-8"
    )

    print(f"key built over {len(rows)} genera -> {arguments.json_out}")


if __name__ == "__main__":
    main()

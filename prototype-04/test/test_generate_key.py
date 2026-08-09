"""Tests for the greedy key-generation splitter (Stage D)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "bin" / "generate_key.py"
SPEC = importlib.util.spec_from_file_location("generate_key", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _row(genus_id: str, genus_name: str, **states: str) -> dict:
    """Build one synthetic matrix row; keyword args are character_id=state_id."""
    return {
        "genus_id": genus_id,
        "genus_name": genus_name,
        "characters": {
            character_id: {"state_id": state_id}
            for character_id, state_id in states.items()
        },
        "review_flags": [],
    }


def _vocabulary(*character_ids: str) -> dict:
    return {
        "schema_version": 1,
        "characters": [
            {
                "character_id": character_id,
                "label": character_id,
                "source_fields": [],
                "states": [{"state_id": "not_stated", "label": "not stated"}],
            }
            for character_id in character_ids
        ],
    }


class SplitScoreTest(unittest.TestCase):
    """Entropy of the resulting groups, discounted by not_stated fraction."""

    def test_character_with_no_not_stated_scores_higher(self) -> None:
        rows = [
            _row("a", "Alpha", clean="x", noisy="x"),
            _row("b", "Beta", clean="y", noisy="not_stated"),
        ]
        clean_score = MODULE.split_score("clean", rows)
        noisy_score = MODULE.split_score("noisy", rows)
        self.assertGreater(clean_score, noisy_score)

    def test_character_that_does_not_split_scores_zero(self) -> None:
        rows = [_row("a", "Alpha", c="x"), _row("b", "Beta", c="x")]
        self.assertEqual(MODULE.split_score("c", rows), 0.0)

    def test_empty_rows_scores_zero(self) -> None:
        self.assertEqual(MODULE.split_score("c", []), 0.0)


class ChooseBestSplitTest(unittest.TestCase):
    """Highest-scoring candidate, never one already used on this path."""

    def test_picks_the_character_that_actually_separates_the_rows(self) -> None:
        rows = [
            _row("a", "Alpha", useful="x", useless="same"),
            _row("b", "Beta", useful="y", useless="same"),
        ]
        chosen = MODULE.choose_best_split(["useful", "useless"], rows)
        self.assertEqual(chosen, "useful")

    def test_returns_none_when_nothing_separates_the_rows(self) -> None:
        rows = [_row("a", "Alpha", c="x"), _row("b", "Beta", c="x")]
        self.assertIsNone(MODULE.choose_best_split(["c"], rows))


class BuildTreeTest(unittest.TestCase):
    """A leaf per fully-separated genus; an honest, reported ambiguous leaf."""

    def test_single_genus_produces_a_clean_leaf(self) -> None:
        rows = [_row("a", "Alpha", c="x")]
        vocabulary = _vocabulary("c")
        tree = MODULE.build_tree(rows, vocabulary)
        self.assertEqual(tree, {"type": "leaf", "genus_ids": ["a"]})

    def test_two_genera_sharing_every_state_form_an_ambiguous_leaf(self) -> None:
        # Requirements, §2: an ambiguous leaf is an allowed, honestly
        # reported outcome, not a failure to hide.
        rows = [
            _row("a", "Alpha", c="same"),
            _row("b", "Beta", c="same"),
        ]
        vocabulary = _vocabulary("c")
        tree = MODULE.build_tree(rows, vocabulary)
        self.assertEqual(tree["type"], "leaf")
        self.assertEqual(sorted(tree["genus_ids"]), ["a", "b"])

    def test_a_separating_character_produces_a_split_with_two_leaves(self) -> None:
        rows = [
            _row("a", "Alpha", c="x"),
            _row("b", "Beta", c="y"),
        ]
        vocabulary = _vocabulary("c")
        tree = MODULE.build_tree(rows, vocabulary)
        self.assertEqual(tree["type"], "split")
        self.assertEqual(tree["character_id"], "c")
        leaves = {
            branch["state_ids"][0]: branch["next"]["genus_ids"]
            for branch in tree["branches"]
        }
        self.assertEqual(leaves, {"x": ["a"], "y": ["b"]})

    def test_a_character_is_never_asked_twice_on_the_same_path(self) -> None:
        # Three genera: "c" only separates two of them from the third,
        # "d" is needed again one level down -- "c" must not reappear.
        rows = [
            _row("a", "Alpha", c="x", d="p"),
            _row("b", "Beta", c="x", d="q"),
            _row("g", "Gamma", c="y", d="p"),
        ]
        vocabulary = _vocabulary("c", "d")
        tree = MODULE.build_tree(rows, vocabulary)
        # Whichever character is chosen first, it must not be the
        # character chosen again for any of its own children.

        def walk(node, used):
            if node["type"] == "leaf":
                return
            self.assertNotIn(node["character_id"], used)
            for branch in node["branches"]:
                walk(branch["next"], used | {node["character_id"]})

        walk(tree, frozenset())


class RenderKeyMarkdownTest(unittest.TestCase):
    """Numbered-couplet rendering in the documented style."""

    def test_renders_a_numbered_couplet_pointing_to_genus_names(self) -> None:
        vocabulary = {
            "schema_version": 1,
            "characters": [
                {
                    "character_id": "lip_lobing",
                    "label": "Lip lobing",
                    "source_fields": [],
                    "states": [
                        {"state_id": "entire", "label": "entire"},
                        {"state_id": "three_lobed", "label": "3-lobed"},
                    ],
                }
            ],
        }
        tree = {
            "type": "split",
            "character_id": "lip_lobing",
            "branches": [
                {"state_ids": ["entire"], "next": {"type": "leaf", "genus_ids": ["a"]}},
                {
                    "state_ids": ["three_lobed"],
                    "next": {"type": "leaf", "genus_ids": ["b"]},
                },
            ],
        }
        genus_names = {"a": "Alpha", "b": "Beta"}
        markdown = MODULE.render_key_markdown(tree, vocabulary, genus_names)
        self.assertIn("1a. Lip lobing: entire", markdown)
        self.assertIn("Alpha", markdown)
        self.assertIn("1b. Lip lobing: 3-lobed", markdown)
        self.assertIn("Beta", markdown)


if __name__ == "__main__":
    unittest.main()

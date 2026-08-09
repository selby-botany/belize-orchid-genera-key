"""Tests for validation analytics (Stage E)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "bin" / "validate_key.py"
SPEC = importlib.util.spec_from_file_location("validate_key", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _row(genus_id: str, genus_name: str, **states: str) -> dict:
    return {
        "genus_id": genus_id,
        "genus_name": genus_name,
        "characters": {
            character_id: {"state_id": state_id}
            for character_id, state_id in states.items()
        },
        "review_flags": [],
    }


class WalkTreeTest(unittest.TestCase):
    """Following a genus's own recorded states down the tree."""

    def test_reaches_the_correct_leaf(self) -> None:
        tree = {
            "type": "split",
            "character_id": "c",
            "branches": [
                {"state_ids": ["x"], "next": {"type": "leaf", "genus_ids": ["a"]}},
                {"state_ids": ["y"], "next": {"type": "leaf", "genus_ids": ["b"]}},
            ],
        }
        self.assertEqual(MODULE.walk_tree(tree, _row("a", "Alpha", c="x")), ["a"])
        self.assertEqual(MODULE.walk_tree(tree, _row("b", "Beta", c="y")), ["b"])

    def test_no_matching_branch_returns_empty(self) -> None:
        tree = {
            "type": "split",
            "character_id": "c",
            "branches": [
                {"state_ids": ["x"], "next": {"type": "leaf", "genus_ids": ["a"]}},
            ],
        }
        self.assertEqual(MODULE.walk_tree(tree, _row("z", "Zeta", c="unseen")), [])


class SelfConsistencyReportTest(unittest.TestCase):
    """The acceptance floor: every genus reaches a leaf containing itself."""

    def test_reports_zero_failures_for_a_tree_built_from_the_same_rows(self) -> None:
        rows = [_row("a", "Alpha", c="x"), _row("b", "Beta", c="y")]
        tree = {
            "type": "split",
            "character_id": "c",
            "branches": [
                {"state_ids": ["x"], "next": {"type": "leaf", "genus_ids": ["a"]}},
                {"state_ids": ["y"], "next": {"type": "leaf", "genus_ids": ["b"]}},
            ],
        }
        report = MODULE.self_consistency_report(tree, rows)
        self.assertEqual(report["failed"], 0)
        self.assertEqual(report["resolved_cleanly"], 2)
        self.assertEqual(report["in_ambiguous_leaf"], 0)

    def test_ambiguous_leaf_counts_as_ambiguous_not_failed(self) -> None:
        rows = [_row("a", "Alpha", c="same"), _row("b", "Beta", c="same")]
        tree = {"type": "leaf", "genus_ids": ["a", "b"]}
        report = MODULE.self_consistency_report(tree, rows)
        self.assertEqual(report["failed"], 0)
        self.assertEqual(report["in_ambiguous_leaf"], 2)

    def test_fires_on_a_deliberately_inconsistent_tree(self) -> None:
        # The direct regression test for the acceptance floor itself: a
        # synthetic tree/row pairing built to be wrong, proving the check
        # actually catches it rather than being assumed to.
        rows = [_row("a", "Alpha", c="x")]
        tree = {"type": "leaf", "genus_ids": ["some_other_genus"]}
        report = MODULE.self_consistency_report(tree, rows)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["failed_genus_ids"], ["a"])


class TreeDepthStatsTest(unittest.TestCase):
    """Mean/max questions to an answer, weighted by genus count per leaf."""

    def test_single_split_gives_depth_one(self) -> None:
        tree = {
            "type": "split",
            "character_id": "c",
            "branches": [
                {"state_ids": ["x"], "next": {"type": "leaf", "genus_ids": ["a"]}},
                {"state_ids": ["y"], "next": {"type": "leaf", "genus_ids": ["b"]}},
            ],
        }
        stats = MODULE.tree_depth_stats(tree)
        self.assertEqual(stats["mean"], 1.0)
        self.assertEqual(stats["max"], 1)

    def test_ambiguous_leaf_with_two_genera_counts_twice(self) -> None:
        tree = {"type": "leaf", "genus_ids": ["a", "b"]}
        stats = MODULE.tree_depth_stats(tree)
        self.assertEqual(stats["mean"], 0.0)


class CharacterUsageTest(unittest.TestCase):
    """How often each character is asked across the whole tree."""

    def test_counts_a_character_used_on_two_different_branches(self) -> None:
        tree = {
            "type": "split",
            "character_id": "top",
            "branches": [
                {
                    "state_ids": ["x"],
                    "next": {
                        "type": "split",
                        "character_id": "reused",
                        "branches": [
                            {"state_ids": ["p"], "next": {"type": "leaf", "genus_ids": ["a"]}},
                        ],
                    },
                },
                {
                    "state_ids": ["y"],
                    "next": {
                        "type": "split",
                        "character_id": "reused",
                        "branches": [
                            {"state_ids": ["q"], "next": {"type": "leaf", "genus_ids": ["b"]}},
                        ],
                    },
                },
            ],
        }
        usage = MODULE.character_usage(tree)
        self.assertEqual(usage["top"], 1)
        self.assertEqual(usage["reused"], 2)


class FindAmbiguousLeavesTest(unittest.TestCase):
    """Every ambiguous leaf, named, with the states that caused it."""

    def test_reports_shared_states_that_led_to_the_leaf(self) -> None:
        tree = {
            "type": "split",
            "character_id": "c",
            "branches": [
                {
                    "state_ids": ["same"],
                    "next": {"type": "leaf", "genus_ids": ["a", "b"]},
                },
            ],
        }
        leaves = MODULE.find_ambiguous_leaves(tree)
        self.assertEqual(len(leaves), 1)
        self.assertEqual(sorted(leaves[0]["genus_ids"]), ["a", "b"])
        self.assertEqual(leaves[0]["shared_states"], {"c": "same"})

    def test_clean_tree_reports_no_ambiguous_leaves(self) -> None:
        tree = {
            "type": "split",
            "character_id": "c",
            "branches": [
                {"state_ids": ["x"], "next": {"type": "leaf", "genus_ids": ["a"]}},
                {"state_ids": ["y"], "next": {"type": "leaf", "genus_ids": ["b"]}},
            ],
        }
        self.assertEqual(MODULE.find_ambiguous_leaves(tree), [])


if __name__ == "__main__":
    unittest.main()

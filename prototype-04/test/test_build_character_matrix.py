"""Tests for character-proposal verification and matrix assembly (Stage C)."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "bin" / "build_character_matrix.py"
SPEC = importlib.util.spec_from_file_location("build_character_matrix", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _genus_record(genus_id="alpha", genus_name="Alpha", fields=None):
    return {
        "genus_id": genus_id,
        "genus_name": genus_name,
        "fields": fields or {},
    }


def _vocabulary(*characters):
    return {"schema_version": 1, "characters": list(characters)}


def _character(character_id, *state_ids):
    return {
        "character_id": character_id,
        "label": character_id,
        "source_fields": [],
        "states": [{"state_id": s, "label": s} for s in state_ids]
        + [{"state_id": "not_stated", "label": "not stated"}],
    }


class VerifyQuoteTest(unittest.TestCase):
    """The sole gate a proposal must pass before it's trusted."""

    def test_true_when_quote_is_an_exact_substring(self) -> None:
        genus = _genus_record(fields={"Lip": {"text": "Lip free, 3-lobed.", "source_image": "p.jpeg", "confidence": 1.0, "status": "scored"}})
        self.assertTrue(MODULE.verify_quote(genus, "Lip", "3-lobed"))

    def test_false_when_quote_is_not_present(self) -> None:
        genus = _genus_record(fields={"Lip": {"text": "Lip free, 3-lobed.", "source_image": "p.jpeg", "confidence": 1.0, "status": "scored"}})
        self.assertFalse(MODULE.verify_quote(genus, "Lip", "4-lobed"))

    def test_false_on_a_near_miss_paraphrase(self) -> None:
        # A quote that means the same thing but isn't literally present is
        # not evidence -- architecture document, design principle 2:
        # mechanically verify, never "plausibly resemble."
        genus = _genus_record(fields={"Lip": {"text": "Lip free, 3-lobed.", "source_image": "p.jpeg", "confidence": 1.0, "status": "scored"}})
        self.assertFalse(MODULE.verify_quote(genus, "Lip", "three-lobed"))

    def test_false_when_field_is_missing(self) -> None:
        genus = _genus_record(fields={})
        self.assertFalse(MODULE.verify_quote(genus, "Lip", "3-lobed"))


class BuildMatrixRowTest(unittest.TestCase):
    """Every vocabulary character is a key, always -- never a subset."""

    def test_every_vocabulary_character_present_even_with_no_proposals(self) -> None:
        vocabulary = _vocabulary(_character("lip_lobing", "entire", "three_lobed"))
        genera_by_id = {"alpha": _genus_record()}
        row = MODULE.build_matrix_row("alpha", [], vocabulary, genera_by_id)
        self.assertEqual(set(row["characters"].keys()), {"lip_lobing"})
        self.assertEqual(row["characters"]["lip_lobing"]["state_id"], "not_stated")
        self.assertEqual(row["characters"]["lip_lobing"]["status"], "not_stated")
        self.assertIsNone(row["characters"]["lip_lobing"]["quote"])

    def test_a_verified_proposal_fills_its_character(self) -> None:
        vocabulary = _vocabulary(
            _character("lip_lobing", "entire", "three_lobed"),
            _character("pollinia_count", "two", "four"),
        )
        genera_by_id = {"alpha": _genus_record()}
        proposals = [
            {
                "genus_id": "alpha",
                "character_id": "lip_lobing",
                "state_id": "three_lobed",
                "quote": "3-lobed",
                "source_field": "Lip",
                "source_image": "page-050.jpeg",
            }
        ]
        row = MODULE.build_matrix_row("alpha", proposals, vocabulary, genera_by_id)
        self.assertEqual(row["characters"]["lip_lobing"]["state_id"], "three_lobed")
        self.assertEqual(row["characters"]["lip_lobing"]["status"], "verified")
        self.assertEqual(row["characters"]["lip_lobing"]["quote"], "3-lobed")
        # Untouched character still gets its not_stated entry, not an
        # omitted key.
        self.assertEqual(row["characters"]["pollinia_count"]["state_id"], "not_stated")

    def test_all_not_stated_row_is_flagged(self) -> None:
        vocabulary = _vocabulary(_character("lip_lobing", "entire", "three_lobed"))
        genera_by_id = {"alpha": _genus_record()}
        row = MODULE.build_matrix_row("alpha", [], vocabulary, genera_by_id)
        self.assertIn("all_not_stated", row["review_flags"])

    def test_row_with_a_verified_character_is_not_flagged(self) -> None:
        vocabulary = _vocabulary(_character("lip_lobing", "entire", "three_lobed"))
        genera_by_id = {"alpha": _genus_record()}
        proposals = [
            {
                "genus_id": "alpha",
                "character_id": "lip_lobing",
                "state_id": "three_lobed",
                "quote": "3-lobed",
                "source_field": "Lip",
                "source_image": "page-050.jpeg",
            }
        ]
        row = MODULE.build_matrix_row("alpha", proposals, vocabulary, genera_by_id)
        self.assertEqual(row["review_flags"], [])


class MainIntegrationTest(unittest.TestCase):
    """An unverified proposal never reaches the matrix -- checked end to end."""

    def test_unverified_proposal_is_dropped_not_silently_trusted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            genera_path = tmp_path / "genera.jsonl"
            genera_path.write_text(
                json.dumps(
                    {
                        "genus_id": "alpha",
                        "genus_name": "Alpha",
                        "fields": {
                            "Lip": {
                                "text": "Lip free, 3-lobed.",
                                "source_image": "p.jpeg",
                                "confidence": 1.0,
                                "status": "scored",
                            }
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            vocabulary_path = tmp_path / "vocabulary.json"
            vocabulary_path.write_text(
                json.dumps(_vocabulary(_character("lip_lobing", "entire", "three_lobed"))),
                encoding="utf-8",
            )
            proposals_path = tmp_path / "proposals.jsonl"
            # This proposal's quote is not actually in the Lip field text.
            proposals_path.write_text(
                json.dumps(
                    {
                        "genus_id": "alpha",
                        "character_id": "lip_lobing",
                        "state_id": "entire",
                        "quote": "not really there",
                        "source_field": "Lip",
                        "source_image": "p.jpeg",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            output_path = tmp_path / "matrix.jsonl"

            argv = [
                "build_character_matrix.py",
                "--genera",
                str(genera_path),
                "--vocabulary",
                str(vocabulary_path),
                "--proposals",
                str(proposals_path),
                "--output",
                str(output_path),
            ]
            original_argv = sys.argv
            sys.argv = argv
            try:
                MODULE.main()
            finally:
                sys.argv = original_argv

            row = json.loads(output_path.read_text(encoding="utf-8").strip())
            self.assertEqual(row["characters"]["lip_lobing"]["state_id"], "not_stated")
            self.assertIn("all_not_stated", row["review_flags"])


if __name__ == "__main__":
    unittest.main()

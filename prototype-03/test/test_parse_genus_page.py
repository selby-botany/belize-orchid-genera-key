"""Tests for the genus and field structural parser (Stage D)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "bin" / "parse_genus_page.py"
SPEC = importlib.util.spec_from_file_location("parse_genus_page", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _line(text, mid_y=0.5, confidence=1.0, column=0, min_x=0.05, source_image="synthetic.jpeg"):
    """Build one OCR line record for a test fixture."""
    return {
        "text": text,
        "confidence": confidence,
        "column": column,
        "min_x": min_x,
        "mid_y": mid_y,
        "source_image": source_image,
    }


class DehyphenateJoinTest(unittest.TestCase):
    """Line-wrap hyphenation is undone when reflowing to a paragraph."""

    def test_trailing_hyphen_is_removed_and_words_joined(self) -> None:
        result = MODULE.dehyphenate_join(["creeping rhi-", "zomes."])
        self.assertEqual(result, "creeping rhizomes.")

    def test_non_hyphenated_lines_join_with_a_space(self) -> None:
        result = MODULE.dehyphenate_join(["Roots adventitious,", "fleshy."])
        self.assertEqual(result, "Roots adventitious, fleshy.")

    def test_empty_input_returns_empty_string(self) -> None:
        self.assertEqual(MODULE.dehyphenate_join([]), "")


class SplitIntoSentencesTest(unittest.TestCase):
    """Sentence splitting is abbreviation-aware, not a bare '. ' split."""

    def test_ordinary_sentences_split(self) -> None:
        sentences = MODULE.split_into_sentences("Flowers few. Sepals free.")
        self.assertEqual(sentences, ["Flowers few.", "Sepals free."])

    def test_known_abbreviation_does_not_cause_a_false_split(self) -> None:
        sentences = MODULE.split_into_sentences(
            "Named for Barb. Rodr. in his honor. Column elongate."
        )
        self.assertEqual(
            sentences,
            ["Named for Barb. Rodr. in his honor.", "Column elongate."],
        )


class FindGenusHeadersTest(unittest.TestCase):
    """Numbered genus headers are matched structurally, not against a list."""

    def test_matches_numbered_title_case_genus_and_author(self) -> None:
        lines = [_line("18. Psilochilus Barb. Rodr.")]
        matches = MODULE.find_genus_headers(lines)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["genus_number"], "18")
        self.assertEqual(matches[0]["genus_name"], "Psilochilus")
        self.assertEqual(matches[0]["author"], "Barb. Rodr.")

    def test_does_not_match_ordinary_body_prose(self) -> None:
        lines = [_line("This is a monotypic genus of tropical America.")]
        self.assertEqual(MODULE.find_genus_headers(lines), [])

    def test_does_not_match_running_head_without_period(self) -> None:
        # No period after the number -- the discriminator against a real
        # header (module docstring, finding 2).
        lines = [_line("18 Psilochilus")]
        self.assertEqual(MODULE.find_genus_headers(lines), [])


class CrossCheckRunningHeadTest(unittest.TestCase):
    """The running head is found by geometry, not by array position."""

    def test_finds_informative_running_head_in_top_band(self) -> None:
        lines = [
            _line("Column elongate.", mid_y=0.5),
            _line("18 Psilochilus", mid_y=0.043),
        ]
        result = MODULE.cross_check_running_head(lines)
        self.assertEqual(result, {"genus_number": "18", "genus_name": "Psilochilus"})

    def test_bare_folio_number_carries_no_genus_signal(self) -> None:
        lines = [_line("50", mid_y=0.042)]
        self.assertIsNone(MODULE.cross_check_running_head(lines))

    def test_running_head_pattern_outside_top_band_is_ignored(self) -> None:
        lines = [_line("18 Psilochilus", mid_y=0.5)]
        self.assertIsNone(MODULE.cross_check_running_head(lines))


class SegmentFieldsTest(unittest.TestCase):
    """Field-label and organ-lead segmentation on a synthetic genus block."""

    def _psilochilus_style_block(self):
        return [
            _line("Terrestrial or epiphytic plants."),
            _line("Roots adventitious, fleshy."),
            _line("Leaves membranaceous."),
            _line("This is a monotypic genus of tropical America."),
            _line("EtymoLogY. From the Greek psilo (smooth)."),
        ]

    def test_field_labels_matched_case_insensitively(self) -> None:
        # Small-caps OCR renders ETYMOLOGY as "EtymoLogY" -- module
        # docstring, finding 1.
        fields = MODULE.segment_fields(self._psilochilus_style_block())
        self.assertIn("ETYMOLOGY", fields)
        self.assertEqual(
            fields["ETYMOLOGY"]["text"], "From the Greek psilo (smooth)."
        )

    def test_organ_leads_split_out_of_the_diagnostic_paragraph(self) -> None:
        fields = MODULE.segment_fields(self._psilochilus_style_block())
        self.assertEqual(fields["Roots"]["text"], "Roots adventitious, fleshy.")
        self.assertEqual(fields["Leaves"]["text"], "Leaves membranaceous.")

    def test_unattributed_sentence_lands_in_summary_as_uncertain(self) -> None:
        fields = MODULE.segment_fields(self._psilochilus_style_block())
        self.assertIn("SUMMARY", fields)
        self.assertEqual(fields["SUMMARY"]["status"], "uncertain")
        self.assertIn("monotypic genus", fields["SUMMARY"]["text"])

    def test_multiple_fields_each_isolated_to_their_own_span(self) -> None:
        block = [
            _line("Plant terrestrial."),
            _line("GENERAL DISTRIBUTION. The West Indies."),
            _line("DISTRIBUTION IN BELIZE. Cayo District."),
            _line("HABITAT. On leaf litter."),
            _line("FLOWERING SEASON. December."),
            _line("NOTE. Reported once."),
        ]
        fields = MODULE.segment_fields(block)
        self.assertEqual(fields["GENERAL DISTRIBUTION"]["text"], "The West Indies.")
        self.assertEqual(fields["DISTRIBUTION IN BELIZE"]["text"], "Cayo District.")
        self.assertEqual(fields["HABITAT"]["text"], "On leaf litter.")
        self.assertEqual(fields["FLOWERING SEASON"]["text"], "December.")
        self.assertEqual(fields["NOTE"]["text"], "Reported once.")

    def test_furniture_lines_are_excluded_from_field_content(self) -> None:
        block = [
            _line("Roots adventitious, fleshy."),
            _line("SUBTRIBE VANILLINAE LINDL.", mid_y=0.4),
            _line("NOTE. Reported once."),
        ]
        fields = MODULE.segment_fields(block)
        self.assertNotIn("SUBTRIBE", fields["NOTE"]["text"])
        self.assertEqual(fields["NOTE"]["text"], "Reported once.")


class FindSpeciesEntriesTest(unittest.TestCase):
    """Species entries are recognized only under their own genus name."""

    def test_species_header_must_repeat_owning_genus_name(self) -> None:
        lines = [
            _line("Roots adventitious, fleshy."),
            _line("Psilochilus macrophyllus (Lindl.) Ames, Orch."),
            _line("Plant terrestrial or epiphytic."),
        ]
        species, first_index = MODULE.find_species_entries(
            lines, "Psilochilus", 0, len(lines)
        )
        self.assertEqual(len(species), 1)
        self.assertEqual(species[0]["species_name"], "Psilochilus macrophyllus")
        self.assertEqual(first_index, 1)

    def test_body_prose_with_capitalized_word_is_not_a_false_species_match(self) -> None:
        # "Plant terrestrial..." looks like "Genus species" structurally,
        # but "Plant" is not the owning genus's name.
        lines = [_line("Plant terrestrial or epiphytic, with fleshy roots.")]
        species, first_index = MODULE.find_species_entries(
            lines, "Psilochilus", 0, len(lines)
        )
        self.assertEqual(species, [])
        self.assertIsNone(first_index)

    def test_species_span_extends_past_field_labels_to_next_species_header(self) -> None:
        # Real book convention (module docstring): fields after a species'
        # description belong to that species, not cut short at them.
        lines = [
            _line("Alpha minor (Test) Fakeauthor."),
            _line("Plant small."),
            _line("HABITAT. On rocks."),
            _line("NOTE. Rare."),
            _line("Alpha major (Test) Fakeauthor."),
            _line("Plant large."),
        ]
        species, _ = MODULE.find_species_entries(lines, "Alpha", 0, len(lines))
        self.assertEqual(len(species), 2)
        self.assertEqual(species[0]["_start"], 1)
        self.assertEqual(species[0]["_end"], 4)
        self.assertEqual(species[1]["_start"], 5)
        self.assertEqual(species[1]["_end"], len(lines))


class BuildGenusRecordsTest(unittest.TestCase):
    """Genus records are stitched across pages and never silently merged."""

    def test_species_entry_appears_in_species_not_merged_into_fields(self) -> None:
        lines = [
            _line("1. Alpha Testauthor"),
            _line("Roots adventitious."),
            _line("Alpha minor (Test) Fakeauthor."),
            _line("Plant small."),
        ]
        pages = [
            {
                "source_image": "synthetic-01.jpeg",
                "page_number": 1,
                "lines": lines,
            }
        ]
        records, discontinuities = MODULE.build_genus_records(pages)
        self.assertEqual(discontinuities, [])
        self.assertEqual(len(records), 1)
        self.assertNotIn("Alpha minor", records[0]["fields"])
        self.assertEqual(len(records[0]["species"]), 1)
        self.assertEqual(records[0]["species"][0]["species_name"], "Alpha minor")

    def test_stitches_a_genus_spanning_two_pages_via_running_head(self) -> None:
        page_one = {
            "source_image": "synthetic-10.jpeg",
            "page_number": 10,
            "lines": [
                _line("5. Alpha Testauthor"),
                _line("Roots adventitious, fleshy."),
            ],
        }
        page_two = {
            "source_image": "synthetic-11.jpeg",
            "page_number": 11,
            "lines": [
                _line("5 Alpha", mid_y=0.04),
                _line("HABITAT. On rocks near streams."),
            ],
        }
        records, discontinuities = MODULE.build_genus_records([page_one, page_two])
        self.assertEqual(discontinuities, [])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["source_pages"], [10, 11])
        self.assertEqual(
            records[0]["fields"]["HABITAT"]["text"], "On rocks near streams."
        )

    def test_discontinuity_is_flagged_not_silently_merged(self) -> None:
        page_one = {
            "source_image": "synthetic-20.jpeg",
            "page_number": 20,
            "lines": [
                _line("7. Gamma Someauthor"),
                _line("Roots adventitious."),
            ],
        }
        # A skipped genus number: the running head names a different
        # genus than the one currently open.
        page_two = {
            "source_image": "synthetic-21.jpeg",
            "page_number": 21,
            "lines": [
                _line("9 Delta", mid_y=0.04),
                _line("HABITAT. Somewhere else."),
            ],
        }
        records, discontinuities = MODULE.build_genus_records([page_one, page_two])
        self.assertEqual(len(discontinuities), 1)
        self.assertEqual(discontinuities[0]["expected_genus"], "Gamma")
        self.assertEqual(discontinuities[0]["running_head_genus"], "Delta")
        self.assertEqual(records[0]["source_pages"], [20])
        self.assertEqual(records[0]["extraction_status"], "needs_review")
        self.assertTrue(records[0]["review_flags"])
        self.assertNotIn("HABITAT", records[0]["fields"])


if __name__ == "__main__":
    unittest.main()

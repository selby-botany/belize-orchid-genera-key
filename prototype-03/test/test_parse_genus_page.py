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

    def test_does_not_match_a_dichotomous_key_couplet(self) -> None:
        # Real false positives from the full run (module docstring,
        # finding 5): a key couplet has the same numbered/capitalized-word
        # shape as a genus header, but descriptive prose in the author
        # position gives it away.
        lines = [
            _line("1. Anther erect, or nearly so; pollinia soft."),
            _line("12. Pollinia mealy, or pastelike ."),
            _line("13. Plant terrestrial, erect, self-supporting."),
        ]
        self.assertEqual(MODULE.find_genus_headers(lines), [])

    def test_matches_a_multi_word_author_citation_with_short_tokens(self) -> None:
        # A longer, real author citation shouldn't be mistaken for prose
        # just because it has several words.
        lines = [_line("19. Epistephium R.O. Williams & Summerh.")]
        matches = MODULE.find_genus_headers(lines)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["genus_name"], "Epistephium")

    def test_does_not_match_a_terse_numeric_couplet_answer(self) -> None:
        # Real residual false positives from the full run, found even
        # after the prose-word fix (module docstring, finding 5): a
        # couplet can answer with a bare count instead of prose, which has
        # no long lowercase word for _PROSE_WORD_PATTERN to catch --
        # "24. Pollinia 2" (page 10) and "70. Pollinia 2 or 4" (page 12).
        # A real author citation always has at least one capital letter;
        # these have none.
        lines = [
            _line("24. Pollinia 2"),
            _line("70. Pollinia 2 or 4"),
        ]
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

    def test_finds_informative_running_head_in_bottom_band(self) -> None:
        # Real full-run finding (module docstring, finding 6): Epidendrum's
        # numbered-species-list pages (183, 185, 187, 189) print the
        # running head at the page bottom, not the top.
        lines = [
            _line("1. Epidendrum acuñae Dressler in Am. Orch. Soc.", mid_y=0.5),
            _line("70 Epidendrum", mid_y=0.965),
        ]
        result = MODULE.cross_check_running_head(lines)
        self.assertEqual(result, {"genus_number": "70", "genus_name": "Epidendrum"})

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

    def test_plate_photo_sidebar_numbers_are_excluded_regardless_of_position(
        self,
    ) -> None:
        # Real full-run finding (module docstring, finding 7): a bare
        # concatenated run of plate/photo numbers ("111112 113114 115",
        # page-142.jpeg) printed outside the running-head band, previously
        # swallowed whole as a genus's SUMMARY.
        block = [_line("111112", mid_y=0.858), _line("113114", mid_y=0.878)]
        self.assertEqual(MODULE.segment_fields(block), {})

    def test_lone_stray_capital_letter_is_excluded(self) -> None:
        # Real full-run finding: "B" alone on its own line (page-062.jpeg),
        # a caption panel label split off by OCR from its own description.
        block = [_line("Roots adventitious.", mid_y=0.3), _line("B", mid_y=0.68)]
        fields = MODULE.segment_fields(block)
        self.assertEqual(fields["Roots"]["text"], "Roots adventitious.")
        self.assertNotIn("SUMMARY", fields)

    def test_trailing_figure_caption_block_is_dropped(self) -> None:
        # Real full-run finding, page-062.jpeg (Eriopsis): genuine
        # diagnostic fragments precede a full plate caption on the same
        # plate page. The caption -- and only the caption -- is dropped.
        block = [
            _line("Column short, thick.", mid_y=0.3),
            _line(
                "Figure 25. Eriopsis biloba. A: habit, x 2/3; B: flower, x 1.",
                mid_y=0.75,
            ),
            _line(
                "H: column, x 4; J: anther cap, x 14. Drawn by Beverley Mears.",
                mid_y=0.76,
            ),
        ]
        fields = MODULE.segment_fields(block)
        self.assertNotIn("Figure 25", fields.get("Column", {}).get("text", ""))
        self.assertEqual(fields["Column"]["text"], "Column short, thick.")

    def test_panel_label_fragment_without_its_own_trigger_line_is_excluded(
        self,
    ) -> None:
        # Real full-run residual case, page holding Sarcoglottis's
        # continuation: a caption's panel-label list ("E: column and lip,
        # x 10; F: column from front, x 13;") can appear on a page whose
        # own "Figure <N>." trigger line fell on a different page's span,
        # so the trailing-block truncation in _filter_furniture never
        # sees it. Caught instead by _is_page_furniture's own per-line
        # check: no real diagnostic sentence starts with "<letter>:".
        block = [
            _line("Column short.", mid_y=0.3),
            _line("E: column and lip, x 10; F: column from front, x 13.", mid_y=0.7),
        ]
        fields = MODULE.segment_fields(block)
        self.assertEqual(fields["Column"]["text"], "Column short.")

    def test_trailing_photo_index_sidebar_is_dropped(self) -> None:
        # Real full-run finding, page-142.jpeg (Trichopilia/Bletia
        # boundary): a "Photographs" heading followed by an unrelated
        # numbered species list, previously swallowed as SUMMARY.
        block = [
            _line("A genus of about 30 species.", mid_y=0.71),
            _line("Photographs", mid_y=0.82),
            _line("111. O. ensatum", mid_y=0.85),
            _line("115. Trichopilia tortillis", mid_y=0.9),
        ]
        fields = MODULE.segment_fields(block)
        self.assertNotIn("Photographs", fields["SUMMARY"]["text"])
        self.assertNotIn("ensatum", fields["SUMMARY"]["text"])


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

    def test_numbered_species_headers_are_recognized(self) -> None:
        # Real full-run text, Dichaea (page-074.jpeg through page-078.jpeg):
        # large, species-rich genera number their species list instead of
        # using the bare "Genus epithet ..." form (module docstring
        # finding 9).
        lines = [
            _line("1. Dichaea brachypoda Rchb. f. in Beitr. Orch."),
            _line("Plant epiphytic, often adhering to tree trunk."),
            _line("2. Dichaea glauca (Sw.) Lindl., Gen. Sp. Orch. Pl.:"),
            _line("Plant epiphytic, small, hanging."),
        ]
        species, first_index = MODULE.find_species_entries(
            lines, "Dichaea", 0, len(lines)
        )
        self.assertEqual(len(species), 2)
        self.assertEqual(species[0]["species_name"], "Dichaea brachypoda")
        self.assertEqual(species[1]["species_name"], "Dichaea glauca")
        self.assertEqual(first_index, 0)

    def test_numbered_species_header_matches_an_accented_epithet(self) -> None:
        # Real full-run text, page-182.jpeg: Epidendrum's own species 1,
        # "Epidendrum acuñae", has an epithet containing ñ. A plain
        # `[a-z]` class silently fails to match it -- the whole header
        # line fails to match, with no error, just an unrecognized
        # species (module docstring finding 9's second half).
        lines = [_line("1. Epidendrum acuñae Dressler in Am. Orch. Soc.")]
        species, first_index = MODULE.find_species_entries(
            lines, "Epidendrum", 0, len(lines)
        )
        self.assertEqual(len(species), 1)
        self.assertEqual(species[0]["species_name"], "Epidendrum acuñae")
        self.assertEqual(first_index, 0)

    def test_numbered_species_header_does_not_match_a_key_couplet_answer(self) -> None:
        # Real full-run text: key-couplet answers use the abbreviated
        # genus form ("7. D. panamensis", "9. H. novemfida"), never the
        # full genus name -- these must not be mistaken for species
        # headers.
        lines = [_line("7. D. panamensis"), _line("9. H. novemfida")]
        species, first_index = MODULE.find_species_entries(
            lines, "Dichaea", 0, len(lines)
        )
        self.assertEqual(species, [])
        self.assertIsNone(first_index)

    def test_numbered_species_header_rejects_a_citationless_fragment(self) -> None:
        # Real full-run artifact, page-182.jpeg: "156. Epidendrum acuqae"
        # is an isolated OCR fragment (a typo'd duplicate of species 1's
        # epithet) with no citation text following it on the line -- not
        # a genuine 156th species. Requiring trailing text after the
        # epithet rejects it.
        lines = [_line("156. Epidendrum acuqae")]
        species, first_index = MODULE.find_species_entries(
            lines, "Epidendrum", 0, len(lines)
        )
        self.assertEqual(species, [])
        self.assertIsNone(first_index)

    def test_bare_and_numbered_forms_can_be_mixed_within_one_genus(self) -> None:
        lines = [
            _line("Alpha minor (Test) Fakeauthor."),
            _line("Plant small."),
            _line("2. Alpha major Fakeauthor, Some Journal 1: 1 (1900)."),
            _line("Plant large."),
        ]
        species, _ = MODULE.find_species_entries(lines, "Alpha", 0, len(lines))
        self.assertEqual(len(species), 2)
        self.assertEqual(species[0]["species_name"], "Alpha minor")
        self.assertEqual(species[1]["species_name"], "Alpha major")


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

    def test_split_running_head_flags_ambiguous_boundary_not_silent_drop(self) -> None:
        # Real pilot-page-66 case: Vision split "28 Clowesia" into two
        # separate line observations, so neither matches the combined
        # "<number> <Genus>" pattern -- no continuity signal survives.
        page_one = {
            "source_image": "synthetic-65.jpeg",
            "page_number": 65,
            "lines": [
                _line("28. Clowesia Testauthor"),
                _line("Roots adventitious."),
            ],
        }
        page_two = {
            "source_image": "synthetic-66.jpeg",
            "page_number": 66,
            "lines": [
                _line("28", mid_y=0.04),
                _line("Clowesia", mid_y=0.041),
                _line("Catasetum russellianum Hook. in Bot. Mag."),
                _line("Catasetum calceolatum Lem. in Jard."),
            ],
        }
        records, discontinuities = MODULE.build_genus_records([page_one, page_two])
        self.assertEqual(discontinuities, [])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["source_pages"], [65])
        self.assertEqual(records[0]["extraction_status"], "needs_review")
        self.assertIn(
            "ambiguous_genus_boundary:synthetic-66.jpeg",
            records[0]["review_flags"],
        )

    def test_numbered_species_list_does_not_open_a_second_genus_record(self) -> None:
        # Real full-run case: Epidendrum ("one of the largest genera with
        # several hundred" species, per its own page-181 text) numbers its
        # own internal species list with the genus name repeated ("1.
        # Epidendrum acuñae Dressler in Am. Orch. Soc. Bull. ..."), which
        # is genuinely citation-shaped and so passes both header
        # discriminators. Originally this produced a bogus second "genus 1
        # Epidendrum" record alongside the real "genus 70 Epidendrum L.";
        # fixed by suppressing the false hit (ba6dd8f-era history). At
        # that point species detection didn't yet recognize the numbered
        # form at all (finding 9), so this same real text was flagged
        # `numbered_species_list_unparsed` instead of actually being
        # parsed -- now it is: species detection recognizes the numbered
        # form (including the ñ in "acuñae", finding 9's second half) and
        # attaches it as a real species entry, no flag needed.
        page_one = {
            "source_image": "synthetic-181.jpeg",
            "page_number": 181,
            "lines": [
                _line("70. Epidendrum L."),
                _line("One of the largest genera with several hundred species."),
            ],
        }
        page_two = {
            "source_image": "synthetic-182.jpeg",
            "page_number": 182,
            "lines": [
                _line("70 Epidendrum", mid_y=0.04),
                _line("1. Epidendrum acuñae Dressler in Am. Orch. Soc."),
                _line("Bull. 28: 358 (1959). Type: Cuba, C. Wright 3333."),
            ],
        }
        records, discontinuities = MODULE.build_genus_records([page_one, page_two])
        self.assertEqual(discontinuities, [])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["genus_id"], "epidendrum")
        self.assertEqual(records[0]["source_pages"], [181, 182])
        self.assertEqual(records[0]["extraction_status"], "complete")
        self.assertEqual(records[0]["review_flags"], [])
        self.assertEqual(len(records[0]["species"]), 1)
        self.assertEqual(records[0]["species"][0]["species_name"], "Epidendrum acuñae")

    def test_genuinely_unparseable_numbered_header_is_still_flagged(self) -> None:
        # The residual case finding 9's flag exists for: a same-genus
        # numbered-header-shaped line that species detection, run against
        # the same page, still can't turn into a real entry (here: no
        # lowercase epithet at all after the genus name -- an author name
        # directly, which is genus-header-shaped, not species-shaped).
        page_one = {
            "source_image": "synthetic-181.jpeg",
            "page_number": 181,
            "lines": [_line("70. Epidendrum L.")],
        }
        page_two = {
            "source_image": "synthetic-182.jpeg",
            "page_number": 182,
            "lines": [
                _line("70 Epidendrum", mid_y=0.04),
                _line("1. Epidendrum Sw."),
            ],
        }
        records, _ = MODULE.build_genus_records([page_one, page_two])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["extraction_status"], "needs_review")
        self.assertIn(
            "numbered_species_list_unparsed:synthetic-182.jpeg",
            records[0]["review_flags"],
        )

    def test_bottom_band_running_head_confirms_continuation_not_ambiguous(self) -> None:
        # Real full-run case: pages 183/185/187/189 print the running head
        # at the page bottom, not the top (module docstring, finding 6).
        # Before this fix these were flagged ambiguous_genus_boundary even
        # though they genuinely continue the open genus.
        page_one = {
            "source_image": "synthetic-181.jpeg",
            "page_number": 181,
            "lines": [
                _line("70. Epidendrum L."),
                _line("Roots adventitious."),
            ],
        }
        page_two = {
            "source_image": "synthetic-183.jpeg",
            "page_number": 183,
            "lines": [
                _line("161. E. hawkesii"),
                _line("Epidendrum flavovirens Rchb. f., Beitr. Orch."),
                _line("183", mid_y=0.964),
                _line("70 Epidendrum", mid_y=0.965),
            ],
        }
        records, discontinuities = MODULE.build_genus_records([page_one, page_two])
        self.assertEqual(discontinuities, [])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["source_pages"], [181, 183])
        self.assertEqual(records[0]["extraction_status"], "complete")
        self.assertEqual(records[0]["review_flags"], [])

    def test_sparse_no_header_page_without_running_head_is_not_flagged(self) -> None:
        # A near-empty page (an illustration with a caption fragment, say)
        # isn't worth a review item on its own -- distinct from the
        # substantive-content case above.
        page_one = {
            "source_image": "synthetic-70.jpeg",
            "page_number": 70,
            "lines": [_line("5. Epsilon Testauthor"), _line("Roots adventitious.")],
        }
        page_two = {
            "source_image": "synthetic-71.jpeg",
            "page_number": 71,
            "lines": [_line("Fig. 5.")],
        }
        records, _ = MODULE.build_genus_records([page_one, page_two])
        self.assertEqual(records[0]["extraction_status"], "complete")
        self.assertEqual(records[0]["review_flags"], [])

    def test_tab_column_layout_flags_the_earlier_genus_not_silently_wrong(self) -> None:
        # Real full-run case, page-040.jpeg: "16. Cranichis Sw." (its own
        # narrow tab column) and "17. Habenaria Willd." (a later tab
        # column) both on one page, with Habenaria's real diagnostic
        # paragraph sitting in a body column that sorts before Habenaria's
        # own header column -- so it silently landed in Cranichis's block.
        # Cranichis's record ended up "complete", zero flags, while
        # containing Habenaria's real facts under Cranichis's name.
        page_one = {
            "source_image": "synthetic-040.jpeg",
            "page_number": 40,
            "lines": [
                _line("16. Alpha Testauthor", column=1),
                _line("SUBTRIBE TESTINAE BENTH.", column=3, mid_y=0.1),
                _line("Beta's own diagnostic paragraph.", column=3, mid_y=0.2),
                _line("17. Beta Testauthor", column=4),
            ],
        }
        records, _ = MODULE.build_genus_records([page_one])
        alpha = next(r for r in records if r["genus_id"] == "alpha")
        self.assertEqual(alpha["extraction_status"], "needs_review")
        self.assertIn(
            "possible_cross_genus_content:synthetic-040.jpeg", alpha["review_flags"]
        )

    def test_ordinary_single_column_tribe_heading_does_not_false_positive(self) -> None:
        # The expected, harmless case (page-050's own finding): a tribe
        # heading between two genera in a straightforward single-column
        # layout is already excluded as furniture and needs no special
        # flag -- the column-adjacency signature must not fire here.
        page_one = {
            "source_image": "synthetic-050.jpeg",
            "page_number": 50,
            "lines": [
                _line("16. Alpha Testauthor", column=0),
                _line("Roots adventitious.", column=0),
                _line("SUBTRIBE TESTINAE BENTH.", column=0, mid_y=0.6),
                _line("17. Beta Testauthor", column=0, mid_y=0.7),
            ],
        }
        records, _ = MODULE.build_genus_records([page_one])
        alpha = next(r for r in records if r["genus_id"] == "alpha")
        self.assertEqual(alpha["extraction_status"], "complete")
        self.assertEqual(alpha["review_flags"], [])

    def test_last_header_on_page_is_never_flagged_by_this_check(self) -> None:
        # No next header on the page -- next_header_column is None, and
        # the check must not fire on a genus's own trailing content.
        page_one = {
            "source_image": "synthetic-060.jpeg",
            "page_number": 60,
            "lines": [
                _line("16. Alpha Testauthor", column=1),
                _line("SUBTRIBE TESTINAE BENTH.", column=3),
                _line("Alpha's own trailing text.", column=3),
            ],
        }
        records, _ = MODULE.build_genus_records([page_one])
        self.assertEqual(records[0]["extraction_status"], "complete")
        self.assertEqual(records[0]["review_flags"], [])


def _etymology_record(genus_name, etymology_text, source_image="synthetic.jpeg"):
    """Build a minimal genus record carrying only an ETYMOLOGY field."""
    return {
        "genus_id": genus_name.lower(),
        "genus_name": genus_name,
        "fields": {
            "ETYMOLOGY": {
                "text": etymology_text,
                "source_image": source_image,
                "confidence": 1.0,
                "status": "scored",
            }
        },
        "species": [],
        "extraction_status": "complete",
        "review_flags": [],
    }


class FlagForeignGenusEtymologyTest(unittest.TestCase):
    """Cross-genus swaps caught by reading a record's own etymology."""

    def test_etymology_deriving_another_genus_is_flagged_with_that_genus(self) -> None:
        # Real page-107 text: Coryanthes' record derives "trigonos",
        # which coins Trigonidium, not Coryanthes (korys, a helmet).
        records = [
            _etymology_record(
                "Coryanthes",
                "From the Greek trigonos (three-",
                source_image="page-107.jpeg",
            ),
            _etymology_record("Trigonidium", "From the Greek trigonos (three-angled)."),
        ]
        MODULE.flag_foreign_genus_etymology(records)
        self.assertEqual(records[0]["extraction_status"], "needs_review")
        self.assertEqual(
            records[0]["review_flags"],
            ["foreign_genus_etymology:page-107.jpeg:Trigonidium"],
        )
        # The genus the text really belongs to is itself consistent.
        self.assertEqual(records[1]["review_flags"], [])

    def test_transliterated_root_still_identifies_its_genus(self) -> None:
        # Real page-065/153 text. Greek as the book spells it does not
        # match the Latinized genus letter for letter: kata -> Catasetum,
        # harpe -> Arpophyllum (silent leading h, and only "arp" shared).
        records = [
            _etymology_record("Clowesia", "From the Greek kata (down) and seta (bristle)"),
            _etymology_record("Catasetum", "Named after James Bateman (1811-"),
            _etymology_record("Coelia", "From the Greek harpe (sickle) and"),
            _etymology_record("Arpophyllum", "From the Latin mucronatus (with a"),
        ]
        MODULE.flag_foreign_genus_etymology(records)
        flags = {r["genus_name"]: r["review_flags"] for r in records}
        self.assertEqual(
            flags["Clowesia"], ["foreign_genus_etymology:synthetic.jpeg:Catasetum"]
        )
        self.assertEqual(
            flags["Coelia"], ["foreign_genus_etymology:synthetic.jpeg:Arpophyllum"]
        )

    def test_self_consistent_etymology_is_not_flagged(self) -> None:
        # Real page text for four genera whose etymology is where it
        # belongs, including two compounds whose matching element sits in
        # the interior of the name (eu + lophos, psygma + orchis).
        records = [
            _etymology_record("Oncidium", "From the Greek onkos (a pad or mass)"),
            _etymology_record("Eulophia", "From the Greek eu (well) and lophos (plume)"),
            _etymology_record(
                "Psygmorchis", "From the Greek psygma (fan) and orchis (an orchid)"
            ),
            _etymology_record(
                "Comparettia", "Named after Andreo Comparetti, an eminent physiologist"
            ),
            _etymology_record("Cycnoches", "From the Greek kyknos (swan) and auchen (neck)"),
        ]
        MODULE.flag_foreign_genus_etymology(records)
        for record in records:
            self.assertEqual(record["review_flags"], [], record["genus_name"])
            self.assertEqual(record["extraction_status"], "complete")

    def test_generic_interior_root_names_no_owner(self) -> None:
        # "anthos" (flower) sits inside Spiranthes, Elleanthus and
        # Epidanthus alike; it identifies none of them, so a record whose
        # etymology contains it must not be handed a made-up owner.
        records = [
            _etymology_record("Maxillaria", "From the Greek acis (a point) and anthos (a flower)."),
            _etymology_record("Spiranthes", "From the Greek speira (a coil) and anthos (a flower)."),
            _etymology_record("Elleanthus", "From the Latin bractea (a bract) and"),
            _etymology_record("Epidanthus", "From the Greek epi (upon) and anthos (a flower)."),
        ]
        MODULE.flag_foreign_genus_etymology(records)
        for record in records:
            self.assertEqual(record["review_flags"], [], record["genus_name"])

    def test_species_level_etymology_is_left_alone(self) -> None:
        # Real page-016 text: a species etymology (P. maculata's) filed
        # under the genus. Wrong, but a different defect -- text
        # misplaced *within* a genus, not across two -- and no other
        # genus in the corpus explains it, so nothing is flagged.
        records = [
            _etymology_record(
                "Platythelys",
                "From the Latin maculatus (spotted, blotched) in reference to the leaves.",
            ),
            _etymology_record("Macradenia", "From the Greek makros (long) and aden (gland)"),
        ]
        MODULE.flag_foreign_genus_etymology(records)
        self.assertEqual(records[0]["review_flags"], [])

    def test_record_without_an_etymology_field_is_skipped(self) -> None:
        record = _etymology_record("Bletia", "")
        record["fields"] = {}
        records = [record]
        MODULE.flag_foreign_genus_etymology(records)
        self.assertEqual(records[0]["review_flags"], [])
        self.assertEqual(records[0]["extraction_status"], "complete")

    def test_etymology_that_derives_nothing_is_skipped(self) -> None:
        # Real page-137 shape: an ETYMOLOGY field the parser filled with
        # continuation prose carrying no glossed root and no eponym.
        records = [
            _etymology_record("Encyclia", "Flowers last several weeks. Uncommon."),
            _etymology_record("Epidendrum", "From the Greek epi (upon) and dendron (tree)"),
        ]
        MODULE.flag_foreign_genus_etymology(records)
        self.assertEqual(records[0]["review_flags"], [])


if __name__ == "__main__":
    unittest.main()

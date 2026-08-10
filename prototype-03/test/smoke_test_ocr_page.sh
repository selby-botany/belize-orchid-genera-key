#!/usr/bin/env bash
#
# Smoke check for bin/ocr_page.swift (Stage C).
#
# Not a correctness test (implementation plan document, §2.5): Vision's
# actual recognition is not mocked and is not asserted against a fixed
# expected transcription. This only confirms the harness runs against a
# real fixture and produces well-formed JSON Lines with the documented
# fields -- the same way prototype-02 validated the original script, by
# running it and inspecting real output.
#
# Usage:
#   prototype-03/test/smoke_test_ocr_page.sh

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
project_root="$(cd "${script_dir}/../.." && pwd -P)"
ocr_script="${script_dir}/../bin/ocr_page.swift"
fixture="${script_dir}/fixtures/ocr_smoke_sample.jpeg"
jq="${project_root}/bin/jq"

[[ -f "${ocr_script}" ]] || { echo "FAIL: missing ${ocr_script}" >&2; exit 1; }
[[ -f "${fixture}" ]] || { echo "FAIL: missing fixture ${fixture}" >&2; exit 1; }

output="$(swift "${ocr_script}" --json "${fixture}")"

# Exactly one JSON object, one line -- a single input file was given.
line_count="$(printf '%s\n' "${output}" | wc -l | tr -d ' ')"
[[ "${line_count}" -eq 1 ]] || {
    echo "FAIL: expected 1 JSONL line, got ${line_count}" >&2
    exit 1
}

# Parses as JSON at all.
printf '%s\n' "${output}" | "${jq}" -e . > /dev/null || {
    echo "FAIL: output is not valid JSON" >&2
    exit 1
}

# Every documented PageResult field is present (data document, §4).
for field in source_image line_count mean_confidence low_confidence_count \
             columns text lines accept_status reject_reasons; do
    printf '%s\n' "${output}" | "${jq}" -e "has(\"${field}\")" > /dev/null || {
        echo "FAIL: missing field ${field}" >&2
        exit 1
    }
done

# Column discovery ran and found at least one column.
columns="$(printf '%s\n' "${output}" | "${jq}" '.columns')"
[[ "${columns}" -ge 1 ]] || {
    echo "FAIL: columns=${columns}, expected >= 1" >&2
    exit 1
}

# The fixture is real body text -- OCR must find some of it, and each
# line record must carry the per-line fields Stage D segments on.
line_count_value="$(printf '%s\n' "${output}" | "${jq}" '.line_count')"
[[ "${line_count_value}" -gt 0 ]] || {
    echo "FAIL: line_count=0 on a fixture with real text" >&2
    exit 1
}
lines_array_length="$(printf '%s\n' "${output}" | "${jq}" '.lines | length')"
[[ "${lines_array_length}" -eq "${line_count_value}" ]] || {
    echo "FAIL: lines array length (${lines_array_length}) != line_count (${line_count_value})" >&2
    exit 1
}
for field in text confidence column min_x mid_y; do
    printf '%s\n' "${output}" \
        | "${jq}" -e ".lines[0] | has(\"${field}\")" > /dev/null || {
        echo "FAIL: lines[0] missing field ${field}" >&2
        exit 1
    }
done

# Reading order must not depend on which way up the page was scanned.
#
# Half this capture batch is upside down, and Vision hides it: it reads
# rotated text correctly and reports a flat 1.0 confidence either way,
# while returning geometry in image space -- so the page reads backwards
# with mirrored columns. The assertion here is rotation *invariance*
# rather than a fixed transcription, so it stays valid if Vision's
# recognition itself changes: the same page, turned over, must produce
# the same first line.
magick="${project_root}/bin/imagemagick"
rotated_dir="${project_root}/.smoke-rotated"
mkdir -p "${rotated_dir}"
trap 'rm -rf "${rotated_dir}"' EXIT

cp "${fixture}" "${rotated_dir}/upright.jpeg"
# bin/imagemagick runs in a container that mounts only the working
# directory, so it is given paths relative to the project root and run
# from there -- an absolute host path is not visible inside the container
# and fails to open the image.
( cd "${project_root}" \
  && "${magick}" convert ".smoke-rotated/upright.jpeg" -rotate 180 \
       ".smoke-rotated/flipped.jpeg" ) 2> /dev/null

both="$(swift "${ocr_script}" --json \
    "${rotated_dir}/upright.jpeg" "${rotated_dir}/flipped.jpeg")"

upright_first="$(printf '%s\n' "${both}" | head -1 | "${jq}" -r '.lines[0].text')"
flipped_first="$(printf '%s\n' "${both}" | tail -1 | "${jq}" -r '.lines[0].text')"
[[ "${upright_first}" == "${flipped_first}" ]] || {
    echo "FAIL: rotating the page changed reading order" >&2
    echo "  upright first line: ${upright_first}" >&2
    echo "  flipped first line: ${flipped_first}" >&2
    exit 1
}

# ... and the corrected page must still read top-down, not bottom-up.
flipped_ascending="$(printf '%s\n' "${both}" | tail -1 \
    | "${jq}" '[.lines | group_by(.column)[]
                | [.[].mid_y] | . == sort] | all')"
[[ "${flipped_ascending}" == "true" ]] || {
    echo "FAIL: flipped page's mid_y values are not in reading order" >&2
    exit 1
}

echo "PASS: ocr_page.swift produced well-formed output for ${line_count_value} lines"
echo "PASS: reading order is invariant to a 180 degree page rotation"

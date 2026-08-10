#!/usr/bin/env swift

// Recognize text on one or more page images and report it in reading order,
// with an accept/reject decision per page.
//
// Forked from prototype-02/bin/ocr_page.swift. `recognize` and
// `assignColumns` are carried over unchanged -- both are already correct
// and already validated against real pages of this same book. What's new:
// an explicit acceptPage() gate (requirements document, §2: confidence
// alone is never a safe accept signal -- an upside-down page can still
// average near-1.0 confidence) and JSON Lines output instead of a single
// pretty array, so a partial run is still readable and a large run never
// needs the whole result set in memory at once.
//
// PageResult carries both a joined `text` string (for a human skimming the
// output) and the underlying `lines` array with per-line confidence and
// geometry -- Stage D's field segmentation works line-by-line and needs
// that granularity preserved in the persisted JSON, not just folded into
// one string (data document, §4). Field names are written snake_case
// (JSONEncoder's `.convertToSnakeCase`) to match that document's schema.
//
// Language correction is disabled deliberately: this book is full of Latin
// binomials and author abbreviations that a language model would "correct"
// into ordinary English, silently corrupting the transcription.
//
// Page orientation is resolved here, before columns are assigned. Every
// odd-numbered page in this capture batch was scanned upside down, and
// Vision gives no direct sign of it: the recognized strings are correct
// (it reads rotated text) and the confidence is a flat 1.0 either way.
// Only the geometry betrays it, and only if something checks -- see
// `pageIsUpsideDown`. Left uncorrected the damage all lands downstream,
// where it looks like anything but a scanning problem: reading order runs
// up the page, columns mirror, sentences splice across the gutter mid-word
// ("slen" + "flower shape"), and a genus's text files itself under its
// neighbour's name. Stage D spent three separate rounds of detectors on
// those symptoms before the cause was found here.
//
// Usage:
//   swift prototype-03/bin/ocr_page.swift [--json] IMAGE...
//
//   --json writes one JSON object per line (JSON Lines) to stdout instead
//   of the human-readable summary. This is the mode run_pipeline uses to
//   build analysis/page_ocr.jsonl.

import AppKit
import Foundation
import Vision

struct Line: Codable {
    let text: String
    let confidence: Double
    let column: Int
    let midY: Double
    let minX: Double
}

/// One recognized line before page orientation has been resolved.
///
/// `maxX` is needed only to mirror the horizontal axis on an upside-down
/// page (a line's left edge there is its right edge here), so it stays
/// internal rather than joining the emitted `Line` schema.
struct RawLine {
    let text: String
    let confidence: Double
    let midY: Double
    let minX: Double
    let maxX: Double
}

struct Thresholds {
    // Provisional values, set with headroom rather than tuned to a
    // specific sample; the pilot run (implementation plan document, §3)
    // is the evidence pass that either confirms or adjusts these before
    // the full 1-190 page range is run through them.
    var minMeanConfidence: Double = 0.75
    var lowConfidenceCutoff: Double = 0.5
    var maxLowConfidenceFraction: Double = 0.10
    var minLineCount: Int = 5
    var maxLineCount: Int = 300
}

struct PageResult: Codable {
    let sourceImage: String
    let lineCount: Int
    let meanConfidence: Double
    let lowConfidenceCount: Int
    let columns: Int
    let text: String
    let lines: [Line]
    let acceptStatus: String
    let rejectReasons: [String]
}

/// Score how well a line order reads as continuous prose.
///
/// A body page's lines mostly continue one another: the line before ends
/// without terminal punctuation and the next begins lowercase, and a
/// hyphenated word break is stronger evidence still. Reversing the order
/// breaks most of those joins. Used only as a last resort, when a page
/// carries no running head, chapter head or folio to read the
/// orientation off -- it is a weak signal on pages with little prose
/// (a map, a key of one-line couplets) and must not outrank them.
func readingCoherence(_ lines: [RawLine], reversed: Bool) -> Int {
    let ordered = lines.sorted { reversed ? $0.midY > $1.midY : $0.midY < $1.midY }
    var score = 0
    for (first, second) in zip(ordered, ordered.dropFirst()) {
        let before = first.text.trimmingCharacters(in: .whitespaces)
        let after = second.text.trimmingCharacters(in: .whitespaces)
        guard let opener = after.first, !before.isEmpty else { continue }
        if before.hasSuffix("-") && opener.isLowercase {
            score += 2
        } else if !".!?:;".contains(before.last!) && opener.isLowercase {
            score += 1
        }
    }
    return score
}

/// Decide whether a scan is rotated 180 degrees.
///
/// Half this capture batch is: every odd-numbered page was fed into the
/// scanner upside down. Vision reads rotated text correctly -- the
/// strings are right and the confidence is a flat 1.0 either way, which
/// is exactly why this went unnoticed -- but it reports geometry in
/// image space, so reading order runs backwards up the page and columns
/// come out mirrored. Downstream that looks like scrambled prose, words
/// spliced across column breaks, and one genus's text filed under
/// another's name, none of which is a parsing defect at all.
///
/// The evidence is the page furniture, which this book always prints at
/// the page top: a running head ("17 Habenaria"), a chapter head
/// ("CHAPTER 2"). Finding one at the foot of the image means the image
/// is upside down. A bare folio number is a weaker witness, and only
/// consulted when no head is present, because a chapter-opening page
/// prints a drop folio at the page *bottom* instead -- on page 13 that
/// drop folio is the only number, and reading it naively gives the
/// wrong answer. Parity is deliberately not used: which pages a
/// scanner operator turned over is an accident of this batch, not a
/// property of the book.
func pageIsUpsideDown(_ lines: [RawLine]) -> Bool {
    let topBand = 0.10
    let bottomBand = 0.90

    var headAtFoot = 0
    var headAtHead = 0
    var folioAtFoot = 0
    var folioAtHead = 0

    for line in lines {
        let atFoot = line.midY > bottomBand
        let atHead = line.midY < topBand
        guard atFoot || atHead else { continue }

        let text = line.text.trimmingCharacters(in: .whitespaces)
        let tokens = text.split(separator: " ")
        guard let first = tokens.first else { continue }
        let leadIsNumber = first.count <= 3 && first.allSatisfy { $0.isNumber }

        if text.uppercased().hasPrefix("CHAPTER ") || (leadIsNumber && tokens.count > 1) {
            if atFoot { headAtFoot += 1 } else { headAtHead += 1 }
        } else if tokens.count == 1 && leadIsNumber {
            if atFoot { folioAtFoot += 1 } else { folioAtHead += 1 }
        }
    }

    if headAtFoot != headAtHead { return headAtFoot > headAtHead }
    if folioAtFoot != folioAtHead { return folioAtFoot > folioAtHead }
    return readingCoherence(lines, reversed: true) > readingCoherence(lines, reversed: false)
}

/// Recognize text in one image and return its lines with geometry.
func recognize(url: URL) -> [Line] {
    guard let image = NSImage(contentsOf: url),
          let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil)
    else {
        FileHandle.standardError.write("cannot read \(url.path)\n".data(using: .utf8)!)
        return []
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    request.recognitionLanguages = ["en-US"]

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    do {
        try handler.perform([request])
    } catch {
        FileHandle.standardError.write("OCR failed on \(url.path): \(error)\n".data(using: .utf8)!)
        return []
    }

    guard let observations = request.results else { return [] }
    // Vision's origin is the lower-left corner, so midY is flipped here
    // to make it read top-down. That alone is not enough when the page
    // itself went through the scanner upside down -- see
    // `pageIsUpsideDown`.
    let raw: [RawLine] = observations.compactMap { observation in
        guard let candidate = observation.topCandidates(1).first else { return nil }
        let box = observation.boundingBox
        return RawLine(
            text: candidate.string,
            confidence: Double(candidate.confidence),
            midY: Double(1.0 - (box.midY)),
            minX: Double(box.minX),
            maxX: Double(box.maxX)
        )
    }

    // Rotating the geometry is equivalent to rotating the image: an
    // upside-down scan re-OCR'd after a 180 degree rotation returns the
    // same strings with y' = 1 - y and x' = 1 - maxX (verified on
    // page-013 against an ImageMagick-rotated copy), so the page is
    // corrected here rather than re-read at twice the cost.
    let upsideDown = pageIsUpsideDown(raw)
    return raw.map { line in
        Line(
            text: line.text,
            confidence: line.confidence,
            column: 0,
            midY: upsideDown ? 1.0 - line.midY : line.midY,
            minX: upsideDown ? 1.0 - line.maxX : line.minX
        )
    }
}

/// Split lines into columns by their left edge, then order for reading.
///
/// The column count is discovered rather than assumed: body pages are set in
/// two columns and the index in three. Every gap in the sorted left-edge
/// distribution wider than `columnGap` becomes a boundary. The threshold has
/// to clear paragraph and sub-entry indentation, which is roughly 0.02 of the
/// page width, while still catching a real column gutter.
///
/// Assuming two columns silently interleaves the second and third columns of
/// the index -- scrambled reading order rather than a visible error, which is
/// far more expensive to detect downstream than a character mistake.
func assignColumns(_ lines: [Line], columnGap: Double = 0.05) -> [Line] {
    guard lines.count > 4 else { return lines }

    let xs = lines.map { $0.minX }.sorted()
    var boundaries: [Double] = []
    for index in 1..<xs.count {
        let gap = xs[index] - xs[index - 1]
        if gap > columnGap {
            boundaries.append((xs[index] + xs[index - 1]) / 2)
        }
    }
    guard !boundaries.isEmpty else { return lines }

    return lines.map { line in
        let column = boundaries.filter { line.minX >= $0 }.count
        return Line(text: line.text, confidence: line.confidence,
                    column: column, midY: line.midY, minX: line.minX)
    }
}

/// Decide whether a page's OCR output is trustworthy enough to accept.
///
/// Two independent checks, both required (requirements document, §2): a
/// confidence-based check and a structural one. Neither alone is a safe
/// gate -- a blank or upside-down page can pass a confidence check by
/// having very little (but very confident) text; a page with no text
/// content but plausible line geometry cannot happen with real OCR
/// output, but the reverse (garbage text at high apparent confidence) is
/// exactly prototype-02's documented failure mode, which this exists to
/// catch structurally rather than statistically.
func acceptPage(_ result: PageResult, thresholds: Thresholds) -> (accept: Bool, reasons: [String]) {
    var reasons: [String] = []

    if result.meanConfidence < thresholds.minMeanConfidence {
        reasons.append("mean_confidence_below_threshold")
    }
    let lowFraction = result.lineCount > 0
        ? Double(result.lowConfidenceCount) / Double(result.lineCount)
        : 1.0
    if lowFraction > thresholds.maxLowConfidenceFraction {
        reasons.append("low_confidence_fraction_above_threshold")
    }
    if result.lineCount < thresholds.minLineCount {
        reasons.append("line_count_below_band")
    }
    if result.lineCount > thresholds.maxLineCount {
        reasons.append("line_count_above_band")
    }

    return (reasons.isEmpty, reasons)
}

var wantJSON = false
var paths: [String] = []
for argument in CommandLine.arguments.dropFirst() {
    if argument == "--json" { wantJSON = true } else { paths.append(argument) }
}

let thresholds = Thresholds()
var results: [PageResult] = []
for path in paths {
    let url = URL(fileURLWithPath: path)
    let lines = assignColumns(recognize(url: url))
    let ordered = lines.sorted {
        $0.column != $1.column ? $0.column < $1.column : $0.midY < $1.midY
    }
    let confidences = ordered.map { $0.confidence }
    let mean = confidences.isEmpty ? 0 : confidences.reduce(0, +) / Double(confidences.count)
    var result = PageResult(
        sourceImage: url.lastPathComponent,
        lineCount: ordered.count,
        meanConfidence: mean,
        lowConfidenceCount: confidences.filter { $0 < thresholds.lowConfidenceCutoff }.count,
        columns: Set(ordered.map { $0.column }).count,
        text: ordered.map { $0.text }.joined(separator: "\n"),
        lines: ordered,
        acceptStatus: "accepted",
        rejectReasons: []
    )
    let (accept, reasons) = acceptPage(result, thresholds: thresholds)
    result = PageResult(
        sourceImage: result.sourceImage,
        lineCount: result.lineCount,
        meanConfidence: result.meanConfidence,
        lowConfidenceCount: result.lowConfidenceCount,
        columns: result.columns,
        text: result.text,
        lines: result.lines,
        acceptStatus: accept ? "accepted" : "rejected",
        rejectReasons: reasons
    )
    results.append(result)
}

if wantJSON {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.sortedKeys]
    encoder.keyEncodingStrategy = .convertToSnakeCase
    for result in results {
        let data = try encoder.encode(result)
        print(String(data: data, encoding: .utf8)!)
    }
} else {
    for result in results {
        print("=== \(result.sourceImage)  lines=\(result.lineCount) "
              + "columns=\(result.columns) "
              + "mean_conf=\(String(format: "%.3f", result.meanConfidence)) "
              + "low_conf=\(result.lowConfidenceCount) "
              + "status=\(result.acceptStatus) "
              + "reasons=\(result.rejectReasons.joined(separator: ",")) ===")
        print(result.text)
        print("")
    }
}

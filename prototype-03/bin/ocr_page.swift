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
// Language correction is disabled deliberately: this book is full of Latin
// binomials and author abbreviations that a language model would "correct"
// into ordinary English, silently corrupting the transcription.
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
    let image: String
    let lineCount: Int
    let meanConfidence: Double
    let lowConfidenceCount: Int
    let columns: Int
    let text: String
    let acceptStatus: String
    let rejectReasons: [String]
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
    return observations.compactMap { observation in
        guard let candidate = observation.topCandidates(1).first else { return nil }
        let box = observation.boundingBox
        return Line(
            text: candidate.string,
            confidence: Double(candidate.confidence),
            column: 0,
            midY: Double(1.0 - (box.midY)),
            minX: Double(box.minX)
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
        image: url.lastPathComponent,
        lineCount: ordered.count,
        meanConfidence: mean,
        lowConfidenceCount: confidences.filter { $0 < thresholds.lowConfidenceCutoff }.count,
        columns: Set(ordered.map { $0.column }).count,
        text: ordered.map { $0.text }.joined(separator: "\n"),
        acceptStatus: "accepted",
        rejectReasons: []
    )
    let (accept, reasons) = acceptPage(result, thresholds: thresholds)
    result = PageResult(
        image: result.image,
        lineCount: result.lineCount,
        meanConfidence: result.meanConfidence,
        lowConfidenceCount: result.lowConfidenceCount,
        columns: result.columns,
        text: result.text,
        acceptStatus: accept ? "accepted" : "rejected",
        rejectReasons: reasons
    )
    results.append(result)
}

if wantJSON {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.sortedKeys]
    for result in results {
        let data = try encoder.encode(result)
        print(String(data: data, encoding: .utf8)!)
    }
} else {
    for result in results {
        print("=== \(result.image)  lines=\(result.lineCount) "
              + "columns=\(result.columns) "
              + "mean_conf=\(String(format: "%.3f", result.meanConfidence)) "
              + "low_conf=\(result.lowConfidenceCount) "
              + "status=\(result.acceptStatus) "
              + "reasons=\(result.rejectReasons.joined(separator: ",")) ===")
        print(result.text)
        print("")
    }
}

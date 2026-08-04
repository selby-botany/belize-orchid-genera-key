#!/usr/bin/env swift

// Recognize text on one or more page images and report it in reading order.
//
// Language correction is disabled deliberately: this book is full of Latin
// binomials and author abbreviations that a language model would "correct"
// into ordinary English, silently corrupting the transcription.
//
// Usage:
//   swift prototype-02/bin/ocr_page.swift [--json] IMAGE...

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

struct PageResult: Codable {
    let image: String
    let lineCount: Int
    let meanConfidence: Double
    let lowConfidenceCount: Int
    let columns: Int
    let text: String
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
/// the index — scrambled reading order rather than a visible error, which is
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

var wantJSON = false
var paths: [String] = []
for argument in CommandLine.arguments.dropFirst() {
    if argument == "--json" { wantJSON = true } else { paths.append(argument) }
}

var results: [PageResult] = []
for path in paths {
    let url = URL(fileURLWithPath: path)
    let lines = assignColumns(recognize(url: url))
    let ordered = lines.sorted {
        $0.column != $1.column ? $0.column < $1.column : $0.midY < $1.midY
    }
    let confidences = ordered.map { $0.confidence }
    let mean = confidences.isEmpty ? 0 : confidences.reduce(0, +) / Double(confidences.count)
    results.append(PageResult(
        image: url.lastPathComponent,
        lineCount: ordered.count,
        meanConfidence: mean,
        lowConfidenceCount: confidences.filter { $0 < 0.5 }.count,
        columns: Set(ordered.map { $0.column }).count,
        text: ordered.map { $0.text }.joined(separator: "\n")
    ))
}

if wantJSON {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let data = try encoder.encode(results)
    print(String(data: data, encoding: .utf8)!)
} else {
    for result in results {
        print("=== \(result.image)  lines=\(result.lineCount) "
              + "columns=\(result.columns) "
              + "mean_conf=\(String(format: "%.3f", result.meanConfidence)) "
              + "low_conf=\(result.lowConfidenceCount) ===")
        print(result.text)
        print("")
    }
}

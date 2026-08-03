#!/usr/bin/env swift

import AppKit
import Foundation
import Vision

// Extracts full-page OCR text from mcleish page images, in reading order,
// merging text recognized across every scan of a given page (primary +
// alternates) so low-confidence or missed lines in one scan can be
// recovered from another.
//
// Usage:
//   swift bin/extract_mcleish_page_text.swift            # all pages
//   swift bin/extract_mcleish_page_text.swift 41 42 48    # specific pages only

struct Line: Codable {
    let text: String
    let confidence: Double
    let column: Int
    let midY: Double
    let minX: Double
    let sourceImage: String
}

struct PageResult: Codable {
    let page: Int
    let images: [String]
    let lines: [Line]
    let text: String
}

struct Output: Codable {
    let schemaVersion: Int
    let generatedFrom: String
    let pages: [PageResult]

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case generatedFrom = "generated_from"
        case pages
    }
}

func recognizeLines(imagePath: String) -> [Line] {
    guard let nsImage = NSImage(contentsOfFile: imagePath),
        let cgImage = nsImage.cgImage(forProposedRect: nil, context: nil, hints: nil)
    else {
        FileHandle.standardError.write("Warning: could not load \(imagePath)\n".data(using: .utf8)!)
        return []
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    do {
        try handler.perform([request])
    } catch {
        FileHandle.standardError.write("Warning: OCR failed for \(imagePath): \(error)\n".data(using: .utf8)!)
        return []
    }

    guard let observations = request.results else { return [] }

    // Two-column page layout: assign each observation to a column by its
    // horizontal midpoint, split at the page's midline. Vision's
    // boundingBox origin is bottom-left, so higher minY is higher on the
    // page; keep raw minY/midY and sort by column then descending y below.
    var lines: [Line] = []
    let imageName = (imagePath as NSString).lastPathComponent
    for observation in observations {
        guard let candidate = observation.topCandidates(1).first else { continue }
        let box = observation.boundingBox
        let midX = box.midX
        let midY = box.midY
        let column = midX < 0.5 ? 0 : 1
        lines.append(
            Line(
                text: candidate.string,
                confidence: Double(candidate.confidence),
                column: column,
                midY: Double(midY),
                minX: Double(box.minX),
                sourceImage: imageName
            )
        )
    }
    return lines
}

// Merge lines recognized from multiple scans of the same page. Lines are
// grouped into row bands per column; within a band, the highest-confidence
// text wins. Bands with no counterpart in other scans are kept as-is, which
// recovers text missed entirely in some scans.
func mergeScans(perScanLines: [[Line]]) -> [Line] {
    let yTolerance = 0.012

    struct Band {
        var column: Int
        var yCenter: Double
        var candidates: [Line]
    }

    var bands: [Band] = []

    for scanLines in perScanLines {
        for line in scanLines {
            if let idx = bands.firstIndex(where: {
                $0.column == line.column && abs($0.yCenter - line.midY) <= yTolerance
            }) {
                bands[idx].candidates.append(line)
                let count = Double(bands[idx].candidates.count)
                bands[idx].yCenter = (bands[idx].yCenter * (count - 1) + line.midY) / count
            } else {
                bands.append(Band(column: line.column, yCenter: line.midY, candidates: [line]))
            }
        }
    }

    var merged: [Line] = []
    for band in bands {
        let best = band.candidates.max(by: { $0.confidence < $1.confidence })!
        merged.append(best)
    }

    // Reading order: left column top-to-bottom, then right column
    // top-to-bottom. Vision y increases upward, so sort descending.
    merged.sort { a, b in
        if a.column != b.column { return a.column < b.column }
        return a.midY > b.midY
    }
    return merged
}

func pageNumber(fromFilename filename: String) -> Int? {
    let stem = (filename as NSString).deletingPathExtension
    let base = stem.split(separator: "-", maxSplits: 1)[0]
    return Int(base)
}

func main() -> Int32 {
    let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
    let imagesDir = root.appendingPathComponent("mcleish", isDirectory: true)
    let outputPath = root.appendingPathComponent("analysis/mcleish_page_text.json")

    let requestedPages = Set(
        CommandLine.arguments.dropFirst().compactMap { Int($0) }
    )

    guard
        let allFiles = try? FileManager.default.contentsOfDirectory(
            at: imagesDir, includingPropertiesForKeys: nil)
    else {
        FileHandle.standardError.write("Error: could not list \(imagesDir.path)\n".data(using: .utf8)!)
        return 1
    }

    var byPage: [Int: [String]] = [:]
    for file in allFiles {
        guard file.pathExtension.lowercased() == "jpg" else { continue }
        guard let page = pageNumber(fromFilename: file.lastPathComponent) else { continue }
        if !requestedPages.isEmpty && !requestedPages.contains(page) { continue }
        byPage[page, default: []].append(file.path)
    }

    var results: [PageResult] = []
    for page in byPage.keys.sorted() {
        let paths = byPage[page]!.sorted()
        var perScanLines: [[Line]] = []
        for path in paths {
            perScanLines.append(recognizeLines(imagePath: path))
        }
        let merged = mergeScans(perScanLines: perScanLines)
        let text = merged.map { $0.text }.joined(separator: "\n")
        let imageNames = paths.map { ($0 as NSString).lastPathComponent }
        results.append(PageResult(page: page, images: imageNames, lines: merged, text: text))
        FileHandle.standardError.write("Processed page \(page) (\(paths.count) scan(s), \(merged.count) lines)\n".data(using: .utf8)!)
    }

    let output = Output(
        schemaVersion: 1,
        generatedFrom: "mcleish/*.jpg",
        pages: results
    )

    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    guard let data = try? encoder.encode(output) else {
        FileHandle.standardError.write("Error: failed to encode output\n".data(using: .utf8)!)
        return 1
    }
    try? data.write(to: outputPath)
    print("Wrote: \(outputPath.path)")
    print("Pages processed: \(results.count)")
    return 0
}

exit(main())

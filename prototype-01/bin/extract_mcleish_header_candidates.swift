#!/usr/bin/env swift

import AppKit
import CoreImage
import CoreImage.CIFilterBuiltins
import Foundation
import Vision

struct Candidate: Codable {
    let page: Int
    let score: Double
    let minX: Double
    let minY: Double
    let orientation: String
    let text: String
}

struct FileResult: Codable {
    let image: String
    let bestPage: Int?
    let bestScore: Double
    let candidates: [Candidate]
    let needsReview: Bool
}

func versionParts(_ value: String) -> [String] {
    var out: [String] = []
    var current = ""
    var lastWasDigit: Bool?
    for ch in value {
        let isDigit = ch.isNumber
        if lastWasDigit == nil || lastWasDigit == isDigit {
            current.append(ch)
        } else {
            out.append(current)
            current = String(ch)
        }
        lastWasDigit = isDigit
    }
    if !current.isEmpty {
        out.append(current)
    }
    return out
}

func versionLess(_ a: String, _ b: String) -> Bool {
    let ap = versionParts(a)
    let bp = versionParts(b)
    let count = max(ap.count, bp.count)
    for i in 0..<count {
        if i >= ap.count { return true }
        if i >= bp.count { return false }
        let x = ap[i]
        let y = bp[i]
        if let xi = Int(x), let yi = Int(y) {
            if xi != yi { return xi < yi }
        } else if x != y {
            return x < y
        }
    }
    return a < b
}

func scoreCandidate(text: String, page: Int, minX: Double, minY: Double) -> Double {
    var score = 0.0

    // Prefer observations very near the top margin.
    score += max(0.0, min(1.0, (minY - 0.90) / 0.10)) * 5.0

    // Printed page numbers appear near the outside edges (left for verso, right for recto).
    let edgeDistance = min(abs(minX - 0.02), abs(minX - 0.90))
    score += max(0.0, 1.0 - min(1.0, edgeDistance / 0.25)) * 4.0

    // Prefer short number-only fragments over longer lines with embedded numbers.
    let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
    let isOnlyDigits = trimmed.range(of: "^[0-9]{1,3}$", options: .regularExpression) != nil
    if isOnlyDigits {
        score += 3.0
    } else if trimmed.count <= 6 {
        score += 1.0
    }

    // De-emphasize tiny values commonly seen in measurements and figure labels.
    if page <= 8 {
        score -= 1.5
    }

    return score
}

func rotate(cgImage: CGImage, degrees: Int, context: CIContext) -> CGImage? {
    let radians = CGFloat(degrees) * .pi / 180.0
    let src = CIImage(cgImage: cgImage)

    var transform = CGAffineTransform(rotationAngle: radians)
    let rotatedRect = CGRect(origin: .zero,
                             size: CGSize(width: cgImage.width, height: cgImage.height))
        .applying(transform)
        .standardized
    transform = transform.translatedBy(x: -rotatedRect.minX, y: -rotatedRect.minY)

    let out = src.transformed(by: transform)
    let finalRect = CGRect(x: 0,
                           y: 0,
                           width: Int(rotatedRect.width.rounded()),
                           height: Int(rotatedRect.height.rounded()))
    return context.createCGImage(out, from: finalRect)
}

func runOCR(fileURL: URL, regex: NSRegularExpression, ciContext: CIContext) throws -> [Candidate] {
    guard let image = NSImage(contentsOf: fileURL),
          let tiff = image.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let cgImage = rep.cgImage else {
        return []
    }

    var out: [Candidate] = []

    let variants: [(String, CGImage?)] = [
        ("0", cgImage),
        ("90", rotate(cgImage: cgImage, degrees: 90, context: ciContext)),
        ("180", rotate(cgImage: cgImage, degrees: 180, context: ciContext)),
        ("270", rotate(cgImage: cgImage, degrees: 270, context: ciContext)),
    ]

    for (orientation, variant) in variants {
        guard let variant else { continue }

        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.usesLanguageCorrection = false

        let handler = VNImageRequestHandler(cgImage: variant, options: [:])
        try handler.perform([request])

        for observation in request.results ?? [] {
            guard let recognized = observation.topCandidates(1).first else {
                continue
            }

            let text = recognized.string
            let box = observation.boundingBox
            guard box.minY > 0.85 else {
                continue
            }

            let range = NSRange(text.startIndex..<text.endIndex, in: text)
            for match in regex.matches(in: text, range: range) {
                guard let swiftRange = Range(match.range, in: text),
                      let page = Int(text[swiftRange]),
                      page >= 1,
                      page <= 400 else {
                    continue
                }

                var score = scoreCandidate(
                    text: text,
                    page: page,
                    minX: Double(box.minX),
                    minY: Double(box.minY)
                )
                // Slightly prefer non-rotated matches if all else equal.
                if orientation != "0" {
                    score -= 0.25
                }

                out.append(Candidate(
                    page: page,
                    score: score,
                    minX: Double(box.minX),
                    minY: Double(box.minY),
                    orientation: orientation,
                    text: text
                ))
            }
        }
    }

    return out.sorted {
        if $0.score == $1.score {
            if $0.page == $1.page {
                return $0.minX < $1.minX
            }
            return $0.page < $1.page
        }
        return $0.score > $1.score
    }
}

let fm = FileManager.default
let workingDir = URL(fileURLWithPath: fm.currentDirectoryPath)
let mcleishDir = workingDir.appendingPathComponent("mcleish", isDirectory: true)
let regex = try NSRegularExpression(pattern: "\\b\\d{1,3}\\b")
let ciContext = CIContext()

let files = try fm.contentsOfDirectory(at: mcleishDir, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension.lowercased() == "jpg" }
    .sorted { versionLess($0.lastPathComponent, $1.lastPathComponent) }

var results: [FileResult] = []
for file in files {
    let candidates = try runOCR(fileURL: file, regex: regex, ciContext: ciContext)
    let best = candidates.first
    let bestPage = best?.page
    let bestScore = best?.score ?? 0.0

    // Require both a strong score and a meaningful gap from runner-up.
    let secondScore = candidates.dropFirst().first?.score ?? -99.0
    let confident = bestScore >= 8.0 && (bestScore - secondScore) >= 1.0

    results.append(FileResult(
        image: file.lastPathComponent,
        bestPage: bestPage,
        bestScore: bestScore,
        candidates: Array(candidates.prefix(5)),
        needsReview: !confident
    ))
}

let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
let outputData = try encoder.encode(results)
FileHandle.standardOutput.write(outputData)
FileHandle.standardOutput.write(Data("\n".utf8))
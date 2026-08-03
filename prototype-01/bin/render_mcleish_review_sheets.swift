#!/usr/bin/env swift

import AppKit
import Foundation

struct Manifest: Decodable {
    let entries: [Entry]
}

struct Entry: Decodable {
    let image: String
    let inferred_page: Int?
    let proposed_page: Int?
    let proposed_source: String
    let needs_review: Bool?
}

struct TargetEntry {
    let index: Int
    let entry: Entry
}

let fileManager = FileManager.default
let root = URL(fileURLWithPath: fileManager.currentDirectoryPath)
let manifestURL = root.appendingPathComponent("analysis/mcleish_manifest_postprocessed.json")
let imagesDir = root.appendingPathComponent("mcleish", isDirectory: true)

let data = try Data(contentsOf: manifestURL)
let manifest = try JSONDecoder().decode(Manifest.self, from: data)

let mode = CommandLine.arguments.dropFirst().first ?? "queue"
let outDirName = mode == "context" ? "mcleish_review_sheets_context" : "mcleish_review_sheets"
let outDir = root.appendingPathComponent("analysis/\(outDirName)", isDirectory: true)

let targets: [TargetEntry]
if mode == "context" {
    let unresolvedIndexes = manifest.entries.enumerated().compactMap { index, entry in
        entry.proposed_source == "unresolved" ? index : nil
    }
    var selected = Set<Int>()
    for index in unresolvedIndexes {
        let start = max(0, index - 2)
        let end = min(manifest.entries.count - 1, index + 2)
        for candidate in start...end {
            selected.insert(candidate)
        }
    }
    targets = selected.sorted().map { TargetEntry(index: $0, entry: manifest.entries[$0]) }
} else {
    targets = manifest.entries.enumerated().compactMap { index, entry in
        if entry.proposed_source == "unresolved" || entry.proposed_source == "ocr_low_confidence" {
            return TargetEntry(index: index, entry: entry)
        }
        return nil
    }
}

try? fileManager.removeItem(at: outDir)
try fileManager.createDirectory(at: outDir, withIntermediateDirectories: true)

let columns = 3
let rows = 4
let pageSize = columns * rows
let thumbWidth: CGFloat = 360
let thumbHeight: CGFloat = 170
let labelHeight: CGFloat = 46
let padding: CGFloat = 16
let canvasWidth = CGFloat(columns) * (thumbWidth + padding) + padding
let canvasHeight = CGFloat(rows) * (thumbHeight + labelHeight + padding) + padding

let paragraph = NSMutableParagraphStyle()
paragraph.alignment = .left

let labelAttrs: [NSAttributedString.Key: Any] = [
    .font: NSFont.monospacedSystemFont(ofSize: 16, weight: .regular),
    .foregroundColor: NSColor.black,
    .paragraphStyle: paragraph,
]

for batchStart in stride(from: 0, to: targets.count, by: pageSize) {
    let batch = Array(targets[batchStart..<min(batchStart + pageSize, targets.count)])

    let canvas = NSImage(size: NSSize(width: canvasWidth, height: canvasHeight))
    canvas.lockFocus()
    NSColor.white.setFill()
    NSBezierPath(rect: NSRect(x: 0, y: 0, width: canvasWidth, height: canvasHeight)).fill()

    for (slot, target) in batch.enumerated() {
        let index = target.index
        let entry = target.entry
        let column = slot % columns
        let row = slot / columns

        let x = padding + CGFloat(column) * (thumbWidth + padding)
        let y = canvasHeight - padding - CGFloat(row + 1) * (thumbHeight + labelHeight + padding) + labelHeight

        let imageURL = imagesDir.appendingPathComponent(entry.image)
        guard let image = NSImage(contentsOf: imageURL) else {
            continue
        }

        let sourceSize = image.size
        let cropRect = NSRect(
            x: 0,
            y: sourceSize.height * 0.78,
            width: sourceSize.width,
            height: sourceSize.height * 0.22
        )
        let thumbRect = NSRect(x: x, y: y, width: thumbWidth, height: thumbHeight)
        image.draw(in: thumbRect, from: cropRect, operation: .copy, fraction: 1.0)

        NSColor.black.setStroke()
        NSBezierPath(rect: thumbRect).stroke()

        let inferred = entry.inferred_page.map(String.init) ?? "-"
        let proposed = entry.proposed_page.map(String.init) ?? "-"
        let reviewFlag = entry.proposed_source == "unresolved" ? "*" : " "
        let label = String(
            format: "%@%03d %@ src=%@ inferred=%@ proposed=%@",
            reviewFlag,
            index + 1,
            entry.image,
            entry.proposed_source,
            inferred,
            proposed
        )
        label.draw(
            in: NSRect(x: x, y: y - labelHeight + 4, width: thumbWidth, height: labelHeight),
            withAttributes: labelAttrs
        )
    }

    canvas.unlockFocus()

    guard let tiff = canvas.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let jpeg = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.72]) else {
        continue
    }

    let batchNumber = batchStart / pageSize + 1
    let outURL = outDir.appendingPathComponent(String(format: "%@-%02d.jpg", mode, batchNumber))
    try jpeg.write(to: outURL)
    print(outURL.path)
}
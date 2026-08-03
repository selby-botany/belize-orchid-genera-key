#!/usr/bin/env python3
"""Build a visual HTML audit report from the scan source manifest."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


STYLES = """
:root {
    color-scheme: light;
    --ink: #202421;
    --muted: #626963;
    --paper: #f4f2eb;
    --surface: #fffef9;
    --line: #c9cec7;
    --accent: #12634a;
    --warning: #a33a24;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    color: var(--ink);
    background: var(--paper);
    font-family: Charter, "Iowan Old Style", Georgia, serif;
}
header {
    position: sticky;
    z-index: 10;
    top: 0;
    padding: 18px clamp(18px, 4vw, 56px);
    border-bottom: 1px solid var(--line);
    background: color-mix(in srgb, var(--paper) 94%, transparent);
    backdrop-filter: blur(12px);
}
h1, h2, p { margin: 0; }
h1 { font-size: clamp(1.35rem, 2vw, 2rem); letter-spacing: 0; }
.summary { margin-top: 6px; color: var(--muted); }
.controls {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 18px;
    align-items: center;
    margin-top: 14px;
    font-family: Aptos, "Helvetica Neue", sans-serif;
    font-size: 0.9rem;
}
.controls label { display: inline-flex; gap: 6px; align-items: center; }
.controls input[type="search"] {
    width: 9rem;
    padding: 7px 9px;
    border: 1px solid var(--line);
    border-radius: 4px;
    background: var(--surface);
    font: inherit;
}
.controls a { color: var(--accent); }
main { padding-bottom: 40px; }
.page {
    padding: 24px clamp(18px, 4vw, 56px) 30px;
    border-bottom: 1px solid var(--line);
}
.page:nth-child(even) { background: rgb(255 255 255 / 34%); }
.page-heading {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 16px;
    align-items: baseline;
    margin-bottom: 16px;
}
.page-heading h2 { font-size: 1.25rem; letter-spacing: 0; }
.status { color: var(--muted); font: 0.86rem Aptos, sans-serif; }
.missing { color: var(--warning); font-weight: 700; }
.candidates {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr));
    gap: 16px;
}
.candidate {
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 6px;
    background: var(--surface);
}
.candidate a { display: block; background: #d9d8d1; }
.candidate img {
    display: block;
    width: 100%;
    height: clamp(320px, 52vw, 620px);
    object-fit: contain;
}
.metadata {
    display: grid;
    gap: 5px;
    padding: 11px 12px 13px;
    font: 0.82rem/1.35 Aptos, "Helvetica Neue", sans-serif;
}
.filename { color: var(--accent); font-weight: 700; }
.digest { overflow-wrap: anywhere; color: var(--muted); }
.empty {
    padding: 24px;
    border-left: 4px solid var(--warning);
    background: var(--surface);
    color: var(--warning);
}
[hidden] { display: none !important; }
@media (max-width: 600px) {
    header { position: static; }
    .candidate img { height: 70vh; }
}
"""


SCRIPT = """
const search = document.querySelector('#page-search');
const filters = [...document.querySelectorAll('[data-filter]')];
const pages = [...document.querySelectorAll('.page')];
const images = [...document.querySelectorAll('img[data-src]')];

const imageObserver = new IntersectionObserver(entries => {
    for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const image = entry.target;
        image.src = image.dataset.src;
        image.removeAttribute('data-src');
        imageObserver.unobserve(image);
    }
}, { rootMargin: '600px 0px' });
for (const image of images) imageObserver.observe(image);

function updateVisibility() {
    const query = search.value.trim().replace(/^0+/, '');
    const enabled = new Set(filters.filter(item => item.checked)
        .map(item => item.dataset.filter));
    for (const page of pages) {
        const matchesPage = !query || page.dataset.page === query;
        const matchesFilter = enabled.has(page.dataset.category);
        page.hidden = !(matchesPage && matchesFilter);
    }
}

search.addEventListener('input', updateVisibility);
for (const filter of filters) filter.addEventListener('change', updateVisibility);
"""


def page_category(candidate_count: int) -> str:
    """Return the audit-priority category for a page."""
    if candidate_count == 0:
        return "missing"
    if candidate_count >= 3:
        return "high-duplicate"
    if candidate_count == 2:
        return "multi"
    return "single"


def candidate_html(candidate: dict[str, object]) -> str:
    """Render one candidate capture."""
    filename = html.escape(str(candidate["filename"]))
    source = f"../../page-scans/{filename}"
    dimensions = f"{candidate['width']} x {candidate['height']} pixels"
    orientation = candidate["display_orientation"]
    exif_orientation = candidate["exif_orientation"] or "not set"
    megabytes = int(candidate["byte_size"]) / (1024 * 1024)
    return f"""
      <article class="candidate">
        <a href="{source}" target="_blank">
                    <img data-src="{source}" alt="Printed page capture {filename}">
        </a>
        <div class="metadata">
          <span class="filename">{filename}</span>
          <span>{dimensions}; {orientation}; EXIF orientation {exif_orientation}</span>
          <span>{megabytes:.2f} MiB</span>
          <span class="digest">SHA-256 {candidate['sha256']}</span>
        </div>
      </article>"""


def page_html(page: dict[str, object]) -> str:
    """Render one printed page and all candidate captures."""
    page_number = int(page["page_number"])
    candidates = page["candidates"]
    category = page_category(len(candidates))
    status_class = "status missing" if category == "missing" else "status"
    status = html.escape(str(page["status"]))
    reasons = ", ".join(page["review_reasons"])
    reason_text = f"; reasons: {html.escape(reasons)}" if reasons else ""

    if candidates:
        candidate_markup = "\n".join(candidate_html(item) for item in candidates)
    else:
        candidate_markup = (
            '<p class="empty">No source capture. Resolve before production OCR.</p>'
        )

    return f"""
  <section class="page" data-page="{page_number}" data-category="{category}">
    <div class="page-heading">
      <h2>Printed page {page_number:03d}</h2>
      <span class="{status_class}">{len(candidates)} capture(s); {status}{reason_text}</span>
    </div>
    <div class="candidates">
{candidate_markup}
    </div>
  </section>"""


def build_html(manifest: dict[str, object]) -> str:
    """Render the complete deterministic audit report."""
    pages = manifest["pages"]
    counts = {
        category: sum(
            page_category(len(page["candidates"])) == category for page in pages
        )
        for category in ("missing", "high-duplicate", "multi", "single")
    }
    page_markup = "\n".join(page_html(page) for page in pages)
    summary = (
        f"{manifest['page_count']} expected pages; {manifest['image_count']} images; "
        f"{counts['missing']} missing; {counts['high-duplicate']} with 3+ captures"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Scan audit report</title>
  <style>{STYLES}</style>
</head>
<body>
<header>
  <h1>Orchids of Belize scan audit</h1>
  <p class="summary">{summary}</p>
  <div class="controls" role="group" aria-label="Page filters">
    <label>Page <input id="page-search" type="search" inputmode="numeric"></label>
    <label><input type="checkbox" data-filter="missing" checked> Missing</label>
    <label><input type="checkbox" data-filter="high-duplicate" checked> 3+ captures</label>
    <label><input type="checkbox" data-filter="multi" checked> 2 captures</label>
    <label><input type="checkbox" data-filter="single" checked> 1 capture</label>
    <a href="../../manifest/pages.csv">Open review manifest</a>
  </div>
</header>
<main>
{page_markup}
</main>
<script>{SCRIPT}</script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    project_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=project_root / "manifest" / "pages.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "qa" / "reports" / "scan-audit.html",
    )
    return parser.parse_args()


def main() -> None:
    """Read the source manifest and write the visual audit report."""
    arguments = parse_args()
    manifest = json.loads(arguments.manifest.read_text(encoding="utf-8"))
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(build_html(manifest), encoding="utf-8")
    print(f"Wrote audit report to {arguments.output}")


if __name__ == "__main__":
    main()
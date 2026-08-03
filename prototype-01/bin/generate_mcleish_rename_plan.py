#!/usr/bin/env python3

import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    analysis = root / "analysis"
    input_path = analysis / "mcleish_manifest_postprocessed.json"
    plan_path = analysis / "mcleish_rename_plan.sh"

    if not input_path.exists():
        raise SystemExit(f"missing input: {input_path}")

    data = json.loads(input_path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])

    unresolved = [e for e in entries if e.get("proposed_page") is None]
    if unresolved:
        print(f"Unresolved entries: {len(unresolved)}")
        print("No rename script emitted. Resolve page numbers first.")
        return 1

    by_page: dict[int, list[dict]] = {}
    for e in entries:
        page = int(e["proposed_page"])
        by_page.setdefault(page, []).append(e)

    collisions = {p: v for p, v in by_page.items() if len(v) > 1}
    if collisions:
        print(f"Page collisions: {len(collisions)}")
        print("No rename script emitted. Multiple images map to same page.")
        return 1

    lines = [
        "#!/usr/bin/env bash",
        "set -o errexit",
        "set -o nounset",
        "set -o pipefail",
        "",
        "cd \"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")/..\" && pwd)\"",
        "",
        "# Two-phase rename to avoid overwrite issues.",
    ]

    ordered = sorted(entries, key=lambda e: int(e["proposed_page"]))
    for e in ordered:
        src = e["image"]
        page = int(e["proposed_page"])
        lines.append(f"mv -n -- \"mcleish/{src}\" \"mcleish/.tmp-{src}\"")

    lines.append("")
    for e in ordered:
        src = e["image"]
        page = int(e["proposed_page"])
        dst = f"{page:03d}.jpg"
        lines.append(f"mv -n -- \"mcleish/.tmp-{src}\" \"mcleish/{dst}\"")

    plan_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    plan_path.chmod(0o755)

    print(f"Wrote: {plan_path}")
    print(f"Planned renames: {len(ordered)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
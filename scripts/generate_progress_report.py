#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "project-system" / "progress-targets.json"
OUTPUT = ROOT / "project-system" / "generated" / "progress-report.md"

WORD_RE = re.compile(r"\b\w+(?:['’-]\w+)?\b")


@dataclass
class Entry:
    label: str
    path: Path
    bucket: str
    target_words: int


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def pct(part: int, whole: int) -> float:
    if whole <= 0:
        return 0.0
    return min(100.0, (part / whole) * 100.0)


def pages(words: int, density: int) -> float:
    return words / density if density else 0.0


def progress_bar(percent: float, width: int = 20) -> str:
    filled = int(round((percent / 100.0) * width))
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def load_config() -> tuple[list[Entry], int, int, list[int]]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    entries = [
        Entry(
            label=item["label"],
            path=ROOT / item["path"],
            bucket=item.get("bucket", "chapter"),
            target_words=int(item["targetWords"]),
        )
        for item in data["entries"]
    ]
    target_total_words = int(data.get("targetTotalWords", 40000))
    default_words_per_page = int(data.get("defaultWordsPerPage", 275))
    page_densities = [int(x) for x in data.get("pageDensities", [250, 275, 300])]
    return entries, target_total_words, default_words_per_page, page_densities


def main() -> None:
    entries, config_target_total, default_words_per_page, page_densities = load_config()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    total_words = 0
    total_target = 0

    for entry in entries:
        text = entry.path.read_text(encoding="utf-8") if entry.path.exists() else ""
        words = count_words(text)
        total_words += words
        total_target += entry.target_words
        percent = pct(words, entry.target_words)
        rows.append((entry, words, percent))

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    total_percent = pct(total_words, total_target)
    target_gap = max(0, total_target - total_words)

    lines = []
    lines.append("# Manuscript Progress Report")
    lines.append("")
    lines.append(f"_Generated: {generated_at}_")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Current manuscript words:** {total_words:,}")
    lines.append(f"- **Target manuscript words:** {total_target:,}")
    lines.append(f"- **Configured overall target:** {config_target_total:,}")
    lines.append(f"- **Estimated completion:** {total_percent:.1f}%")
    lines.append(f"- **Words remaining to target:** {target_gap:,}")
    lines.append("")
    lines.append("## Estimated Page Count")
    lines.append("")
    for density in page_densities:
        lines.append(f"- **At {density} words/page:** {pages(total_words, density):.1f} pages")
    lines.append(f"- **Default planning density:** {default_words_per_page} words/page")
    lines.append("")
    lines.append("## Overall Progress")
    lines.append("")
    lines.append(f"- `{progress_bar(total_percent)}` {total_percent:.1f}%")
    lines.append("")
    lines.append("## Chapter-by-Chapter Progress")
    lines.append("")
    lines.append("| Section | Current Words | Target Words | Completion | Progress |")
    lines.append("|---|---:|---:|---:|---|")
    for entry, words, percent in rows:
        lines.append(
            f"| {entry.label} | {words:,} | {entry.target_words:,} | {percent:.1f}% | {progress_bar(percent)} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Completion is estimated by **word count versus target word count**, not by editorial polish.")
    lines.append("- A chapter may read as conceptually complete while still being below target because examples, case material, or practical walkthroughs are still missing.")
    lines.append("- Percentages cap at 100% per section even if a chapter exceeds its target.")
    lines.append("- Targets are loaded from `project-system/progress-targets.json`.")
    lines.append("")
    lines.append("## How to Regenerate")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 scripts/generate_progress_report.py")
    lines.append("```")
    lines.append("")

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()

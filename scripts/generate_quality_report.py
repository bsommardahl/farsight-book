#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "project-system" / "quality-rubric.json"
OUTPUT = ROOT / "project-system" / "generated" / "quality-report.md"

WORD_RE = re.compile(r"\b\w+(?:['’-]\w+)?\b")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")


@dataclass
class Entry:
    label: str
    path: Path


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.findall(text) if s.strip()]


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def headings(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip().startswith("#")]


def top_repeated_phrases(words: list[str], n: int = 3, top_k: int = 5) -> list[tuple[str, int]]:
    if len(words) < n:
        return []
    grams = [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]
    counter = Counter(grams)
    filtered = [(phrase, count) for phrase, count in counter.items() if count > 1]
    filtered.sort(key=lambda x: (-x[1], x[0]))
    return filtered[:top_k]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def count_markers(text: str, markers: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(marker.lower()) for marker in markers)


def count_abstract_terms(words: list[str], abstract_terms: set[str]) -> int:
    return sum(1 for w in words if w.lower() in abstract_terms)


def lexical_diversity(words: list[str]) -> float:
    if not words:
        return 0.0
    unique = len(set(w.lower() for w in words))
    return unique / len(words)


def score_readability(avg_sentence_len: float, avg_paragraph_len: float, heading_density: float) -> float:
    sentence_score = 10 - max(0, (avg_sentence_len - 18) * 0.18)
    paragraph_score = 10 - max(0, (avg_paragraph_len - 90) * 0.025)
    heading_score = min(10, 4 + heading_density * 120)
    return round(clamp((sentence_score * 0.45) + (paragraph_score * 0.35) + (heading_score * 0.20), 1, 10), 1)


def score_intelligibility(avg_sentence_len: float, abstract_ratio: float, lexical: float, repeated_phrases_count: int) -> float:
    sentence_component = 10 - max(0, (avg_sentence_len - 20) * 0.16)
    abstract_component = 10 - max(0, (abstract_ratio - 0.06) * 90)
    lexical_component = 5 + min(5, lexical * 10)
    repetition_component = 10 - min(4, repeated_phrases_count * 0.5)
    return round(clamp((sentence_component * 0.35) + (abstract_component * 0.25) + (lexical_component * 0.25) + (repetition_component * 0.15), 1, 10), 1)


def score_impact(example_density: float, avg_sentence_len: float, heading_count: int, short_sentence_ratio: float) -> float:
    example_component = min(10, 3 + example_density * 180)
    rhythm_component = min(10, 4 + short_sentence_ratio * 14)
    structure_component = min(10, 4 + heading_count * 0.6)
    sentence_component = 10 - max(0, abs(avg_sentence_len - 18) * 0.15)
    return round(clamp((example_component * 0.35) + (rhythm_component * 0.25) + (structure_component * 0.20) + (sentence_component * 0.20), 1, 10), 1)


def score_quality(word_count: int, heading_count: int, lexical: float, repeated_phrases_count: int) -> float:
    length_component = 6 + min(4, word_count / 1200)
    structure_component = min(10, 4 + heading_count * 0.7)
    lexical_component = 5 + min(5, lexical * 10)
    repetition_component = 10 - min(4, repeated_phrases_count * 0.4)
    return round(clamp((length_component * 0.25) + (structure_component * 0.30) + (lexical_component * 0.25) + (repetition_component * 0.20), 1, 10), 1)


def score_practicality(example_markers: int, heading_count: int, abstract_ratio: float) -> float:
    example_component = min(10, 3 + example_markers * 0.9)
    structure_component = min(10, 4 + heading_count * 0.7)
    abstract_penalty_component = 10 - max(0, (abstract_ratio - 0.07) * 80)
    return round(clamp((example_component * 0.5) + (structure_component * 0.2) + (abstract_penalty_component * 0.3), 1, 10), 1)


def weighted_total(scores: dict[str, float], weights: dict[str, float]) -> float:
    total = 0.0
    for key, weight in weights.items():
        total += scores[key] * weight
    return round(total, 2)


def load_config() -> tuple[list[Entry], list[str], set[str], dict[str, float]]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    entries = [Entry(item["label"], ROOT / item["path"]) for item in data["entries"]]
    example_markers = data.get("exampleMarkers", [])
    abstract_terms = set(term.lower() for term in data.get("abstractTerms", []))
    weights = data.get("weights", {
        "readability": 0.25,
        "intelligibility": 0.25,
        "impact": 0.2,
        "quality": 0.2,
        "practicality": 0.1,
    })
    return entries, example_markers, abstract_terms, weights


def main() -> None:
    entries, example_markers, abstract_terms, weights = load_config()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    chapter_rows = []

    for entry in entries:
        text = entry.path.read_text(encoding="utf-8") if entry.path.exists() else ""
        normalized = normalize_text(text)
        words = WORD_RE.findall(text)
        word_count = len(words)
        sentences = split_sentences(text)
        paragraphs = split_paragraphs(text)
        heading_lines = headings(text)
        avg_sentence_len = word_count / len(sentences) if sentences else 0.0
        avg_paragraph_len = word_count / len(paragraphs) if paragraphs else 0.0
        heading_density = len(heading_lines) / len(paragraphs) if paragraphs else 0.0
        repeated = top_repeated_phrases([w.lower() for w in words], n=3)
        repeated_phrases_count = sum(count for _, count in repeated)
        marker_count = count_markers(normalized, example_markers)
        abstract_count = count_abstract_terms(words, abstract_terms)
        abstract_ratio = abstract_count / word_count if word_count else 0.0
        lexical = lexical_diversity(words)
        short_sentence_ratio = (
            sum(1 for s in sentences if count_words(s) <= 12) / len(sentences)
            if sentences else 0.0
        )
        example_density = marker_count / max(1, len(paragraphs))

        scores = {
            "readability": score_readability(avg_sentence_len, avg_paragraph_len, heading_density),
            "intelligibility": score_intelligibility(avg_sentence_len, abstract_ratio, lexical, repeated_phrases_count),
            "impact": score_impact(example_density, avg_sentence_len, len(heading_lines), short_sentence_ratio),
            "quality": score_quality(word_count, len(heading_lines), lexical, repeated_phrases_count),
            "practicality": score_practicality(marker_count, len(heading_lines), abstract_ratio),
        }
        total = weighted_total(scores, weights)
        chapter_rows.append({
            "label": entry.label,
            "word_count": word_count,
            "scores": scores,
            "total": total,
            "avg_sentence_len": avg_sentence_len,
            "avg_paragraph_len": avg_paragraph_len,
            "heading_count": len(heading_lines),
            "example_markers": marker_count,
            "abstract_ratio": abstract_ratio,
            "repeated": repeated,
        })

    overall = round(sum(row["total"] for row in chapter_rows) / len(chapter_rows), 2) if chapter_rows else 0.0
    strongest = sorted(chapter_rows, key=lambda r: r["total"], reverse=True)[:3]
    weakest = sorted(chapter_rows, key=lambda r: r["total"])[:3]
    most_abstract = sorted(chapter_rows, key=lambda r: r["abstract_ratio"], reverse=True)[:3]
    most_example_rich = sorted(chapter_rows, key=lambda r: r["example_markers"], reverse=True)[:3]

    lines = []
    lines.append("# Manuscript Quality Report")
    lines.append("")
    lines.append(f"_Generated: {generated_at}_")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Overall manuscript quality score:** {overall:.2f} / 10")
    lines.append("- **Scoring dimensions:** readability, intelligibility, impact, quality, practicality")
    lines.append("- **Method:** heuristic scoring from configurable rubric and text-level signals")
    lines.append("")
    lines.append("## Strongest Sections")
    lines.append("")
    for row in strongest:
        lines.append(f"- **{row['label']}** — {row['total']:.2f}/10")
    lines.append("")
    lines.append("## Weakest Sections")
    lines.append("")
    for row in weakest:
        lines.append(f"- **{row['label']}** — {row['total']:.2f}/10")
    lines.append("")
    lines.append("## Most Abstract Sections")
    lines.append("")
    for row in most_abstract:
        lines.append(f"- **{row['label']}** — {row['abstract_ratio']*100:.1f}% tracked abstract-term density")
    lines.append("")
    lines.append("## Most Example-Rich Sections")
    lines.append("")
    for row in most_example_rich:
        lines.append(f"- **{row['label']}** — {row['example_markers']} example markers")
    lines.append("")
    lines.append("## Chapter Scorecard")
    lines.append("")
    lines.append("| Section | Words | Readability | Intelligibility | Impact | Quality | Practicality | Total |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for row in chapter_rows:
        s = row["scores"]
        lines.append(
            f"| {row['label']} | {row['word_count']:,} | {s['readability']:.1f} | {s['intelligibility']:.1f} | {s['impact']:.1f} | {s['quality']:.1f} | {s['practicality']:.1f} | {row['total']:.2f} |"
        )
    lines.append("")
    lines.append("## Diagnostic Notes")
    lines.append("")
    for row in chapter_rows:
        repeated_text = ", ".join(f"`{phrase}` ({count})" for phrase, count in row["repeated"][:3]) or "none"
        lines.append(f"### {row['label']}")
        lines.append(f"- **Average sentence length:** {row['avg_sentence_len']:.1f} words")
        lines.append(f"- **Average paragraph length:** {row['avg_paragraph_len']:.1f} words")
        lines.append(f"- **Headings:** {row['heading_count']}")
        lines.append(f"- **Example markers:** {row['example_markers']}")
        lines.append(f"- **Tracked abstract-term density:** {row['abstract_ratio']*100:.1f}%")
        lines.append(f"- **Repeated phrases:** {repeated_text}")
        weakest_dimension = min(row['scores'].items(), key=lambda item: item[1])
        strongest_dimension = max(row['scores'].items(), key=lambda item: item[1])
        lines.append(f"- **Strongest dimension:** {strongest_dimension[0]} ({strongest_dimension[1]:.1f})")
        lines.append(f"- **Weakest dimension:** {weakest_dimension[0]} ({weakest_dimension[1]:.1f})")
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This report is a **diagnostic aid**, not an authoritative verdict on literary quality.")
    lines.append("- High scores may still mask weak ideas; low scores may reflect dense but valuable draft material.")
    lines.append("- The best use of this report is to identify likely weak spots, over-abstract sections, and chapters that need examples or sharper prose.")
    lines.append("- Scoring criteria and weights are configurable in `project-system/quality-rubric.json`.")
    lines.append("")
    lines.append("## How to Regenerate")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 scripts/generate_quality_report.py")
    lines.append("```")
    lines.append("")

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()

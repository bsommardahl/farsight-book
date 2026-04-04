# Manuscript Quality Report

_Generated: 2026-04-04 21:54:26 UTC_

## Summary

- **Overall manuscript quality score:** 8.71 / 10
- **Scoring dimensions:** readability, intelligibility, impact, quality, practicality
- **Method:** heuristic scoring from configurable rubric and text-level signals

## Strongest Sections

- **Sanctification** — 8.85/10
- **God Lenses** — 8.80/10
- **Near-Sighted** — 8.75/10

## Weakest Sections

- **Human Lenses** — 8.56/10
- **On Fire** — 8.66/10
- **Availability** — 8.68/10

## Most Abstract Sections

- **Salvation** — 4.7% tracked abstract-term density
- **Sanctification** — 2.8% tracked abstract-term density
- **Near-Sighted** — 1.8% tracked abstract-term density

## Most Example-Rich Sections

- **God Lenses** — 2 example markers
- **Sanctification** — 2 example markers
- **Near-Sighted** — 1 example markers

## Chapter Scorecard

| Section | Words | Readability | Intelligibility | Impact | Quality | Practicality | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Near-Sighted | 2,021 | 10.0 | 9.0 | 8.3 | 8.2 | 7.0 | 8.75 |
| On Fire | 2,582 | 10.0 | 8.9 | 8.0 | 8.2 | 7.0 | 8.66 |
| Availability | 2,594 | 10.0 | 8.9 | 8.1 | 8.2 | 7.0 | 8.68 |
| God Lenses | 2,875 | 10.0 | 8.9 | 8.4 | 8.3 | 7.4 | 8.80 |
| Human Lenses | 2,375 | 10.0 | 9.0 | 7.5 | 8.3 | 6.5 | 8.56 |
| Salvation | 2,339 | 10.0 | 8.9 | 8.2 | 8.1 | 7.0 | 8.68 |
| Sanctification | 2,360 | 10.0 | 9.0 | 8.5 | 8.3 | 7.4 | 8.85 |

## Diagnostic Notes

### Near-Sighted
- **Average sentence length:** 14.1 words
- **Average paragraph length:** 26.6 words
- **Headings:** 17
- **Example markers:** 1
- **Tracked abstract-term density:** 1.8%
- **Repeated phrases:** `distorts our understanding` (6), `it distorts our` (6), `our understanding of` (6)
- **Strongest dimension:** readability (10.0)
- **Weakest dimension:** practicality (7.0)

### On Fire
- **Average sentence length:** 15.4 words
- **Average paragraph length:** 22.5 words
- **Headings:** 64
- **Example markers:** 1
- **Tracked abstract-term density:** 1.6%
- **Repeated phrases:** `ideas to include` (8), `a moment of` (7), `which is better` (6)
- **Strongest dimension:** readability (10.0)
- **Weakest dimension:** practicality (7.0)

### Availability
- **Average sentence length:** 17.5 words
- **Average paragraph length:** 21.4 words
- **Headings:** 76
- **Example markers:** 1
- **Tracked abstract-term density:** 1.7%
- **Repeated phrases:** `ideas to include` (10), `a b contrast` (9), `b contrast which` (9)
- **Strongest dimension:** readability (10.0)
- **Weakest dimension:** practicality (7.0)

### God Lenses
- **Average sentence length:** 11.5 words
- **Average paragraph length:** 24.4 words
- **Headings:** 21
- **Example markers:** 2
- **Tracked abstract-term density:** 1.1%
- **Repeated phrases:** `than we do` (11), `he is not` (8), `he knows what` (7)
- **Strongest dimension:** readability (10.0)
- **Weakest dimension:** practicality (7.4)

### Human Lenses
- **Average sentence length:** 16.5 words
- **Average paragraph length:** 22.2 words
- **Headings:** 66
- **Example markers:** 0
- **Tracked abstract-term density:** 1.1%
- **Repeated phrases:** `ideas to include` (8), `lines source ideas` (8), `useful lines source` (8)
- **Strongest dimension:** readability (10.0)
- **Weakest dimension:** practicality (6.5)

### Salvation
- **Average sentence length:** 17.2 words
- **Average paragraph length:** 23.4 words
- **Headings:** 63
- **Example markers:** 1
- **Tracked abstract-term density:** 4.7%
- **Repeated phrases:** `ideas to include` (8), `is not the` (8), `salvation is not` (8)
- **Strongest dimension:** readability (10.0)
- **Weakest dimension:** practicality (7.0)

### Sanctification
- **Average sentence length:** 11.6 words
- **Average paragraph length:** 21.1 words
- **Headings:** 24
- **Example markers:** 2
- **Tracked abstract-term density:** 2.8%
- **Repeated phrases:** `we begin to` (8), `we should become` (7), `sanctification is not` (6)
- **Strongest dimension:** readability (10.0)
- **Weakest dimension:** practicality (7.4)

## Notes

- This report is a **diagnostic aid**, not an authoritative verdict on literary quality.
- High scores may still mask weak ideas; low scores may reflect dense but valuable draft material.
- The best use of this report is to identify likely weak spots, over-abstract sections, and chapters that need examples or sharper prose.
- Scoring criteria and weights are configurable in `project-system/quality-rubric.json`.

## How to Regenerate

```bash
python3 scripts/generate_quality_report.py
```


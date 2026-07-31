# Output formats

Use the configured language. Keep source titles in their original language when possible.

## Daily knowledge card

Aim for a 3-5 minute direct read. Do not begin with a quiz.

```markdown
# [今天的边界 / Today's Boundary] · [Title]

**领域 / Domain:** [primary] · [secondary]
**模式 / Mode:** [Boundary/Wander]

## 核心知识 / Core idea
[Explain the central fact, mechanism, person, event, or concept in plain language.]

## 为什么值得知道 / Why it matters
[Show which common assumption or mental model this improves.]

## 向外连接 / Zoom out
[Connect it meaningfully to another domain, era, culture, or present-day system.]

## 可信度 / Confidence
[High/Medium plus uncertainty, disagreement, or date sensitivity.]

## 来源 / Sources
- [Original source title](URL) — why it supports the card
- [Original source title](URL) — why it supports the card

**下一步 / Next:** 已知道 / 新知识 / 深入了解 / 暂时跳过
```

Avoid clickbait, fake quotations, inflated claims, unexplained jargon, and long lists of loosely related facts.

## Structured source metadata

Every card and brief must provide a UTF-8 JSON array to `state.py`. Each source object requires:

```json
{
  "title": "Original source title",
  "url": "https://...",
  "kind": "primary",
  "publisher": "Independent publisher or institution",
  "supports": "The specific claim or evidence this source supports"
}
```

Allowed `kind` values are `primary`, `academic`, `review`, `authoritative`, `expert`, and `journalism`. URLs and publishers must be distinct. A daily card requires at least two sources; a research brief requires at least three.

## Small research brief

Always use this format after the user chooses `Deep dive`/`深入了解`. A deep-dive response is a research brief, never a full report. Its scope is one central question derived from the card; reading time is a consequence of that scope, not the definition of quality.

```markdown
# [Topic] — Research Brief

## Research question
## Executive answer
## Background and definitions
## What the strongest evidence shows
## What remains disputed or unknown
## Cross-domain implications
## What this changes from the original card
## References

**Next:** Enough / Continue to full report
```

Adapt the middle sections to the subject. For academic, medical, financial, legal, historical, or contested material, include every domain-specific item required by `source-policy.md`.

Every brief must pass all eight checks:

1. State one central question at the beginning.
2. Give the direct answer before the detailed explanation.
3. Explain the strongest evidence and why it is credible.
4. Use at least three strong, genuinely independent sources.
5. Place links next to the important claims they support.
6. State material uncertainty, disagreement, or missing evidence.
7. Include only the background needed to answer the question; do not turn the brief into an encyclopedia entry.
8. End by explaining how the deeper evidence changes, qualifies, or extends the original card.

## Full research report

Generate only after an explicit request for a complete/full report. Establish a specific research question before researching. If the user's question is already clear, use it; otherwise ask for it. Do not generate a full report by merely expanding the card title.

The final deliverable must be a polished PDF. Use the following as the report's content structure, not as a raw Markdown deliverable:

1. Title and specific research question
2. Executive summary
3. Scope and source-selection method
4. Necessary background
5. Main findings
6. Competing interpretations or counter-evidence
7. Cross-domain synthesis
8. Limitations and open questions
9. Practical implications (educational, not personal advice)
10. Complete bibliography
11. Methodology appendix

Verify every material claim and citation before delivery. State assumptions explicitly.

Write the report input as UTF-8 JSON:

```json
{
  "title": "...",
  "question": "...",
  "language": "zh",
  "generated_at": "YYYY-MM-DD",
  "summary": "...",
  "sections": [
    {
      "heading": "...",
      "paragraphs": ["..."],
      "bullets": ["..."]
    }
  ],
  "references": [
    {
      "title": "...",
      "url": "https://...",
      "publisher": "..."
    }
  ]
}
```

Use numbered citations such as `[1]` in section paragraphs and keep their numbering aligned with `references`.

### PDF delivery and visual quality

- Save the final file as `Reports/<filesystem-safe-title>.pdf` inside the user-approved Boundary root. Do not deliver raw Markdown in place of the PDF.
- Use an A4 page design with a restrained visual system: readable body type, clear heading hierarchy, consistent margins and spacing, balanced whitespace, and a limited color palette.
- Include a designed title page with the title, research question, generation date, and Boundary label. Add a table of contents when the report has enough sections to benefit from one.
- Use fonts that fully support the report language. Chinese and English text must render without missing glyphs, black squares, or unintended font substitutions.
- Add consistent page numbers and unobtrusive headers or footers. Keep headings with the paragraphs they introduce and avoid nearly empty pages.
- Place citations next to the claims they support. Make links readable and, when supported, clickable. The bibliography must include usable URLs, DOIs, or stable identifiers.
- Keep tables, charts, diagrams, and images sharp, aligned, labeled, and legible at normal viewing size. Every visual must contribute to the research question.
- Render every PDF page to an image and inspect the entire document. Correct clipped text, overlaps, broken tables, awkward page breaks, inconsistent spacing, unreadable citations, and other visual defects before delivery.
- Deliver only after both content verification and the complete visual inspection pass.

## Examples of good framing

- Do not stop at “Mount Tai was used for feng and shan rites.” Explain how sacred geography, imperial legitimacy, and political order became connected.
- Do not reduce the DNA story to two discoverers. Explain the evidence chain, model building, and contributions such as Rosalind Franklin's and Maurice Wilkins's X-ray work without replacing one simplistic hero story with another.
- Do not report a stock's daily move as knowledge. Explain a durable mechanism such as market making, liquidity, or the difference between nominal and real returns, with dated sources.

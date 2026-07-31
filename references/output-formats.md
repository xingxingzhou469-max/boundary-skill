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

Every card and deep research report must provide a UTF-8 JSON array to `state.py`. Each source object requires:

```json
{
  "title": "Original source title",
  "url": "https://...",
  "kind": "primary",
  "publisher": "Independent publisher or institution",
  "supports": "The specific claim or evidence this source supports"
}
```

Allowed `kind` values are `primary`, `academic`, `review`, `authoritative`, `expert`, and `journalism`. URLs and publishers must be distinct. A daily card requires at least two sources; a deep research report requires at least three.

## Deep research report

Always use this level after the user chooses `Deep dive`/`深入了解`. A deep-dive response is one complete, in-depth research report — it is the final depth level and is never followed by another "choose your depth" step. Its depth should match what a full research report would deliver, but written for a curious reader rather than an academic audience.

The report answers one central question derived from the card. The question must be specific; never expand a card title into a report without a research question.

```markdown
# [Topic] — 深度研究报告 / Deep Research Report

## 研究问题 / Research question
## 直接答案 / Executive answer
## 背景与定义 / Background and definitions
## 最强证据说明了什么 / What the strongest evidence shows
## 争议与未知 / What remains disputed or unknown
## 跨领域连接 / Cross-domain implications
## 这如何改变原卡片 / What this changes from the original card
## 完整参考来源 / References

**下一步 / Next:** 已知道 / 足够了
```

### Depth and readability

- **Depth:** cover background, the strongest evidence and why it is credible, competing interpretations, limitations, cross-domain implications, and the full reference list. Be comprehensive, not a summary.
- **Readability:** write in plain, direct language. Explain specialized terms on first use; prefer concrete examples over abstract phrasing. The report should read like a long-form explainer, not a journal article or a dry literature review.
- **Length:** as long as the research question requires. There is no upper cap; a genuinely deep question may need several thousand words.
- Use at least three strong, genuinely independent sources, with more when the question demands it. Place links next to the important claims they support.
- Keep the numbered structure above; adapt the middle sections to the subject. For academic, medical, financial, legal, historical, or contested material, include every domain-specific item required by `source-policy.md`.

### Quality checks (all must pass)

1. State one central research question at the beginning.
2. Give the direct answer before the detailed explanation.
3. Explain the strongest evidence and why it is credible.
4. Use at least three strong, genuinely independent sources.
5. Place links next to the important claims they support.
6. State material uncertainty, disagreement, or missing evidence.
7. Include only the background needed to answer the question; do not pad with an encyclopedia entry.
8. Explain how the deeper evidence changes, qualifies, or extends the original card.
9. Readable without the card: a reader who has never seen the card can follow the report alone.
10. Plain language: no unexplained jargon, no academic hedging for its own sake.

## Examples of good framing

- Do not stop at "Mount Tai was used for feng and shan rites." Explain how sacred geography, imperial legitimacy, and political order became connected.
- Do not reduce the DNA story to two discoverers. Explain the evidence chain, model building, and contributions such as Rosalind Franklin's and Maurice Wilkins's X-ray work without replacing one simplistic hero story with another.
- Do not report a stock's daily move as knowledge. Explain a durable mechanism such as market making, liquidity, or the difference between nominal and real returns, with dated sources.

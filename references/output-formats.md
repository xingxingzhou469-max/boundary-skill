# Output formats

Use the configured language. Keep source titles in their original language when possible. Apply the shared [quality standard](quality-rubric.md); the formats below express it for locally saved artifacts.

## Daily knowledge card

Aim for a 3–5 minute direct read. Do not begin with a quiz. Choose headings in the output language; the bilingual labels below describe alternatives, not literal combined headings. State the same central question passed to `record --question`, and place source links next to the important claims as well as in the source list.

```markdown
# [今天的边界 / Today's Boundary] · [Title]

**核心问题 / Question:** [one specific explanatory question]
**领域 / Domain:** [primary] · [secondary]
**模式 / Mode:** [Boundary/Wander]

## 核心知识 / Core idea
[Explain the central fact, mechanism, person, event, or concept in plain language.]

## 为什么值得知道 / Why it matters
[Name the reusable idea or concrete decision this improves, and state one implication for understanding or action. Do not justify the topic only by saying it is rare, surprising, or culturally distant.]

## 一个具体例子 / A concrete example
[Show how the mechanism works; label hypothetical numbers or situations. This may be integrated into Core idea when clearer.]

## 带走一个用法 / One usable takeaway
[A diagnostic question, comparison, or low-stakes observation; no compulsory exercise or personalized professional advice.]

## 适用边界 / Where it stops applying
[One meaningful limitation or counterexample.]

## 向外连接 / Zoom out
[Connect it meaningfully to another domain, era, culture, or present-day system.]

## 可信度 / Confidence
[High/Medium plus uncertainty, disagreement, or date sensitivity.]

## 来源 / Sources
- [Original source title](URL) — why it supports the card
- [Original source title](URL) — why it supports the card

**下一步 / Next:** [已知道 / 新知识 / 深入了解 / 暂时跳过 OR Known / New / Deep dive / Skip]
```

Before delivery, check:

- The topic is worth knowing even if it is not obscure.
- Its main payload is a concept, mechanism, institution, consensus, or consequential context—not an isolated fact.
- `Why it matters` gives a concrete, transferable implication.
- It takes one manageable step beyond demonstrated coverage; do not jump into specialist detail merely to appear novel.

Avoid clickbait, fake quotations, inflated claims, unexplained jargon, and long lists of loosely related facts.

## Structured source metadata

Every card and deep research report must provide a UTF-8 JSON array to `state.py`. Each source object requires:

```json
{
  "title": "Original source title",
  "url": "https://...",
  "kind": "primary",
  "publisher": "Independent publisher or institution",
  "supports": "The specific claim or evidence this source supports",
  "accessed_at": "2026-10-05"
}
```

Allowed `kind` values are `primary`, `academic`, `review`, `authoritative`, `expert`, and `journalism`. URLs must be unique. A daily card requires at least two distinct independent publishers; a report requires at least three. Additional sources may come from those same publishers. `accessed_at` and `published_at` are optional ISO dates (`YYYY-MM-DD`), retained by the script when supplied; record the actual access date for each researched source. Do not invent a publication date when none is stated. Counting publisher labels is only a structural check: the agent must still verify independence and actual support.

## Deep research report

Always use this level after the user chooses `Deep dive`/`深入了解`. A deep-dive response is one complete, in-depth research report — it is the final depth level and is never followed by another "choose your depth" step. Its depth should match what a full research report would deliver, but written for a curious reader rather than an academic audience.

The report answers the stored central question from the card unless the user explicitly changes it. Do not ask the user to restate the question when they select Deep dive.

```markdown
# [Topic] — 深度研究报告 / Deep Research Report

## 研究问题 / Research question
## 直接答案 / Executive answer
## 背景与定义 / Background and definitions
## 最强证据说明了什么 / What the strongest evidence shows
## 争议与未知 / What remains disputed or unknown
## 如何运用与适用边界 / Application and limits
## 跨领域连接 / Cross-domain implications
## 这如何改变原卡片 / What this changes from the original card
## 完整参考来源 / References

```

### Depth and readability

- **Depth:** cover background, the strongest evidence and why it is credible, competing interpretations, limitations, cross-domain implications, and the full reference list. Be comprehensive, not a summary.
- **Readability:** write in plain, direct language. Explain specialized terms on first use; prefer concrete examples over abstract phrasing. The report should read like a long-form explainer, not a journal article or a dry literature review.
- **Length:** as long as the research question requires. There is no upper cap; a genuinely deep question may need several thousand words.
- Use at least three strong, genuinely independent sources, with more when the question demands it. Place links next to the important claims they support.
- Keep the section structure above; adapt the middle sections to the subject. For academic, medical, financial, legal, historical, or contested material, include every domain-specific item required by `source-policy.md`.

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

## Worked examples

See [English card](../examples/card.en.md), [中文知识卡](../examples/card.zh-CN.md), and [full English report](../examples/report.en.md). These are dated, curated examples, not a topic bank; never reuse them as a new daily card without fresh research and history checks.

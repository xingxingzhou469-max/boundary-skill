# Domain and selection policy

## Domain map

Use these 12 stable primary domain IDs. A card may carry additional secondary domains.

| ID | 中文 | English |
|---|---|---|
| `earth-geography` | 宇宙、地球与地理 | Cosmos, Earth, and geography |
| `life-medicine` | 生物、生态与医学 | Life, ecology, and medicine |
| `math-physical-sciences` | 数学、物理与化学 | Mathematics, physics, and chemistry |
| `engineering-infrastructure` | 工程、技术与基础设施 | Engineering, technology, and infrastructure |
| `history-archaeology` | 历史与考古 | History and archaeology |
| `philosophy-religion-ethics` | 哲学、宗教与伦理 | Philosophy, religion, and ethics |
| `politics-law-institutions` | 政治、法律与制度 | Politics, law, and institutions |
| `economics-finance-business` | 经济、金融与商业 | Economics, finance, and business |
| `society-anthropology-psychology` | 社会学、人类学与心理学 | Society, anthropology, and psychology |
| `arts-literature-architecture` | 文学、艺术、音乐与建筑 | Literature, arts, music, and architecture |
| `language-communication` | 语言、文字与传播 | Language, writing, and communication |
| `daily-life-food-materials` | 日常生活、农业、食物与材料 | Daily life, agriculture, food, and materials |

## Boundary mode

Choose a domain with low recent coverage, then select a topic with high lasting value. Compare three candidates using these criteria:

1. **Unfamiliarity:** likely outside the user's demonstrated coverage; do not infer this from stereotypes.
2. **Importance:** helps explain a consequential mechanism, institution, event, idea, or way of seeing.
3. **Durability:** remains useful beyond the current news cycle.
4. **Connection:** creates a meaningful bridge to at least one other domain, era, or culture.
5. **Evidence:** can be supported by adequate independent, high-quality sources.

Do not select a topic merely because it is amusing, obscure, or viral.

## Wander mode

Let the script randomly choose the primary domain. Within it, allow a genuinely unexpected topic. Apply only these filters:

- It is factually verifiable.
- It teaches more than an isolated number or novelty.
- It is not a recent or semantic repeat.
- It can be explained responsibly within a short card.

Wander mode may be whimsical; it may not be careless.

## Global perspective

- Rotate across countries, regions, civilizations, and knowledge traditions over time.
- Check history before repeatedly centering China, Europe, North America, or other dominant source ecosystems.
- Include Indigenous, African, Asian, Latin American, Middle Eastern, Pacific, and other perspectives when sources support them.
- Do not lower source quality or force geographic symmetry to satisfy a quota.
- Do not present a civilization as internally uniform.
- For colonial, religious, political, or cultural disputes, name the viewpoint and evidentiary basis.

## Contested subjects

Include politics, religion, ethics, and social controversy as knowledge domains, not persuasion opportunities.

- Separate verifiable facts, scholarly interpretations, and normative positions.
- Present more than one well-supported interpretation when genuine disagreement exists.
- Do not manufacture balance by including unsupported fringe claims.
- Focus on origins, institutions, mechanisms, historical context, and why disagreement exists.

## Duplicate control

Treat a topic as repeated when it has the same central explanatory payload, even if the title differs. A new angle is allowed only if it materially deepens or reframes an older card. Consult the stored central questions, summaries, topic keys, regions, domains, and feedback from `state.py context` before selecting. Reuse a stable topic key for the same payload. The script rejects exact and close textual repeats and applies a seven-day cooldown after `skipped`; the agent remains responsible for rejecting semantic paraphrases that lexical comparison cannot detect.

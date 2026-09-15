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

## Selection objective

Boundary mode seeks important ideas just beyond the user's demonstrated coverage, not the most distant or obscure topic available. A good card usually does at least one of the following:

- teaches a field's foundational concept, core mechanism, or broadly supported consensus;
- explains an institution, system, or historical process that shapes real decisions and society;
- provides a reusable mental model that transfers across problems;
- corrects a consequential misconception;
- explains a meaningful everyday mechanism that improves practical judgment.

A case study, cultural tradition, place, person, or historical episode is appropriate when it makes one of those larger ideas easier to understand. It is not sufficient that the subject is unusual, geographically distant, or rarely discussed.

Familiarity is uncertain unless the user has stated it directly or demonstrated it in the current context or Boundary history. Do not infer it from demographics or stereotypes, and do not inspect unrelated conversations. When familiarity is uncertain, prefer a canonical concept over a niche topic. Aim for one manageable conceptual step beyond the user's current coverage, not a jump into specialist detail.

## Boundary mode

Choose the highest-value candidate that passes the quality gate below. Recent domain coverage is only a mild diversity prior; it must never override topic quality or force equal rotation across all 12 domains.

Compare three candidates in this order:

1. **Importance and transferability:** Will learning this improve understanding, reasoning, or a real decision beyond this one example?
2. **Field centrality or consensus:** Is it foundational, canonical, widely supported, or central to understanding the field?
3. **Consequence and relevance:** Does it help explain an important part of society, work, learning, health, technology, culture, or everyday life?
4. **Durability:** Will it remain useful beyond a news cycle or a single conversation?
5. **Unfamiliarity:** Is it plausibly outside the user's demonstrated coverage? This is a discovery signal, not a reason to prefer obscurity.
6. **Connection:** Does it create a genuine bridge to another domain, era, culture, or present-day system?
7. **Evidence:** Can the central claims be supported by the required independent, high-quality sources? Evidence is a hard gate, not a novelty score.

For each candidate, write a private one-line justification covering what it unlocks, why it may be unfamiliar, and what concrete understanding or judgment it improves. Select the candidate with the strongest value and transferability. Use unfamiliarity and cross-domain distance only to break close ties.

Reject a candidate when:

- its main appeal is that it is rare, amusing, surprising, viral, or culturally distant;
- it is mostly an isolated number, name, artifact, place, or anecdote with no reusable idea;
- its importance can be stated only as “most people do not know this”;
- the card would need specialist detail to make the topic seem substantial;
- no reliable source supports the central claim;
- a more foundational or consequential candidate is available.

If no candidate clears the importance floor, do not fill the slot. Pick another domain or generate a new candidate set.

## Wander mode

Wander mode is optional random exploration, not the default meaning of Boundary. It may begin with a randomly selected domain or an unexpected connection, but it must still pass a minimum value floor:

- it teaches a mechanism, concept, important context, or meaningful human practice;
- it offers more than an isolated fact or novelty;
- it can be explained responsibly in a short card;
- it is factually verifiable and not a recent or semantic repeat.

Randomness chooses where to look, not whether a topic is worth knowing. If a random candidate is merely odd or decorative, reject it and try again.

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

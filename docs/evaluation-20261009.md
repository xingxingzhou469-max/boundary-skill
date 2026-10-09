# Question coverage and source reconciliation: 2026-10-09

The [previous seven-generation test](evaluation-20261008.md) found a concrete failure: the stainless-steel question promised to explain welding, but the delivered body omitted it. This follow-up changes the shared writing standard and checks real generated cards. It does not certify general factual accuracy or scheduled delivery.

## Changes

- Treat every clause of the central question as a promise. Explain it with support, or disclose the specific gap. Use the shortest complete explanation rather than expanding a daily card into a report.
- Retain the opened item's original title, responsible organization, identifier, access level and supporting passage. Put named direct links by central claims when available; reconcile the finished body, reference list and local source JSON before recording.
- Give the main text an editing guide of about 1,000–1,800 Chinese characters or 500–800 English words, excluding references. This is neither measured reading time nor a replacement for completeness.
- Require a concrete comparison with another field or system, label analogies, and check illustrative quantities separately from measured results.

These rules live in the existing shared quality rubric. The four English/Chinese ChatGPT setup/runtime artifacts are regenerated from it. The local `SKILL.md` adds a read-back of the draft and JSON before `record`. No product Python, state schema, tests or evaluation inputs changed in this follow-up.

## Test method and preserved attempts

The fixed catalog remains `boundary-fixed-2026-10-07-v1`, SHA-256 `f5846d2d48a6335751f4dd5c87c707acbfddb93c0d9b16638ec4ce7ca60d94ec`. Its Chinese arts and English bread prompts were used verbatim. A separate stainless-steel question was replayed in Chinese and English. The full 24-card catalog was **not rerun**.

There were 12 real deliveries across five instruction revisions: four Chinese stainless-steel replays in the same existing ChatGPT conversation and eight native Agent cards. Native batches contained three, three and two cases; each batch used a fresh Agent context, while cases within a batch shared that context and used separate configurations and empty local libraries. Generation prompts did not include the frozen checks, reviewers' findings or previous native outputs. Chinese replays intentionally retained the existing conversation, so they are not independent fresh-context trials. A separate reviewer Agent worked across attempts; reviews were not blinded fresh sessions. Frozen case checks stayed unchanged while the shared editorial standard evolved, so this is a repair record rather than a controlled benchmark.

Original bodies, message/record identifiers, source files, state and hashes were preserved before independent review. Eleven deliveries received that review; the second Chinese replay was an intermediate diagnostic capture with review **NOT RUN**. Failed outputs were not edited into successes. Five source snapshots were checked against their exact Git commits. The eight local delivered bodies matched their pending files, and saved source metadata matched the original JSON.

| Revision | Commit | Deliveries and review |
|---|---|---|
| A | `5fd54a9` | Chinese stainless: FAIL for reading burden; English stainless: FAIL for source correspondence and a weak cross-domain connection; arts and bread: PASS within recorded checks. |
| B | `cc6eebf` | English stainless: FAIL for its same-topic connection, while coverage and source correspondence passed; arts and bread: PASS. Chinese stainless: diagnostic capture, review NOT RUN. |
| C | `c84b55a` | Chinese stainless: FAIL; a specific welding-risk claim lacked a matching listed source, and an illustrative percentage was insufficiently labeled. |
| D | `723e0b9` | English stainless and bread: PASS within recorded checks, with concrete labeled cross-domain comparisons. |
| E | `4315525` | Chinese stainless: PASS for the checked central mechanisms and coverage, with the secondary citation and illustrative-number limitations below. |

The initial English stainless card had a fifth body URL absent from both its source list and JSON. Later English replays reconciled all three. The missing page actually supported the weld-geometry point: the established failure was missing source correspondence, not proof that the statement itself was scientifically false. Original peer judgments and the main reviewer's calibration are retained separately.

Native citation markers in the Chinese cards were genuine platform markers whose hidden target mapping was unavailable. That limitation alone does not establish fabrication. The later Chinese replay provides named direct links, and replaces the insufficiently supported modern-grade welding claim with a narrower low-carbon-grade explanation.

## Latest case observations

These are the latest observed versions of four cases, generated at different commits and hosts. They are not four generations at the final source commit, an accuracy percentage, or a controlled causal estimate of the instruction changes.

| Case | Evidence commit / host | Latest result | Checked behavior and limits |
|---|---|---|---|
| Stainless steel, Chinese | `4315525` / existing ChatGPT conversation | PASS within checked scope | Passivation, salt, crevices and three welding paths supported; four visible source identities verified. A secondary film-composition boundary sentence lacks support in the listed four sources; the labeled analogy's 30%/100% values would be clearer if explicitly marked hypothetical. |
| Stainless steel, English | `723e0b9` / native Agent | PASS | All question clauses supported; five body source identifiers match the list and JSON; building-envelope comparison explicitly labeled. |
| Negative space in visual art, Chinese | `cc6eebf` / native Agent | PASS | Named museum artwork and bounded interpretation; auxiliary eye-tracking evidence disclosed as abstract-only and not a direct experiment on blank-space area. |
| Bread firming and reheating, English | `723e0b9` / native Agent | PASS | Storage and partial reheating distinguished; method-specific results retained, with no universal household recipe. One review was accessible only as an abstract. |

Chinese main-text length went from approximately 2,836 Han characters in A to 1,143 in E, while retaining explanations of salt, crevices and welding. This local count excludes the confidence/reference section and includes Chinese headings. No reader timing was performed.

## Verification boundaries

Repository and generated-prompt checks pass. A fresh local 25-test run passed after the first instruction revision; Python and test files did not change afterward. Final commit CI and installed-artifact verification are tracked separately in the delivery record.

The Skill creator's `quick_validate.py` rejects the existing `compatibility` frontmatter field. The same rejection was reproduced on the untouched baseline. It is an existing validator/schema incompatibility, not a successful validation or an error introduced by this revision; the repository's own metadata check passes.

Requested native generator/reviewer configuration was `gpt-6-luna / max`; effective model identities remain **UNKNOWN**. The ChatGPT reading interface did not expose generation-time source-opening traces or native citation-target mappings. Independent source reopening supports review findings, not proof of the generation host's source access. Some source access was limited to abstracts or locally extracted PDF text, as recorded per case. An unrelated navigation anomaly on BSSA pages was ignored and technical claims cross-checked; its cause was not established.

The Chinese ChatGPT output does not provide a local structured source array; only visible body/reference URLs can be reconciled there. No local JSON was fabricated to fill that gap. Its reviewer-only film study was not retroactively added to the card's source list, and the original wording remains intact. A case PASS therefore does not mean every secondary sentence or hidden citation target was verified.

The installed Skill and generated templates are updated through the delivery process. The existing daily ChatGPT task's saved instructions, schedule, timezone and notifications were not changed. Runtime rules were supplied only for the authorized manual replays. No new task or calendar follow-up was created, and manual deliveries are not presented as scheduled runs. Private account identifiers and transcripts stay outside the repository.

## 中文说明

本轮针对“问题承诺与正文覆盖一致”和“来源可核验”做了共享规则改进，同时缩短冗余解释、明确跨领域类比。12次真实生成均保留原稿；整套24张固定题库没有重跑。最新各案例的结果按实际生成版本列出，模型溯源、原始工具追踪和真人阅读时间仍未核验。现有每日云任务的已保存指令没有自动替换。

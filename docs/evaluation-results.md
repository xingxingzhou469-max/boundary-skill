# Content review — 2026-10-06 / 生成质量检查

This is a redacted record of seven native Codex Agent trials: **three baseline cases, three first-revision cases, and one final science trial**. Each generated a Chinese card and, after a separate “深入了解” request, a report. These fourteen outputs are observed samples, not a statistical quality benchmark or acceptance of real ChatGPT scheduled delivery.

## Reproduction scope

| Stage | Pinned Boundary commit | Cases |
|---|---|---|
| Baseline | [`a68b5a8`](https://github.com/xingxingzhou469-max/boundary-skill/commit/a68b5a81548bb2872356cd09c5d101c60a5fe64a) | Free discovery; bread staling/reheating; medieval European guilds |
| First revision | [`1542090`](https://github.com/xingxingzhou469-max/boundary-skill/commit/15420908579737c07ce6161eb62c3d115841b543) | Same three user requests, fresh Agents |
| Final revision | [`223d889`](https://github.com/xingxingzhou469-max/boundary-skill/commit/223d8897f647b49843ce958609b17147fe17e10d) | Same bread request, another fresh Agent |

The final revision was merged through [PR #5](https://github.com/xingxingzhou469-max/boundary-skill/pull/5) as [`9d57e63`](https://github.com/xingxingzhou469-max/boundary-skill/commit/9d57e6382feb401cd06abbab5e7e8d9497fdfaf1), with an identical file tree.

Inputs, each followed by “深入了解”:

```text
给我今天的知识边界。
今天想知道：面包放久了为什么会变硬，而再加热后有时又会变软？给我一张知识卡。
中世纪欧洲为什么会出现行会？它们既保障质量，又可能限制竞争，这该怎么理解？给我一张知识卡。
```

Every generator downloaded its pinned version, inspected the scripts, and ran repository validation, generated-prompt checking, and the curated demo before using only `integrations/chatgpt/instructions.zh-CN.txt` for content behavior. Those scripts do not generate or fact-check new research. Agents then searched and opened sources using the available research tools. No additional model API was called.

The requested configuration was `gpt-6-luna / max`; the effective runtime model identifier was not exposed and is **UNKNOWN**. Each revision used fresh conversation history and the same user input. Generators did not receive earlier outputs, suspected errors, or reviewer corrections. Free discovery selected different topics; even fixed questions used some different studies. Source access also varied, so these are not controlled measurements of a model or percentage improvement.

Final outputs after normal self-review, source-access records, and file hashes were retained locally. An independent reviewing Agent reopened original materials, and the primary Agent checked key calculations, records, and original tables. No failed final output was rewritten to manufacture a pass. An earlier science draft was reconstructed separately after the generator's own correction; it was not counted as the final baseline output.

## Observed results

| Case | Supported behavior | Problems or limits retained |
|---|---|---|
| Baseline discovery: multiple comparisons | Correct probability calculation and assumptions; report added useful distinctions | Card citations only in the footer; nonbinding guidance described too strongly |
| Baseline bread | Useful starch/water explanation and deeper experimental discussion | A body source missing from card references; some experimental conditions generalized into practical advice |
| Baseline guilds | Useful local records and competing historical interpretations | Different legal objects/rules combined; an unsupported “same mark” inference; footer-only card citations and an omitted report reference |
| First-revision discovery: map projections | Supported local-scale calculation, projection trade-offs, navigation distinctions | No material factual or calculation error identified in the reviewed claims; a different topic from baseline |
| First-revision guilds | Clearer separation of rules, places, and evidence; complete body/reference correspondence | Apprenticeship wording too absolute; theft-response wording should be narrower |
| First-revision bread | Supported numerical results; experimental heating explicitly separated from household instructions | An unconditional claim about water contradicted steam evidence; an inaccurate denial of structural measurement |
| Final bread | Supported core mechanisms, thermal ranges, microwave explanation, and bibliography; the preceding blanket assertions were absent | Early-firming inference still needed narrowing; the 96-hour result needed room-temperature, unwrapped, post-baking conditions |

Every body source in the six first-revision outputs and two final-revision outputs appeared in its reference list. This checks link identity, not whether every sentence is true. Reports added methods, comparisons, or applicability limits rather than merely expanding the cards.

## Evidence behind the remaining issues

- [Baik and Chinachoti (2000)](https://onlinelibrary.wiley.com/doi/10.1094/CCHEM.2000.77.4.484) report early firming in sealed bread but do not establish its specific cause. The final card should separate that observation from the general starch mechanism supported by other research.
- [Novotni et al. (2013)](https://academic.oup.com/ijfst/article/48/10/2133/7865853) describe the approximately fourfold firming after final baking and 96 hours **unwrapped at room temperature**. The final report's number is supported, but those conditions should accompany it.
- The first-revision water claim was too broad because [Rogers et al. (1990)](https://www.cerealsgrains.org/publications/cc/backissues/1990/Documents/67_188.pdf) include steam treatment that increases moisture. [Pisesookbuntern et al. (1983)](https://www.cerealsgrains.org/publications/cc/backissues/1983/Documents/Chem60_301.pdf) also measured starch structure by X-ray diffraction; this is structural evidence, even though it does not track individual chains in real time.

The shared standard was strengthened to preserve claim scope, check practical takeaways, reconcile citations, and challenge categorical lead answers with researched counterexamples. These rules guide behavior; the trials show that self-review can still miss precision issues. More caveats, more links, or a longer prompt alone do not certify accuracy.

## Acceptance boundary

- The reviewed code tree passed all six Linux/macOS/Windows, Python 3.10/3.14 [main CI jobs](https://github.com/xingxingzhou469-max/boundary-skill/actions/runs/37473909804). The suite covers local structure and lifecycle, not factual truth.
- Real ChatGPT task creation, saved-instruction isolation, a scheduled first run, and continuous multi-day delivery remain **unverified**. Use the [live-host cases](evaluation.md#scheduled-task-adapter-cases) for that separate acceptance.
- Upstream projects were inspected for methods; their model services and benchmarks were not run. No automatic truth guarantee or quality percentage is claimed.

## 中文说明

本轮实际完成七组、十四份卡片与报告，逐条检查了关键结论和原始来源。引用位置、书目对应和条件表达有所改善；最终科学盲测仍保留两处范围精度问题，未把原稿改成“通过”。

这些是小样本观察，各次使用的资料和访问条件存在差异，实际模型运行标识为 `UNKNOWN`；不能据此计算准确率提升或把差异归因于某一版本改动。

所有测试是原生 Agent 对话，不能证明真实 GPT 定时任务按时交付。下一步重点是实际账户连续七次运行，以及一次“反馈后深入、下一次恢复新卡片”的完整流程；方法见[评估说明](evaluation.md)。

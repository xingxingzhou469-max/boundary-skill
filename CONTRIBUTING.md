# Contributing / 参与改进

Thank you for helping Boundary make unfamiliar knowledge useful and checkable. Small, evidence-backed changes are welcome. You do not need to be a programmer to report a weak topic or misleading source.

## What helps

- **Knowledge quality:** an unsupported claim, a citation that does not support it, a repeated idea, or a topic with little transferable value.
- **Usability:** installation trouble, confusing first-run questions, unclear feedback, or interrupted research that cannot resume.
- **Reliability:** a reproducible state, file, timezone, or platform problem.
- **Examples and language:** clearer explanations with opened sources; equivalent Chinese and English evidence standards.

Use the [issue forms](https://github.com/xingxingzhou469-max/boundary-skill/issues/new/choose). Share a minimal, anonymized excerpt—not your config, whole learning history, credentials, or personal notes. Suggesting a feature starts with the user problem and a concrete usage example.

## Local checks

```bash
git clone https://github.com/xingxingzhou469-max/boundary-skill.git
cd boundary-skill
python3 scripts/check_repo.py
python3 scripts/build_task_prompts.py --check
python3 -m unittest discover -v
python3 scripts/demo.py
```

Use Python 3.10+ and an IANA timezone database. Windows normally needs `python -m pip install tzdata`. There are no other runtime or test dependencies.

Tests run in isolated temporary directories with explicit config paths. Follow that pattern: never run fixtures against your real Boundary folder. The demo uses checked-in examples and performs no network or model calls.

## Making a change

1. Read `SKILL.md` and the relevant reference before editing behavior.
2. Keep a single implementation and preserve the existing v2 data contract unless a migration is part of an explicitly discussed change.
3. For a bug fix, reproduce it and add a regression test that fails before the fix.
4. For instruction or content changes, run the relevant scenarios in [docs/evaluation.md](docs/evaluation.md) with a real agent. Record host/model, date, observable outcome, and any tool limitation. Do not invent a pass.
5. Keep the two READMEs aligned. Detailed operational rules belong in references or the getting-started guide.
6. Open a pull request describing the problem, resulting behavior, actual validation, and limitations.

The state script enforces structural rules; source quality and semantic novelty require research and review. A new regular expression or longer prompt is not by itself proof of a better learning experience.

## Scope

Keep Boundary focused on important cross-domain knowledge, explicit random wandering, sourced explanations, and local readable files. Avoid engagement streaks, personality profiling, news feeds, automatic messaging, hosted accounts, and large frameworks without a concrete user need.

Do not copy upstream code or prose without checking and preserving its license. Design inspiration should be credited with a link. Contributions to this repository are provided under its [MIT license](LICENSE); cited source materials retain their own rights.

## 中文

欢迎提交可复现的故障、知识质量问题、可靠示例和中文表达改进。请说明“哪里不对、期望是什么、依据在哪里”，并删除个人路径、历史和密钥。修改程序后运行本地检查；修改指令后，用真实 Agent 验证对应场景，写明实际结果和未验证部分。贡献采用本仓库 MIT 许可证，外部引用仍保留原权利。

For content-quality rules, edit `references/quality-rubric.md` and run `python3 scripts/build_task_prompts.py` to regenerate both ChatGPT task prompts. Do not maintain separate copies of the research policy. The task adapter changes host behavior only; it is not another storage implementation.

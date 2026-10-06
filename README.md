<div align="center">

![Boundary — discover, verify, connect](assets/boundary.svg)

# Boundary

**Discover important ideas you did not know to ask about.**

One source-checked knowledge card. Twelve fields to explore. A full deep dive when you want it.

[![CI](https://github.com/xingxingzhou469-max/boundary-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/xingxingzhou469-max/boundary-skill/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB)](docs/getting-started.md#requirements)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-compatible-6f42c1)](https://agentskills.io)

**English** · [简体中文](README.zh-CN.md)

[Add a daily ChatGPT task](integrations/chatgpt/task.en.md) · [Read a card](examples/card.en.md) · [Install locally](#quick-start) · [Contribute](CONTRIBUTING.md)

</div>

Boundary helps curious people understand one important cross-domain question each day. Add a daily task in ChatGPT to receive cards directly in conversation, or install it as an [Agent Skill](https://agentskills.io) to keep a local Markdown library with your existing agent. No interest questionnaire is needed.

Ask for today's boundary. Your agent selects a worthwhile topic, opens reliable sources, and writes a direct 3–5 minute card. Reply **Deep dive** for a complete, plain-language research report on that card's central question. With the local Agent Skill, cards, citations, and reports stay in a folder you choose. The ChatGPT task edition delivers directly in its conversation.

## See what you get

> **Why can melting sea ice lead to more warming?**
>
> A bright surface reflects more incoming sunlight. When sea ice gives way to darker water, more sunlight can be absorbed, reinforcing warming. The useful idea is a **feedback loop**: an effect can become part of its own cause.
>
> Understanding the mechanism is different from predicting exactly how much ice will disappear in a given year.

*Short preview of the [full English card](examples/card.en.md) / [中文知识卡](examples/card.zh-CN.md). Read the [deep research report](examples/report.en.md) for evidence, limitations, and cross-domain connections. Examples include opened source links and a verification date; they are curated examples, not live output or a fixed question bank.*

## Pick your starting point

| I want to… | Start here |
|---|---|
| Receive a card in **ChatGPT Scheduled** without installing anything | [Copy the English task prompt](integrations/chatgpt/task.en.md) · [复制中文任务指令](integrations/chatgpt/task.zh-CN.md) |
| Keep a persistent **local Markdown library** with Codex or another agent | Follow the installation below |

For a new task, copy the setup prompt. For an existing one, [replace only its runtime instructions](integrations/chatgpt/instructions.en.txt), preserving its schedule. The task uses available history, and Deep dive works after earlier feedback too. [Setup, preview, updates, sharing, and validation status →](integrations/chatgpt/README.md)

## Quick start

You need a skill-capable agent with **web search, source-opening, shell, and local file access**, plus **Python 3.10+**. Boundary does not supply a model or search service. Your host's normal usage limits and costs apply.

Install using the [Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add xingxingzhou469-max/boundary-skill --skill boundary -g
```

Start a new agent session and ask:

```text
Use Boundary. Give me an important idea outside my usual fields.
Save my cards in /absolute/path/to/my/Boundary folder.
```

Use your own absolute folder path. Language defaults to your current language and selection defaults to Boundary mode. The agent asks for the save folder if you have not supplied one. There is no interest quiz.

[Manual installation, host requirements, updates, scheduling, and troubleshooting →](docs/getting-started.md)

## Choose how to explore

| Mode | What changes |
|---|---|
| **Boundary** · default | Prioritizes important, transferable concepts. Recent coverage helps broaden the search without forcing a quota. |
| **Wander** · on request | Randomly chooses where to look, then applies the same usefulness and evidence standards. |
| **Alternate** · optional | Alternates Boundary and Wander after each recorded card. |

Try “Use Wander mode today” for a one-off change. It does not change your saved preference.

The twelve domains span Earth and space, life and medicine, mathematics and physical sciences, engineering, history, philosophy, institutions, economics, society, the arts, language, and everyday materials. See the [selection rules](references/domains.md).

## Four replies, two reading levels

| Reply | Result |
|---|---|
| **Known / 已知道** | Save the card and add it to the index. |
| **New / 新知识** | Save it and retain the feedback in local history. |
| **Deep dive / 深入了解** | Save the card, research its question further, and attach one complete report. |
| **Skip / 暂时跳过** | Remove the pending body; keep metadata for a seven-day topic cooldown. No formal note. |

A shown card is saved before delivery, so you can resume after closing the chat. Deep dive uses the question already on the card; no second depth menu. Feedback is final for that card. Shown cards contribute to coverage; a skip slightly reduces a domain's short-term weight and never blocks it permanently.

## Evidence you can inspect

- The agent must open sources before drafting: at least **two independent publishers per card**, **three per report**.
- Important claims get links at the point of use. Cards include a concrete example, a usable takeaway, and a boundary of applicability. Reports investigate alternative explanations and describe what the evidence can actually establish.
- No adequate sources? Choose another topic. No browsing capability? Report the blocker.
- The Python script checks metadata, duplicates, and the save/feedback lifecycle. **It cannot verify factual truth, publisher independence, or whether the agent opened a page.**
- Medical, legal, financial, and contested topics follow [specific evidence rules](references/source-policy.md). Outputs remain educational.

## Your files, ordinary formats

```text
Your-Boundary-folder/
├── INDEX.md             # Reading list
├── Cards/               # Accepted cards with citations
├── Reports/             # Linked deep research reports
└── _system/
    ├── state.json       # Transparent history and feedback
    ├── pending/         # Complete cards awaiting your response
    └── tmp/             # Draft inputs
```

No notes app, account, hosted Boundary service, or proprietary format is required. You can read the Markdown on a phone after transferring or syncing the folder yourself. Boundary does not provide device sync.

**Privacy boundary:** the state script makes no network calls. Your host agent still processes prompts, sources, and the history it reads under that host's own data policy. “Local storage” does not mean the AI host is offline. Boundary does not inspect unrelated chats or build political, religious, medical, financial, or personality profiles.

## Try the storage workflow without an agent

Clone the repository, then run from its root:

```bash
python3 scripts/demo.py
```

This replays the bundled example through **initialize → record → restart context → feedback → attach report** in a temporary folder, verifies the resulting files and links, and removes that folder afterward. It does not browse, call a model, or touch your existing Boundary configuration. Use `python` if that is your Python 3 command.

To keep the example in a new directory:

```bash
python3 scripts/demo.py --output ./boundary-demo
```

The destination must not exist. This is a storage demonstration, not a fresh fact-check or a benchmark of an agent's research quality.

## Development and contributions

```bash
python3 scripts/check_repo.py
python3 scripts/build_task_prompts.py --check
python3 -m unittest discover -v
```

CI runs these checks and the demo on Linux, macOS, and Windows with Python 3.10 and 3.14. Windows also needs the IANA timezone database (`tzdata`); see [requirements](docs/getting-started.md#requirements).

Useful contributions include reproducible bugs, evidence-quality reports, better examples, and measured improvements to skill behavior. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the [behavior evaluation cases](docs/evaluation.md). The latter require real agent runs; a green Python test suite does not prove research quality.

If Boundary helped you understand something new, a star helps other curious readers find it. A specific example of what worked—or failed—is just as useful.

## Design credits

Boundary's original design drew on [BelCorentin/curiosity](https://github.com/BelCorentin/curiosity) for daily discovery, [Koulb/paper-scout](https://github.com/Koulb/paper-scout) for history-aware selection, and [199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill) for research discipline.

This maintenance pass also takes cues from [Vercel's Skills CLI](https://github.com/vercel-labs/skills) for explicit installation, [Anthropic's skills](https://github.com/anthropics/skills) for examples and evaluation, and [Superpowers](https://github.com/obra/superpowers) for observable workflow checks. The shared research standard adapts question-led research and synthesis ideas from [STORM](https://github.com/stanford-oval/storm) and [GPT Researcher](https://github.com/assafelovic/gpt-researcher); see the [source map and method notes](references/source-map.md). These are design references, not endorsements or bundled dependencies.

[MIT](LICENSE). Linked sources and upstream projects retain their own licenses and rights.

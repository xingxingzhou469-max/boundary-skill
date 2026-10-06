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

## 中文简介

**Boundary 是一个帮助你拓宽知识边界的开源 AI 技能：发现你还没想到要搜索、却值得理解的重要问题。**

它从科学、历史、经济、哲学等十二个领域选择主题，让 AI 先打开可靠来源，再写成 3～5 分钟可读完的中文知识卡。每张卡说明核心原理、具体例子、能怎样运用以及适用边界，并附上来源。回复“深入了解”，就能围绕同一个问题继续阅读完整的研究报告。

你可以复制 [ChatGPT 中文任务指令](integrations/chatgpt/task.zh-CN.md)，在对话中接收内容；也可以安装到 Codex 等支持技能的 AI 工具，把卡片和报告保存在自己的文件夹里。使用时需要 AI 工具具备联网搜索和打开来源的能力；本地安装另需 Python 3.10+。

**[阅读完整中文说明](README.zh-CN.md) · [先看一张中文知识卡](examples/card.zh-CN.md) · [设置 ChatGPT 每日任务](integrations/chatgpt/task.zh-CN.md)**

## Overview

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

For a new task, copy the setup prompt. For an existing one, [replace only its runtime instructions](integrations/chatgpt/instructions.en.txt), preserving its schedule. The instructions use available history and allow Deep dive after earlier feedback. [Setup, preview, updates, sharing, and validation status →](integrations/chatgpt/README.md)

## Quick start

These installation requirements apply to the local Agent Skill. ChatGPT users can use the [task prompt](integrations/chatgpt/task.en.md) directly without Python or a local folder.

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
| **Alternate** · optional | Alternates Boundary and Wander. |

Try “Use Wander mode today” for a one-off change. It does not change your saved preference.

For Alternate mode, the local skill uses recorded card modes; ChatGPT uses the last card's mode actually visible in its conversation. Repeat avoidance still checks all available history. Neither edition changes a future default from a one-off mode request.

The twelve domains span Earth and space, life and medicine, mathematics and physical sciences, engineering, history, philosophy, institutions, economics, society, the arts, language, and everyday materials. See the [selection rules](references/domains.md).

## Four replies, two reading levels

**In ChatGPT:** Known / New / Skip acknowledges feedback briefly. Deep dive remains available after any of those replies and delivers a report in conversation. History and repeat avoidance use only visible context; see [the task behavior table](integrations/chatgpt/README.md#收到卡片之后).

**With the local Agent Skill:**

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
- For a card with inadequate sources, try another candidate; if evidence is still inadequate, report the limitation. For a report, retain its question and state the evidence gap. No browsing capability? Report the blocker.
- The Python script checks metadata, duplicates, and the save/feedback lifecycle. **It cannot verify factual truth, publisher independence, or whether the agent opened a page.**
- Medical, legal, financial, and contested topics follow [specific evidence rules](references/source-policy.md). Outputs remain educational.

The [2026-10-06 quality review](docs/evaluation-results.md) records seven native Agent trials, observed improvements, and remaining precision issues. Real ChatGPT scheduled delivery remains unverified.

## Your files, ordinary formats

The local Agent Skill creates this folder structure. The ChatGPT task edition delivers its content in conversation.

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

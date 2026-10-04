# Add Boundary to ChatGPT Scheduled / 添加到 ChatGPT 定时任务

**No local installation. Copy one prompt, then confirm the task.**

**无需本地安装：复制整段指令，确认任务创建即可。**

## Add your task

1. Open the [中文 task prompt](task.zh-CN.md) or [English task prompt](task.en.md). Use the copy button on its code block.
2. Paste it into [ChatGPT](https://chatgpt.com). The first sentence requests daily delivery at 9:00 AM in your local timezone; change it to your preferred schedule. If the timezone is unknown, answer that one question.
3. If the account offers only a flexible delivery window, choose whether to accept it; the prompt must not silently substitute that for 9:00 AM.
4. Check the **actual task confirmation**, its instructions, schedule, and timezone. A chat response saying “done” is not sufficient.
5. Check the first scheduled result. It should answer a useful question and contain opened, relevant source links. If the run reports unavailable browsing, change to a host with those capabilities; do not accept an unsourced substitute.

中文：打开中文指令 → 复制代码块 → 粘贴到 ChatGPT → 核对任务确认、时间与时区 → 检查首次执行的来源与内容。没有创建确认就不算安装完成。可以先在普通对话里试读一张，但那不能证明定时任务已经执行成功。

The instructions are self-contained, so scheduled runs do not need to fetch this repository. They are generated from the same [quality standard](../../references/quality-rubric.md) used by the local skill; the host-specific part only changes scheduling, storage, and feedback handling.

## Know which edition you are using

| Capability | ChatGPT conversation edition | Local Agent Skill |
|---|---|---|
| Install Python / choose a folder | No | Yes |
| Deliver cards and requested reports | In the task conversation, when research tools are available | In chat plus your chosen Markdown folder |
| Duplicate avoidance | Based only on visible task context; may be incomplete | Persistent local history, lexical checks plus agent review |
| Feedback | Acknowledged in the conversation | Saved through the tested state CLI |
| Seven-day cooldown | No durable guarantee | Enforced for recorded skipped topics |
| Files on your computer | No promised access or writes | Explicit chosen-root writes |
| Timing | ChatGPT Scheduled | Your host's scheduler / Codex automation |

This adapter never claims to execute Python, maintain `state.json`, or save to your computer. It carries the content workflow to a different host. The local CLI remains the sole file-storage implementation.

## Official task support and sharing

As checked on **2026-10-05**, OpenAI documents scheduled tasks separately from Codex automations, excludes custom GPTs, and says project tasks cannot access uploaded/project files. Task and tool availability vary by account and settings. See [OpenAI's scheduled tasks documentation](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt). This is why the adapter includes its necessary instructions directly.

For accounts with task sharing, create and validate a task, then use **Scheduled → task menu → Share → Copy link**. Recipients review the snapshot and schedule their own copy. A shared link is not automatically updated when the original instructions change; refresh it through the share dialog. These steps and eligibility are documented by [OpenAI](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt).

本项目不提供伪造的“一键安装”链接。若你的账号有任务分享入口，可以先用这份指令创建、试跑并确认结果，再复制官方分享链接；接收者审阅后自行添加。发布前检查指令里没有个人信息。

**No shared task URL is bundled yet.** A maintainer should add one only after verifying an actual cloud run in that account. Until then, the copyable prompt is the supported entry point. Do not use an undocumented URL trick that claims to create tasks automatically.

## Validation status

- Generated prompts are reproducible and checked in CI against the shared source.
- Their content and host boundaries can be tested in ordinary agent sessions using [evaluation cases](../../docs/evaluation.md).
- These checks **do not prove a real ChatGPT Scheduled execution**. For host acceptance, create a task in an eligible account, observe its scheduled run, and record tool access, output quality, and the next scheduled time. Live host acceptance is currently **not verified** in this repository.
- A copied task is a snapshot. To adopt future Boundary improvements, replace its instructions from the new generated prompt and verify the result again.

For a persistent Markdown library instead, use the [local installation guide](../../docs/getting-started.md).

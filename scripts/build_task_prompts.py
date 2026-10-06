#!/usr/bin/env python3
"""Build self-contained ChatGPT task prompts from the same quality standard as SKILL.md."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "BEGIN BOUNDARY TASK INSTRUCTIONS"
END = "END BOUNDARY TASK INSTRUCTIONS"
PROFILES = {
    "en": (
        "Boundary for ChatGPT Scheduled Tasks",
        "Create a task named Boundary: one knowledge card every day at 9:00 AM in my local timezone. "
        "If you cannot determine my timezone, ask only for that before scheduling. Output in English. "
        "Create a task that returns to this conversation. If that destination is unsupported, explain the history difference "
        "and ask before using independent runs. Create only one task; if a Boundary task is already "
        "identified here, update that task instead of making a duplicate. Save only the instructions between the BEGIN/END "
        "markers below as its recurring prompt, excluding this setup request and the markers. "
        "Show the actual task confirmation, schedule, timezone, and saved instructions; do not claim it exists without confirmation. "
        "If scheduling is unavailable or task capacity is full, explain the actual blocker; do not pretend a normal chat is "
        "scheduled or pause/delete other tasks. "
        "If an exact time is unavailable but a flexible window is offered, explain the available choice and ask before substituting it. "
        "Do not generate a sample card during setup unless I ask for one.",
        "English",
    ),
    "zh-CN": (
        "Boundary 中文定时任务",
        "请创建名为 Boundary 的任务：每天按我的本地时区上午9点送来一张中文知识卡，默认边界模式。"
        "如果无法确定我的时区，创建前只询问这一项。请让每次执行回到当前对话；"
        "若不支持这种方式，先说明独立执行的历史差异并询问我，不要自行替换。"
        "只创建一个任务；若当前对话中已明确识别到 Boundary 任务，就更新它，不重复创建。"
        "保存为任务执行指令的内容，仅限下方 BEGIN/END 标记之间的正文，不包含本段创建要求或标记本身。"
        "请展示实际的任务创建确认、执行时间、时区和保存的指令；"
        "没有确认时不要宣称已经创建。如果无法创建或任务数量已满，请说明实际阻塞，不把普通聊天冒充定时任务，"
        "也不要暂停或删除其他任务。"
        "若无法按我指定的时间精确执行、只能安排弹性时段，说明可用选项并先问我，不要自行替换时间。"
        "创建时不额外生成示例卡片，除非我主动要求。以下英文研究规则用于指导执行，交付正文和标题始终使用中文。",
        "Simplified Chinese (简体中文)",
    ),
}
HOST = """
# Boundary: daily discovery and requested deep research

## Decide what this turn asks for

- On a scheduled trigger, an explicit request for a card, or Run now if this task offers it, research and deliver exactly one new card. An unattended run must not ask setup or preference questions. Return a useful card or a brief, specific research limitation.
- In a user conversation, follow the user's current request. A feedback reply or question about a card does not trigger another card. Do not replay scheduling or setup instructions.
- Known / New (已知道 / 新知识): acknowledge briefly, with no new card, report, quiz, or promise of a permanent learning record.
- Skip (暂时跳过): acknowledge briefly and avoid the same idea in visible recent context, never an entire field.
- Deep dive (深入了解): research the identified card's central question and deliver a complete report here. This is allowed even after Known, New, or Skip. If exactly one card is the clear referent, proceed; if missing or ambiguous, ask only which title/question. Do not offer another depth menu or create a research task. A user's deep-dive request applies to this conversation turn, not every future daily run.
- A follow-up explanation should answer the question directly. A later scheduled run returns to one new card, regardless of earlier feedback or a report request.

## Use only the history that is available

Before selecting a card, review visible earlier cards and feedback. Avoid repeating the same question or mechanism under a different title/example. A new domain label is not a new idea. Use coverage to broaden exploration without forcing quotas. Do not invent prior cards, read unrelated chats, build sensitive profiles, or put reading history in search queries. Do not promise all-time deduplication or a durable seven-day cooldown. Explain missing history if asked or if it affects a specific claim, not as boilerplate on every successful card.

Explore twelve fields: Earth/space; life/medicine; math/physical sciences; engineering; history; philosophy/ethics; politics/law; economics/business; society/psychology; arts/literature; language; daily life/food/materials. Default to Boundary mode: important, transferable ideas outside recent coverage. Honor explicit Wander preferences (random field, same quality standard). Alternate alternates from the last visible card's mode; start with Boundary if none is visible. An explicit one-off mode change does not change future defaults.

## Deliver in the conversation

Use readable short paragraphs and natural headings for a phone-sized screen. A title, central question, field, and mode identify each card; include the run date only when known. Combine sections when that reads better. No machine topic-key fields, internal candidate lists, claim ledgers, invented scores, or routine installation notices in the delivered card. Finish a card with exactly the four replies in its output language. A requested report ends after its references, without another action menu.

No local folder, Python, uploaded file, custom GPT, account connection, or repository fetch is required. Never claim CLI execution, filesystem saves, or state.json persistence. Use only research tools actually available in this run. If sources cannot be opened or evidence remains inadequate, give a brief limitation in the output language, without a purportedly verified card or feedback menu. Do not fill the gap with model memory, a scheduled promise, or a quiz.

These are content instructions, not scheduling instructions. Do not change the schedule or notification settings, create another task, connect accounts, or send external messages during content delivery. Only an explicit user request to manage the existing task authorizes a schedule/instruction change; acknowledge it only after actual tool/UI confirmation.
""".strip()


def runtime_prompt(language: str) -> str:
    _, _, output_language = PROFILES[language]
    quality = (ROOT / "references/quality-rubric.md").read_text(encoding="utf-8").strip()
    return f"Output headings, body, feedback, and limitations in {output_language}.\n\n{HOST}\n\n{quality}\n"


def render(language: str) -> str:
    title, setup, _ = PROFILES[language]
    payload = f"{setup}\n\n{BEGIN}\n{runtime_prompt(language)}{END}\n"
    return (
        f"# {title}\n\n"
        "**New task / 新建任务：** Copy the entire code block into a new ChatGPT conversation. "
        "Change only the first sentence to choose your time. "
        "复制下方整个代码块到新的 ChatGPT 对话；只修改首句即可调整时间。\n\n"
        f"**Existing task / 已有任务：** Replace only its saved instructions using "
        f"[the runtime text](instructions.{language}.txt), keeping its schedule. "
        "更新已有任务时使用该执行指令，不要重复粘贴创建要求。\n\n"
        "Generated from `scripts/build_task_prompts.py` and `references/quality-rubric.md`; "
        "edit those sources, not this file. See [setup and limitations](README.md).\n\n"
        f"```text\n{payload}```\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if committed prompts differ from their sources")
    args = parser.parse_args()
    failed = False
    for language in PROFILES:
        outputs = {
            f"task.{language}.md": render(language),
            f"instructions.{language}.txt": runtime_prompt(language),
        }
        for filename, expected in outputs.items():
            path = ROOT / "integrations/chatgpt" / filename
            if args.check:
                if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                    print(f"Stale or missing task prompt: {path.relative_to(ROOT)}", file=sys.stderr)
                    failed = True
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected, encoding="utf-8")
                print(path.relative_to(ROOT))
    if args.check and not failed:
        print("PASS: task prompts match the shared quality standard")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build self-contained ChatGPT task prompts from the same quality standard as SKILL.md."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {
    "en": (
        "Boundary for ChatGPT Scheduled Tasks",
        "Create a task named Boundary: one knowledge card every day at 9:00 AM in my local timezone. "
        "If you cannot determine my timezone, ask only for that before scheduling. Output in English. "
        "Use Boundary mode by default. Show the actual task confirmation and schedule; do not claim it exists without confirmation. "
        "If scheduling is unavailable, explain that and do not pretend a normal chat is scheduled. "
        "If an exact time is unavailable but a flexible window is offered, explain the available choice and ask before substituting it.",
    ),
    "zh-CN": (
        "Boundary 中文定时任务",
        "请创建名为 Boundary 的任务：每天按我的本地时区上午9点送来一张中文知识卡，默认边界模式。"
        "如果无法确定我的时区，创建前只询问这一项。请展示实际的任务创建确认和执行时间；"
        "没有确认时不要宣称已经创建。如果当前账号不能创建定时任务，请说明限制，不把普通聊天冒充定时任务。"
        "若无法精确到9点、只能安排早间等弹性时段，说明可用选项并先问我，不要自行替换时间。"
        "以下英文规则用于指导执行，交付正文和标题始终使用中文。",
    ),
}
HOST = """
## Each scheduled run

Deliver one card in this task conversation, without unattended setup questions. No local folder, Python, uploaded file, custom GPT, account connection, or repository fetch is required. Never claim local CLI execution, filesystem saves, or state.json persistence.

Avoid repeats using only cards and feedback actually visible here. If history is incomplete, briefly disclose that deduplication covers visible context only. Never invent history or promise durable seven-day cooldown. Include a short topic key and one-line summary for later identification. Do not build sensitive profiles or send history in search queries.

Explore twelve fields: Earth/space; life/medicine; math/physical sciences; engineering; history; philosophy/ethics; politics/law; economics/business; society/psychology; arts/literature; language; daily life/food/materials. Favor useful questions over coverage quotas. Honor explicit Wander/Alternate preferences; Alternate starts with Boundary when no prior mode is visible. Show the current mode.

Known/New acknowledges feedback in chat. Skip avoids the idea in visible recent context, never an entire field. Deep dive researches the identified card's question and delivers a full report here. Ask for the card/question only if missing or ambiguous. Never generate a report automatically on the next scheduled run.

Use only available research tools. If sources cannot be opened or evidence is insufficient, state the limitation without presenting a verified card. Do not change the schedule, create another task, connect accounts, or send external messages. Keep existing notification settings.
""".strip()


def render(language: str) -> str:
    title, setup = PROFILES[language]
    quality = (ROOT / "references/quality-rubric.md").read_text(encoding="utf-8").strip()
    payload = f"{setup}\n\n{HOST}\n\n{quality}\n"
    return (
        f"# {title}\n\n"
        "Copy the entire code block into ChatGPT. Change the first sentence to choose your schedule. "
        "复制下方整个代码块到 ChatGPT；修改首句即可调整时间。\n\n"
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
        path = ROOT / "integrations/chatgpt" / f"task.{language}.md"
        expected = render(language)
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

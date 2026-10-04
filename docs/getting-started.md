# Getting started / 安装与使用

Boundary is a skill for an existing agent, not a standalone chatbot. Start with the [English README](../README.md) or [中文介绍](../README.zh-CN.md).

## Requirements

- Python **3.10+** (`python3 --version`, or `python --version` on Windows).
- An **IANA timezone database**. macOS and most Linux installations supply one. On Windows or minimal containers, install it into the same Python environment: `python -m pip install tzdata`. Boundary's code otherwise uses only the standard library.
- A host that can load `SKILL.md`, execute Python, read/write local files, search the web, and **open underlying sources**.
- Git for manual installation; Node.js/npm only if using `npx skills`.

Skill-format compatibility alone does not establish that a host has all these tools. Codex, Claude Code, Cursor, and other Skills CLI targets must have the required tools enabled in the actual session. A browser-only chat with no local shell cannot run the persistence workflow. Boundary has no bundled model or API key; your host controls research access, costs, and data handling.

## Install

The [Skills CLI](https://github.com/vercel-labs/skills) lets you select agents and installation scope:

```bash
npx skills add xingxingzhou469-max/boundary-skill --skill boundary -g
```

To target only Codex:

```bash
npx skills add xingxingzhou469-max/boundary-skill --skill boundary -a codex -g
```

For a local checkout you are evaluating, replace the repository name with its path. Do not install a second copy over an existing customized skill without inspecting it.

### Manual install

For [Codex](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) on macOS/Linux:

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/xingxingzhou469-max/boundary-skill.git ~/.agents/skills/boundary
```

For [Claude Code](https://code.claude.com/docs/en/skills) on macOS/Linux:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/xingxingzhou469-max/boundary-skill.git ~/.claude/skills/boundary
```

For other hosts or Windows, use the host's documented skill directory or the Skills CLI. The installed skill directory should be named `boundary`; the GitHub repository may still be named `boundary-skill`. Start a fresh agent session after installing.

## First card

```text
Use Boundary in English. Save cards in /absolute/path/to/Boundary.
Give me today's knowledge boundary.
```

```text
用 Boundary 给我今天的知识边界，保存到 /你选择的绝对路径/Boundary。
```

Use your actual absolute path, such as `C:\Users\you\Documents\Boundary` on Windows. Defaults are the current language and Boundary mode; no interest questionnaire. A one-off “Use Wander today” changes that card only. To change the saved setting, say “Use Alternate as my default from now on.”

The state helper uses a pointer configuration at `$XDG_CONFIG_HOME/boundary/config.json`, or `~/.config/boundary/config.json` when the variable is unset. `BOUNDARY_CONFIG` overrides that location. The CLI's global `--config` takes precedence and goes **before** the subcommand:

```bash
python3 scripts/state.py --config /absolute/path/config.json init \
  --root /absolute/path/Boundary --language en --mode boundary \
  --timezone Europe/London
python3 scripts/state.py --config /absolute/path/config.json context
```

Commands above run from the skill directory. An agent normally performs setup and selects the local IANA timezone; specify `--timezone` when automatic detection is inappropriate. Configuration and history are separate from the installed skill, so updating the skill does not need to erase learning history.

## Feedback and returning later

Reply **Known / New / Deep dive / Skip** (中文：**已知道 / 新知识 / 深入了解 / 暂时跳过**). Feedback is final for each shown card. If several pending cards could match, the agent should ask which one you mean.

After an interrupted Deep dive, ask “Continue the unfinished Boundary report.” The agent reads `context.pending_reports` and researches the stored question without repeating feedback. It must not create a placeholder to hide a research failure.

## ChatGPT Scheduled without local installation

Use the [copyable task adapter](../integrations/chatgpt/README.md). It delivers into the task conversation and has a different persistence boundary. The CLI instructions above apply to local agents only.

## Optional daily delivery

Only if your host supports scheduling, ask it explicitly:

```text
Run Boundary every day at 9:00 AM in my local timezone.
Use my saved folder and alternate modes. Generate one card in English.
```

Boundary owns research and local files; the host scheduler owns timing. Scheduling is not installed by the Python helper. It is never enabled by default. No separate outbound messaging integration is included.

## Updates and removal

For a Skills CLI install, use the update and remove commands supported by your installed CLI (`npx skills --help`). For a clean manual Git checkout, inspect local changes first, then update with `git pull --ff-only` inside that checkout. Back up custom changes before updating.

Removing the skill stops discovery of its instructions. It does not delete your chosen cards folder, pointer configuration, or host schedules. Preserve the folder; remove a schedule separately in your host if you created one.

## Troubleshooting

| Symptom | Check or action |
|---|---|
| Skill not discovered | Start a fresh session; check the host's skill directory and that `SKILL.md` exists under `boundary`. |
| Missing configuration on first use | Provide an absolute save folder, then initialize once. Do not copy someone else's config. |
| Configured folder moved | Relink with `configure --root /new/absolute/path` only after moving the complete folder, including `_system/state.json`. |
| Invalid JSON / unsupported version | Preserve the files and exact error. Restore a known-good backup or report the issue; do not initialize over existing history. |
| Missing index/card/report | Check whether you intentionally moved or deleted it. Boundary should not reconstruct your edited files without your request. |
| Timezone unavailable | Install IANA data (`tzdata` on Windows), then use a real zone such as `Asia/Shanghai` or `Europe/London`. |
| Browsing disabled or source blocked | Enable the host's research tools or use another accessible source. Do not call a memory-only response verified. |
| Duplicate or cooldown rejection | Pick a materially different explanatory idea. Renaming the same idea is not a fix. |
| Interrupted or simultaneous writes | Stop competing writers; preserve the error and files. See [storage guarantees](../references/storage.md#write-guarantees-and-recovery). |

Run `python3 scripts/demo.py` from a repository checkout to isolate storage problems from your live configuration. A successful demo does not verify live browsing or model behavior.

## 中文提示

- 安装后新开会话；先确认 Agent 具备搜索、打开来源、命令执行和文件读写能力。
- 首次只需确定保存目录，语言和模式可沿用默认值；已经说清的选项不会重复询问。
- Windows 的 Python 通常需要额外安装 `tzdata` 时区数据。
- 配置损坏时保留原文件，不要重新初始化来覆盖历史。完整移动文件夹后再改指针路径。
- 本地演示只验证文件流程，不代表模型事实核验已经通过；数据也不会自动同步到手机。

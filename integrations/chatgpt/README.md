# Boundary in ChatGPT / 在 ChatGPT 每天读一张知识卡

**复制一次，每天收到一张有来源、有解释、有用处的卡片。无需安装。**

**Copy once. Receive one sourced, useful card each day. No installation.**

## 新用户：添加每日任务

1. 打开[中文创建指令](task.zh-CN.md)，复制整个代码块，粘贴到一个新的 [ChatGPT 对话](https://chatgpt.com)。默认每天当地时间上午 9 点；只修改首句即可换时间。无需下载仓库。
2. 指令要求每次执行回到当前对话，方便回看卡片和继续深入。如果无法确定时区，回答这一项；如果账号只能选弹性时段或不支持同对话执行，先确认你是否接受。
3. 在 **Scheduled / 定时任务**中核对任务确实存在：名称、时间、时区、下次执行，以及保存的指令。保存内容应以输出语言要求和 Boundary 内容规则开头，**不应包含“请创建任务”那段要求**。聊天里一句“已创建”不算完成。
4. 等待一次真实定时执行。也可先用 **Run now / 立即运行**检查内容，但立即运行、普通试读和真实按时执行是不同的验证。若账号没有该按钮，直接等待计划时间。

创建时不额外送一张示例卡，避免把“设置成功”和“运行成功”混在一起。研究规则使用英文，标题、正文、反馈和能力限制始终用中文。

## 已有任务：更新指令，不再建一个

打开[中文执行指令](instructions.zh-CN.txt)，复制全文。在 Scheduled 中找到原来的 Boundary 任务，编辑并替换它的**指令**，保留原有时间和时区，保存后重新核对。

这份执行指令不含创建要求，也适合直接填写任务编辑器的指令栏。不要把“中文创建指令”的完整代码块填进周期执行栏。更新后的首次结果也需要检查；仓库更新不会自动改写你的任务。

## 先试读，不创建任务

复制[中文执行指令](instructions.zh-CN.txt)到普通对话，末尾加：

```text
现在给我一张知识卡。不要创建或修改任何定时任务。
```

这能体验内容，不能证明定时任务已创建或按时运行。

## 收到卡片之后

| 你回复 | 会发生什么 |
|---|---|
| 已知道 / 新知识 | 简短确认，不自动追加内容。 |
| 暂时跳过 | 简短确认；在可见近期记录中避开相同想法，不屏蔽整个领域。 |
| 深入了解 | 围绕这张卡的核心问题交付完整研究报告。先前选过“已知道”“新知识”或“暂时跳过”也可以继续深入。 |
| 针对卡片提问 | 直接解释你的问题，不自动生成另一张卡。 |

深入较早的卡片时，写“深入了解：卡片标题”即可；只有对象确实不明确时才询问。第二天的定时执行仍然送一张新卡，不把某次深入请求变成每天的长文任务。卡片在对话中交付，不承诺已写入电脑或建立永久学习记录。

## 如果没有按预期收到

| 情况 | 下一步 |
|---|---|
| 没有实际任务确认，或任务数量已满 | 查看 Scheduled；按账号实际能力处理。Boundary 不会擅自停掉你的其他任务。 |
| 时间不符合预期 | 核对计划及其时区；弹性早间时段不等于精确 9 点。 |
| 任务暂停或缺少通知 | 核对任务状态和通知设置。不要删除关联对话来“清理”；官方说明删除它会暂停任务。 |
| 结果说明无法打开来源 | 这次没有交付查证卡。检查该任务可用的研究工具；不要用无来源内容替代或把失败当成成功。 |
| 重复了以前的主题 | 指出重复卡片的标题或问题；仅能使用本次实际可见的历史，不能保证跨所有对话永久去重。 |

## English quick start

1. Copy the entire code block from [the English setup prompt](task.en.md) into a new ChatGPT conversation. Change the first sentence if you want a different time. It requests daily 9:00 AM delivery and a task that returns to that conversation.
2. Resolve the timezone or confirm a supported scheduling alternative if needed. Check the actual task, schedule, timezone, next run, and saved instructions in Scheduled. The recurring instructions must exclude the setup request.
3. Inspect a real scheduled result. Run now, if offered, tests delivery sooner but does not prove scheduled timing.

For an existing task, replace only its saved instructions with [the English runtime text](instructions.en.txt), preserving its schedule. For an unscheduled preview, paste the runtime text into chat and append “Give me a card now; do not create or change a task.”

Known / New / Skip acknowledges feedback briefly. Deep dive works even after any of those replies; use a title to identify an older card. An ordinary follow-up answers your question. The next scheduled run always returns to one new card. No local files or permanent history are promised.

## Official support, sharing, and history

Checked **2026-10-06** against [ChatGPT Learn](https://learn.chatgpt.com/docs/automations) and [OpenAI Help](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt). Learn distinguishes a task that returns to its chat with existing context from standalone runs starting with the saved prompt. Prefer the former for Boundary, but verify the actual destination and available history. Account, app, workspace, task capacity, and tool availability still determine what works. Exact-time delivery is not available to every account.

Both the setup and runtime instructions embed the necessary research rules; they do not depend on custom GPTs, uploads, connected apps, local files, or fetching this repository. They are generated from [one shared quality standard](../../references/quality-rubric.md), which also guides the local skill.

For eligible accounts, an official shared task link can make adding a copy easier: **Scheduled → task menu → Share → Copy link**. Validate the original task's actual cloud run before publishing its link. Recipients review the saved instructions, schedule, original timezone, and their own task/tool eligibility, then schedule a separate copy. It contains no old cards or creator history. Changes to the original do not update the link automatically; refresh it in the share dialog. Updating the share does not automatically update recipients' existing copies.

官方分享副本不带你的旧卡片；接收者要核对自己的时间、时区和工具权限。当前仓库**尚未提供经过真实定时运行验收的分享链接**，支持的入口是上述复制指令。不要用未公开的 URL 参数冒充自动安装。

## Validation status

- CI checks that setup and runtime outputs match their shared sources.
- [Evaluation cases](../../docs/evaluation.md) cover setup, feedback, later deep dives, repeat avoidance, missing tools, and unattended execution. Ordinary agent replay does not prove ChatGPT account behavior.
- The [2026-10-06 content review](../../docs/evaluation-results.md) records seven native Agent trials with real research tools, independent source review, and unresolved precision issues.
- **A real ChatGPT scheduled run and continuous multi-day delivery remain unverified.** Check actual creation, tools, first scheduled output, and next run before treating the integration as accepted.
- A copied task is a snapshot. Update its runtime instructions deliberately when adopting a new Boundary version.

For a persistent Markdown library, use the [local installation guide](../../docs/getting-started.md).

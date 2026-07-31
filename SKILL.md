---
name: boundary
description: Expand a user's knowledge boundary with a verified daily knowledge card selected either for high-value cross-domain discovery or genuine random wandering. Use when the user asks for today's boundary, a daily fact, something worth knowing outside their field, a random unfamiliar topic, help escaping an information bubble, or a deep-dive report about a Boundary card. Also use when the user replies to an active Boundary card with 已知道, 新知识, 深入了解, 暂时跳过, known, new, deep dive, or skip.
---

# Boundary

Deliver one verified, worthwhile encounter with the wider world. Optimize for durable understanding and genuine novelty, not engagement, trendiness, or agreement with the user.

## Load only what the task needs

- Read [references/domains.md](references/domains.md) before selecting a topic.
- Read [references/source-policy.md](references/source-policy.md) before researching or citing.
- Read [references/output-formats.md](references/output-formats.md) before drafting a card or report.
- Read [references/storage.md](references/storage.md) when configuring the save folder or writing notes.

## First run

If Boundary is not configured, ask for only these operational choices in one compact exchange:

1. Output language: Chinese or English. Default to the user's current language.
2. Selection mode: `boundary`, `wander`, or `alternate`.
3. The absolute folder where Boundary should save its files. Any folder works; all files are plain Markdown and JSON readable on any device.

Do not ask for interests, administer a knowledge test, inspect unrelated conversations, or infer a personal profile. Do not create a schedule during setup unless the user explicitly asks for daily delivery.

Resolve this skill's directory as `SKILL_DIR`, then initialize local state:

```bash
python3 "$SKILL_DIR/scripts/state.py" init \
  --root "/absolute/path/chosen/by/user" \
  --language zh \
  --mode boundary
```

Use `--config` when the runtime or user requires a non-default config path. Never overwrite an existing configuration without confirmation.

Change the saved language or default mode without rebuilding history:

```bash
python3 "$SKILL_DIR/scripts/state.py" configure --language en --mode alternate
```

If the user intentionally moves the Boundary folder, relink only to a path that already contains `_system/state.json`:

```bash
python3 "$SKILL_DIR/scripts/state.py" configure --root "/new/absolute/path"
```

## Daily card workflow

1. Load context:

   ```bash
   python3 "$SKILL_DIR/scripts/state.py" context
   ```

2. Resolve the mode. For an interactive run, honor the user's current choice. For scheduled delivery, use the saved default. `alternate` switches between `boundary` and `wander`.
3. Pick a primary domain with the script:

   ```bash
   python3 "$SKILL_DIR/scripts/state.py" pick --mode default
   ```

4. Generate 3 candidate topics inside that domain. Apply the selected mode's rules from `domains.md`. Compare candidate questions and summaries with the recent context. Reject semantic repeats, topics in skip cooldown, weak trivia, and topics without adequate sources.
5. Research before writing. Never publish a card from model memory alone. Follow `source-policy.md`, open the underlying sources, and prepare the structured source metadata required by `output-formats.md`.
6. Draft exactly one direct-reading card using `output-formats.md`. Do not require a guess or quiz. Write the exact delivered Markdown and structured sources to temporary files inside `<boundary-root>/_system/tmp/`.
7. Persist the complete card as `shown` before delivering it:

   ```bash
   python3 "$SKILL_DIR/scripts/state.py" record \
     --title "..." --slug "..." \
     --question "One central explanatory question" \
     --summary "One-line central explanatory payload" \
     --topic-key "stable-topic-key" \
     --domain history-archaeology \
     --domain philosophy-religion-ethics \
     --region "southern-africa" \
     --mode boundary \
     --body "<boundary-root>/_system/tmp/card.md" \
     --sources "<boundary-root>/_system/tmp/card-sources.json"
   ```

   Pass the primary domain first, followed by every applicable secondary domain. Add every applicable geographic or knowledge-tradition region. Reuse the same `topic-key` for the same central explanatory payload even when the title changes. The command saves the full card under `_system/pending/` and returns its stable `id`.

8. End with four responses in the output language: `Known`, `New`, `Deep dive`, `Skip`.

Remove the temporary input files after `record` succeeds. If the user asks for another card, repeat the workflow with full source quality. Do not impose a daily hard limit. If the user opens Boundary again on the same day, use `context.active` and `context.today` to mention existing cards and offer review, deep dive, or a new card.

## Process feedback

Use the stable card `id` returned by `record`:

```bash
python3 "$SKILL_DIR/scripts/state.py" feedback --id "..." --value new
```

Map responses as follows:

- `known`: finalize the pending card under `Cards/` and append it to the index.
- `new`: finalize the pending card, append it to the index, and count the shown domain and regions as coverage.
- `deep`: finalize the pending card and index, then produce exactly one deep research report (see "Deep dive" below). Never interpret `deep`/`深入了解` as anything less than the full in-depth report.
- `skipped`: delete the pending body, create no formal note, and retain only transparent metadata for the seven-day topic cooldown and domain weighting.

`feedback` performs the card and index writes. Do not recreate those files manually. Feedback is final for that shown card.

## Deep dive

`Deep dive`/`深入了解` is the single deepening path, and it goes all the way down. It produces one complete, in-depth research report — there is no intermediate brief and no further "choose your depth" step afterward.

1. Formulate one central research question from the card. If the user's question is already clear, use it; otherwise ask the user to define it before researching. Never expand a card title into a report without a research question.
2. Research fresh for this level, following `source-policy.md`. At least three strong, independent sources are required; use more when the question demands it. Save the exact report Markdown and its structured sources to temporary files.
3. Write the report using the deep research report format in `output-formats.md`. It must be comprehensive in depth but written in plain, accessible language — like a long-form explainer for a curious reader, not a journal article. It must be readable on its own, without the card.
4. Attach it:

   ```bash
   python3 "$SKILL_DIR/scripts/state.py" deep \
     --id "..." \
     --question "..." \
     --body "<boundary-root>/_system/tmp/deep-report.md" \
     --sources "<boundary-root>/_system/tmp/deep-report-sources.json"
   ```

   This creates `Reports/<slug>-deep-research.md` and links it back to the card. Remove the temporary input files after success.

5. End the report with two choices in the output language: `Known` and `Enough`. A deep dive never spawns an automatic follow-up.

Each level requires fresh source verification. For academic, medical, financial, legal, and contested subjects, apply the domain-specific rules in `source-policy.md`. Never provide personal diagnosis, individualized legal advice, or direct buy/sell instructions.

## Language behavior

- Support Chinese and English equally.
- Follow the configured language unless the user switches explicitly.
- Preserve original source titles; add a translated title only when helpful.
- Keep the evidence standard identical across languages.
- Search beyond the output language when better primary sources exist.

## Delivery boundary

Boundary owns topic selection, research, generation, feedback, history, and notes. A scheduler owns timing. Create, change, pause, or resume an automated daily task only when the user explicitly requests it. Let the user choose manual use, daily delivery, or both, plus a fixed or alternating selection mode.

## Non-goals

- Do not become a daily news or social-media trends digest.
- Do not optimize selections only for the user's likes.
- Do not permanently block a knowledge domain.
- Do not build political, religious, medical, financial, or personality profiles.
- Do not upload the learning history or require an external storage service.
- Do not rely on a specific notes app, plugin, or vault; every saved file is plain Markdown or JSON.
- Do not fabricate citations, quotations, dates, consensus, or false balance.

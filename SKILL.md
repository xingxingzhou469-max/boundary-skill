---
name: boundary
description: Expand a user's knowledge boundary with a verified daily knowledge card selected either for high-value cross-domain discovery or genuine random wandering. Use when the user asks for today's boundary, a daily fact, something worth knowing outside their field, a random unfamiliar topic, help escaping an information bubble, or a deeper brief/report about a Boundary card. Also use when the user replies to an active Boundary card with 已知道, 新知识, 深入了解, 暂时跳过, known, new, deep dive, or skip.
---

# Boundary

Deliver one verified, worthwhile encounter with the wider world. Optimize for durable understanding and genuine novelty, not engagement, trendiness, or agreement with the user.

## Load only what the task needs

- Read [references/domains.md](references/domains.md) before selecting a topic.
- Read [references/source-policy.md](references/source-policy.md) before researching or citing.
- Read [references/output-formats.md](references/output-formats.md) before drafting a card or report.
- Read [references/obsidian.md](references/obsidian.md) when configuring storage, saving notes, or updating the map.
- Before creating a full research report, load and follow an available PDF creation skill. The final full report must be a visually validated PDF.

## First run

If Boundary is not configured, ask for only these operational choices in one compact exchange:

1. Output language: Chinese or English. Default to the user's current language.
2. Selection mode: `boundary`, `wander`, or `alternate`.
3. Obsidian storage: a `Boundary` folder inside an existing vault, or a new independent vault.
4. The chosen absolute vault/folder path.

Do not ask for interests, administer a knowledge test, inspect unrelated conversations, or infer a personal profile. Do not create a schedule during setup unless the user explicitly asks for daily delivery.

Resolve this skill's directory as `SKILL_DIR`, then initialize local state:

```bash
python3 "$SKILL_DIR/scripts/state.py" init \
  --root "/absolute/path/chosen/by/user" \
  --language zh \
  --mode boundary \
  --storage existing
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

- `known`: finalize the pending card under `Cards/` and update the knowledge map.
- `new`: finalize the pending card, update the map, and count the shown domain and regions as coverage.
- `deep`: finalize the pending card and map, then produce exactly one small research brief. Never interpret `deep`/`深入了解` as a request for a full report.
- `skipped`: delete the pending body, create no formal note, and retain only transparent metadata for the seven-day topic cooldown and domain weighting.

`feedback` performs the card and knowledge-map writes. Do not recreate those files manually. Feedback is final for that shown card.

## Deepen in stages

Use three levels. The user's action, not the model's judgment, determines the level:

1. Daily card: explain what the topic is and why it matters.
2. Small research brief: always use this level after `deep`/`深入了解`. Formulate one central question from the card, answer it directly, and satisfy every brief quality requirement in `output-formats.md`. After fresh research, save the exact brief Markdown and its structured sources, then attach it:

   ```bash
   python3 "$SKILL_DIR/scripts/state.py" brief \
     --id "..." \
     --question "..." \
     --body "<boundary-root>/_system/tmp/brief.md" \
     --sources "<boundary-root>/_system/tmp/brief-sources.json"
   ```

   This creates `Reports/<slug>-research-brief.md` and links it back to the card. Remove the temporary input files after success.

3. Full research report: use only after the user explicitly requests a complete/full report. A full report requires a specific research question; use the user's question when it is already clear, otherwise ask the user to define it before researching. Never expand a card title into a full report without a research question. Deliver the completed report as a polished PDF, not as raw Markdown.

End every small research brief with two choices in the output language: `Enough` and `Continue to full report`. The second choice is an invitation, not permission to generate the report until the user selects it or otherwise explicitly requests a full report.

Each level requires fresh source verification. For academic, medical, financial, legal, and contested subjects, apply the domain-specific rules in `source-policy.md`. Never provide personal diagnosis, individualized legal advice, or direct buy/sell instructions.

For a full report:

1. Load the PDF skill. Verify that ReportLab, pypdf, and `pdftoppm` are available; install `requirements-pdf.txt` when the host permits it.
2. Research and create the structured report JSON defined in `output-formats.md`.
3. Build and render the report:

   ```bash
   python3 "$SKILL_DIR/scripts/report.py" build \
     --input "<boundary-root>/_system/tmp/report.json" \
     --output "<boundary-root>/Reports/<filesystem-safe-title>.pdf" \
     --render-dir "<boundary-root>/_system/tmp/pdf" \
     --manifest "<boundary-root>/_system/report-validation.json"
   ```

4. Open and visually inspect every path in `rendered_pages`. Correct the report and rebuild if any page has clipping, overlap, missing glyphs, broken tables, unreadable text, inconsistent spacing, or poor page breaks.
5. Only after every rendered page passes visual inspection, approve the unchanged PDF:

   ```bash
   python3 "$SKILL_DIR/scripts/report.py" approve \
     --manifest "<boundary-root>/_system/report-validation.json"
   ```

6. Attach the approved PDF to its originating accepted card:

   ```bash
   python3 "$SKILL_DIR/scripts/state.py" report \
     --id "..." \
     --manifest "<boundary-root>/_system/report-validation.json"
   ```

The final command verifies the PDF hash and visual approval, records its path, links it from the card, and removes rendered temporary pages. Return the PDF to the user. If PDF creation or page-by-page visual validation is unavailable, stop and explain the missing capability; do not substitute another final format.

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
- Do not modify `.obsidian` settings or require Obsidian plugins.
- Do not fabricate citations, quotations, dates, consensus, or false balance.

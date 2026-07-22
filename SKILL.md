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

4. Generate 3 candidate topics inside that domain. Apply the selected mode's rules from `domains.md`. Reject recent repeats, close paraphrases of earlier cards, weak trivia, and topics without adequate sources.
5. Research before writing. Never publish a card from model memory alone. Follow `source-policy.md` and open the underlying sources.
6. Draft exactly one direct-reading card using `output-formats.md`. Do not require a guess or quiz.
7. Record the card as `shown` immediately, including its sources:

   ```bash
   python3 "$SKILL_DIR/scripts/state.py" record \
     --title "..." --slug "..." --domain history-archaeology \
     --domain philosophy-religion-ethics \
     --mode boundary --source "https://..." --source "https://..."
   ```

   Pass the primary domain first, followed by every applicable secondary domain from the stable domain map.

8. End with four responses in the output language: `Known`, `New`, `Deep dive`, `Skip`.

If the user asks for another card, repeat the workflow with full source quality. Do not impose a daily hard limit. If the user opens Boundary again on the same day, mention today's existing card and offer review, deep dive, or a new card.

## Process feedback

Update the latest matching history item:

```bash
python3 "$SKILL_DIR/scripts/state.py" feedback --slug "..." --value new
```

Map responses as follows:

- `known`: save the card; avoid similarly basic treatments later.
- `new`: save the card and count it as an expanded boundary.
- `deep`: save the card, produce the small research brief, then link the two notes.
- `skipped`: do not create a formal Obsidian note. Reduce only the short-term frequency of that topic/primary domain; never permanently exclude a whole domain.

Save accepted cards (`known`, `new`, `deep`) and update the knowledge map using `obsidian.md`. Keep skipped items only in transparent state for temporary avoidance.

## Deepen in stages

Use three levels and advance only when requested:

1. Daily card: 3-5 minute read.
2. Small research brief: 5-10 minute read after `deep`/`深入了解`.
3. Full research report: only after the user explicitly requests a complete report.

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
- Do not modify `.obsidian` settings or require Obsidian plugins.
- Do not fabricate citations, quotations, dates, consensus, or false balance.

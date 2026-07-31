# Obsidian storage

## Storage choice

Let the user choose one of two first-class layouts:

1. **Existing vault:** create a user-approved folder, default `Boundary`, inside the chosen vault.
2. **Independent vault:** use a new user-chosen folder as the Boundary vault root.

Do not install plugins or modify `.obsidian`. Knowledge cards and research briefs remain ordinary Markdown, full research reports are PDF files, and history remains a transparent JSON state file.

## Layout

```text
<boundary-root>/
├── 知识边界地图.md or Knowledge Boundary Map.md
├── Cards/
├── Reports/
└── _system/
    ├── pending/
    ├── tmp/
    └── state.json
```

A small pointer configuration may live in the platform's user config directory so later runs can locate `<boundary-root>`. Create it only after the user explicitly chooses the destination. Allow `--config` to place it elsewhere.

## Card notes

- `state.py feedback` creates one note per accepted topic under `Cards/` and updates the managed domain block in the map.
- Use a filesystem-safe title and retain the human title inside the note.
- Include YAML frontmatter with `created`, `updated`, `type`, `mode`, `domains`, `feedback`, and `source_urls`.
- Preserve the delivered card's claim-level inline links in the saved body; a source list alone is not enough for factual claims.
- Add `[[wikilinks]]` only when the relationship is meaningful and the target note exists or is intentionally added as an open thread.
- A materially different central question may become a separate card. Reject disguised duplicates before `record`; do not merge unrelated angles into an existing note.
- Do not create a formal note for `skipped` cards.

## Research reports

- `state.py brief` saves small research briefs as Markdown under `Reports/` and creates the card link.
- `state.py report` accepts only a visually approved, unchanged PDF under `Reports/` and creates the card link. Do not create a raw Markdown full-report substitute.
- Preserve full references and source dates.
- Use `_system/tmp/pdf/` only for temporary PDF rendering files and remove them after visual validation.

## Knowledge map

Maintain a readable map grouped by the 12 primary domains. For every accepted card, add:

- a wikilink to the card;
- one sentence describing the idea that expanded the boundary;
- optional links to its report and meaningful cross-domain neighbors.

The map shows coverage, not a score, rank, streak, or judgment of the user's intelligence.

## Safety and ownership

- Write only inside the user-approved Boundary root, except for the optional pointer config.
- Treat `_system/pending/` as durable pending-card storage, not disposable cache. Use `_system/tmp/` only for reproducible inputs and rendered PDF pages.
- Keep paths visible and explain them during setup.
- Never upload notes or history.
- Preserve user edits when updating a note or map.
- If the configured root is missing or moved, stop and ask for the new location; do not guess another vault.
- The user may move, edit, or delete any file. Treat deletion as intentional unless asked to restore it.

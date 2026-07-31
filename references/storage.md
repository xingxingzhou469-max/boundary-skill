# Local storage

## Storage choice

Let the user choose one absolute folder as the Boundary root. Boundary creates
everything it needs inside that folder; there is no vault, plugin, or external
service. All files are plain Markdown and JSON, so they open on any device,
including phones.

## Layout

```text
<boundary-root>/
├── INDEX.md
├── Cards/
├── Reports/
└── _system/
    ├── pending/
    ├── tmp/
    └── state.json
```

A small pointer configuration may live in the platform's user config directory
so later runs can locate `<boundary-root>`. Create it only after the user
explicitly chooses the destination. Allow `--config` to place it elsewhere.

## Card notes

- `state.py feedback` creates one note per accepted topic under `Cards/` and
  appends one line to the index.
- Use a filesystem-safe title and retain the human title inside the note.
- Include YAML frontmatter with `created`, `updated`, `type`, `mode`,
  `domains`, `feedback`, and `source_urls`.
- Preserve the delivered card's claim-level inline links in the saved body; a
  source list alone is not enough for factual claims.
- Use only plain relative Markdown links (`[title](Cards/slug.md)`). No
  wikilinks, tags, or vault-specific syntax.
- A materially different central question may become a separate card. Reject
  disguised duplicates before `record`; do not merge unrelated angles into an
  existing note.
- Do not create a formal note for `skipped` cards.

## Deep research reports

- `state.py deep` saves the deep research report as Markdown under `Reports/`
  and links it from the originating card. A `deep` report is a standalone,
  readable document, not a wrapper that requires the card.
- Preserve full references and source dates.
- Use `_system/tmp/` only for reproducible inputs; remove temporary files after
  success.

## Index

Maintain one readable `INDEX.md` at the root. For every accepted card, append:

- a plain relative link to the card;
- one sentence describing the idea that expanded the boundary.

The index is a reading list, not a score, rank, streak, or judgment of the
user's intelligence.

## Safety and ownership

- Write only inside the user-approved Boundary root, except for the optional
  pointer config.
- Treat `_system/pending/` as durable pending-card storage, not disposable
  cache. Use `_system/tmp/` only for reproducible inputs.
- Keep paths visible and explain them during setup.
- Never upload notes or history.
- Preserve user edits when updating a note or index.
- If the configured root is missing or moved, stop and ask for the new
  location; do not guess another folder.
- The user may move, edit, or delete any file. Treat deletion as intentional
  unless asked to restore it.

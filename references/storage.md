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
- An accepted Known/New card can receive a later report. Run `feedback --id
  "..." --value deep` once to persist the request; the original feedback,
  card body, and index entry remain unchanged. Attach the report with the same
  `deep` command. Do not create a second card or rewrite feedback to Deep.
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

## Write guarantees and recovery

The local CLI uses OS file locks around mutations, first for the pointer config
and then for the resolved Boundary root. Different configs pointing to the same
root share its write lock. A competing writer fails with a visible busy message;
retry after the other process finishes. The OS releases locks when a process
exits. Lock files may remain; their existence alone does not mean a lock is held.
Do not delete a lock file while a writer may be running.

For init, record, feedback, and deep, the script stages the changed files and
keeps temporary backups. If a catchable write error occurs, it attempts to restore
the prior files so the same operation can be retried. If rollback also fails,
keep the named recovery backups and the exact error; do not initialize over the
folder or delete artifacts to bypass the error.

This is not a crash-recovery database: a power loss or forced process kill during
a multi-file update can leave partial changes. Read-only context commands read
atomic JSON files but do not lock a whole multi-file snapshot. External editors
and sync programs do not participate in the CLI locks; avoid simultaneous edits
while a command is writing. Keep normal backups of a valued library.

`context.pending_reports` lists every card with a requested but unattached
report, including entries older than the recent-history window. This includes
finalized Deep cards and Known/New cards with a recorded `report_requested_at`.
Resume those reports using their card ID without repeating feedback. `deep`
defaults to the stored question; `--question` is available for an explicit user
change. An attached report is never replaced by another request.

Source metadata retains optional `accessed_at` and `published_at` dates when
provided as valid `YYYY-MM-DD` strings. These dates record research provenance;
they do not prove that the source was opened or that its claims are correct.

These filesystem guarantees apply only to the local CLI. The
[ChatGPT task adapter](../integrations/chatgpt/README.md) delivers in a conversation
and makes no equivalent persistence or cooldown guarantee.

---
name: polyglot-notes
description: Organize durable language learning notes. Use for lesson summaries, grammar notes, vocabulary pages, mistake logs, source-text notes, Obsidian-compatible Markdown, indexes, backlinks, and review prompts.
---

# Polyglot Notes

## Role

Turn learning events into concise, retrievable notes. Notes should help future sessions resume quickly and help the learner review independently.

When note paths are created or changed, stage `note_updates[]` for `polyglot-memory`. Store paths and tags in memory, not full note bodies. Use `../polyglot-router/references/exercise-protocols.md` for note type and review prompt requirements.

Use `scripts/note_writer.py` for deterministic Markdown output:

```bash
python3 scripts/note_writer.py write < note-payload.json
```

The script prints a `note_updates[]`-compatible object. Include that object in the next `polyglot-memory` record payload.

## Note Types

- `language-index`: active goals, level, plan, links.
- `grammar-note`: one pattern, examples, contrast, drills.
- `vocabulary-topic`: words, phrases, collocations, examples.
- `mistake-pattern`: repeated error with correction history.
- `session-note`: what happened, evidence, next focus.
- `source-note`: article/dialogue/source with extracted learnings.

## Workflow

1. Read the session result or learner request.
2. Decide what deserves a durable note.
3. Write compact Markdown with frontmatter and backlinks.
4. Avoid transcript dumping; keep the lesson usable.
5. Return updated note paths and next review prompts.

## Rules

- Notes must be language-scoped and level-aware.
- Each grammar note should include examples and at least one active recall prompt.
- Each session note should include next action.
- Do not save empty roadmaps as notes.

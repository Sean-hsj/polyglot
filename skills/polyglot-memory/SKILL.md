---
name: polyglot-memory
description: Persist Polyglot Learning OS memory. Use after a real learning session or plan update to save profile changes, session results, SRS updates, assessments, note references, weak patterns, and next-focus recommendations.
---

# Polyglot Memory

## Role

Be the only mutation path for durable learning data. Specialists produce structured deltas; this skill validates and applies them through the router's `learning_store.py` script.

## Required Reference

Read `../polyglot-router/references/data-contract.md` before changing payload fields.

## Workflow

1. Validate that the session produced meaningful learning evidence.
2. Build a payload with `session`, `errors`, `new_items`, `review_results`, `assessment`, `note_updates`, and `next_focus` as applicable.
3. Run:

```bash
python3 ../polyglot-router/scripts/learning_store.py record < payload.json
```

4. Re-read the store and confirm the mutation.

## Rules

- Do not hand-edit JSON files.
- Do not persist unverified guesses as level changes.
- Collapse duplicate errors into one pattern with count.
- Store source and context for vocabulary and mistake items.
- Failed writes must be reported; never pretend progress was saved.

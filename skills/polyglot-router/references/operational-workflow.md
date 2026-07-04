# Operational Workflow

Use this reference when the learner asks for a complete session, a new roadmap, or a status-driven next step.

## Invariant

`polyglot-router` owns sequencing. `polyglot-memory` owns durable state. Other specialists produce teaching, exercises, notes, assessments, and record payload fragments, but the final persisted update must go through `skills/polyglot-router/scripts/learning_store.py record`.

## Loop

1. Resolve and validate state:
   - Run `skills/polyglot-router/scripts/learning_store.py where`.
   - Run `skills/polyglot-router/scripts/learning_store.py init` when no profile exists.
   - Run `skills/polyglot-router/scripts/learning_store.py validate`.
   - Run `skills/polyglot-router/scripts/learning_store.py read`.
2. Decide the next action:
   - Unknown or stale level -> route to `polyglot-level-check`.
   - Changed target, deadline, daily time, or goal -> route to `polyglot-roadmap`.
   - Due reviews or vocabulary expansion -> route to `polyglot-vocab`.
   - Weak grammar pattern -> route to `polyglot-grammar`.
   - Input, output, or exam need -> route to the matching specialist.
3. Produce one compact plan for the current session:
   - Include due reviews, weak patterns, target evidence, and available minutes.
   - Keep the plan small enough to finish now.
4. Run the specialist work:
   - Use `session-protocol.md` for session shape.
   - Use `exercise-protocols.md` for tasks.
   - Use `feedback-protocol.md` and `rubrics.md` for corrections and scoring.
5. Write notes when durable recall material exists:
   - Call `skills/polyglot-notes/scripts/note_writer.py write`.
   - Include the returned object in `note_updates[]`.
6. Persist learning evidence:
   - Build a record payload using `data-contract.md` and `payload-examples.md`.
   - Include only meaningful updates: session, errors, new items, review results, assessments, note updates, or next focus.
   - Run `skills/polyglot-router/scripts/learning_store.py record`.
7. Close with the next focus:
   - Run `skills/polyglot-router/scripts/learning_store.py progress` after milestone sessions or when the learner asks for status.
   - Tell the learner what changed and what the next session should do.

## First-Run Sequence

```bash
skills/polyglot-router/scripts/learning_store.py init \
  --native-language English \
  --target-language Spanish \
  --current-level A1 \
  --target-level A2 \
  --deadline 2027-07-04 \
  --daily-minutes 30 \
  --goal conversation
```

Then calculate a roadmap:

```bash
skills/polyglot-roadmap/scripts/roadmap_calculator.py calculate < roadmap-input.json
```

Then create a roadmap note:

```bash
skills/polyglot-notes/scripts/note_writer.py write < roadmap-note.json
```

Then persist the session and note index together:

```bash
skills/polyglot-router/scripts/learning_store.py record < record-payload.json
```

## Quality Bar

A complete learning turn is not just an explanation. It should leave at least one of these artifacts:

- A scored assessment or checkpoint.
- A due-review update.
- A new SRS item with a future review date.
- A weak pattern with an example and repair action.
- A durable note linked through `note_updates[]`.
- A concrete `next_focus` that the router can use next time.

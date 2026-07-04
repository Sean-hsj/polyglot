# Polyglot Learning OS

Polyglot Learning OS is an original Codex skill set for goal-driven language learning. It uses one router skill to coordinate focused specialists for level checks, roadmaps, grammar, vocabulary review, reading, conversation, writing, notes, tests, progress analysis, and durable learning memory.

## Skill Set

Use `$polyglot-router` as the normal entry point. The router decides when to call the specialist skills:

| Skill | Role |
|---|---|
| `$polyglot-router` | Chooses the next best learning action and routes the session. |
| `$polyglot-level-check` | Estimates current level from evidence. |
| `$polyglot-roadmap` | Builds a realistic plan for a target level and deadline. |
| `$polyglot-vocab` | Reviews due items and grows vocabulary with SRS. |
| `$polyglot-grammar` | Teaches and drills grammar patterns. |
| `$polyglot-reading` | Turns texts into comprehensible input practice. |
| `$polyglot-conversation` | Runs role-play and fluency practice. |
| `$polyglot-writing` | Corrects writing and extracts reusable patterns. |
| `$polyglot-notes` | Organizes durable study notes. |
| `$polyglot-test` | Runs level checks, weekly tests, and mock exams. |
| `$polyglot-progress` | Analyzes progress and repairs the plan. |
| `$polyglot-memory` | Persists profile, sessions, SRS, tests, and notes. |

## Example Prompts

- `Use $polyglot-router to help me reach B1 Japanese by December with 30 minutes per day.`
- `Use $polyglot-router to decide what I should study today.`
- `Use $polyglot-level-check to estimate my current Spanish level.`
- `Use $polyglot-writing to correct this German email and turn my mistakes into drills.`

## Local Learning Store

The router stores learning data through `skills/polyglot-router/scripts/learning_store.py`.

Default data location:

1. `POLYGLOT_LEARNING_DIR`
2. `./data` when it already contains `profile.json`
3. `~/.codex/polyglot-learning-os`

The store contains profile, session, SRS, assessment, and notes-index JSON files.

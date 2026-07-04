---
name: polyglot-level-check
description: Diagnose the learner's current level for a target language. Use for onboarding, stale progress evidence, self-reported uncertainty, CEFR/JLPT/HSK/TOPIK/DELE/Goethe-style placement, or when the router needs baseline skill estimates before planning.
---

# Polyglot Level Check

## Role

Estimate usable level from evidence, not confidence. Test recognition, production, comprehension, grammar control, vocabulary range, and task completion.

Use `../polyglot-router/references/exercise-protocols.md` for level-check structure, `../polyglot-router/references/rubrics.md` for confidence and scoring, and `../polyglot-router/references/payload-examples.md` when saving assessment evidence.

## Workflow

1. Identify target language, native language, script familiarity, and assessment target.
2. Run a short adaptive placement: begin one level below the claimed level, then move up or down.
3. Test at least three modes: comprehension, controlled production, and free production.
4. Return a level estimate per skill: reading, writing, listening, speaking/conversation, grammar, vocabulary.
5. Mark uncertainty explicitly when evidence is thin.

## Output

Return:

- `overall_level`: CEFR or closest local equivalent.
- `skill_levels`: per-skill estimates.
- `evidence`: 3-6 concrete observations.
- `blocking_gaps`: what prevents the next level.
- `recommended_next`: assessment, plan, or immediate practice.

## Rules

- One question at a time during interactive assessment.
- Avoid trivia. Prefer tasks that reveal real communicative ability.
- If the target language uses a non-native script, assess script separately.
- For exam goals, assess both language level and format readiness.

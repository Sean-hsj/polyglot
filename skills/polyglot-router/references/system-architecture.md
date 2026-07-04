# Polyglot Learning OS Architecture

## Design Goal

Build a router-led language learning system that helps a learner reach a target level by a target date across multiple languages.

## Skill Graph

`polyglot-router` is the primary entry point. It routes to:

- `polyglot-level-check`: baseline and periodic placement.
- `polyglot-roadmap`: deadline-aware learning plans.
- `polyglot-grammar`: grammar patterns and targeted drills.
- `polyglot-vocab`: vocabulary growth and spaced repetition.
- `polyglot-reading`: comprehensible input from texts and sources.
- `polyglot-conversation`: role-play and fluency practice.
- `polyglot-writing`: writing feedback and pattern extraction.
- `polyglot-notes`: durable study notes.
- `polyglot-test`: checks, level probes, and mock tests.
- `polyglot-progress`: trend analysis and plan repair.
- `polyglot-memory`: profile, session, SRS, assessment, and note persistence.

## Operating Loop

1. Assess current evidence.
2. Plan against deadline and available hours.
3. Review due items.
4. Teach the smallest blocking concept.
5. Practice through recall or production.
6. Give immediate feedback.
7. Persist structured evidence.
8. Update notes and next focus.
9. Re-test periodically.

## Durable Store Interface

All persistent state crosses one seam: `skills/polyglot-router/scripts/learning_store.py`.

Supported commands:

- `init`: create a profile and empty store.
- `validate`: verify all store files.
- `read`: return store files plus computed fields.
- `due`: list due review items.
- `progress`: summarize current progress and weak areas.
- `record`: validate and apply one structured mutation with a pre-record backup.

Specialist skills should produce session evidence. They should not write JSON directly.

## Design Principles

- One obvious entry point; many focused specialists.
- Multi-language state is first-class.
- Review load is part of the plan, not an afterthought.
- Every session should produce evidence or durable learning material.
- Level claims must be backed by assessment or performance evidence.
- The system should support CEFR by default and local exams where relevant.

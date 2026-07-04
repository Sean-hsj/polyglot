---
name: polyglot-roadmap
description: Build or revise a time-bounded language learning plan from current level, target level, deadline, daily/weekly minutes, motivation, preferred modalities, and exam or real-world outcome.
---

# Polyglot Roadmap

## Role

Convert a language goal into a weekly path with measurable checkpoints. The plan must be realistic about hours, skill balance, review load, and the learner's target use case.

Before planning, inspect current state with `../polyglot-router/scripts/learning_store.py read` or use the router-provided computed state.

Use `scripts/roadmap_calculator.py` before giving a deadline-based plan:

```bash
python3 scripts/roadmap_calculator.py calculate < roadmap-input.json
```

The script returns feasibility, required hours, available hours, weekly allocation, phases, checkpoint tests, and the next seven days.

## Inputs

- Target language and native language.
- Current level, target level, deadline.
- Daily/weekly study minutes.
- Primary goal: travel, work, exam, relocation, family, academic, reading, media, or conversation.
- Constraints: script, pronunciation, grammar distance, available materials, test date.

## Planning Method

1. Estimate required hours by level jump and goal type.
2. Compare required hours to available hours; flag impossible timelines.
3. Split the path into phases: foundation, controlled practice, input expansion, output fluency, test/readiness.
4. Allocate weekly time across review, vocabulary, grammar, input, output, and testing.
5. Define checkpoints that can be tested, not vague milestones.

## Output

Return:

- `feasibility`: realistic, aggressive, or unrealistic.
- `weekly_plan`: recurring schedule.
- `phase_plan`: date ranges, objectives, outputs.
- `checkpoint_tests`: what will prove progress.
- `next_7_days`: concrete study sessions.

## Rules

- Prefer smaller daily sessions over occasional long sessions.
- Always include review capacity; new vocabulary without review is debt.
- Exam plans must include format practice and mock tests.
- Conversation goals must include production from week one.

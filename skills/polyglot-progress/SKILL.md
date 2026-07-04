---
name: polyglot-progress
description: Analyze language learning progress, weak areas, review load, study consistency, target feasibility, and next-session priorities.
---

# Polyglot Progress

## Role

Turn logs into decisions. The learner should leave knowing whether the plan is working and exactly what to practice next.

Start with `../polyglot-router/scripts/learning_store.py progress`; inspect raw `read` output only when the progress summary is insufficient.

## Workflow

1. Load profile, sessions, SRS, assessments, and notes index.
2. Compare recent evidence against target date and target level.
3. Find trends: accuracy, weak patterns, SRS backlog, neglected skills, consistency.
4. Recommend schedule or curriculum changes.
5. Produce a concise next-session plan.

## Output

Return:

- `status`: on-track, at-risk, or off-track.
- `evidence`: concrete data points.
- `top_weaknesses`: ranked and actionable.
- `review_load`: manageable or overloaded.
- `next_session`: one recommended session.

## Rules

- Do not flatter vague progress; use evidence.
- If the target is unrealistic, say so and offer a repaired target.
- Separate "studied a lot" from "improved measurably".

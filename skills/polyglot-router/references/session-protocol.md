# Session Protocol

## Purpose

Use this protocol for any real study session. It turns a learner request into a repeatable loop that produces evidence, feedback, and durable memory updates.

## Session Types

- `review`: due SRS first, no new content unless review load is light.
- `teach`: introduce one new grammar, vocabulary, reading, writing, or conversation pattern.
- `practice`: drill known material with active recall or production.
- `test`: measure readiness or diagnose a level.
- `notes`: consolidate durable study material.
- `mixed`: combine review plus one targeted weakness.

## Opening

1. Run `validate`, then `read`.
2. Inspect `computed.due_reviews_count`, `computed.next_focus`, `computed.weak_patterns`, target level, deadline, and available minutes.
3. State the plan in one compact paragraph: session type, target skill, reason, and expected duration.

## Exercise Loop

Run one exercise at a time:

1. Present the task and expected answer format.
2. Wait for the learner's answer.
3. Apply `feedback-protocol.md`.
4. Decide whether to continue, simplify, increase difficulty, or switch patterns.
5. Stage structured evidence for the final payload.

Keep most sessions to one or two primary patterns. Interleaving is useful, but unfocused sessions do not create stable progress.

## Difficulty Control

- Accuracy below 50%: simplify and add scaffolding.
- Accuracy 50-75%: stay at the current difficulty.
- Accuracy above 75%: remove scaffolding or add a transfer task.
- Repeated critical mistake: stop and teach the smallest rule before continuing.

## Closing

End with what improved, what still blocks progress, SRS items added or reviewed, weak patterns recorded, and exact next focus.

Then call `polyglot-memory` with a structured payload.

## Minimal Payload Checklist

Every real session should include:

- `session.language`
- `session.date`
- `session.duration_minutes`
- `session.skills`
- `session.summary`
- `session.accuracy` when exercises were scored
- `errors[]` for repeated or important mistakes
- `new_items[]` for high-utility vocabulary/chunks
- `review_results[]` for SRS answers
- `next_focus[]`

# Exercise Protocols

## Purpose

Use these protocols to turn a broad session goal into concrete exercises. The router chooses the session type; each specialist chooses the smallest protocol that produces evidence.

## Vocabulary Protocol

Use for `polyglot-vocab`.

Sequence:

1. `recognition`: target language -> learner language.
2. `production`: learner language -> target language.
3. `context cloze`: fill the target item inside a sentence.
4. `collocation check`: choose or produce a natural partner word.
5. `transfer`: use the item in a sentence relevant to the learner's goal.

Rules:

- Review due items before new items.
- Add at most 5-8 new items in a normal 20-minute session.
- Prefer phrases and collocations over isolated words when they improve usage.
- Store only useful items: high-frequency, goal-relevant, repeated, or personally meaningful.

Evidence to stage:

- `review_results[]` with SM-2 quality.
- `new_items[]` with `type`, `front`, `back`, `example`, `level`, and `source`.
- `errors[]` only for repeated recall failures or wrong-meaning confusions.

## Grammar Protocol

Use for `polyglot-grammar`.

Sequence:

1. `notice`: show two examples and ask what changes.
2. `rule`: give the smallest actionable rule.
3. `recognition`: choose the correct form.
4. `controlled production`: transform or fill a sentence.
5. `error repair`: fix a realistic wrong sentence.
6. `free production`: produce one goal-relevant sentence.
7. `mixed retrieval`: combine with old vocabulary or a prior weak pattern.

Rules:

- Teach one pattern at a time.
- Use stable `pattern_id`s from `feedback-protocol.md`.
- Stop and simplify when the learner misses the same form twice.
- End with a retry of the most important corrected form.

Evidence to stage:

- `errors[]` for tracked pattern failures.
- `new_items[]` for reusable grammar chunks.
- `next_focus[]` naming the exact pattern and context.

## Writing Protocol

Use for `polyglot-writing`.

Sequence:

1. Clarify task type: sentence, message, email, journal, essay, exam answer, translation.
2. Ask for expected register and level if missing.
3. Produce a corrected version.
4. Score with `rubrics.md`.
5. Extract 1-3 highest-leverage patterns.
6. Ask for a short revision that targets one pattern.

Rules:

- Preserve intended meaning.
- Separate correctness, naturalness, register, and task completion.
- Do not turn beginner writing into advanced prose.
- Convert repeated issues into stable weak patterns.

Evidence to stage:

- `errors[]` for high-leverage or repeated patterns.
- `new_items[]` for useful phrases or collocations.
- `assessment` only when the writing task is explicitly a level/test task.

## Reading Protocol

Use for `polyglot-reading`.

Sequence:

1. Preview: title, topic, and 3-5 essential words.
2. Gist: ask for main idea before detailed translation.
3. Detail: ask 2-4 comprehension questions.
4. Language mining: extract vocabulary, chunks, grammar observations.
5. Output: summary, opinion, or transformation task.

Rules:

- Keep input at current level plus one step.
- Do not translate the whole text by default.
- Triage unknown words: ignore, infer, explain, or add to SRS.
- Avoid long copyrighted excerpts in persisted notes.

Evidence to stage:

- `new_items[]` for selected vocabulary and chunks.
- `note_updates[]` for source notes.
- `errors[]` when comprehension failure reveals a pattern.

## Conversation Protocol

Use for `polyglot-conversation`.

Sequence:

1. Set scenario, role, register, and target pattern.
2. Run one conversational turn at a time.
3. Correct according to mode: fluency, accuracy, survival, exam.
4. Ask for retry after meaning-changing or target-pattern errors.
5. End with a replay: the learner performs the same scenario more smoothly.

Rules:

- Fluency mode should not over-correct.
- Accuracy mode should record weak patterns.
- Survival mode should teach repair phrases.
- Exam mode should score task success, range, accuracy, and repair ability.

Evidence to stage:

- `errors[]` for repeated breakdowns.
- `new_items[]` for repair phrases and scenario chunks.
- `session.accuracy` only when turns were scored.

## Test Protocol

Use for `polyglot-test` and `polyglot-level-check`.

Sequence:

1. State test purpose and expected level.
2. Test comprehension and production.
3. Include at least one free-production task.
4. Score with `rubrics.md`.
5. Produce a confidence level: high, medium, or low.
6. Save assessment only when evidence is sufficient.

Rules:

- Do not infer a level from vocabulary recognition alone.
- Use exam-specific formats when the learner has an exam goal.
- Low-confidence results should trigger more evidence, not a firm level change.

Evidence to stage:

- `assessment` with `type`, `overall_level`, `skill_levels`, `evidence`, and confidence.
- `next_focus[]` naming the plan repair.

## Notes Protocol

Use for `polyglot-notes`.

Sequence:

1. Choose note type: session, grammar, vocabulary, mistake, source, roadmap.
2. Write compact Markdown with frontmatter.
3. Include examples and active recall prompts.
4. Link related notes and source session.
5. Stage `note_updates[]` with path, tags, language, and linked objects.

Rules:

- Store durable learning material, not raw chat transcripts.
- Every note should support later review or resumption.
- Empty roadmaps and generic advice should not become notes.

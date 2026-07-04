# Feedback Protocol

## Goal

Give feedback that changes future behavior. Correctness alone is not enough; the learner needs a reason, a usable pattern, and a next retrieval opportunity.

## Per-Answer Feedback

Use this order:

1. Verdict: correct, mostly correct, understandable but unnatural, or incorrect.
2. Corrected answer.
3. One reason at the learner's level.
4. Pattern label when the issue should be tracked.
5. Retry or micro-drill when the error matters.

## Severity

- `minor`: typo, small agreement issue, meaning clear.
- `moderate`: recurring form issue or unnatural phrase that affects quality.
- `major`: grammar, vocabulary, or structure issue that blocks reliable communication.
- `critical`: misunderstanding, wrong meaning, exam-failing task error, or fossilized pattern.

## Error Pattern IDs

Use stable IDs:

`<language-code>-<category>-<short-pattern>`

Examples:

- `es-grammar-adjective-gender`
- `ja-particle-wa-ga`
- `de-case-dative-after-mit`
- `fr-register-tu-vous`

## Scoring

When scoring an exercise, use:

- `1.0`: correct and natural for the target level.
- `0.75`: correct core answer with minor issue.
- `0.5`: understandable but needs correction.
- `0.25`: partial recall.
- `0`: wrong, blank, or different meaning.

For SRS review, map to SM-2 quality:

- `5`: instant correct recall.
- `4`: correct with hesitation.
- `3`: correct with effort or small self-correction.
- `2`: incorrect but recognized after seeing answer.
- `1`: familiar but not recalled.
- `0`: complete miss.

## Correction Discipline

- Do not correct every possible flaw in fluency mode.
- Do correct the target pattern and any meaning-changing error.
- Separate "wrong" from "grammatical but unnatural".
- Ask the learner to retry critical forms immediately.

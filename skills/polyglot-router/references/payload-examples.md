# Payload Examples

## Vocabulary And Grammar Session

```json
{
  "session": {
    "language": "Spanish",
    "date": "2026-07-04",
    "duration_minutes": 20,
    "skills": ["vocabulary", "grammar"],
    "summary": "Practiced introductions and adjective gender agreement.",
    "accuracy": 0.7
  },
  "errors": [
    {
      "pattern_id": "es-grammar-adjective-gender",
      "category": "grammar",
      "severity": "major",
      "learner_answer": "casa bonito",
      "correct_answer": "casa bonita",
      "context": "noun-adjective agreement"
    }
  ],
  "new_items": [
    {
      "id": "es-phrase-encantado",
      "type": "phrase",
      "front": "encantado",
      "back": "pleased to meet you",
      "example": "Encantado de conocerte.",
      "level": "A1"
    }
  ],
  "review_results": [
    {
      "id": "es-phrase-encantado",
      "quality": 4
    }
  ],
  "next_focus": ["Drill adjective gender agreement in self-introductions"]
}
```

## Assessment Result

```json
{
  "session": {
    "language": "Spanish",
    "date": "2026-07-04",
    "duration_minutes": 15,
    "skills": ["reading", "writing", "grammar", "vocabulary"],
    "summary": "Ran a short level check.",
    "accuracy": 0.62
  },
  "assessment": {
    "type": "level_probe",
    "overall_level": "A2",
    "skill_levels": {
      "reading": "A2",
      "writing": "A1",
      "grammar": "A2",
      "vocabulary": "A2"
    },
    "evidence": [
      "Can understand short everyday texts.",
      "Writing breaks down on past tense and agreement."
    ]
  },
  "next_focus": ["Build A2 writing control before increasing reading difficulty"]
}
```

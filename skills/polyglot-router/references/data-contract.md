# Data Contract

## Store Location

Default resolution:

1. `POLYGLOT_LEARNING_DIR`
2. `./data` when it already contains `profile.json`
3. `~/.codex/polyglot-learning-os`

## Files

- `profile.json`: learner identity, languages, active language, goals, preferences.
- `sessions.json`: immutable session summaries.
- `srs.json`: review items and scheduling fields.
- `assessments.json`: placement tests, mock tests, checkpoint results.
- `notes-index.json`: note paths and linked learning objects.

## Profile Shape

```json
{
  "learner": {
    "name": "",
    "native_language": "",
    "other_languages": []
  },
  "active_language": "Japanese",
  "languages": {
    "Japanese": {
      "current_level": "A1",
      "target_level": "B1",
      "deadline": "2026-12-31",
      "daily_minutes": 30,
      "goal": "travel and conversation",
      "skill_levels": {
        "reading": "A1",
        "writing": "A1",
        "listening": "A1",
        "conversation": "A1",
        "grammar": "A1",
        "vocabulary": "A1"
      },
      "weak_patterns": [],
      "next_focus": []
    }
  }
}
```

## Session Payload

```json
{
  "session": {
    "language": "Japanese",
    "date": "2026-07-04",
    "duration_minutes": 20,
    "skills": ["grammar", "vocabulary"],
    "summary": "",
    "accuracy": 0.7
  },
  "errors": [
    {
      "pattern_id": "ja-particle-wa-ga",
      "category": "grammar",
      "severity": "moderate",
      "learner_answer": "",
      "correct_answer": "",
      "context": ""
    }
  ],
  "new_items": [
    {
      "id": "ja-phrase-001",
      "type": "phrase",
      "front": "",
      "back": "",
      "example": "",
      "level": "A1",
      "source": "session"
    }
  ],
  "review_results": [
    {
      "id": "ja-phrase-001",
      "quality": 4
    }
  ],
  "next_focus": ["Practice は vs が in self-introductions"]
}
```

## Mutation Rules

- Sessions are append-only.
- SRS items are upserted by `id`.
- Level changes require assessment evidence.
- Weak patterns are keyed by stable `pattern_id`.
- Notes store paths and tags, not full note bodies.

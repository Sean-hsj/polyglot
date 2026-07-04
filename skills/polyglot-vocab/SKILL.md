---
name: polyglot-vocab
description: Build, review, and maintain vocabulary with spaced repetition. Use for due reviews, new word intake, topic vocabulary, collocations, example sentences, active recall, and forgetting-curve management.
---

# Polyglot Vocab

## Role

Maintain vocabulary as a durable active-recall system. Prioritize useful words, collocations, phrases, and reusable chunks over isolated translation lists.

Before running a review, inspect due items through `../polyglot-router/scripts/learning_store.py due`. Use `../polyglot-router/references/feedback-protocol.md` for SRS quality scoring.

## Workflow

1. Load due items through the router store.
2. Review due items before adding new words.
3. Introduce new vocabulary in context.
4. Test both directions when useful: target -> native and native -> target.
5. Store each item with example, category, level, source, and review quality.

## Review Order

1. Due items with prior failed recall.
2. Due high-priority phrases and collocations.
3. Due normal vocabulary.
4. New items only if review load is manageable.

Cap new items when the learner has many due reviews.

## Item Types

- `word`: single lexical item.
- `phrase`: reusable expression.
- `collocation`: words that naturally appear together.
- `grammar_chunk`: pattern worth memorizing.
- `kanji_hanzi_hanja_script`: script item when relevant.

## Rules

- Do not add every unknown word. Add high-utility or repeatedly encountered items.
- Prefer learner-relevant topics: work, travel, daily life, exams, interests.
- A correct answer with slow recall is not the same as instant recall.
- Failed items should reappear soon and also inform grammar or reading sessions.

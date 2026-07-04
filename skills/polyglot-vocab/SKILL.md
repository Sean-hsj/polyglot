---
name: polyglot-vocab
description: Build, review, and maintain vocabulary with spaced repetition. Use for due reviews, new word intake, topic vocabulary, collocations, example sentences, active recall, and forgetting-curve management.
---

# Polyglot Vocab

## Role

Maintain vocabulary as a durable active-recall system. Prioritize useful words, collocations, phrases, and reusable chunks over isolated translation lists.

## Workflow

1. Load due items through the router store.
2. Review due items before adding new words.
3. Introduce new vocabulary in context.
4. Test both directions when useful: target -> native and native -> target.
5. Store each item with example, category, level, source, and review quality.

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

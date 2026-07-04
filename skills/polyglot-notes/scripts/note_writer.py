#!/usr/bin/env python3
"""Create deterministic Polyglot Learning OS Markdown notes.

Input is a JSON object on stdin. The script writes one note and prints a
`note_updates[]`-compatible JSON object for polyglot-memory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


NOTE_TYPES = {
    "session": "Sessions",
    "grammar": "Grammar",
    "vocabulary": "Vocabulary",
    "mistake": "Mistakes",
    "source": "Sources",
    "roadmap": "Roadmaps",
}


class NoteError(Exception):
    pass


def today() -> str:
    return date.today().isoformat()


def notes_root() -> Path:
    env = os.environ.get("POLYGLOT_NOTES_DIR")
    if env:
        return Path(env).expanduser()
    store = os.environ.get("POLYGLOT_LEARNING_DIR")
    if store:
        return Path(store).expanduser() / "notes"
    return Path.home() / ".codex" / "polyglot-learning-os" / "notes"


def slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "note"


def require_str(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise NoteError(f"{field} must be a string")
    if not allow_empty and not value.strip():
        raise NoteError(f"{field} must not be empty")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise NoteError(f"{field} must be a list")
    return value


def yaml_list(values: list[Any]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(json.dumps(str(value), ensure_ascii=False) for value in values) + "]"


def bullet_list(values: list[Any], fallback: str = "None yet.") -> str:
    if not values:
        return fallback
    return "\n".join(f"- {value}" for value in values)


def build_markdown(payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    note_type = require_str(payload.get("type"), "type")
    if note_type not in NOTE_TYPES:
        raise NoteError(f"type must be one of {sorted(NOTE_TYPES)}")
    language = require_str(payload.get("language"), "language")
    title = require_str(payload.get("title"), "title")
    created = payload.get("date") or today()
    tags = [str(tag) for tag in require_list(payload.get("tags"), "tags")]
    linked = [str(item) for item in require_list(payload.get("linked_objects"), "linked_objects")]

    frontmatter = [
        "---",
        f'title: "{title}"',
        f'type: "{note_type}"',
        f'language: "{language}"',
        f'date: "{created}"',
        f"tags: {yaml_list(tags)}",
        f"linked_objects: {yaml_list(linked)}",
        "---",
        "",
    ]

    sections = [f"# {title}", ""]
    summary = payload.get("summary", "")
    if summary:
        sections += ["## Summary", str(summary), ""]

    examples = require_list(payload.get("examples"), "examples")
    if examples:
        sections += ["## Examples", bullet_list(examples), ""]

    patterns = require_list(payload.get("patterns"), "patterns")
    if patterns:
        sections += ["## Patterns", bullet_list(patterns), ""]

    vocabulary = require_list(payload.get("vocabulary"), "vocabulary")
    if vocabulary:
        sections += ["## Vocabulary", bullet_list(vocabulary), ""]

    mistakes = require_list(payload.get("mistakes"), "mistakes")
    if mistakes:
        sections += ["## Mistakes", bullet_list(mistakes), ""]

    prompts = require_list(payload.get("review_prompts"), "review_prompts")
    if prompts:
        sections += ["## Review Prompts", bullet_list(prompts), ""]

    next_actions = require_list(payload.get("next_actions"), "next_actions")
    sections += ["## Next Actions", bullet_list(next_actions), ""]

    body = "\n".join(frontmatter + sections).rstrip() + "\n"
    note_update = {
        "path": "",
        "language": language,
        "type": note_type,
        "title": title,
        "tags": tags,
        "linked_objects": linked,
    }
    return body, note_update


def command_write(args: argparse.Namespace) -> None:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise NoteError("payload must be an object")
        markdown, update = build_markdown(payload)
        note_type = payload["type"]
        language = payload["language"]
        title = payload["title"]
        root = Path(args.root).expanduser() if args.root else notes_root()
        path = root / language / NOTE_TYPES[note_type] / f"{payload.get('date') or today()}-{slug(title)}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not args.force:
            raise NoteError(f"note already exists: {path}; pass --force to replace it")
        path.write_text(markdown, encoding="utf-8")
        update["path"] = str(path)
        print(json.dumps(update, ensure_ascii=False, indent=2))
    except (json.JSONDecodeError, NoteError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write Polyglot Learning OS notes")
    sub = parser.add_subparsers(required=True)
    p_write = sub.add_parser("write")
    p_write.add_argument("--root")
    p_write.add_argument("--force", action="store_true")
    p_write.set_defaults(func=command_write)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

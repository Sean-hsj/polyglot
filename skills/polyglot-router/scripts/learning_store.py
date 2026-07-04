#!/usr/bin/env python3
"""Local durable store for Polyglot Learning OS.

This script is the narrow interface for all persistent learning state. Skills
should call it instead of hand-editing JSON files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any


STORE_FILES = {
    "profile": "profile.json",
    "sessions": "sessions.json",
    "srs": "srs.json",
    "assessments": "assessments.json",
    "notes_index": "notes-index.json",
}

SKILLS = ("reading", "writing", "listening", "conversation", "grammar", "vocabulary")
LEVELS = {"unknown", "A0", "A1", "A2", "B1", "B2", "C1", "C2"}
ITEM_TYPES = {"word", "phrase", "collocation", "grammar_chunk", "script", "sentence"}
SEVERITY_RANK = {"minor": 1, "moderate": 2, "major": 3, "critical": 4}


class StoreError(Exception):
    """User-facing validation or I/O error."""


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def today() -> str:
    return date.today().isoformat()


def parse_ymd(value: str, field: str = "date") -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise StoreError(f"{field} must be YYYY-MM-DD, got {value!r}") from exc


def date_plus(value: str, days: int) -> str:
    return (parse_ymd(value) + timedelta(days=days)).isoformat()


def store_dir() -> Path:
    env = os.environ.get("POLYGLOT_LEARNING_DIR")
    if env:
        return Path(env).expanduser()
    cwd_data = Path.cwd() / "data"
    if (cwd_data / STORE_FILES["profile"]).exists():
        return cwd_data
    return Path.home() / ".codex" / "polyglot-learning-os"


def json_path(root: Path, key: str) -> Path:
    return root / STORE_FILES[key]


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StoreError(f"Invalid JSON in {path}: {exc}") from exc


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(path)
    try:
        dir_fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError:
        pass


def load_store(root: Path) -> dict[str, Any]:
    return {
        "profile": read_json(json_path(root, "profile"), None),
        "sessions": read_json(json_path(root, "sessions"), {"sessions": []}),
        "srs": read_json(json_path(root, "srs"), {"items": []}),
        "assessments": read_json(json_path(root, "assessments"), {"assessments": []}),
        "notes_index": read_json(json_path(root, "notes_index"), {"notes": []}),
    }


def write_store(root: Path, store: dict[str, Any]) -> None:
    for key in STORE_FILES:
        atomic_write_json(json_path(root, key), store[key])


def backup_store(root: Path, tag: str) -> Path:
    backup_dir = root / ".backups" / tag
    backup_dir.mkdir(parents=True, exist_ok=True)
    for filename in STORE_FILES.values():
        source = root / filename
        if source.exists():
            shutil.copy2(source, backup_dir / filename)
    return backup_dir


def require_dict(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StoreError(f"{field} must be an object")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise StoreError(f"{field} must be a list")
    return value


def require_str(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise StoreError(f"{field} must be a string")
    if not allow_empty and not value.strip():
        raise StoreError(f"{field} must not be empty")
    return value


def require_number(value: Any, field: str, *, minimum: float | None = None, maximum: float | None = None) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise StoreError(f"{field} must be a number")
    if minimum is not None and value < minimum:
        raise StoreError(f"{field} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise StoreError(f"{field} must be <= {maximum}")
    return float(value)


def normalize_level(value: str, field: str) -> str:
    value = require_str(value, field)
    if value not in LEVELS:
        raise StoreError(f"{field} must be one of {sorted(LEVELS)}")
    return value


def slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "item"


def next_session_id(sessions: dict[str, Any]) -> str:
    max_id = 0
    for session in sessions.get("sessions", []):
        raw = str(session.get("session_id", ""))
        match = re.fullmatch(r"session-(\d+)", raw)
        if match:
            max_id = max(max_id, int(match.group(1)))
    return f"session-{max_id + 1:03d}"


def streak_from_sessions(sessions: dict[str, Any]) -> int:
    dates = sorted({s.get("date") for s in sessions.get("sessions", []) if isinstance(s.get("date"), str)}, reverse=True)
    if not dates:
        return 0
    expected = parse_ymd(dates[0])
    streak = 0
    for raw in dates:
        current = parse_ymd(raw)
        if current == expected:
            streak += 1
            expected = expected - timedelta(days=1)
        elif current < expected:
            break
    return streak


def computed_state(store: dict[str, Any]) -> dict[str, Any]:
    profile = store["profile"] or {}
    sessions = store["sessions"]
    srs = store["srs"]
    today_value = today()
    due_items = [item for item in srs.get("items", []) if item.get("due", today_value) <= today_value]
    active_language = profile.get("active_language")
    language_state = profile.get("languages", {}).get(active_language, {}) if active_language else {}
    skill_counts = Counter()
    for session in sessions.get("sessions", []):
        for skill in session.get("skills", []):
            skill_counts[skill] += 1
    return {
        "active_language": active_language,
        "total_sessions": len(sessions.get("sessions", [])),
        "next_session_id": next_session_id(sessions),
        "streak_days": streak_from_sessions(sessions),
        "due_reviews_count": len(due_items),
        "due_review_ids": [item.get("id") for item in due_items],
        "next_focus": language_state.get("next_focus", []),
        "weak_patterns": language_state.get("weak_patterns", []),
        "skills_practiced": dict(skill_counts),
    }


def build_profile(args: argparse.Namespace) -> dict[str, Any]:
    language = require_str(args.target_language, "target_language")
    current_level = normalize_level(args.current_level, "current_level")
    target_level = normalize_level(args.target_level, "target_level")
    parse_ymd(args.deadline, "deadline")
    daily_minutes = int(require_number(args.daily_minutes, "daily_minutes", minimum=1))
    return {
        "learner": {
            "name": args.name,
            "native_language": require_str(args.native_language, "native_language"),
            "other_languages": [v.strip() for v in args.other_languages if v.strip()],
        },
        "active_language": language,
        "created": today(),
        "updated": today(),
        "languages": {
            language: {
                "current_level": current_level,
                "target_level": target_level,
                "deadline": args.deadline,
                "daily_minutes": daily_minutes,
                "goal": args.goal,
                "total_sessions": 0,
                "total_study_minutes": 0,
                "skill_levels": {skill: current_level for skill in SKILLS},
                "weak_patterns": [],
                "next_focus": [],
            }
        },
        "preferences": {
            "feedback_language": args.native_language,
            "session_style": "balanced",
            "gamification": False,
        },
    }


def validate_profile(profile: Any) -> None:
    profile = require_dict(profile, "profile")
    learner = require_dict(profile.get("learner"), "profile.learner")
    require_str(learner.get("native_language"), "profile.learner.native_language")
    require_list(learner.get("other_languages", []), "profile.learner.other_languages")
    active = require_str(profile.get("active_language"), "profile.active_language")
    languages = require_dict(profile.get("languages"), "profile.languages")
    if active not in languages:
        raise StoreError("profile.active_language must exist in profile.languages")
    for language, state in languages.items():
        state = require_dict(state, f"profile.languages.{language}")
        normalize_level(state.get("current_level"), f"profile.languages.{language}.current_level")
        normalize_level(state.get("target_level"), f"profile.languages.{language}.target_level")
        parse_ymd(state.get("deadline"), f"profile.languages.{language}.deadline")
        require_number(state.get("daily_minutes"), f"profile.languages.{language}.daily_minutes", minimum=1)
        require_dict(state.get("skill_levels"), f"profile.languages.{language}.skill_levels")
        require_list(state.get("weak_patterns", []), f"profile.languages.{language}.weak_patterns")
        require_list(state.get("next_focus", []), f"profile.languages.{language}.next_focus")


def validate_srs_item(item: Any, field: str) -> None:
    item = require_dict(item, field)
    require_str(item.get("id"), f"{field}.id")
    item_type = require_str(item.get("type"), f"{field}.type")
    if item_type not in ITEM_TYPES:
        raise StoreError(f"{field}.type must be one of {sorted(ITEM_TYPES)}")
    require_str(item.get("front"), f"{field}.front")
    require_str(item.get("back"), f"{field}.back")
    parse_ymd(item.get("due", today()), f"{field}.due")
    require_number(item.get("repetitions", 0), f"{field}.repetitions", minimum=0)
    require_number(item.get("interval_days", 0), f"{field}.interval_days", minimum=0)
    require_number(item.get("easiness_factor", 2.5), f"{field}.easiness_factor", minimum=1.3)


def validate_store(store: dict[str, Any]) -> None:
    validate_profile(store["profile"])
    sessions = require_dict(store["sessions"], "sessions")
    for i, session in enumerate(require_list(sessions.get("sessions", []), "sessions.sessions")):
        validate_session(session, f"sessions.sessions[{i}]", allow_missing_id=False)
    srs = require_dict(store["srs"], "srs")
    ids = set()
    for i, item in enumerate(require_list(srs.get("items", []), "srs.items")):
        validate_srs_item(item, f"srs.items[{i}]")
        item_id = item["id"]
        if item_id in ids:
            raise StoreError(f"duplicate SRS item id {item_id!r}")
        ids.add(item_id)
    require_list(require_dict(store["assessments"], "assessments").get("assessments", []), "assessments.assessments")
    require_list(require_dict(store["notes_index"], "notes_index").get("notes", []), "notes_index.notes")


def validate_session(session: Any, field: str, *, allow_missing_id: bool) -> None:
    session = require_dict(session, field)
    if not allow_missing_id or session.get("session_id") is not None:
        require_str(session.get("session_id"), f"{field}.session_id")
    require_str(session.get("language"), f"{field}.language")
    parse_ymd(session.get("date"), f"{field}.date")
    require_number(session.get("duration_minutes"), f"{field}.duration_minutes", minimum=0)
    skills = require_list(session.get("skills"), f"{field}.skills")
    if not skills:
        raise StoreError(f"{field}.skills must not be empty")
    for skill in skills:
        if skill not in SKILLS:
            raise StoreError(f"{field}.skills contains unknown skill {skill!r}")
    if "accuracy" in session:
        require_number(session["accuracy"], f"{field}.accuracy", minimum=0, maximum=1)
    require_str(session.get("summary", ""), f"{field}.summary", allow_empty=True)


def validate_payload(payload: Any, store: dict[str, Any]) -> None:
    payload = require_dict(payload, "payload")
    if not any(payload.get(key) for key in ("session", "errors", "new_items", "review_results", "assessment", "note_updates", "next_focus")):
        raise StoreError("payload must contain at least one meaningful update")
    if payload.get("session"):
        validate_session(payload["session"], "payload.session", allow_missing_id=True)
    for i, error in enumerate(payload.get("errors", [])):
        error = require_dict(error, f"payload.errors[{i}]")
        require_str(error.get("pattern_id"), f"payload.errors[{i}].pattern_id")
        require_str(error.get("category"), f"payload.errors[{i}].category")
        severity = require_str(error.get("severity", "moderate"), f"payload.errors[{i}].severity")
        if severity not in SEVERITY_RANK:
            raise StoreError(f"payload.errors[{i}].severity must be one of {sorted(SEVERITY_RANK)}")
    new_ids = set()
    for i, item in enumerate(payload.get("new_items", [])):
        validate_srs_item({**item, "due": item.get("due", today())}, f"payload.new_items[{i}]")
        item_id = item["id"]
        if item_id in new_ids:
            raise StoreError(f"duplicate new item id {item_id!r}")
        new_ids.add(item_id)
    existing_ids = {item.get("id") for item in store["srs"].get("items", [])}
    for i, result in enumerate(payload.get("review_results", [])):
        result = require_dict(result, f"payload.review_results[{i}]")
        item_id = require_str(result.get("id"), f"payload.review_results[{i}].id")
        if item_id not in existing_ids and item_id not in new_ids:
            raise StoreError(f"review result references unknown SRS item {item_id!r}")
        require_number(result.get("quality"), f"payload.review_results[{i}].quality", minimum=0, maximum=5)
    for i, note in enumerate(payload.get("note_updates", [])):
        note = require_dict(note, f"payload.note_updates[{i}]")
        require_str(note.get("path"), f"payload.note_updates[{i}].path")
    if payload.get("next_focus") is not None:
        focus = require_list(payload["next_focus"], "payload.next_focus")
        for i, value in enumerate(focus):
            require_str(value, f"payload.next_focus[{i}]")


def sm2(item: dict[str, Any], quality: int, review_date: str) -> dict[str, Any]:
    quality = max(0, min(5, int(quality)))
    reps = int(item.get("repetitions", 0))
    interval = int(item.get("interval_days", 0))
    ef = float(item.get("easiness_factor", 2.5))

    if quality < 3:
        reps = 0
        interval = 1
    else:
        reps += 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            interval = max(1, round(interval * ef))
        ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    updated = dict(item)
    updated["repetitions"] = reps
    updated["interval_days"] = interval
    updated["easiness_factor"] = round(ef, 3)
    updated["last_reviewed"] = review_date
    updated["due"] = date_plus(review_date, interval)
    updated["last_quality"] = quality
    updated["total_reviews"] = int(updated.get("total_reviews", 0)) + 1
    return updated


def upsert_weak_patterns(profile: dict[str, Any], language: str, errors: list[dict[str, Any]], session_date: str) -> None:
    if not errors:
        return
    language_state = profile["languages"].setdefault(language, {})
    existing = {item["pattern_id"]: item for item in language_state.get("weak_patterns", []) if "pattern_id" in item}
    for error in errors:
        pattern_id = error["pattern_id"]
        current = existing.setdefault(pattern_id, {
            "pattern_id": pattern_id,
            "category": error.get("category", "unknown"),
            "severity": error.get("severity", "moderate"),
            "count": 0,
            "last_seen": session_date,
            "examples": [],
        })
        current["count"] = int(current.get("count", 0)) + int(error.get("count", 1))
        current["last_seen"] = session_date
        if SEVERITY_RANK.get(error.get("severity", "moderate"), 2) > SEVERITY_RANK.get(current.get("severity", "moderate"), 2):
            current["severity"] = error["severity"]
        example = {
            "learner_answer": error.get("learner_answer", ""),
            "correct_answer": error.get("correct_answer", ""),
            "context": error.get("context", ""),
            "date": session_date,
        }
        if any(example.values()):
            current.setdefault("examples", []).append(example)
            current["examples"] = current["examples"][-3:]
    language_state["weak_patterns"] = sorted(
        existing.values(),
        key=lambda item: (-SEVERITY_RANK.get(item.get("severity", "moderate"), 2), -int(item.get("count", 0)), item["pattern_id"]),
    )


def apply_record(store: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    profile = store["profile"]
    if not profile:
        raise StoreError("store is not initialized; run init first")
    session = dict(payload.get("session") or {})
    language = session.get("language") or profile.get("active_language")
    if language not in profile.get("languages", {}):
        raise StoreError(f"language {language!r} does not exist in profile.languages")
    session_date = session.get("date") or today()

    if session:
        session.setdefault("session_id", next_session_id(store["sessions"]))
        session.setdefault("recorded_at", utc_now())
        session.setdefault("summary", "")
        session["errors"] = payload.get("errors", [])
        store["sessions"].setdefault("sessions", []).append(session)
        language_state = profile["languages"][language]
        language_state["total_sessions"] = int(language_state.get("total_sessions", 0)) + 1
        language_state["total_study_minutes"] = int(language_state.get("total_study_minutes", 0)) + int(session.get("duration_minutes", 0))
        language_state["last_session_date"] = session_date

    srs_by_id = {item["id"]: item for item in store["srs"].get("items", []) if "id" in item}
    for item in payload.get("new_items", []):
        normalized = dict(item)
        normalized.setdefault("language", language)
        normalized.setdefault("created", session_date)
        normalized.setdefault("due", session_date)
        normalized.setdefault("repetitions", 0)
        normalized.setdefault("interval_days", 0)
        normalized.setdefault("easiness_factor", 2.5)
        normalized.setdefault("priority", "medium")
        normalized.setdefault("source", session.get("session_id", "manual"))
        srs_by_id[normalized["id"]] = {**srs_by_id.get(normalized["id"], {}), **normalized}
    for result in payload.get("review_results", []):
        item_id = result["id"]
        srs_by_id[item_id] = sm2(srs_by_id[item_id], int(result["quality"]), session_date)
    store["srs"]["items"] = sorted(srs_by_id.values(), key=lambda item: (item.get("due", ""), item.get("language", ""), item.get("id", "")))

    if payload.get("assessment"):
        assessment = dict(payload["assessment"])
        assessment.setdefault("id", f"assessment-{len(store['assessments'].get('assessments', [])) + 1:03d}")
        assessment.setdefault("language", language)
        assessment.setdefault("date", session_date)
        store["assessments"].setdefault("assessments", []).append(assessment)
        if assessment.get("overall_level"):
            profile["languages"][language]["current_level"] = normalize_level(assessment["overall_level"], "assessment.overall_level")

    for note in payload.get("note_updates", []):
        normalized_note = dict(note)
        normalized_note.setdefault("language", language)
        normalized_note.setdefault("created", session_date)
        store["notes_index"].setdefault("notes", []).append(normalized_note)

    upsert_weak_patterns(profile, language, payload.get("errors", []), session_date)
    if payload.get("next_focus") is not None:
        profile["languages"][language]["next_focus"] = payload["next_focus"]
    profile["active_language"] = language
    profile["updated"] = today()
    return store


def cmd_init(args: argparse.Namespace) -> None:
    root = store_dir()
    if json_path(root, "profile").exists() and not args.force:
        raise StoreError(f"store already initialized at {root}; pass --force to replace it")
    store = {
        "profile": build_profile(args),
        "sessions": {"sessions": []},
        "srs": {"items": []},
        "assessments": {"assessments": []},
        "notes_index": {"notes": []},
    }
    write_store(root, store)
    print(root)


def cmd_read(_args: argparse.Namespace) -> None:
    root = store_dir()
    store = load_store(root)
    output = {"store": str(root), **store, "computed": computed_state(store)}
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_due(args: argparse.Namespace) -> None:
    root = store_dir()
    store = load_store(root)
    today_value = args.date or today()
    parse_ymd(today_value, "date")
    items = [item for item in store["srs"].get("items", []) if item.get("due", today_value) <= today_value]
    if args.language:
        items = [item for item in items if item.get("language") == args.language]
    print(json.dumps({"date": today_value, "due": items, "count": len(items)}, ensure_ascii=False, indent=2))


def cmd_record(_args: argparse.Namespace) -> None:
    root = store_dir()
    store = load_store(root)
    payload = json.load(sys.stdin)
    validate_payload(payload, store)
    tag = f"pre-record-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
    backup_path = backup_store(root, tag)
    updated = apply_record(store, payload)
    validate_store(updated)
    write_store(root, updated)
    print(json.dumps({"ok": True, "store": str(root), "backup": str(backup_path), "computed": computed_state(updated)}, ensure_ascii=False))


def cmd_validate(_args: argparse.Namespace) -> None:
    root = store_dir()
    store = load_store(root)
    validate_store(store)
    print(json.dumps({"ok": True, "store": str(root), "computed": computed_state(store)}, ensure_ascii=False, indent=2))


def cmd_progress(_args: argparse.Namespace) -> None:
    root = store_dir()
    store = load_store(root)
    validate_store(store)
    computed = computed_state(store)
    language = computed["active_language"]
    sessions = [s for s in store["sessions"].get("sessions", []) if s.get("language") == language]
    recent = sessions[-5:]
    avg_accuracy_values = [s["accuracy"] for s in recent if isinstance(s.get("accuracy"), (int, float))]
    avg_accuracy = sum(avg_accuracy_values) / len(avg_accuracy_values) if avg_accuracy_values else None
    output = {
        "language": language,
        "status": {
            "sessions": len(sessions),
            "streak_days": computed["streak_days"],
            "due_reviews_count": computed["due_reviews_count"],
            "average_recent_accuracy": avg_accuracy,
        },
        "next_focus": computed["next_focus"],
        "weak_patterns": computed["weak_patterns"][:5],
        "recent_sessions": recent,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Polyglot Learning OS local store")
    sub = parser.add_subparsers(required=True)

    sub.add_parser("where").set_defaults(func=lambda _args: print(store_dir()))
    sub.add_parser("read").set_defaults(func=cmd_read)
    sub.add_parser("validate").set_defaults(func=cmd_validate)
    sub.add_parser("progress").set_defaults(func=cmd_progress)

    p_due = sub.add_parser("due")
    p_due.add_argument("--date")
    p_due.add_argument("--language")
    p_due.set_defaults(func=cmd_due)

    p_init = sub.add_parser("init")
    p_init.add_argument("--name", default="")
    p_init.add_argument("--native-language", required=True)
    p_init.add_argument("--other-languages", nargs="*", default=[])
    p_init.add_argument("--target-language", required=True)
    p_init.add_argument("--current-level", default="unknown")
    p_init.add_argument("--target-level", required=True)
    p_init.add_argument("--deadline", required=True)
    p_init.add_argument("--daily-minutes", type=int, default=30)
    p_init.add_argument("--goal", default="")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=cmd_init)

    sub.add_parser("record").set_defaults(func=cmd_record)
    return parser


def main() -> None:
    try:
        args = build_parser().parse_args()
        args.func(args)
    except StoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

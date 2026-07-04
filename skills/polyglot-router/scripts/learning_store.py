#!/usr/bin/env python3
import argparse
import json
import os
from datetime import UTC, date, datetime, timedelta
from pathlib import Path


def store_dir() -> Path:
    env = os.environ.get("POLYGLOT_LEARNING_DIR")
    if env:
        return Path(env).expanduser()
    cwd_data = Path.cwd() / "data"
    if (cwd_data / "profile.json").exists():
        return cwd_data
    return Path.home() / ".codex" / "polyglot-learning-os"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def today() -> str:
    return date.today().isoformat()


def sm2(item, quality: int):
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
            interval = round(interval * ef)
        ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    item["repetitions"] = reps
    item["interval_days"] = interval
    item["easiness_factor"] = round(ef, 3)
    item["last_reviewed"] = today()
    item["due"] = (date.today() + timedelta(days=interval)).isoformat()
    return item


def init(args):
    root = store_dir()
    language = args.target_language
    profile = {
        "learner": {
            "name": args.name,
            "native_language": args.native_language,
            "other_languages": [],
        },
        "active_language": language,
        "created": today(),
        "updated": today(),
        "languages": {
            language: {
                "current_level": args.current_level,
                "target_level": args.target_level,
                "deadline": args.deadline,
                "daily_minutes": args.daily_minutes,
                "goal": args.goal,
                "skill_levels": {
                    "reading": args.current_level,
                    "writing": args.current_level,
                    "listening": args.current_level,
                    "conversation": args.current_level,
                    "grammar": args.current_level,
                    "vocabulary": args.current_level,
                },
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
    write_json(root / "profile.json", profile)
    write_json(root / "sessions.json", {"sessions": []})
    write_json(root / "srs.json", {"items": []})
    write_json(root / "assessments.json", {"assessments": []})
    write_json(root / "notes-index.json", {"notes": []})
    print(root)


def read(_args):
    root = store_dir()
    payload = {
        "store": str(root),
        "profile": read_json(root / "profile.json", None),
        "sessions": read_json(root / "sessions.json", {"sessions": []}),
        "srs": read_json(root / "srs.json", {"items": []}),
        "assessments": read_json(root / "assessments.json", {"assessments": []}),
        "notes_index": read_json(root / "notes-index.json", {"notes": []}),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def due(_args):
    root = store_dir()
    srs = read_json(root / "srs.json", {"items": []})
    today_value = today()
    items = [item for item in srs.get("items", []) if item.get("due", today_value) <= today_value]
    print(json.dumps({"due": items}, ensure_ascii=False, indent=2))


def record(_args):
    root = store_dir()
    payload = json.load(os.sys.stdin)
    sessions = read_json(root / "sessions.json", {"sessions": []})
    srs = read_json(root / "srs.json", {"items": []})
    assessments = read_json(root / "assessments.json", {"assessments": []})
    notes_index = read_json(root / "notes-index.json", {"notes": []})
    profile = read_json(root / "profile.json", None)

    session = payload.get("session")
    if session:
        session.setdefault("recorded_at", datetime.now(UTC).isoformat(timespec="seconds"))
        sessions.setdefault("sessions", []).append(session)

    by_id = {item["id"]: item for item in srs.get("items", []) if "id" in item}
    for item in payload.get("new_items", []):
        item.setdefault("created", today())
        item.setdefault("due", today())
        item.setdefault("repetitions", 0)
        item.setdefault("interval_days", 0)
        item.setdefault("easiness_factor", 2.5)
        by_id[item["id"]] = {**by_id.get(item["id"], {}), **item}
    for result in payload.get("review_results", []):
        item_id = result["id"]
        if item_id in by_id:
            by_id[item_id] = sm2(by_id[item_id], result.get("quality", 3))
    srs["items"] = sorted(by_id.values(), key=lambda item: (item.get("due", ""), item.get("id", "")))

    if payload.get("assessment"):
        assessments.setdefault("assessments", []).append(payload["assessment"])

    for note in payload.get("note_updates", []):
        notes_index.setdefault("notes", []).append(note)

    if profile and payload.get("next_focus"):
        language = payload.get("session", {}).get("language") or profile.get("active_language")
        if language in profile.get("languages", {}):
            profile["languages"][language]["next_focus"] = payload["next_focus"]
            profile["updated"] = today()
            write_json(root / "profile.json", profile)

    write_json(root / "sessions.json", sessions)
    write_json(root / "srs.json", srs)
    write_json(root / "assessments.json", assessments)
    write_json(root / "notes-index.json", notes_index)
    print(json.dumps({"ok": True, "store": str(root)}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(required=True)

    sub.add_parser("where").set_defaults(func=lambda _args: print(store_dir()))
    sub.add_parser("read").set_defaults(func=read)
    sub.add_parser("due").set_defaults(func=due)

    p_init = sub.add_parser("init")
    p_init.add_argument("--name", default="")
    p_init.add_argument("--native-language", required=True)
    p_init.add_argument("--target-language", required=True)
    p_init.add_argument("--current-level", default="unknown")
    p_init.add_argument("--target-level", required=True)
    p_init.add_argument("--deadline", required=True)
    p_init.add_argument("--daily-minutes", type=int, default=30)
    p_init.add_argument("--goal", default="")
    p_init.set_defaults(func=init)

    sub.add_parser("record").set_defaults(func=record)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Deadline-aware roadmap calculator for Polyglot Learning OS."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, timedelta
from typing import Any


LEVEL_ORDER = ["A0", "A1", "A2", "B1", "B2", "C1", "C2"]
LEVEL_HOURS = {
    ("A0", "A1"): 90,
    ("A1", "A2"): 110,
    ("A2", "B1"): 160,
    ("B1", "B2"): 220,
    ("B2", "C1"): 320,
    ("C1", "C2"): 420,
}
GOAL_MULTIPLIER = {
    "travel": 0.8,
    "conversation": 0.9,
    "reading": 0.9,
    "work": 1.1,
    "exam": 1.2,
    "academic": 1.25,
    "relocation": 1.15,
    "balanced": 1.0,
}


class RoadmapError(Exception):
    pass


def parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RoadmapError(f"{field} must be YYYY-MM-DD") from exc


def level_index(level: str) -> int:
    if level == "unknown":
        raise RoadmapError("current_level cannot be unknown for roadmap calculation; run polyglot-level-check first")
    if level not in LEVEL_ORDER:
        raise RoadmapError(f"level must be one of {LEVEL_ORDER}")
    return LEVEL_ORDER.index(level)


def required_hours(current: str, target: str, goal: str) -> int:
    start = level_index(current)
    end = level_index(target)
    if end <= start:
        return 0
    hours = 0
    for idx in range(start, end):
        hours += LEVEL_HOURS[(LEVEL_ORDER[idx], LEVEL_ORDER[idx + 1])]
    multiplier = GOAL_MULTIPLIER.get(goal, GOAL_MULTIPLIER["balanced"])
    return math.ceil(hours * multiplier)


def feasibility(required: int, available: float) -> str:
    if required == 0:
        return "already_at_or_above_target"
    ratio = available / required
    if ratio >= 1.1:
        return "realistic"
    if ratio >= 0.85:
        return "aggressive"
    return "unrealistic"


def weekly_allocation(goal: str, weekly_hours: float) -> dict[str, float]:
    if goal == "exam":
        weights = {"review": 0.2, "vocabulary": 0.2, "grammar": 0.2, "input": 0.15, "output": 0.15, "test": 0.1}
    elif goal == "conversation":
        weights = {"review": 0.2, "vocabulary": 0.2, "grammar": 0.15, "input": 0.15, "output": 0.25, "test": 0.05}
    elif goal == "reading":
        weights = {"review": 0.2, "vocabulary": 0.25, "grammar": 0.15, "input": 0.3, "output": 0.05, "test": 0.05}
    else:
        weights = {"review": 0.2, "vocabulary": 0.2, "grammar": 0.2, "input": 0.2, "output": 0.15, "test": 0.05}
    return {key: round(weekly_hours * value, 2) for key, value in weights.items()}


def phase_plan(start: date, deadline: date, current: str, target: str) -> list[dict[str, Any]]:
    total_days = max(1, (deadline - start).days + 1)
    phases = [
        ("foundation", 0.25, "Close core grammar and high-frequency vocabulary gaps."),
        ("controlled-practice", 0.25, "Build reliable production through drills and short output."),
        ("input-output-expansion", 0.3, "Increase authentic input and longer spoken/written output."),
        ("readiness", 0.2, "Run tests, repair weak patterns, and simulate target tasks."),
    ]
    cursor = start
    output = []
    for index, (name, share, objective) in enumerate(phases):
        if index == len(phases) - 1:
            end = deadline
        else:
            end = cursor + timedelta(days=max(1, round(total_days * share)) - 1)
            end = min(end, deadline)
        output.append({
            "phase": name,
            "start": cursor.isoformat(),
            "end": end.isoformat(),
            "objective": objective,
            "checkpoint": f"Evidence of progress from {current} toward {target}: {name} checkpoint",
        })
        cursor = end + timedelta(days=1)
        if cursor > deadline:
            break
    return output


def next_7_days(goal: str) -> list[dict[str, str]]:
    base = [
        ("Day 1", "review + level-targeted vocabulary"),
        ("Day 2", "grammar pattern + controlled production"),
        ("Day 3", "reading input + vocabulary mining"),
        ("Day 4", "conversation or writing output"),
        ("Day 5", "review + weak-pattern repair"),
        ("Day 6", "mixed practice session"),
        ("Day 7", "short test + progress check"),
    ]
    if goal == "exam":
        base[6] = ("Day 7", "exam-format checkpoint + progress check")
    elif goal == "conversation":
        base[3] = ("Day 4", "role-play conversation output")
    elif goal == "reading":
        base[3] = ("Day 4", "source summary writing output")
    return [{"day": day, "session": session} for day, session in base]


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    current = payload.get("current_level", "unknown")
    target = payload.get("target_level")
    if not target:
        raise RoadmapError("target_level is required")
    start = parse_date(payload.get("start_date") or date.today().isoformat(), "start_date")
    deadline = parse_date(payload.get("deadline"), "deadline")
    if deadline < start:
        raise RoadmapError("deadline must be on or after start_date")
    daily_minutes = int(payload.get("daily_minutes", 30))
    if daily_minutes <= 0:
        raise RoadmapError("daily_minutes must be positive")
    goal = payload.get("goal", "balanced")
    days = (deadline - start).days + 1
    available = round(days * daily_minutes / 60, 1)
    required = required_hours(current, target, goal)
    weekly_hours = round(daily_minutes * 7 / 60, 2)
    status = feasibility(required, available)
    return {
        "language": payload.get("language"),
        "current_level": current,
        "target_level": target,
        "goal": goal,
        "start_date": start.isoformat(),
        "deadline": deadline.isoformat(),
        "days_available": days,
        "daily_minutes": daily_minutes,
        "available_hours": available,
        "required_hours": required,
        "hour_gap": round(available - required, 1),
        "feasibility": status,
        "weekly_hours": weekly_hours,
        "weekly_allocation": weekly_allocation(goal, weekly_hours),
        "phase_plan": phase_plan(start, deadline, current, target),
        "checkpoint_tests": [
            "Weekly quick check on due reviews and weak patterns.",
            "Biweekly production sample scored with rubrics.md.",
            "Final target-task simulation before deadline.",
        ],
        "next_7_days": next_7_days(goal),
        "recommendation": recommendation(status, required, available, daily_minutes),
    }


def recommendation(status: str, required: int, available: float, daily_minutes: int) -> str:
    if status == "already_at_or_above_target":
        return "Maintain the level with review, input, and target-task practice."
    if status == "realistic":
        return "Plan is realistic if review and output sessions stay consistent."
    if status == "aggressive":
        needed = math.ceil(required * 60 / max(1, daily_minutes * 0.85))
        return f"Plan is aggressive; protect daily consistency and consider extending toward roughly {needed} study-days."
    extra_minutes = math.ceil(required * 60 / max(1, available / daily_minutes))
    return f"Plan is unrealistic at {daily_minutes} min/day; increase daily time substantially or lower the target/deadline."


def command_calculate(_args: argparse.Namespace) -> None:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise RoadmapError("payload must be an object")
        print(json.dumps(calculate(payload), ensure_ascii=False, indent=2))
    except (json.JSONDecodeError, RoadmapError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate a Polyglot Learning OS roadmap")
    sub = parser.add_subparsers(required=True)
    sub.add_parser("calculate").set_defaults(func=command_calculate)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

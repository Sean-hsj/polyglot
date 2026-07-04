import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_SCRIPT = ROOT / "skills" / "polyglot-router" / "scripts" / "learning_store.py"
ROADMAP_SCRIPT = ROOT / "skills" / "polyglot-roadmap" / "scripts" / "roadmap_calculator.py"
NOTE_SCRIPT = ROOT / "skills" / "polyglot-notes" / "scripts" / "note_writer.py"


class EndToEndWorkflowTests(unittest.TestCase):
    def run_cmd(self, args, *, input_data=None, env=None, expect_ok=True):
        proc = subprocess.run(
            [sys.executable, *map(str, args)],
            input=json.dumps(input_data) if input_data is not None else None,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        if expect_ok and proc.returncode != 0:
            self.fail(f"command failed: {proc.args}\nstdout={proc.stdout}\nstderr={proc.stderr}")
        if not expect_ok and proc.returncode == 0:
            self.fail(f"command unexpectedly passed: {proc.args}\nstdout={proc.stdout}")
        return proc

    def test_goal_to_session_to_memory_loop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = root / "store"
            notes = root / "notes"
            env = os.environ.copy()
            env["POLYGLOT_LEARNING_DIR"] = str(store)

            self.run_cmd(
                [
                    STORE_SCRIPT,
                    "init",
                    "--name",
                    "Learner",
                    "--native-language",
                    "English",
                    "--target-language",
                    "Spanish",
                    "--current-level",
                    "A1",
                    "--target-level",
                    "A2",
                    "--deadline",
                    "2027-07-04",
                    "--daily-minutes",
                    "30",
                    "--goal",
                    "conversation",
                ],
                env=env,
            )

            roadmap = json.loads(
                self.run_cmd(
                    [ROADMAP_SCRIPT, "calculate"],
                    input_data={
                        "language": "Spanish",
                        "current_level": "A1",
                        "target_level": "A2",
                        "start_date": "2026-07-04",
                        "deadline": "2027-07-04",
                        "daily_minutes": 30,
                        "goal": "conversation",
                    },
                ).stdout
            )
            self.assertEqual(roadmap["feasibility"], "realistic")
            self.assertEqual(len(roadmap["next_7_days"]), 7)

            note_update = json.loads(
                self.run_cmd(
                    [NOTE_SCRIPT, "write", "--root", notes],
                    input_data={
                        "type": "roadmap",
                        "language": "Spanish",
                        "title": "Spanish A1 to A2 Roadmap",
                        "date": "2026-07-04",
                        "summary": f"{roadmap['feasibility']} plan with {roadmap['weekly_hours']} weekly hours.",
                        "patterns": [
                            f"{phase['phase']}: {phase['objective']}"
                            for phase in roadmap["phase_plan"]
                        ],
                        "review_prompts": [
                            "Which weekly allocation should change if conversation output is weak?",
                            "What is the next checkpoint test?",
                        ],
                        "next_actions": [day["session"] for day in roadmap["next_7_days"][:3]],
                        "tags": ["roadmap", "A1", "A2"],
                        "linked_objects": ["roadmap-2026-07-04"],
                    },
                ).stdout
            )
            self.assertTrue(Path(note_update["path"]).exists())

            record_result = json.loads(
                self.run_cmd(
                    [STORE_SCRIPT, "record"],
                    input_data={
                        "session": {
                            "language": "Spanish",
                            "date": "2026-07-04",
                            "duration_minutes": 30,
                            "skills": ["vocabulary", "grammar", "conversation"],
                            "summary": "Started the roadmap with introductions and adjective agreement.",
                            "accuracy": 0.76,
                        },
                        "errors": [
                            {
                                "pattern_id": "es-adjective-gender",
                                "category": "grammar",
                                "severity": "major",
                                "learner_answer": "una casa bonito",
                                "correct_answer": "una casa bonita",
                                "context": "noun-adjective agreement",
                            }
                        ],
                        "new_items": [
                            {
                                "id": "es-phrase-encantado",
                                "type": "phrase",
                                "front": "encantado de conocerte",
                                "back": "pleased to meet you",
                                "due": "2026-07-04",
                                "level": "A1",
                                "example": "Encantado de conocerte.",
                            }
                        ],
                        "review_results": [{"id": "es-phrase-encantado", "quality": 4}],
                        "note_updates": [note_update],
                        "next_focus": [
                            "Review adjective gender agreement.",
                            "Run one short introduction role-play.",
                        ],
                    },
                    env=env,
                ).stdout
            )
            self.assertTrue(record_result["ok"])
            self.assertTrue(Path(record_result["backup"]).exists())

            validate = json.loads(self.run_cmd([STORE_SCRIPT, "validate"], env=env).stdout)
            self.assertTrue(validate["ok"])

            read = json.loads(self.run_cmd([STORE_SCRIPT, "read"], env=env).stdout)
            language_state = read["profile"]["languages"]["Spanish"]
            self.assertEqual(language_state["total_sessions"], 1)
            self.assertEqual(language_state["total_study_minutes"], 30)
            self.assertEqual(read["sessions"]["sessions"][0]["session_id"], "session-001")
            self.assertEqual(read["notes_index"]["notes"][0]["path"], note_update["path"])

            item = read["srs"]["items"][0]
            self.assertEqual(item["id"], "es-phrase-encantado")
            self.assertEqual(item["source"], "session-001")
            self.assertEqual(item["due"], "2026-07-05")
            self.assertEqual(item["total_reviews"], 1)

            weak = language_state["weak_patterns"][0]
            self.assertEqual(weak["pattern_id"], "es-adjective-gender")
            self.assertEqual(weak["severity"], "major")

            due = json.loads(self.run_cmd([STORE_SCRIPT, "due", "--date", "2026-07-04"], env=env).stdout)
            self.assertEqual(due["count"], 0)

            progress = json.loads(self.run_cmd([STORE_SCRIPT, "progress"], env=env).stdout)
            self.assertEqual(progress["status"]["sessions"], 1)
            self.assertEqual(progress["status"]["average_recent_accuracy"], 0.76)
            self.assertEqual(progress["next_focus"], language_state["next_focus"])


if __name__ == "__main__":
    unittest.main()

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "polyglot-router" / "scripts" / "learning_store.py"


class LearningStoreTests(unittest.TestCase):
    def run_store(self, store_dir, *args, input_data=None, expect_ok=True):
        env = os.environ.copy()
        env["POLYGLOT_LEARNING_DIR"] = str(store_dir)
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
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

    def init_store(self, store_dir):
        self.run_store(
            store_dir,
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
            "B1",
            "--deadline",
            "2026-12-31",
            "--daily-minutes",
            "30",
            "--goal",
            "travel conversation",
        )

    def test_init_read_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp)
            self.init_store(store)
            read = json.loads(self.run_store(store, "read").stdout)
            self.assertEqual(read["profile"]["active_language"], "Spanish")
            self.assertEqual(read["computed"]["next_session_id"], "session-001")
            validate = json.loads(self.run_store(store, "validate").stdout)
            self.assertTrue(validate["ok"])

    def test_record_updates_srs_progress_and_weak_patterns(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp)
            self.init_store(store)
            payload = {
                "session": {
                    "language": "Spanish",
                    "date": "2026-07-04",
                    "duration_minutes": 20,
                    "skills": ["vocabulary", "grammar"],
                    "summary": "Practiced introductions and adjective agreement.",
                    "accuracy": 0.7,
                },
                "errors": [
                    {
                        "pattern_id": "es-adjective-gender",
                        "category": "grammar",
                        "severity": "major",
                        "learner_answer": "casa bonito",
                        "correct_answer": "casa bonita",
                        "context": "noun-adjective agreement",
                    }
                ],
                "new_items": [
                    {
                        "id": "es-phrase-encantado",
                        "type": "phrase",
                        "front": "encantado",
                        "back": "pleased to meet you",
                        "example": "Encantado de conocerte.",
                        "level": "A1",
                    }
                ],
                "review_results": [{"id": "es-phrase-encantado", "quality": 4}],
                "next_focus": ["Drill adjective gender agreement"],
            }
            result = json.loads(self.run_store(store, "record", input_data=payload).stdout)
            self.assertTrue(result["ok"])
            self.assertTrue(Path(result["backup"]).exists())

            read = json.loads(self.run_store(store, "read").stdout)
            self.assertEqual(read["computed"]["next_session_id"], "session-002")
            self.assertEqual(read["computed"]["due_reviews_count"], 0)
            item = read["srs"]["items"][0]
            self.assertEqual(item["interval_days"], 1)
            self.assertEqual(item["total_reviews"], 1)
            weak = read["profile"]["languages"]["Spanish"]["weak_patterns"][0]
            self.assertEqual(weak["pattern_id"], "es-adjective-gender")
            self.assertEqual(weak["count"], 1)

    def test_invalid_payload_fails_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp)
            self.init_store(store)
            bad_payload = {
                "session": {
                    "language": "Spanish",
                    "date": "2026-07-04",
                    "duration_minutes": 20,
                    "skills": ["vocabulary"],
                    "summary": "Bad payload.",
                    "accuracy": 0.5,
                },
                "review_results": [{"id": "missing-item", "quality": 4}],
            }
            self.run_store(store, "record", input_data=bad_payload, expect_ok=False)
            read = json.loads(self.run_store(store, "read").stdout)
            self.assertEqual(read["sessions"]["sessions"], [])
            self.assertEqual(read["srs"]["items"], [])

    def test_due_filters_by_date_and_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp)
            self.init_store(store)
            payload = {
                "session": {
                    "language": "Spanish",
                    "date": "2026-07-04",
                    "duration_minutes": 5,
                    "skills": ["vocabulary"],
                    "summary": "Added a phrase.",
                    "accuracy": 1,
                },
                "new_items": [
                    {
                        "id": "es-word-hola",
                        "type": "word",
                        "front": "hola",
                        "back": "hello",
                        "due": "2026-07-04",
                    }
                ],
            }
            self.run_store(store, "record", input_data=payload)
            due = json.loads(self.run_store(store, "due", "--date", "2026-07-04", "--language", "Spanish").stdout)
            self.assertEqual(due["count"], 1)

    def test_progress_summary_uses_recent_sessions_and_focus(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp)
            self.init_store(store)
            payload = {
                "session": {
                    "language": "Spanish",
                    "date": "2026-07-04",
                    "duration_minutes": 10,
                    "skills": ["conversation"],
                    "summary": "Practiced cafe ordering.",
                    "accuracy": 0.8,
                },
                "next_focus": ["Practice polite requests in cafes"],
            }
            self.run_store(store, "record", input_data=payload)
            progress = json.loads(self.run_store(store, "progress").stdout)
            self.assertEqual(progress["language"], "Spanish")
            self.assertEqual(progress["status"]["sessions"], 1)
            self.assertEqual(progress["status"]["average_recent_accuracy"], 0.8)
            self.assertEqual(progress["next_focus"], ["Practice polite requests in cafes"])


if __name__ == "__main__":
    unittest.main()

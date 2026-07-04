import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "polyglot-notes" / "scripts" / "note_writer.py"


class NoteWriterTests(unittest.TestCase):
    def run_writer(self, root, payload, *extra, expect_ok=True):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "write", "--root", str(root), *extra],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        if expect_ok and proc.returncode != 0:
            self.fail(f"note_writer failed\nstdout={proc.stdout}\nstderr={proc.stderr}")
        if not expect_ok and proc.returncode == 0:
            self.fail(f"note_writer unexpectedly passed\nstdout={proc.stdout}")
        return proc

    def test_writes_session_note_and_note_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = {
                "type": "session",
                "language": "Spanish",
                "title": "Cafe ordering session",
                "date": "2026-07-04",
                "summary": "Practiced ordering coffee politely.",
                "examples": ["Quisiera un cafe, por favor."],
                "review_prompts": ["How do you politely ask for a coffee?"],
                "next_actions": ["Review polite request phrases."],
                "tags": ["conversation", "A1"],
                "linked_objects": ["session-001"],
            }
            proc = self.run_writer(Path(tmp), payload)
            update = json.loads(proc.stdout)
            note_path = Path(update["path"])
            self.assertTrue(note_path.exists())
            text = note_path.read_text(encoding="utf-8")
            self.assertIn('type: "session"', text)
            self.assertIn("## Review Prompts", text)
            self.assertEqual(update["tags"], ["conversation", "A1"])

    def test_refuses_to_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = {
                "type": "grammar",
                "language": "Spanish",
                "title": "Adjective gender",
                "date": "2026-07-04",
                "summary": "Adjectives agree with noun gender.",
            }
            self.run_writer(Path(tmp), payload)
            self.run_writer(Path(tmp), payload, expect_ok=False)
            self.run_writer(Path(tmp), payload, "--force")


if __name__ == "__main__":
    unittest.main()

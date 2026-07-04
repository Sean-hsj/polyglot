import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "polyglot-roadmap" / "scripts" / "roadmap_calculator.py"


class RoadmapCalculatorTests(unittest.TestCase):
    def run_calculator(self, payload, expect_ok=True):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "calculate"],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        if expect_ok and proc.returncode != 0:
            self.fail(f"roadmap_calculator failed\nstdout={proc.stdout}\nstderr={proc.stderr}")
        if not expect_ok and proc.returncode == 0:
            self.fail(f"roadmap_calculator unexpectedly passed\nstdout={proc.stdout}")
        return proc

    def test_calculates_realistic_plan(self):
        result = json.loads(self.run_calculator({
            "language": "Spanish",
            "current_level": "A1",
            "target_level": "A2",
            "start_date": "2026-07-04",
            "deadline": "2027-07-04",
            "daily_minutes": 30,
            "goal": "conversation",
        }).stdout)
        self.assertEqual(result["feasibility"], "realistic")
        self.assertEqual(result["required_hours"], 99)
        self.assertGreater(result["available_hours"], result["required_hours"])
        self.assertEqual(len(result["next_7_days"]), 7)
        self.assertIn("weekly_allocation", result)

    def test_flags_unrealistic_plan(self):
        result = json.loads(self.run_calculator({
            "language": "Japanese",
            "current_level": "A1",
            "target_level": "B2",
            "start_date": "2026-07-04",
            "deadline": "2026-10-04",
            "daily_minutes": 20,
            "goal": "exam",
        }).stdout)
        self.assertEqual(result["feasibility"], "unrealistic")
        self.assertLess(result["available_hours"], result["required_hours"])

    def test_rejects_unknown_current_level(self):
        self.run_calculator({
            "language": "Spanish",
            "current_level": "unknown",
            "target_level": "B1",
            "start_date": "2026-07-04",
            "deadline": "2026-12-31",
            "daily_minutes": 30,
        }, expect_ok=False)


if __name__ == "__main__":
    unittest.main()

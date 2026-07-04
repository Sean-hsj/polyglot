import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
ROUTER_REFS = SKILLS / "polyglot-router" / "references"


class SkillProtocolTests(unittest.TestCase):
    def read_skill(self, name):
        return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")

    def test_shared_protocol_references_exist(self):
        for filename in [
            "session-protocol.md",
            "exercise-protocols.md",
            "feedback-protocol.md",
            "rubrics.md",
            "data-contract.md",
            "payload-examples.md",
        ]:
            self.assertTrue((ROUTER_REFS / filename).exists(), filename)

    def test_router_names_required_protocols(self):
        text = self.read_skill("polyglot-router")
        for filename in [
            "system-architecture.md",
            "data-contract.md",
            "session-protocol.md",
            "exercise-protocols.md",
            "feedback-protocol.md",
            "rubrics.md",
        ]:
            self.assertIn(filename, text)

    def test_core_specialists_reference_exercise_or_rubric_protocols(self):
        requirements = {
            "polyglot-vocab": ["exercise-protocols.md", "rubrics.md"],
            "polyglot-grammar": ["exercise-protocols.md", "rubrics.md", "feedback-protocol.md"],
            "polyglot-writing": ["exercise-protocols.md", "rubrics.md", "feedback-protocol.md"],
            "polyglot-reading": ["exercise-protocols.md", "rubrics.md"],
            "polyglot-conversation": ["exercise-protocols.md", "rubrics.md", "feedback-protocol.md"],
            "polyglot-test": ["exercise-protocols.md", "rubrics.md", "payload-examples.md"],
            "polyglot-level-check": ["exercise-protocols.md", "rubrics.md", "payload-examples.md"],
        }
        for skill, filenames in requirements.items():
            text = self.read_skill(skill)
            for filename in filenames:
                self.assertIn(filename, text, f"{skill} should reference {filename}")

    def test_payload_examples_are_valid_json(self):
        text = (ROUTER_REFS / "payload-examples.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```json\n(.*?)\n```", text, flags=re.DOTALL)
        self.assertGreaterEqual(len(blocks), 2)
        for block in blocks:
            payload = json.loads(block)
            self.assertIn("session", payload)
            self.assertIn("next_focus", payload)

    def test_specialist_scripts_are_documented(self):
        notes = self.read_skill("polyglot-notes")
        roadmap = self.read_skill("polyglot-roadmap")
        self.assertIn("scripts/note_writer.py", notes)
        self.assertIn("note_updates[]", notes)
        self.assertIn("scripts/roadmap_calculator.py", roadmap)
        self.assertIn("feasibility", roadmap)


if __name__ == "__main__":
    unittest.main()

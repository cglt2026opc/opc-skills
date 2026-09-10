#!/usr/bin/env python3
"""Exercise installation and packaging in temporary directories."""
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from opc_skills import DEFAULT_SKILL, MODULES_ROOT, REPO_ROOT, discover_modules


class DistributionTests(unittest.TestCase):
    def run_cli(self, *arguments, ok=True):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts/opc_skills.py"), *arguments],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def test_default_install_and_existing_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills"
            self.run_cli("install", "--agent", "openclaw", "--target", str(target), "--dry-run")
            self.assertFalse(target.exists())
            self.run_cli("install", "--agent", "openclaw", "--target", str(target))
            self.assertEqual([p.name for p in target.iterdir()], [DEFAULT_SKILL])
            self.assertEqual(len(list(target.rglob("SKILL.md"))), 1)
            self.assertEqual(len(list(target.rglob("WORKFLOW.md"))), 21)
            for source in MODULES_ROOT.rglob("*"):
                if source.is_file() and "__pycache__" not in source.parts and source.suffix != ".pyc":
                    installed = target / DEFAULT_SKILL / "references/modules" / source.relative_to(MODULES_ROOT)
                    self.assertEqual(installed.read_bytes(), source.read_bytes())
            sentinel = target / DEFAULT_SKILL / "local.txt"
            sentinel.write_text("preserve")
            self.run_cli("install", "--agent", "openclaw", "--target", str(target))
            self.assertTrue(sentinel.exists())
            old = target / "mvp-validator"
            old.mkdir()
            result = self.run_cli("install", "--agent", "openclaw", "--target", str(target), "--force")
            self.assertIn("迁移提示", result.stdout)
            self.assertTrue(old.exists())
            self.assertFalse(sentinel.exists())

    def test_workbuddy_and_standalone_exports(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.run_cli("package", "--agent", "workbuddy", "--output", temporary)
            output = Path(temporary) / "workbuddy"
            self.assertEqual([p.name for p in output.iterdir()], [DEFAULT_SKILL + ".zip"])
            with zipfile.ZipFile(output / (DEFAULT_SKILL + ".zip")) as bundle:
                self.assertEqual([n for n in bundle.namelist() if n.endswith("/SKILL.md")],
                                 [DEFAULT_SKILL + "/SKILL.md"])
                self.assertEqual(sum(n.endswith("/WORKFLOW.md") for n in bundle.namelist()), 21)
            for name, source in discover_modules().items():
                self.run_cli("package", "--agent", "workbuddy", "--output", temporary, "--skill", name)
                with zipfile.ZipFile(output / (name + ".zip")) as bundle:
                    self.assertEqual(bundle.read(name + "/SKILL.md"), (source / "WORKFLOW.md").read_bytes())
                    self.assertNotIn(name + "/WORKFLOW.md", bundle.namelist())
            target = Path(temporary) / "standalone"
            self.run_cli("install", "--agent", "openclaw", "--target", str(target),
                         "--skill", "super-individual-assessment")
            skill = target / "super-individual-assessment"
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertTrue((skill / "scripts/score_assessment.py").is_file())
            self.assertTrue((skill / "references/assessment.md").is_file())
            self.run_cli("install", "--agent", "openclaw", "--target", str(target),
                         "--skill", "mvp-validator", "--mode", "link", ok=False)
            self.run_cli("package", "--agent", "workbuddy", "--output", temporary,
                         "--skill", "missing-skill", ok=False)

    def test_link_and_doubao(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "linked"
            self.run_cli("install", "--agent", "openclaw", "--target", str(target), "--mode", "link")
            self.assertTrue((target / DEFAULT_SKILL / "SKILL.md").is_file())
            self.run_cli("package", "--agent", "doubao", "--output", temporary)
            prompts = list((Path(temporary) / "doubao").glob("*.prompt.md"))
            self.assertEqual(len(prompts), 21)
            self.assertFalse(any(p.name.startswith(DEFAULT_SKILL) for p in prompts))


if __name__ == "__main__":
    unittest.main()

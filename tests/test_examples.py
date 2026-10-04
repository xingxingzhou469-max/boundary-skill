from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("boundary_demo", ROOT / "scripts/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class ExampleWorkflowTests(unittest.TestCase):
    def test_bundled_examples_complete_real_cli_lifecycle(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = demo.run_demo(Path(temp))
            for path in paths.values():
                self.assertTrue(Path(path).is_file())
            state = json.loads((Path(temp) / "Boundary/_system/state.json").read_text(encoding="utf-8"))
            self.assertEqual(len(state["history"]), 1)
            self.assertEqual(state["history"][0]["feedback"], "deep")
            self.assertTrue(state["history"][0]["report"])
            self.assertTrue(state["history"][0]["sources"][0]["accessed_at"])

    def test_demo_refuses_an_existing_destination_without_changing_it(self):
        with tempfile.TemporaryDirectory() as temp:
            sentinel = Path(temp) / "keep.txt"
            sentinel.write_text("user content", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/demo.py"), "--output", temp],
                text=True, encoding="utf-8", capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "user content")
            self.assertEqual(list(Path(temp).iterdir()), [sentinel])

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATE_SCRIPT = PROJECT_ROOT / "scripts" / "state.py"


class BoundaryCliTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp = Path(self.temp_dir.name)
        self.config = self.temp / "config.json"
        self.root = self.temp / "Boundary"
        self.run_cli(
            "init",
            "--root",
            str(self.root),
            "--language",
            "zh",
            "--mode",
            "boundary",
            "--timezone",
            "Asia/Shanghai",
        )

    def run_cli(self, *args: str, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(STATE_SCRIPT), "--config", str(self.config), *args],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if expect_ok and result.returncode != 0:
            self.fail(f"CLI failed ({result.returncode}): {result.stderr or result.stdout}")
        return result

    def write_card_input(self) -> tuple[Path, Path]:
        body = self.temp / "card.md"
        body.write_text(
            "# 今天的边界 · 巨津巴布韦\n\n"
            "## 核心知识\n"
            "当地绍纳文化相关社群建造了这座石城。[来源](https://example.org/a)\n",
            encoding="utf-8",
        )
        sources = self.temp / "sources.json"
        sources.write_text(
            json.dumps(
                [
                    {
                        "title": "Archaeological record",
                        "url": "https://example.org/a",
                        "kind": "primary",
                        "publisher": "Example Museum",
                        "supports": "The site's builders and material record",
                    },
                    {
                        "title": "Historical synthesis",
                        "url": "https://example.net/b",
                        "kind": "authoritative",
                        "publisher": "Example University",
                        "supports": "Historical interpretation and trade context",
                    },
                ]
            ),
            encoding="utf-8",
        )
        return body, sources

    def test_card_survives_restart_and_feedback_saves_note(self) -> None:
        body, sources = self.write_card_input()
        recorded = json.loads(
            self.run_cli(
                "record",
                "--title",
                "巨津巴布韦",
                "--slug",
                "great-zimbabwe",
                "--question",
                "谁建造了巨津巴布韦，证据是什么？",
                "--summary",
                "考古证据显示当地绍纳文化相关社群建造了石城并参与印度洋贸易。",
                "--domain",
                "history-archaeology",
                "--region",
                "Southern Africa",
                "--mode",
                "boundary",
                "--body",
                str(body),
                "--sources",
                str(sources),
            ).stdout
        )

        context = json.loads(self.run_cli("context").stdout)
        self.assertEqual([recorded["id"]], [item["id"] for item in context["active"]])
        draft = self.root / recorded["draft"]
        self.assertTrue(draft.is_file())
        self.assertIn("绍纳文化", draft.read_text(encoding="utf-8"))

        accepted = json.loads(
            self.run_cli("feedback", "--id", recorded["id"], "--value", "new").stdout
        )
        note = self.root / accepted["note"]
        self.assertTrue(note.is_file())
        self.assertIn("feedback: new", note.read_text(encoding="utf-8"))
        self.assertIn("绍纳文化", note.read_text(encoding="utf-8"))
        self.assertFalse(draft.exists())

        index_path = self.root / "INDEX.md"
        self.assertIn(
            "- [巨津巴布韦](Cards/great-zimbabwe.md)",
            index_path.read_text(encoding="utf-8"),
        )

    def test_deep_feedback_can_attach_a_linked_deep_research_report(self) -> None:
        body, sources = self.write_card_input()
        recorded = json.loads(
            self.run_cli(
                "record",
                "--title",
                "巨津巴布韦",
                "--slug",
                "great-zimbabwe",
                "--question",
                "谁建造了巨津巴布韦，证据是什么？",
                "--summary",
                "考古证据显示当地绍纳文化相关社群建造了石城并参与印度洋贸易。",
                "--domain",
                "history-archaeology",
                "--region",
                "Southern Africa",
                "--mode",
                "boundary",
                "--body",
                str(body),
                "--sources",
                str(sources),
            ).stdout
        )
        self.run_cli("feedback", "--id", recorded["id"], "--value", "deep")

        report_body = self.temp / "deep-report.md"
        report_body.write_text(
            "# 巨津巴布韦 — 深度研究报告\n\n"
            "## 核心问题\n谁建造了这座城市，考古证据如何支持这一结论？\n\n"
            "## 直接结论\n证据指向当地社会，而不是殖民时期假设的外来建造者。\n\n"
            "## 证据详解\n年代学与物质文化相互印证。[来源](https://example.org/a)\n",
            encoding="utf-8",
        )
        report_sources = self.temp / "deep-report-sources.json"
        report_sources.write_text(
            json.dumps(
                [
                    {
                        "title": "Excavation evidence",
                        "url": "https://example.org/a",
                        "kind": "primary",
                        "publisher": "Example Museum",
                        "supports": "Material chronology",
                    },
                    {
                        "title": "Historical synthesis",
                        "url": "https://example.net/b",
                        "kind": "academic",
                        "publisher": "Example University",
                        "supports": "Interpretive history",
                    },
                    {
                        "title": "Heritage record",
                        "url": "https://example.com/c",
                        "kind": "authoritative",
                        "publisher": "Example Heritage Agency",
                        "supports": "Site significance",
                    },
                ]
            ),
            encoding="utf-8",
        )

        attached = json.loads(
            self.run_cli(
                "deep",
                "--id",
                recorded["id"],
                "--question",
                "谁建造了这座城市，考古证据如何支持这一结论？",
                "--body",
                str(report_body),
                "--sources",
                str(report_sources),
            ).stdout
        )
        report_path = self.root / attached["report"]
        card_path = self.root / attached["note"]
        self.assertTrue(report_path.is_file())
        self.assertIn(
            "[巨津巴布韦](../Cards/great-zimbabwe.md)",
            report_path.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "[深度研究报告](../Reports/great-zimbabwe-deep-research.md)",
            card_path.read_text(encoding="utf-8"),
        )

    def test_record_rejects_invalid_source_urls(self) -> None:
        body, _ = self.write_card_input()
        sources = self.temp / "invalid-sources.json"
        sources.write_text(
            json.dumps(
                [
                    {
                        "title": "Invalid source",
                        "url": "not-a-url",
                        "kind": "primary",
                        "publisher": "Publisher A",
                        "supports": "Claim A",
                    },
                    {
                        "title": "Valid source",
                        "url": "https://example.net/b",
                        "kind": "authoritative",
                        "publisher": "Publisher B",
                        "supports": "Claim B",
                    },
                ]
            ),
            encoding="utf-8",
        )
        result = self.run_cli(
            "record",
            "--title",
            "无效来源测试",
            "--question",
            "这个来源是否有效？",
            "--summary",
            "无效来源不应进入历史。",
            "--domain",
            "history-archaeology",
            "--region",
            "Southern Africa",
            "--mode",
            "boundary",
            "--body",
            str(body),
            "--sources",
            str(sources),
            expect_ok=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid URL", result.stderr)

    def test_shown_card_counts_as_coverage_and_skipped_topic_cools_down(self) -> None:
        body, sources = self.write_card_input()
        recorded = json.loads(
            self.run_cli(
                "record",
                "--title",
                "巨津巴布韦",
                "--slug",
                "great-zimbabwe",
                "--question",
                "谁建造了巨津巴布韦，证据是什么？",
                "--summary",
                "考古证据显示当地绍纳文化相关社群建造了石城并参与印度洋贸易。",
                "--domain",
                "history-archaeology",
                "--region",
                "Southern Africa",
                "--mode",
                "boundary",
                "--body",
                str(body),
                "--sources",
                str(sources),
            ).stdout
        )
        context = json.loads(self.run_cli("context").stdout)
        self.assertEqual(1, context["domain_counts"]["history-archaeology"])
        self.assertEqual(1, context["region_counts"]["southern-africa"])

        self.run_cli("feedback", "--id", recorded["id"], "--value", "skipped")
        duplicate = self.run_cli(
            "record",
            "--title",
            "非洲石城的建造者",
            "--slug",
            "african-stone-city-builders",
            "--question",
            "谁建造了巨津巴布韦，证据是什么？",
            "--summary",
            "考古证据显示当地绍纳文化相关社群建造了石城并参与印度洋贸易。",
            "--domain",
            "history-archaeology",
            "--region",
            "Southern Africa",
            "--mode",
            "boundary",
            "--body",
            str(body),
            "--sources",
            str(sources),
            expect_ok=False,
        )
        self.assertNotEqual(0, duplicate.returncode)
        self.assertIn("skip cooldown", duplicate.stderr)

    def test_alternate_mode_flips_after_a_card_is_shown(self) -> None:
        self.run_cli("configure", "--mode", "alternate")
        first_pick = json.loads(self.run_cli("pick", "--mode", "default", "--seed", "3").stdout)
        self.assertEqual("boundary", first_pick["mode"])

        body, sources = self.write_card_input()
        self.run_cli(
            "record",
            "--title",
            "巨津巴布韦",
            "--question",
            "谁建造了巨津巴布韦，证据是什么？",
            "--summary",
            "考古证据显示当地绍纳文化相关社群建造了石城并参与印度洋贸易。",
            "--domain",
            first_pick["domain"],
            "--region",
            "Southern Africa",
            "--mode",
            first_pick["mode"],
            "--body",
            str(body),
            "--sources",
            str(sources),
        )
        second_pick = json.loads(
            self.run_cli("pick", "--mode", "default", "--seed", "3").stdout
        )
        self.assertEqual("wander", second_pick["mode"])

    def test_known_feedback_is_final_and_saves_the_card(self) -> None:
        body, sources = self.write_card_input()
        recorded = json.loads(
            self.run_cli(
                "record",
                "--title",
                "巨津巴布韦",
                "--question",
                "谁建造了巨津巴布韦，证据是什么？",
                "--summary",
                "考古证据显示当地绍纳文化相关社群建造了石城并参与印度洋贸易。",
                "--domain",
                "history-archaeology",
                "--region",
                "Southern Africa",
                "--mode",
                "boundary",
                "--body",
                str(body),
                "--sources",
                str(sources),
            ).stdout
        )
        accepted = json.loads(
            self.run_cli("feedback", "--id", recorded["id"], "--value", "known").stdout
        )
        self.assertTrue((self.root / accepted["note"]).is_file())
        repeated = self.run_cli(
            "feedback",
            "--id",
            recorded["id"],
            "--value",
            "new",
            expect_ok=False,
        )
        self.assertNotEqual(0, repeated.returncode)
        self.assertIn("already finalized", repeated.stderr)

    def test_language_change_keeps_the_existing_index(self) -> None:
        self.run_cli("configure", "--language", "en")
        body, sources = self.write_card_input()
        recorded = json.loads(
            self.run_cli(
                "record",
                "--title",
                "Great Zimbabwe",
                "--question",
                "Who built Great Zimbabwe and what is the evidence?",
                "--summary",
                "Archaeological evidence identifies local Shona-related communities.",
                "--domain",
                "history-archaeology",
                "--region",
                "southern-africa",
                "--mode",
                "boundary",
                "--body",
                str(body),
                "--sources",
                str(sources),
            ).stdout
        )
        self.run_cli("feedback", "--id", recorded["id"], "--value", "new")
        index_file = self.root / "INDEX.md"
        self.assertTrue(index_file.is_file())
        self.assertIn(
            "- [Great Zimbabwe](Cards/great-zimbabwe.md)",
            index_file.read_text(encoding="utf-8"),
        )

    def test_tampered_state_cannot_delete_a_file_outside_boundary(self) -> None:
        body, sources = self.write_card_input()
        recorded = json.loads(
            self.run_cli(
                "record",
                "--title",
                "巨津巴布韦",
                "--question",
                "谁建造了巨津巴布韦，证据是什么？",
                "--summary",
                "考古证据显示当地绍纳文化相关社群建造了石城。",
                "--domain",
                "history-archaeology",
                "--region",
                "southern-africa",
                "--mode",
                "boundary",
                "--body",
                str(body),
                "--sources",
                str(sources),
            ).stdout
        )
        outside = self.temp / "outside.md"
        outside.write_text("must remain", encoding="utf-8")
        state_path = self.root / "_system" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["history"][0]["draft"] = "../outside.md"
        state_path.write_text(json.dumps(state), encoding="utf-8")

        result = self.run_cli(
            "feedback",
            "--id",
            recorded["id"],
            "--value",
            "skipped",
            expect_ok=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertTrue(outside.is_file())
        self.assertEqual("must remain", outside.read_text(encoding="utf-8"))

    def test_boundary_domain_coverage_is_only_a_soft_prior(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("boundary_state", STATE_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        history = [
            {
                "domains": ["history-archaeology"],
                "shown_at": module.now_iso(),
                "feedback": "new",
            }
            for _ in range(30)
        ]
        weights = module.boundary_domain_weights(history)
        self.assertGreater(
            weights["history-archaeology"],
            weights["earth-geography"] * 0.5,
        )


if __name__ == "__main__":
    unittest.main()

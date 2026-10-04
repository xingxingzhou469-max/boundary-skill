from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATE_SCRIPT = PROJECT_ROOT / "scripts" / "state.py"


def load_state_module():
    spec = importlib.util.spec_from_file_location("boundary_state_test", STATE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Boundary state module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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

    def run_cli(
        self,
        *args: str,
        expect_ok: bool = True,
        config: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        selected_config = config or self.config
        result = subprocess.run(
            [sys.executable, str(STATE_SCRIPT), "--config", str(selected_config), *args],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            timeout=10,
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

    def record_card(
        self,
        *,
        title: str = "测试主题",
        slug: str = "test-topic",
        question: str = "这个主题的核心问题是什么？",
        summary: str = "这是一个可复用的解释。",
        body: Path | None = None,
        sources: Path | None = None,
        config: Path | None = None,
    ) -> dict[str, object]:
        if body is None or sources is None:
            body, sources = self.write_card_input()
        result = self.run_cli(
            "record",
            "--title",
            title,
            "--slug",
            slug,
            "--question",
            question,
            "--summary",
            summary,
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
            config=config,
        )
        return json.loads(result.stdout)

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
        pending = json.loads(self.run_cli("context").stdout)["pending_reports"]
        self.assertEqual([recorded["id"]], [item["id"] for item in pending])

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

        report_path = self.root / "Reports" / "great-zimbabwe-deep-research.md"
        card_path = self.root / "Cards" / "great-zimbabwe.md"
        module = load_state_module()
        original_replace = module.os.replace
        injected = False

        def fail_state_replace(source: object, destination: object) -> None:
            nonlocal injected
            if Path(destination).resolve() == (self.root / "_system" / "state.json").resolve() and not injected:
                injected = True
                raise OSError("simulated state write failure")
            original_replace(source, destination)

        with patch.object(module.os, "replace", fail_state_replace):
            with self.assertRaisesRegex(SystemExit, "prior files were restored"):
                module.cmd_deep(
                    argparse.Namespace(
                        config=str(self.config),
                        id=recorded["id"],
                        question=None,
                        body=str(report_body),
                        sources=str(report_sources),
                    )
                )

        self.assertFalse(report_path.exists())
        self.assertNotIn("Deep research report", card_path.read_text(encoding="utf-8"))
        self.assertEqual([recorded["id"]], [item["id"] for item in json.loads(self.run_cli("context").stdout)["pending_reports"]])

        attached = json.loads(
            self.run_cli(
                "deep",
                "--id",
                recorded["id"],
                "--body",
                str(report_body),
                "--sources",
                str(report_sources),
            ).stdout
        )
        report_path = self.root / attached["report"]
        card_path = self.root / attached["note"]
        self.assertEqual(recorded["question"], attached["report_question"])
        self.assertTrue(report_path.is_file())
        self.assertIn(
            "[巨津巴布韦](../Cards/great-zimbabwe.md)",
            report_path.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "[深度研究报告](../Reports/great-zimbabwe-deep-research.md)",
            card_path.read_text(encoding="utf-8"),
        )
        self.assertEqual([], json.loads(self.run_cli("context").stdout)["pending_reports"])

    def test_old_pending_report_remains_visible_beyond_recent_context_limit(self) -> None:
        recorded = self.record_card()
        self.run_cli("feedback", "--id", recorded["id"], "--value", "deep")
        state_path = self.root / "_system" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        pending = state["history"][0]
        pending["shown_at"] = (
            datetime.now(timezone.utc) - timedelta(days=31)
        ).replace(microsecond=0).isoformat()
        current = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        for number in range(30):
            state["history"].append(
                {
                    "id": f"later-{number}",
                    "title": f"Later {number}",
                    "slug": f"later-{number}",
                    "question": f"Question {number}?",
                    "summary": f"Summary {number}.",
                    "topic_key": f"later-{number}",
                    "domains": ["history-archaeology"],
                    "regions": ["Southern Africa"],
                    "mode": "boundary",
                    "shown_at": current,
                    "feedback": "known",
                    "sources": pending["sources"],
                    "draft": None,
                    "note": f"Cards/later-{number}.md",
                    "report": None,
                }
            )
        state_path.write_text(json.dumps(state), encoding="utf-8")

        context = json.loads(self.run_cli("context").stdout)
        self.assertNotIn(recorded["id"], [item["id"] for item in context["today"]])
        self.assertNotIn(recorded["id"], [item["id"] for item in context["recent"]])
        self.assertEqual([recorded["id"]], [item["id"] for item in context["pending_reports"]])

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

    def test_source_dates_are_validated_and_persisted_without_stringifying_values(self) -> None:
        body, sources = self.write_card_input()
        source_rows = json.loads(sources.read_text(encoding="utf-8"))
        source_rows[0]["accessed_at"] = "2026-10-05"
        source_rows[0]["published_at"] = "2024-06-30"
        sources.write_text(json.dumps(source_rows), encoding="utf-8")

        recorded = self.record_card(body=body, sources=sources)
        state = json.loads((self.root / "_system" / "state.json").read_text(encoding="utf-8"))
        stored_source = state["history"][0]["sources"][0]
        self.assertEqual("2026-10-05", stored_source["accessed_at"])
        self.assertEqual("2024-06-30", stored_source["published_at"])

        source_rows[0]["published_at"] = "2025-02-30"
        sources.write_text(json.dumps(source_rows), encoding="utf-8")
        module = load_state_module()
        with self.assertRaisesRegex(SystemExit, "real date"):
            module.read_sources(sources)

        source_rows[0].pop("published_at")
        source_rows[0]["publisher"] = None
        sources.write_text(json.dumps(source_rows), encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "required fields must be strings"):
            module.read_sources(sources)

    def test_feedback_io_failure_rolls_back_then_cli_retry_succeeds(self) -> None:
        recorded = self.record_card()
        draft = self.root / recorded["draft"]
        index = self.root / "INDEX.md"
        index_before = index.read_text(encoding="utf-8")
        module = load_state_module()
        original_replace = module.os.replace
        injected = False

        def fail_index_replace(source: object, destination: object) -> None:
            nonlocal injected
            if Path(destination).resolve() == index.resolve() and not injected:
                injected = True
                raise OSError("simulated index write failure")
            original_replace(source, destination)

        with patch.object(module.os, "replace", fail_index_replace):
            with self.assertRaisesRegex(SystemExit, "prior files were restored"):
                module.cmd_feedback(
                    argparse.Namespace(config=str(self.config), id=recorded["id"], value="new")
                )

        self.assertFalse((self.root / "Cards" / "test-topic.md").exists())
        self.assertEqual(index_before, index.read_text(encoding="utf-8"))
        self.assertTrue(draft.is_file())
        stored = json.loads((self.root / "_system" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual("shown", stored["history"][0]["feedback"])

        accepted = json.loads(
            self.run_cli("feedback", "--id", recorded["id"], "--value", "new").stdout
        )
        self.assertTrue((self.root / accepted["note"]).is_file())
        self.assertFalse(draft.exists())

    def test_record_state_write_failure_removes_pending_file_then_retry_succeeds(self) -> None:
        body, sources = self.write_card_input()
        module = load_state_module()
        original_replace = module.os.replace
        state_path = self.root / "_system" / "state.json"
        injected = False

        def fail_state_replace(source: object, destination: object) -> None:
            nonlocal injected
            if Path(destination).resolve() == state_path.resolve() and not injected:
                injected = True
                raise OSError("simulated state write failure")
            original_replace(source, destination)

        args = argparse.Namespace(
            config=str(self.config),
            title="Record retry test",
            slug="record-retry-test",
            question="Can a failed record be retried?",
            summary="A failed record leaves neither a state item nor a draft.",
            topic_key="record-retry-test",
            domain=["history-archaeology"],
            region=["Southern Africa"],
            mode="boundary",
            body=str(body),
            sources=str(sources),
        )
        with patch.object(module.os, "replace", fail_state_replace):
            with self.assertRaisesRegex(SystemExit, "prior files were restored"):
                module.cmd_record(args)

        self.assertEqual([], list((self.root / "_system" / "pending").glob("*.md")))
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual([], state["history"])
        recorded = self.record_card(
            title=args.title,
            slug=args.slug,
            question=args.question,
            summary=args.summary,
            body=body,
            sources=sources,
        )
        self.assertTrue((self.root / recorded["draft"]).is_file())

    def test_cli_json_output_is_utf8_even_when_python_io_encoding_is_ascii(self) -> None:
        body, sources = self.write_card_input()
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "ascii"
        result = subprocess.run(
            [
                sys.executable,
                str(STATE_SCRIPT),
                "--config",
                str(self.config),
                "record",
                "--title",
                "中文边界卡",
                "--slug",
                "utf8-output-test",
                "--question",
                "中文输出能否保持 UTF-8？",
                "--summary",
                "命令行输出需要稳定使用 UTF-8。",
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
            ],
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            timeout=10,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("中文边界卡", json.loads(result.stdout)["title"])

    def test_init_io_failure_leaves_no_pointer_and_retry_succeeds(self) -> None:
        config = self.temp / "retry-config.json"
        root = self.temp / "RetryBoundary"
        module = load_state_module()
        original_replace = module.os.replace
        injected = False

        def fail_config_replace(source: object, destination: object) -> None:
            nonlocal injected
            if Path(destination).resolve() == config.resolve() and not injected:
                injected = True
                raise OSError("simulated config write failure")
            original_replace(source, destination)

        with patch.object(module.os, "replace", fail_config_replace):
            with self.assertRaisesRegex(SystemExit, "prior files were restored"):
                module.cmd_init(
                    argparse.Namespace(
                        config=str(config),
                        root=str(root),
                        language="en",
                        mode="boundary",
                        timezone="UTC",
                    )
                )

        self.assertFalse(config.exists())
        self.assertFalse((root / "_system" / "state.json").exists())
        self.assertFalse((root / "INDEX.md").exists())
        self.run_cli(
            "init",
            "--root",
            str(root),
            "--language",
            "en",
            "--mode",
            "boundary",
            "--timezone",
            "UTC",
            config=config,
        )
        self.assertTrue((root / "_system" / "state.json").is_file())
        self.assertTrue((root / "INDEX.md").is_file())

    def test_init_rejects_config_path_collisions_before_creating_root(self) -> None:
        for relative in (
            "INDEX.md",
            "_system/state.json",
            "Cards/config.json",
            "Reports/config.json",
            "_system/config.json",
        ):
            with self.subTest(config=relative):
                root = self.temp / f"Conflict-{relative.replace('/', '-')}"
                config = root / relative
                result = self.run_cli(
                    "init",
                    "--root",
                    str(root),
                    "--language",
                    "en",
                    "--mode",
                    "boundary",
                    "--timezone",
                    "UTC",
                    config=config,
                    expect_ok=False,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn("managed Boundary path", result.stderr)
                self.assertFalse(root.exists())

        root = self.temp / "TopLevelConfigBoundary"
        config = root / "config.json"
        self.run_cli(
            "init",
            "--root",
            str(root),
            "--language",
            "en",
            "--mode",
            "boundary",
            "--timezone",
            "UTC",
            config=config,
        )
        self.assertTrue(config.is_file())
        self.assertTrue((root / "_system" / "state.json").is_file())

    def test_missing_root_is_not_recreated_by_record(self) -> None:
        self.root.rename(self.temp / "MovedBoundary")
        body, sources = self.write_card_input()
        result = self.run_cli(
            "record",
            "--title",
            "Missing root test",
            "--question",
            "Does a missing root stay missing?",
            "--summary",
            "A moved root should not be recreated.",
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
        self.assertIn("Configured Boundary root is missing", result.stderr)
        self.assertFalse(self.root.exists())

    def test_configure_root_validates_target_state_without_recreating_old_root(self) -> None:
        second_config = self.temp / "second-config.json"
        second_root = self.temp / "SecondBoundary"
        self.run_cli(
            "init",
            "--root",
            str(second_root),
            "--language",
            "en",
            "--mode",
            "boundary",
            "--timezone",
            "UTC",
            config=second_config,
        )
        self.root.rename(self.temp / "MovedBoundary")
        self.run_cli("configure", "--root", str(second_root))
        self.assertFalse(self.root.exists())
        self.assertEqual(str(second_root.resolve()), json.loads(self.run_cli("context").stdout)["root"])

        bad_root = self.temp / "InvalidBoundary"
        bad_config = self.temp / "bad-config.json"
        self.run_cli(
            "init",
            "--root",
            str(bad_root),
            "--language",
            "en",
            "--mode",
            "boundary",
            "--timezone",
            "UTC",
            config=bad_config,
        )
        state_path = bad_root / "_system" / "state.json"
        invalid_state = json.loads(state_path.read_text(encoding="utf-8"))
        invalid_state["history"] = None
        state_path.write_text(json.dumps(invalid_state), encoding="utf-8")
        current_config = json.loads(self.config.read_text(encoding="utf-8"))
        result = self.run_cli("configure", "--root", str(bad_root), expect_ok=False)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Invalid history", result.stderr)
        self.assertEqual(current_config["root"], json.loads(self.config.read_text(encoding="utf-8"))["root"])

    def test_distinct_config_paths_share_root_write_lock(self) -> None:
        module = load_state_module()
        alternate_config = self.temp / "alternate-config.json"
        alternate_config.write_text(self.config.read_text(encoding="utf-8"), encoding="utf-8")
        holder_code = (
            "import importlib.util, sys\n"
            "from pathlib import Path\n"
            "spec = importlib.util.spec_from_file_location('lock_holder_state', sys.argv[1])\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "with module.exclusive_file_lock(Path(sys.argv[2]), create_parent=False):\n"
            "    print('locked', flush=True)\n"
            "    sys.stdin.readline()\n"
        )
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        holder = subprocess.Popen(
            [sys.executable, "-c", holder_code, str(STATE_SCRIPT), str(module.root_lock_path(self.root))],
            cwd=PROJECT_ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=env,
        )
        try:
            self.assertEqual("locked\n", holder.stdout.readline())
            body, sources = self.write_card_input()
            args = [
                "record",
                "--title",
                "Concurrent card",
                "--question",
                "How does the shared root lock work?",
                "--summary",
                "Two config pointers still share one Boundary history.",
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
            ]
            blocked = self.run_cli(*args, config=alternate_config, expect_ok=False)
            self.assertNotEqual(0, blocked.returncode)
            self.assertIn("Boundary is busy", blocked.stderr)
            self.assertEqual([], json.loads(self.run_cli("context").stdout)["active"])
        finally:
            if holder.stdin:
                holder.stdin.write("release\n")
                holder.stdin.flush()
            holder.communicate(timeout=10)

        recorded = json.loads(self.run_cli(*args, config=alternate_config).stdout)
        self.assertEqual(1, len(json.loads(self.run_cli("context").stdout)["active"]))
        self.assertEqual(recorded["id"], json.loads(self.run_cli("context").stdout)["active"][0]["id"])

    def test_record_refuses_pending_directory_symlink_outside_root(self) -> None:
        outside = self.temp / "outside"
        outside.mkdir()
        sentinel = outside / "keep.md"
        sentinel.write_text("user file", encoding="utf-8")
        pending = self.root / "_system" / "pending"
        pending.rmdir()
        try:
            pending.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"directory symlinks are unavailable: {exc}")

        body, sources = self.write_card_input()
        result = self.run_cli(
            "record",
            "--title",
            "Symlink path test",
            "--question",
            "Can a Boundary output escape through a symlink?",
            "--summary",
            "Output artifacts remain inside the selected root.",
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
        self.assertIn("must stay inside", result.stderr)
        self.assertEqual("user file", sentinel.read_text(encoding="utf-8"))
        self.assertEqual([sentinel], list(outside.iterdir()))

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

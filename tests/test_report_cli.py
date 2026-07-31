from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_SCRIPT = PROJECT_ROOT / "scripts" / "report.py"


class BoundaryReportCliTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp = Path(self.temp_dir.name)

    def run_cli(self, *args: str, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(REPORT_SCRIPT), *args],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if expect_ok and result.returncode != 0:
            self.fail(f"Report CLI failed ({result.returncode}): {result.stderr or result.stdout}")
        return result

    def test_full_report_is_rendered_before_visual_approval(self) -> None:
        report_input = self.temp / "report.json"
        report_input.write_text(
            json.dumps(
                {
                    "title": "巨津巴布韦：证据与解释",
                    "question": "考古证据如何确认城市的建造者？",
                    "language": "zh",
                    "generated_at": "2026-07-28",
                    "summary": "多类相互支持的证据指向当地绍纳文化相关社群。",
                    "sections": [
                        {
                            "heading": "研究范围",
                            "paragraphs": ["本报告区分考古材料、后世解释和殖民时期假说。"],
                        },
                        {
                            "heading": "主要证据",
                            "paragraphs": ["建筑年代、聚落连续性与当地物质文化形成一致证据链。[1]"],
                            "bullets": ["石墙技术", "陶器序列", "区域贸易"],
                        },
                        {
                            "heading": "竞争性解释",
                            "paragraphs": ["早期外来建造者假说缺乏相应考古证据。[2]"],
                        },
                        {
                            "heading": "限制与开放问题",
                            "paragraphs": ["部分社会组织细节仍需要进一步研究。"],
                        },
                    ],
                    "references": [
                        {
                            "title": "Archaeological record",
                            "url": "https://example.org/a",
                            "publisher": "Example Museum",
                        },
                        {
                            "title": "Historical synthesis",
                            "url": "https://example.net/b",
                            "publisher": "Example University",
                        },
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        pdf = self.temp / "Reports" / "great-zimbabwe.pdf"
        render_dir = self.temp / "_system" / "tmp" / "pdf"
        manifest = self.temp / "_system" / "report-validation.json"

        built = json.loads(
            self.run_cli(
                "build",
                "--input",
                str(report_input),
                "--output",
                str(pdf),
                "--render-dir",
                str(render_dir),
                "--manifest",
                str(manifest),
            ).stdout
        )
        self.assertTrue(pdf.is_file())
        self.assertGreaterEqual(built["page_count"], 2)
        self.assertEqual(built["page_count"], len(built["rendered_pages"]))
        self.assertNotIn("visual_approved_at", built)
        self.assertEqual(
            hashlib.sha256(pdf.read_bytes()).hexdigest(),
            built["pdf_sha256"],
        )
        for page in built["rendered_pages"]:
            self.assertTrue(Path(page).is_file())

        approved = json.loads(
            self.run_cli("approve", "--manifest", str(manifest)).stdout
        )
        self.assertIn("visual_approved_at", approved)
        self.assertEqual(built["pdf_sha256"], approved["pdf_sha256"])

    def test_approval_fails_if_pdf_changed_after_rendering(self) -> None:
        report_input = self.temp / "report.json"
        report_input.write_text(
            json.dumps(
                {
                    "title": "Evidence report",
                    "question": "What does the evidence establish?",
                    "language": "en",
                    "generated_at": "2026-07-28",
                    "summary": "The strongest available evidence supports the central conclusion.",
                    "sections": [
                        {
                            "heading": "Evidence",
                            "paragraphs": ["Independent records support the conclusion."],
                        }
                    ],
                    "references": [
                        {
                            "title": "Record A",
                            "url": "https://example.org/a",
                            "publisher": "Publisher A",
                        },
                        {
                            "title": "Record B",
                            "url": "https://example.net/b",
                            "publisher": "Publisher B",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        pdf = self.temp / "report.pdf"
        manifest = self.temp / "manifest.json"
        self.run_cli(
            "build",
            "--input",
            str(report_input),
            "--output",
            str(pdf),
            "--render-dir",
            str(self.temp / "rendered"),
            "--manifest",
            str(manifest),
        )
        pdf.write_bytes(pdf.read_bytes() + b"\nchanged")
        result = self.run_cli(
            "approve",
            "--manifest",
            str(manifest),
            expect_ok=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("changed after rendering", result.stderr)


if __name__ == "__main__":
    unittest.main()

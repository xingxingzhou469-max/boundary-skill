#!/usr/bin/env python3
"""Replay curated examples through the real CLI in an isolated directory. No network."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def run_demo(destination: Path) -> dict[str, str]:
    config = destination / "config.json"
    library = destination / "Boundary"

    def run(*args: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/state.py"), "--config", str(config), *args],
            text=True, encoding="utf-8", capture_output=True, check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        return json.loads(result.stdout)

    run("init", "--root", str(library), "--language", "en", "--mode", "boundary", "--timezone", "UTC")
    metadata = json.loads((EXAMPLES / "card.metadata.json").read_text(encoding="utf-8"))
    record = run(
        "record", "--title", metadata["title"], "--slug", metadata["slug"],
        "--question", metadata["question"], "--summary", metadata["summary"],
        "--topic-key", metadata["topic_key"], "--domain", metadata["domain"],
        "--region", metadata["region"], "--mode", "boundary",
        "--body", str(EXAMPLES / "card.en.md"), "--sources", str(EXAMPLES / "card.sources.json"),
    )
    # Each command is a fresh process: context must recover the persisted card.
    context = run("context")
    if [entry["id"] for entry in context["active"]] != [record["id"]]:
        raise RuntimeError("Context did not recover the pending card")
    accepted = run("feedback", "--id", record["id"], "--value", "deep")
    attached = run(
        "deep", "--id", record["id"], "--body", str(EXAMPLES / "report.en.md"),
        "--sources", str(EXAMPLES / "report.sources.json"),
    )
    card = library / accepted["note"]
    report = library / attached["report"]
    index = library / "INDEX.md"
    card_text, report_text = card.read_text(encoding="utf-8"), report.read_text(encoding="utf-8")
    expected = (
        (EXAMPLES / "card.en.md").read_text(encoding="utf-8").strip() in card_text,
        (EXAMPLES / "report.en.md").read_text(encoding="utf-8").strip() in report_text,
        f"../{attached['report']}" in card_text,
        f"../{accepted['note']}" in report_text,
        accepted["note"] in index.read_text(encoding="utf-8"),
        not (library / record["draft"]).exists(),
        attached["report_question"] == metadata["question"],
        not run("context")["pending_reports"],
    )
    if not all(expected):
        raise RuntimeError("Demo artifact or lifecycle verification failed")
    return {"card": str(card), "report": str(report), "index": str(index)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Keep output in a NEW directory; never replaces existing files")
    args = parser.parse_args()
    try:
        if args.output is not None:
            destination = args.output.expanduser().resolve()
            destination.mkdir(parents=True, exist_ok=False)
            paths = run_demo(destination)
            print(json.dumps(paths, ensure_ascii=False, indent=2))
        else:
            with tempfile.TemporaryDirectory(prefix="boundary-demo-") as temp:
                run_demo(Path(temp))
            print("PASS: initialize -> record -> resume -> feedback -> linked report; temporary files removed")
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(f"Demo failed: {exc}", file=sys.stderr)
        return 1
    print("Curated example replay only. No model calls or live fact-check; existing configuration untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

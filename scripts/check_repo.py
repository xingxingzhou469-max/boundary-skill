#!/usr/bin/env python3
"""Check the distributable skill and local documentation links without network access."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

from state import DOMAINS

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "SKILL.md", "LICENSE", "README.md", "README.zh-CN.md", "CONTRIBUTING.md",
    "agents/openai.yaml", "scripts/state.py", "scripts/demo.py",
    "references/domains.md", "references/source-policy.md",
    "references/output-formats.md", "references/storage.md",
    "references/quality-rubric.md", "references/source-map.md",
    "integrations/chatgpt/task.en.md", "integrations/chatgpt/task.zh-CN.md",
    "integrations/chatgpt/instructions.en.txt", "integrations/chatgpt/instructions.zh-CN.txt",
    "examples/card.en.md", "examples/card.zh-CN.md", "examples/report.en.md",
    "examples/card.sources.json", "examples/report.sources.json", "examples/card.metadata.json",
    "evals/cases.json",
)


def check(root: Path) -> list[str]:
    errors = [f"Missing required file: {name}" for name in REQUIRED if not (root / name).is_file()]
    skill = root / "SKILL.md"
    if not skill.is_file():
        return errors
    text = skill.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        errors.append("SKILL.md must start with YAML frontmatter")
    else:
        # This repository deliberately uses simple, single-line frontmatter fields.
        fields = dict(re.findall(r"^([a-z-]+): (.+)$", parts[1], re.MULTILINE))
        if fields.get("name") != "boundary":
            errors.append("Skill name must be boundary")
        if not 1 <= len(fields.get("description", "")) <= 1024:
            errors.append("Description must be 1–1024 characters")
        if fields.get("license") != "MIT":
            errors.append("Skill license must match LICENSE (MIT)")
        if not 1 <= len(fields.get("compatibility", "")) <= 500:
            errors.append("Compatibility must state runtime requirements within 500 characters")
    for path in sorted(root.rglob("*.md")):
        if any(part.startswith(".") or part in {"boundary-demo", "__pycache__"}
               for part in path.relative_to(root).parts):
            continue
        contents = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
        contents = re.sub(r"`[^`]*`", "", contents)
        # Repository-owned Markdown uses inline links; remote URLs and fragments
        # are intentionally excluded from this deterministic offline check.
        for target in re.findall(r"\]\(([^\s)]+)\)", contents):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"Link escapes repository: {path.relative_to(root)} -> {target}")
                continue
            if not resolved.exists():
                errors.append(f"Broken local link: {path.relative_to(root)} -> {target}")
    for path in sorted((root / "examples").glob("*.sources.json")):
        try:
            sources = json.loads(path.read_text(encoding="utf-8"))
            minimum = 3 if path.name.startswith("report.") else 2
            if not isinstance(sources, list) or len(sources) < minimum:
                errors.append(f"Too few sources in {path.name}")
        except (ValueError, OSError) as exc:
            errors.append(f"Invalid example source JSON: {path.name}: {exc}")
    case_path = root / "evals/cases.json"
    if case_path.is_file():
        try:
            catalog = json.loads(case_path.read_text(encoding="utf-8"))
            if not isinstance(catalog, dict) or not isinstance(catalog.get("cases"), list):
                raise ValueError("expected a versioned case object with a cases list")
            if not isinstance(catalog.get("eval_set_version"), str) or not catalog["eval_set_version"].strip():
                raise ValueError("eval_set_version must be nonempty")
            cases = catalog["cases"]
            fields = {"id", "domain", "language", "prompt", "setup", "observable_checks"}
            for case in cases:
                if not isinstance(case, dict) or fields - case.keys():
                    raise ValueError("every case needs id, domain, language, prompt, setup, and observable_checks")
                if any(not isinstance(case[key], str) or not case[key].strip() for key in ("id", "prompt")):
                    raise ValueError("case IDs and prompts must be nonempty strings")
                if case["language"] not in {"zh", "en"} or case["domain"] not in [None, *DOMAINS]:
                    raise ValueError(f"invalid language or domain in {case['id']}")
                if case["setup"] is not None and not isinstance(case["setup"], dict):
                    raise ValueError(f"invalid setup in {case['id']}")
                checks = case["observable_checks"]
                if not isinstance(checks, list) or not checks or any(not isinstance(item, str) or not item.strip() for item in checks):
                    raise ValueError(f"observable_checks must be nonempty strings in {case['id']}")
            if len({case["id"] for case in cases}) != len(cases):
                raise ValueError("case IDs must be unique")
            pairs = Counter((case["domain"], case["language"]) for case in cases if case["domain"] is not None)
            expected = {(domain, language) for domain in DOMAINS for language in ("zh", "en")}
            if set(pairs) != expected or any(count != 1 for count in pairs.values()):
                raise ValueError("fixed cards must cover each of the 12 domains exactly once per language")
            if sum(case["domain"] is None for case in cases) != 5:
                raise ValueError("expected five guard cases")
        except (ValueError, OSError, TypeError) as exc:
            errors.append(f"Invalid fixed evaluation catalog: {exc}")
    return errors


def main() -> int:
    errors = check(ROOT)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("PASS: skill metadata, required files, example JSON, fixed evaluation catalog, and local Markdown links")
    print("Not checked: external URL availability, research accuracy, or host/model behavior")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

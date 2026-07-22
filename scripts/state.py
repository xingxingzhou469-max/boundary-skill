#!/usr/bin/env python3
"""Transparent local state for the Boundary skill. Standard library only."""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import tempfile
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DOMAINS = [
    "earth-geography",
    "life-medicine",
    "math-physical-sciences",
    "engineering-infrastructure",
    "history-archaeology",
    "philosophy-religion-ethics",
    "politics-law-institutions",
    "economics-finance-business",
    "society-anthropology-psychology",
    "arts-literature-architecture",
    "language-communication",
    "daily-life-food-materials",
]

FEEDBACK = {"shown", "known", "new", "deep", "skipped"}
MODES = {"boundary", "wander", "alternate"}


def default_config_path() -> Path:
    override = os.environ.get("BOUNDARY_CONFIG")
    if override:
        return Path(override).expanduser().resolve()
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "boundary" / "config.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing Boundary file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Expected a JSON object in {path}")
    return value


def config_path(args: argparse.Namespace) -> Path:
    return Path(args.config).expanduser().resolve() if args.config else default_config_path()


def read_config(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    path = config_path(args)
    config = load_json(path)
    root = Path(str(config.get("root", ""))).expanduser()
    if not root.is_absolute():
        raise SystemExit(f"Configured Boundary root must be absolute: {root}")
    return path, config


def load_config(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    path, config = read_config(args)
    root = Path(config["root"])
    if not root.exists():
        raise SystemExit(f"Configured Boundary root is missing: {root}")
    return path, config


def state_path(config: dict[str, Any]) -> Path:
    return Path(config["root"]) / "_system" / "state.json"


def load_state(config: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    path = state_path(config)
    state = load_json(path)
    history = state.get("history")
    if not isinstance(history, list):
        raise SystemExit(f"Invalid history in {path}")
    return path, state


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    normalized = re.sub(r"[^\w\u4e00-\u9fff]+", "-", normalized, flags=re.UNICODE)
    return normalized.strip("-") or "topic"


def parse_time(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def resolve_mode(requested: str, config: dict[str, Any], history: list[dict[str, Any]]) -> str:
    mode = config.get("mode", "boundary") if requested == "default" else requested
    if mode != "alternate":
        return mode
    previous = next((item.get("mode") for item in reversed(history) if item.get("mode") in {"boundary", "wander"}), None)
    return "wander" if previous == "boundary" else "boundary"


def recent_skip_domains(history: list[dict[str, Any]], days: int = 7) -> set[str]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result: set[str] = set()
    for item in history:
        if item.get("feedback") != "skipped":
            continue
        timestamp = parse_time(item.get("shown_at", ""))
        domains = item.get("domains", [])
        if timestamp and timestamp >= cutoff and domains:
            result.add(domains[0])
    return result


def choose_domain(mode: str, history: list[dict[str, Any]], seed: int | None) -> str:
    rng = random.Random(seed)
    if mode == "wander":
        return rng.choice(DOMAINS)

    accepted = [item for item in history if item.get("feedback") in {"known", "new", "deep"}]
    counts = Counter(item["domains"][0] for item in accepted if item.get("domains"))
    skipped = recent_skip_domains(history)
    weights = []
    for domain in DOMAINS:
        weight = 1.0 / (1.0 + counts[domain])
        if domain in skipped:
            weight *= 0.35
        weights.append(weight)
    return rng.choices(DOMAINS, weights=weights, k=1)[0]


def cmd_init(args: argparse.Namespace) -> None:
    cfg_path = config_path(args)
    if cfg_path.exists() and not args.force:
        raise SystemExit(f"Configuration already exists: {cfg_path}. Use --force only after user confirmation.")

    root = Path(args.root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    for directory in ("Cards", "Reports", "_system"):
        (root / directory).mkdir(exist_ok=True)

    created = now_iso()
    config = {
        "version": 1,
        "root": str(root),
        "language": args.language,
        "mode": args.mode,
        "storage": args.storage,
        "created_at": created,
    }
    state = {"version": 1, "created_at": created, "history": []}
    atomic_write(cfg_path, config)
    atomic_write(root / "_system" / "state.json", state)
    print(json.dumps({"config": str(cfg_path), "root": str(root)}, ensure_ascii=False))


def cmd_context(args: argparse.Namespace) -> None:
    cfg_path, config = load_config(args)
    _, state = load_state(config)
    history = state["history"]
    counts = Counter(
        item["domains"][0]
        for item in history
        if item.get("feedback") in {"known", "new", "deep"} and item.get("domains")
    )
    recent = history[-args.limit :]
    payload = {
        "config_path": str(cfg_path),
        "root": config["root"],
        "language": config.get("language", "zh"),
        "default_mode": config.get("mode", "boundary"),
        "domain_counts": {domain: counts[domain] for domain in DOMAINS},
        "recent": recent,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_pick(args: argparse.Namespace) -> None:
    _, config = load_config(args)
    _, state = load_state(config)
    mode = resolve_mode(args.mode, config, state["history"])
    domain = choose_domain(mode, state["history"], args.seed)
    print(json.dumps({"mode": mode, "domain": domain}, ensure_ascii=False))


def cmd_record(args: argparse.Namespace) -> None:
    _, config = load_config(args)
    path, state = load_state(config)
    slug = slugify(args.slug or args.title)
    sources = list(dict.fromkeys(args.source))
    if len(sources) < 2:
        raise SystemExit("A Boundary card requires at least two distinct source URLs")
    for item in state["history"]:
        if item.get("slug") == slug and item.get("feedback") != "skipped":
            raise SystemExit(f"Duplicate topic slug: {slug}")
    entry = {
        "id": f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{slug}",
        "title": args.title,
        "slug": slug,
        "domains": list(dict.fromkeys(args.domain)),
        "mode": args.mode,
        "shown_at": now_iso(),
        "feedback": "shown",
        "sources": sources,
        "note": None,
        "report": None,
    }
    state["history"].append(entry)
    atomic_write(path, state)
    print(json.dumps(entry, ensure_ascii=False, indent=2))


def cmd_configure(args: argparse.Namespace) -> None:
    path, config = read_config(args)
    changed = False
    if args.language:
        config["language"] = args.language
        changed = True
    if args.mode:
        config["mode"] = args.mode
        changed = True
    if args.root:
        new_root = Path(args.root).expanduser().resolve()
        new_state = new_root / "_system" / "state.json"
        if not new_state.is_file():
            raise SystemExit(f"New Boundary root has no state file: {new_state}")
        config["root"] = str(new_root)
        changed = True
    if not changed:
        raise SystemExit("Provide at least one of --language, --mode, or --root")
    config["updated_at"] = now_iso()
    atomic_write(path, config)
    print(json.dumps(config, ensure_ascii=False, indent=2))


def cmd_feedback(args: argparse.Namespace) -> None:
    _, config = load_config(args)
    path, state = load_state(config)
    slug = slugify(args.slug)
    match = next((item for item in reversed(state["history"]) if item.get("slug") == slug), None)
    if match is None:
        raise SystemExit(f"No recorded topic found for slug: {slug}")
    match["feedback"] = args.value
    match["feedback_at"] = now_iso()
    if args.note:
        match["note"] = args.note
    if args.report:
        match["report"] = args.report
    atomic_write(path, state)
    print(json.dumps(match, ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--config", help="Override the pointer config path")
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Initialize a chosen Boundary root")
    init.add_argument("--root", required=True)
    init.add_argument("--language", choices=("zh", "en"), required=True)
    init.add_argument("--mode", choices=tuple(sorted(MODES)), required=True)
    init.add_argument("--storage", choices=("existing", "new"), required=True)
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    context = commands.add_parser("context", help="Show transparent selection context")
    context.add_argument("--limit", type=int, default=30)
    context.set_defaults(func=cmd_context)

    configure = commands.add_parser("configure", help="Change language, mode, or relink a moved root")
    configure.add_argument("--language", choices=("zh", "en"))
    configure.add_argument("--mode", choices=tuple(sorted(MODES)))
    configure.add_argument("--root", help="Existing Boundary root containing _system/state.json")
    configure.set_defaults(func=cmd_configure)

    pick = commands.add_parser("pick", help="Pick a mode and primary domain")
    pick.add_argument("--mode", choices=("default", "boundary", "wander", "alternate"), default="default")
    pick.add_argument("--seed", type=int, help="Deterministic seed for tests")
    pick.set_defaults(func=cmd_pick)

    record = commands.add_parser("record", help="Record a shown card")
    record.add_argument("--title", required=True)
    record.add_argument("--slug")
    record.add_argument("--domain", action="append", choices=DOMAINS, required=True)
    record.add_argument("--mode", choices=("boundary", "wander"), required=True)
    record.add_argument("--source", action="append", required=True)
    record.set_defaults(func=cmd_record)

    feedback = commands.add_parser("feedback", help="Apply user feedback to the latest matching card")
    feedback.add_argument("--slug", required=True)
    feedback.add_argument("--value", choices=tuple(sorted(FEEDBACK - {"shown"})), required=True)
    feedback.add_argument("--note")
    feedback.add_argument("--report")
    feedback.set_defaults(func=cmd_feedback)
    return root


def main() -> int:
    args = parser().parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

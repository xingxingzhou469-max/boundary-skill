#!/usr/bin/env python3
"""Boundary v2: durable local state and artifact lifecycle. Standard library only."""

from __future__ import annotations

import argparse
import copy
import errno
import json
import os
import random
import re
import sys
import tempfile
import unicodedata
from collections import Counter
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher
from functools import wraps
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


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

DOMAIN_LABELS = {
    "zh": {
        "earth-geography": "宇宙、地球与地理",
        "life-medicine": "生物、生态与医学",
        "math-physical-sciences": "数学、物理与化学",
        "engineering-infrastructure": "工程、技术与基础设施",
        "history-archaeology": "历史与考古",
        "philosophy-religion-ethics": "哲学、宗教与伦理",
        "politics-law-institutions": "政治、法律与制度",
        "economics-finance-business": "经济、金融与商业",
        "society-anthropology-psychology": "社会学、人类学与心理学",
        "arts-literature-architecture": "文学、艺术、音乐与建筑",
        "language-communication": "语言、文字与传播",
        "daily-life-food-materials": "日常生活、农业、食物与材料",
    },
    "en": {
        "earth-geography": "Cosmos, Earth, and geography",
        "life-medicine": "Life, ecology, and medicine",
        "math-physical-sciences": "Mathematics, physics, and chemistry",
        "engineering-infrastructure": "Engineering, technology, and infrastructure",
        "history-archaeology": "History and archaeology",
        "philosophy-religion-ethics": "Philosophy, religion, and ethics",
        "politics-law-institutions": "Politics, law, and institutions",
        "economics-finance-business": "Economics, finance, and business",
        "society-anthropology-psychology": "Society, anthropology, and psychology",
        "arts-literature-architecture": "Literature, arts, music, and architecture",
        "language-communication": "Language, writing, and communication",
        "daily-life-food-materials": "Daily life, agriculture, food, and materials",
    },
}

FEEDBACK = {"shown", "known", "new", "deep", "skipped"}
MODES = {"boundary", "wander", "alternate"}
SOURCE_KINDS = {
    "primary",
    "academic",
    "review",
    "authoritative",
    "expert",
    "journalism",
}
STATE_VERSION = 2
COVERAGE_DAYS = 90
SKIP_COOLDOWN_DAYS = 7


def default_config_path() -> Path:
    override = os.environ.get("BOUNDARY_CONFIG")
    if override:
        return Path(override).expanduser().resolve()
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "boundary" / "config.json"


def detect_timezone() -> str:
    environment = os.environ.get("TZ")
    if environment:
        try:
            ZoneInfo(environment)
            return environment
        except ZoneInfoNotFoundError:
            pass
    local = datetime.now().astimezone().tzinfo
    key = getattr(local, "key", None)
    if isinstance(key, str):
        return key
    try:
        resolved = Path("/etc/localtime").resolve()
        marker = "zoneinfo/"
        if marker in resolved.as_posix():
            candidate = resolved.as_posix().split(marker, 1)[1]
            ZoneInfo(candidate)
            return candidate
    except (OSError, ZoneInfoNotFoundError):
        pass
    return "UTC"


def timezone_for(config: dict[str, Any]) -> ZoneInfo:
    value = config.get("timezone")
    try:
        return ZoneInfo(value)
    except (TypeError, ZoneInfoNotFoundError) as exc:
        raise SystemExit(f"Invalid configured timezone: {value}") from exc


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def local_date(config: dict[str, Any], instant: datetime | None = None) -> str:
    current = instant or datetime.now(timezone.utc)
    return current.astimezone(timezone_for(config)).date().isoformat()


def atomic_text_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def atomic_json_write(path: Path, data: dict[str, Any]) -> None:
    serialized = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    atomic_text_write(path, serialized)


def atomic_write_batch(writes: dict[Path, str | None]) -> None:
    """Replace a small set of files together, restoring prior files on I/O errors."""
    prepared: list[dict[str, Any]] = []
    applied: list[dict[str, Any]] = []
    try:
        for path, content in writes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.is_symlink():
                raise SystemExit(f"Refusing to replace a Boundary output symlink: {path}")
            item: dict[str, Any] = {
                "path": path,
                "content": content,
                "existed": path.exists(),
                "stage": None,
                "backup": None,
            }
            prepared.append(item)

            if item["existed"]:
                if not path.is_file():
                    raise SystemExit(f"Boundary output is not a regular file: {path}")
                backup_fd, backup_name = tempfile.mkstemp(
                    prefix=f".{path.name}.backup.", dir=path.parent
                )
                item["backup"] = Path(backup_name)
                with os.fdopen(backup_fd, "wb") as handle:
                    handle.write(path.read_bytes())

            if content is not None:
                stage_fd, stage_name = tempfile.mkstemp(
                    prefix=f".{path.name}.stage.", dir=path.parent
                )
                item["stage"] = Path(stage_name)
                with os.fdopen(stage_fd, "w", encoding="utf-8") as handle:
                    handle.write(content)

        for item in prepared:
            path = item["path"]
            content = item["content"]
            if content is None:
                path.unlink(missing_ok=True)
            else:
                os.replace(item["stage"], path)
                item["stage"] = None
            applied.append(item)
    except BaseException as exc:
        rollback_errors: list[tuple[Path, OSError]] = []
        for item in reversed(applied):
            path = item["path"]
            backup = item["backup"]
            try:
                if backup is not None:
                    os.replace(backup, path)
                    item["backup"] = None
                else:
                    path.unlink(missing_ok=True)
            except OSError as rollback_error:
                rollback_errors.append((path, rollback_error))

        for item in prepared:
            stage = item["stage"]
            if stage is not None:
                try:
                    stage.unlink(missing_ok=True)
                except OSError:
                    pass

        if rollback_errors:
            details = "; ".join(
                f"{path}: {error}" for path, error in rollback_errors
            )
            retained = [
                str(item["backup"])
                for item in prepared
                if item["backup"] is not None and item["backup"].exists()
            ]
            backup_note = (
                " Recovery backups: " + ", ".join(retained)
                if retained
                else " No recovery backup remains for the affected new files."
            )
            raise SystemExit(
                f"Boundary write failed ({exc}); rollback also failed for {details}.{backup_note}"
            ) from exc

        for item in prepared:
            backup = item["backup"]
            if backup is not None:
                try:
                    backup.unlink(missing_ok=True)
                except OSError:
                    pass
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        if isinstance(exc, OSError):
            raise SystemExit(f"Boundary write failed; prior files were restored: {exc}") from exc
        raise

    for item in prepared:
        backup = item["backup"]
        if backup is not None:
            try:
                backup.unlink(missing_ok=True)
            except OSError:
                pass


@contextmanager
def exclusive_file_lock(path: Path, *, create_parent: bool = True) -> Iterator[None]:
    """Take a fail-fast OS lock that is released automatically when the process exits."""
    path = path.expanduser().resolve()
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    elif not path.parent.is_dir():
        raise SystemExit(f"Boundary root is missing or moved: {path.parent.parent}")
    with path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                if exc.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                    raise
                raise SystemExit(f"Boundary is busy; retry shortly (lock: {path})") from exc
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                if exc.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                    raise
                raise SystemExit(f"Boundary is busy; retry shortly (lock: {path})") from exc
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def config_lock_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    return resolved.with_name(f".{resolved.name}.lock")


def validate_init_config_location(config: Path, root: Path) -> None:
    resolved_root = root.expanduser().resolve()
    resolved_config = config.expanduser().resolve()
    try:
        relative = resolved_config.relative_to(resolved_root)
    except ValueError:
        return
    if (
        not relative.parts
        or relative.as_posix().casefold() == "index.md"
        or relative.parts[0].casefold() in {"cards", "reports", "_system"}
    ):
        raise SystemExit(
            f"Configuration cannot be stored in a managed Boundary path: {resolved_config}"
        )


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


def validate_config(config: dict[str, Any], path: Path) -> None:
    if config.get("version") != STATE_VERSION:
        raise SystemExit(
            f"Unsupported Boundary configuration version in {path}: "
            f"expected {STATE_VERSION}, found {config.get('version')}"
        )
    root = Path(str(config.get("root", ""))).expanduser()
    if not root.is_absolute():
        raise SystemExit(f"Configured Boundary root must be absolute: {root}")
    if config.get("language") not in {"zh", "en"}:
        raise SystemExit(f"Invalid configured language in {path}")
    if config.get("mode") not in MODES:
        raise SystemExit(f"Invalid configured mode in {path}")
    index_name = config.get("index")
    if (
        not isinstance(index_name, str)
        or not index_name
        or Path(index_name).name != index_name
        or Path(index_name).suffix.lower() != ".md"
    ):
        raise SystemExit(f"Invalid configured index file in {path}")
    timezone_for(config)


def read_config(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    path = config_path(args)
    config = load_json(path)
    validate_config(config, path)
    return path, config


def load_config(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    path, config = read_config(args)
    root = Path(config["root"])
    if not root.is_dir():
        raise SystemExit(f"Configured Boundary root is missing: {root}")
    return path, config


def state_path(config: dict[str, Any]) -> Path:
    return Path(config["root"]) / "_system" / "state.json"


def validate_entry(item: Any, path: Path) -> None:
    if not isinstance(item, dict):
        raise SystemExit(f"Invalid history entry in {path}")
    required = {
        "id",
        "title",
        "slug",
        "question",
        "summary",
        "topic_key",
        "domains",
        "regions",
        "mode",
        "shown_at",
        "feedback",
        "sources",
        "draft",
        "note",
        "report",
    }
    missing = sorted(required - item.keys())
    if missing:
        raise SystemExit(f"History entry {item.get('id', '<unknown>')} is missing: {', '.join(missing)}")
    if not valid_timestamp(item["shown_at"]):
        raise SystemExit(
            f"Invalid shown_at in history entry {item['id']} in {path}: "
            "expected an ISO 8601 date-time"
        )
    if "report_requested_at" in item and not valid_timestamp(item["report_requested_at"]):
        raise SystemExit(
            f"Invalid report_requested_at in history entry {item['id']} in {path}: "
            "expected an ISO 8601 date-time"
        )
    if item["feedback"] not in FEEDBACK:
        raise SystemExit(f"Invalid feedback in {path}: {item['feedback']}")
    if not isinstance(item["domains"], list) or not item["domains"]:
        raise SystemExit(f"Invalid domains in {path}")
    if any(domain not in DOMAINS for domain in item["domains"]):
        raise SystemExit(f"Unknown domain in {path}")
    if not isinstance(item["sources"], list) or len(item["sources"]) < 2:
        raise SystemExit(f"Invalid sources in {path}")


def load_state(config: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    path = state_path(config)
    normalized = relative_to_root(Path(config["root"]), path)
    if not normalized.startswith("_system/"):
        raise SystemExit(f"Boundary state must stay under _system/: {path}")
    state = load_json(path)
    if state.get("version") != STATE_VERSION:
        raise SystemExit(
            f"Unsupported Boundary state version in {path}: "
            f"expected {STATE_VERSION}, found {state.get('version')}"
        )
    history = state.get("history")
    if not isinstance(history, list):
        raise SystemExit(f"Invalid history in {path}")
    for item in history:
        validate_entry(item, path)
    return path, state


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    normalized = re.sub(r"[^\w\u4e00-\u9fff]+", "-", normalized, flags=re.UNICODE)
    return normalized.strip("-") or "topic"


def normalized_text(value: str) -> str:
    return re.sub(r"[\W_]+", "", unicodedata.normalize("NFKC", value).lower())


def parse_time(value: str) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def valid_timestamp(value: Any) -> bool:
    return isinstance(value, str) and "T" in value and parse_time(value) is not None


def relative_to_root(root: Path, path: Path) -> str:
    resolved_root = root.resolve()
    resolved = path.resolve()
    try:
        return resolved.relative_to(resolved_root).as_posix()
    except ValueError as exc:
        raise SystemExit(f"Boundary artifact must stay inside {resolved_root}: {resolved}") from exc


def root_lock_path(root: Path) -> Path:
    resolved_root = root.expanduser().resolve()
    path = resolved_root / "_system" / ".write.lock"
    normalized = relative_to_root(resolved_root, path)
    if not normalized.startswith("_system/"):
        raise SystemExit(f"Boundary system directory must stay inside {resolved_root}")
    return path


def lock_state_mutation(*, root_from_args: bool = False, root_lock: bool = True):
    def decorate(command):
        @wraps(command)
        def wrapped(args):
            cfg_path = config_path(args).expanduser().resolve()
            root = Path(args.root).expanduser().resolve() if root_from_args else None
            if root_from_args:
                validate_init_config_location(cfg_path, root)
            with exclusive_file_lock(config_lock_path(cfg_path)):
                if root_from_args:
                    if cfg_path.exists():
                        return command(args)
                else:
                    if not root_lock:
                        return command(args)
                    _, config = load_config(args)
                    load_state(config)
                    root = Path(config["root"]).expanduser().resolve()
                with exclusive_file_lock(
                    root_lock_path(root), create_parent=root_from_args
                ):
                    return command(args)

        return wrapped

    return decorate


def stored_artifact_path(root: Path, relative: Any, required_prefix: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise SystemExit("Boundary state contains a missing artifact path")
    candidate = (root / relative).resolve()
    normalized = relative_to_root(root, candidate)
    if not normalized.startswith(required_prefix):
        raise SystemExit(
            f"Boundary state artifact must stay under {required_prefix}: {relative}"
        )
    return candidate


def index_path(config: dict[str, Any]) -> Path:
    return Path(config["root"]) / config["index"]


def initial_index(language: str) -> str:
    title = "# 知识索引" if language == "zh" else "# Knowledge Index"
    intro = (
        "这里按时间列出已经确认的知识卡，每张卡是一个独立 Markdown 文件，可直接在手机上打开阅读。"
        if language == "zh"
        else "Accepted Boundary cards in reading order. Each card is a standalone Markdown file."
    )
    return f"{title}\n\n{intro}\n"


def resolve_mode(requested: str, config: dict[str, Any], history: list[dict[str, Any]]) -> str:
    mode = config["mode"] if requested == "default" else requested
    if mode != "alternate":
        return mode
    previous = next(
        (item["mode"] for item in reversed(history) if item.get("mode") in {"boundary", "wander"}),
        None,
    )
    return "wander" if previous == "boundary" else "boundary"


def recent_items(history: list[dict[str, Any]], days: int) -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return [
        item
        for item in history
        if (timestamp := parse_time(item.get("shown_at", ""))) is not None and timestamp >= cutoff
    ]


def recent_skip_domains(history: list[dict[str, Any]]) -> set[str]:
    return {
        item["domains"][0]
        for item in recent_items(history, SKIP_COOLDOWN_DAYS)
        if item["feedback"] == "skipped"
    }


def boundary_domain_weights(history: list[dict[str, Any]]) -> dict[str, float]:
    """Return a mild diversity prior for Boundary-mode domain hints."""
    coverage = recent_items(history, COVERAGE_DAYS)
    counts = Counter(item["domains"][0] for item in coverage)
    skipped = recent_skip_domains(history)
    weights: dict[str, float] = {}
    for domain in DOMAINS:
        # Coverage helps breadth but must not become a quality objective.
        recent_count = min(counts[domain], 4)
        weight = 1.0 / (1.0 + 0.15 * recent_count)
        if domain in skipped:
            # Skipping one topic is weak evidence about the whole domain.
            weight *= 0.9
        weights[domain] = weight
    return weights


def choose_domain(mode: str, history: list[dict[str, Any]], seed: int | None) -> str:
    rng = random.Random(seed)
    if mode == "wander":
        return rng.choice(DOMAINS)

    weights = boundary_domain_weights(history)
    return rng.choices(
        DOMAINS,
        weights=[weights[domain] for domain in DOMAINS],
        k=1,
    )[0]


def read_sources(path: Path, minimum: int = 2) -> list[dict[str, str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing source metadata file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid source metadata JSON in {path}: {exc}") from exc
    if not isinstance(value, list) or len(value) < minimum:
        raise SystemExit(f"At least {minimum} structured sources are required")

    result: list[dict[str, str]] = []
    urls: set[str] = set()
    publishers: set[str] = set()
    required = {"title", "url", "kind", "publisher", "supports"}
    optional_dates = {"accessed_at", "published_at"}
    for index, raw in enumerate(value, start=1):
        if not isinstance(raw, dict):
            raise SystemExit(f"Source {index} must be a JSON object")
        missing = required - raw.keys()
        if missing:
            raise SystemExit(f"Source {index} is missing: {', '.join(sorted(missing))}")
        if any(not isinstance(raw[key], str) for key in required):
            raise SystemExit(f"Source {index} required fields must be strings")
        source = {key: raw[key].strip() for key in required}
        if any(not source[key] for key in required):
            raise SystemExit(f"Source {index} contains an empty required field")
        for key in optional_dates & raw.keys():
            value = raw[key]
            if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise SystemExit(f"Source {index} {key} must be a real date in YYYY-MM-DD format")
            try:
                parsed_date = date.fromisoformat(value)
            except ValueError as exc:
                raise SystemExit(
                    f"Source {index} {key} must be a real date in YYYY-MM-DD format"
                ) from exc
            if parsed_date.isoformat() != value:
                raise SystemExit(f"Source {index} {key} must be a real date in YYYY-MM-DD format")
            source[key] = value
        parsed = urlparse(source["url"])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise SystemExit(f"Source {index} has an invalid URL: {source['url']}")
        if source["kind"] not in SOURCE_KINDS:
            raise SystemExit(f"Source {index} has an invalid kind: {source['kind']}")
        if source["url"] in urls:
            raise SystemExit(f"Duplicate source URL: {source['url']}")
        urls.add(source["url"])
        publishers.add(normalized_text(source["publisher"]))
        result.append(source)
    if len(publishers) < minimum:
        raise SystemExit(f"At least {minimum} independent publishers are required")
    return result


def topic_is_duplicate(
    history: list[dict[str, Any]],
    slug: str,
    topic_key: str,
    question: str,
    summary: str,
) -> tuple[dict[str, Any], bool] | None:
    now = datetime.now(timezone.utc)
    question_norm = normalized_text(question)
    summary_norm = normalized_text(summary)
    for item in reversed(history):
        exact = item["slug"] == slug or item["topic_key"] == topic_key
        question_similarity = SequenceMatcher(
            None, question_norm, normalized_text(item["question"])
        ).ratio()
        summary_similarity = SequenceMatcher(
            None, summary_norm, normalized_text(item["summary"])
        ).ratio()
        if not exact and question_similarity < 0.88 and summary_similarity < 0.90:
            continue
        timestamp = parse_time(item["shown_at"])
        cooling_down = (
            item["feedback"] == "skipped"
            and timestamp is not None
            and timestamp >= now - timedelta(days=SKIP_COOLDOWN_DAYS)
        )
        if item["feedback"] != "skipped" or cooling_down:
            return item, cooling_down
    return None


def card_frontmatter(entry: dict[str, Any]) -> str:
    lines = [
        "---",
        f'created: "{entry["shown_at"]}"',
        f'updated: "{entry["feedback_at"]}"',
        "type: boundary-card",
        f'mode: {entry["mode"]}',
        f'feedback: {entry["feedback"]}',
        "domains:",
    ]
    lines.extend(f'  - "{value}"' for value in entry["domains"])
    lines.append("regions:")
    lines.extend(f'  - "{value}"' for value in entry["regions"])
    lines.append("source_urls:")
    lines.extend(f'  - "{source["url"]}"' for source in entry["sources"])
    lines.extend(["---", ""])
    return "\n".join(lines)


def deep_frontmatter(
    entry: dict[str, Any], question: str, sources: list[dict[str, str]]
) -> str:
    lines = [
        "---",
        f'created: "{now_iso()}"',
        "type: boundary-deep-research",
        f'originating_card: "Cards/{entry["slug"]}.md"',
        f'question: {json.dumps(question, ensure_ascii=False)}',
        "source_urls:",
    ]
    lines.extend(f'  - "{source["url"]}"' for source in sources)
    lines.extend(["---", ""])
    return "\n".join(lines)


def add_index_entry(index_text: str, entry: dict[str, Any]) -> str:
    row = f'- [{entry["title"]}](Cards/{entry["slug"]}.md) — {entry["summary"]}\n'
    if row in index_text:
        return index_text
    return index_text.rstrip() + "\n" + row


def find_entry(state: dict[str, Any], identifier: str) -> dict[str, Any]:
    match = next((item for item in reversed(state["history"]) if item["id"] == identifier), None)
    if match is None:
        raise SystemExit(f"No recorded Boundary card found for id: {identifier}")
    return match


def report_is_pending(entry: dict[str, Any]) -> bool:
    if entry["report"] is not None:
        return False
    return entry["feedback"] == "deep" or (
        entry["feedback"] in {"known", "new"}
        and entry.get("report_requested_at") is not None
    )


@lock_state_mutation(root_from_args=True)
def cmd_init(args: argparse.Namespace) -> None:
    cfg_path = config_path(args)
    if cfg_path.exists():
        raise SystemExit(f"Configuration already exists: {cfg_path}")

    try:
        ZoneInfo(args.timezone)
    except ZoneInfoNotFoundError as exc:
        raise SystemExit(f"Unknown timezone: {args.timezone}") from exc

    root = Path(args.root).expanduser().resolve()
    existing_state = root / "_system" / "state.json"
    if existing_state.exists():
        raise SystemExit(f"Boundary state already exists: {existing_state}")
    directories = ("Cards", "Reports", "_system/pending", "_system/tmp")
    for directory in directories:
        normalized = relative_to_root(root, root / directory / ".boundary-path-check")
        if not normalized.startswith(directory + "/"):
            raise SystemExit(f"Boundary directory must stay under {directory}: {root / directory}")
    for directory in directories:
        (root / directory).mkdir(parents=True, exist_ok=True)

    created = now_iso()
    config = {
        "version": STATE_VERSION,
        "root": str(root),
        "language": args.language,
        "mode": args.mode,
        "timezone": args.timezone,
        "index": "INDEX.md",
        "created_at": created,
    }
    state = {"version": STATE_VERSION, "created_at": created, "history": []}
    index_file = index_path(config)
    relative_to_root(root, index_file)
    writes = {
        existing_state: json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    }
    if not index_file.exists():
        writes[index_file] = initial_index(args.language)
    writes[cfg_path] = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    atomic_write_batch(writes)
    print(json.dumps({"config": str(cfg_path), "root": str(root)}, ensure_ascii=False))


def cmd_context(args: argparse.Namespace) -> None:
    cfg_path, config = load_config(args)
    _, state = load_state(config)
    history = state["history"]
    coverage = recent_items(history, COVERAGE_DAYS)
    domain_counts = Counter(item["domains"][0] for item in coverage)
    region_counts = Counter(region for item in coverage for region in item["regions"])
    today = local_date(config)

    def shown_local_date(item: dict[str, Any]) -> str | None:
        timestamp = parse_time(item["shown_at"])
        return local_date(config, timestamp) if timestamp else None

    payload = {
        "config_path": str(cfg_path),
        "root": config["root"],
        "language": config["language"],
        "timezone": config["timezone"],
        "local_date": today,
        "default_mode": config["mode"],
        "coverage_days": COVERAGE_DAYS,
        "domain_counts": {domain: domain_counts[domain] for domain in DOMAINS},
        "region_counts": dict(sorted(region_counts.items())),
        "active": [item for item in history if item["feedback"] == "shown"],
        "pending_reports": [
            item for item in history if report_is_pending(item)
        ],
        "today": [item for item in history if shown_local_date(item) == today],
        "recent": history[-args.limit :],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_pick(args: argparse.Namespace) -> None:
    _, config = load_config(args)
    _, state = load_state(config)
    mode = resolve_mode(args.mode, config, state["history"])
    domain = choose_domain(mode, state["history"], args.seed)
    print(json.dumps({"mode": mode, "domain": domain}, ensure_ascii=False))


@lock_state_mutation()
def cmd_record(args: argparse.Namespace) -> None:
    _, config = load_config(args)
    path, state = load_state(config)
    root = Path(config["root"])
    title = args.title.strip()
    question = args.question.strip()
    summary = args.summary.strip()
    if not title:
        raise SystemExit("Card title cannot be empty")
    if not question:
        raise SystemExit("Card question cannot be empty")
    if not summary:
        raise SystemExit("Card summary cannot be empty")
    slug = slugify(args.slug or title)
    topic_key = slugify(args.topic_key or question)
    body_path = Path(args.body).expanduser().resolve()
    try:
        body = body_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing card body file: {body_path}") from exc
    if not body:
        raise SystemExit("Card body cannot be empty")
    if "\n" in summary:
        raise SystemExit("Card summary must be one line")
    sources = read_sources(Path(args.sources).expanduser().resolve(), minimum=2)
    duplicate = topic_is_duplicate(
        state["history"], slug, topic_key, question, summary
    )
    if duplicate:
        item, cooling_down = duplicate
        reason = "is still in its skip cooldown" if cooling_down else "already exists"
        raise SystemExit(f"Duplicate topic {reason}: {item['id']}")

    instant = datetime.now(timezone.utc)
    identifier = f"{instant.strftime('%Y%m%dT%H%M%S%fZ')}-{slug}"
    draft_path = root / "_system" / "pending" / f"{identifier}.md"
    draft_relative = relative_to_root(root, draft_path)
    if not draft_relative.startswith("_system/pending/"):
        raise SystemExit(f"Boundary pending card must stay under _system/pending/: {draft_path}")
    entry = {
        "id": identifier,
        "title": title,
        "slug": slug,
        "question": question,
        "summary": summary,
        "topic_key": topic_key,
        "domains": list(dict.fromkeys(args.domain)),
        "regions": list(dict.fromkeys(slugify(region) for region in args.region)),
        "mode": args.mode,
        "shown_at": now_iso(),
        "feedback": "shown",
        "sources": sources,
        "draft": draft_relative,
        "note": None,
        "report": None,
    }
    state["history"].append(entry)
    atomic_write_batch(
        {
            draft_path: body + "\n",
            path: json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        }
    )
    print(json.dumps(entry, ensure_ascii=False, indent=2))


@lock_state_mutation(root_lock=False)
def cmd_configure(args: argparse.Namespace) -> None:
    path, config = read_config(args)
    changed = False
    if args.language:
        config["language"] = args.language
        changed = True
    if args.mode:
        config["mode"] = args.mode
        changed = True
    if args.timezone:
        try:
            ZoneInfo(args.timezone)
        except ZoneInfoNotFoundError as exc:
            raise SystemExit(f"Unknown timezone: {args.timezone}") from exc
        config["timezone"] = args.timezone
        changed = True
    if args.root:
        new_root = Path(args.root).expanduser().resolve()
        load_state({"root": str(new_root)})
        config["root"] = str(new_root)
        changed = True
    if not changed:
        raise SystemExit("Provide at least one of --language, --mode, --timezone, or --root")
    config["updated_at"] = now_iso()
    validate_config(config, path)
    atomic_json_write(path, config)
    print(json.dumps(config, ensure_ascii=False, indent=2))


@lock_state_mutation()
def cmd_feedback(args: argparse.Namespace) -> None:
    _, config = load_config(args)
    path, state = load_state(config)
    root = Path(config["root"])
    entry = find_entry(state, args.id)
    if args.value == "deep" and entry["feedback"] in {"known", "new"}:
        if entry["report"] is not None or entry.get("report_requested_at") is not None:
            raise SystemExit(f"A deep research report was already requested for {entry['id']}")
        if not entry["note"]:
            raise SystemExit("The originating card note is missing from state")
        note_path = stored_artifact_path(root, entry["note"], "Cards/")
        if not note_path.is_file():
            raise SystemExit(f"Originating card note is missing: {note_path}")
        entry["report_requested_at"] = now_iso()
        atomic_write_batch({path: json.dumps(state, ensure_ascii=False, indent=2) + "\n"})
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return
    if entry["feedback"] != "shown":
        raise SystemExit(f"Feedback is already finalized for {entry['id']}: {entry['feedback']}")
    draft_path = stored_artifact_path(root, entry["draft"], "_system/pending/")
    if not draft_path.is_file():
        raise SystemExit(f"Pending card body is missing: {draft_path}")

    updated = copy.deepcopy(entry)
    updated["feedback"] = args.value
    updated["feedback_at"] = now_iso()
    updated["draft"] = None

    if args.value == "skipped":
        entry.update(updated)
        atomic_write_batch(
            {
                path: json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                draft_path: None,
            }
        )
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return

    index_file = index_path(config)
    relative_to_root(root, index_file)
    try:
        index_text = index_file.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"Index file is missing: {index_file}") from exc
    note_path = root / "Cards" / f"{entry['slug']}.md"
    note_relative = relative_to_root(root, note_path)
    if not note_relative.startswith("Cards/"):
        raise SystemExit(f"Boundary card must stay under Cards/: {note_path}")
    if note_path.exists():
        raise SystemExit(f"Card note already exists: {note_path}")
    body = draft_path.read_text(encoding="utf-8").strip()
    updated["note"] = note_relative
    note_text = card_frontmatter(updated) + body + "\n"
    index_text = add_index_entry(index_text, updated)

    entry.update(updated)
    atomic_write_batch(
        {
            note_path: note_text,
            index_file: index_text,
            path: json.dumps(state, ensure_ascii=False, indent=2) + "\n",
            draft_path: None,
        }
    )
    print(json.dumps(entry, ensure_ascii=False, indent=2))


@lock_state_mutation()
def cmd_deep(args: argparse.Namespace) -> None:
    _, config = load_config(args)
    path, state = load_state(config)
    root = Path(config["root"])
    entry = find_entry(state, args.id)
    if entry["report"]:
        raise SystemExit(f"Deep research report already exists: {entry['report']}")
    if not report_is_pending(entry):
        raise SystemExit("A deep research report requires a pending deep research request")
    if not entry["note"]:
        raise SystemExit("The originating card note is missing from state")

    input_path = Path(args.body).expanduser().resolve()
    try:
        body = input_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing deep research report body: {input_path}") from exc
    if not body:
        raise SystemExit("Deep research report body cannot be empty")
    sources = read_sources(Path(args.sources).expanduser().resolve(), minimum=3)
    question = (args.question or entry["question"]).strip()
    if not question:
        raise SystemExit("Deep research question cannot be empty")

    card_path = stored_artifact_path(root, entry["note"], "Cards/")
    if not card_path.is_file():
        raise SystemExit(f"Originating card note is missing: {card_path}")
    report_path = root / "Reports" / f"{entry['slug']}-deep-research.md"
    report_relative = relative_to_root(root, report_path)
    if not report_relative.startswith("Reports/"):
        raise SystemExit(f"Deep research report must stay under Reports/: {report_path}")
    if report_path.exists():
        raise SystemExit(f"Deep research report file already exists: {report_path}")

    origin_link = f"[{entry['title']}](../Cards/{entry['slug']}.md)"
    report_text = (
        deep_frontmatter(entry, question, sources)
        + f"**Originating card:** {origin_link}\n\n"
        + body
        + "\n"
    )
    card_text = card_path.read_text(encoding="utf-8").rstrip()
    heading = "深入了解" if config["language"] == "zh" else "Deep dive"
    label = "深度研究报告" if config["language"] == "zh" else "Deep research report"
    report_link = f"[{label}](../Reports/{entry['slug']}-deep-research.md)"
    if report_link not in card_text:
        card_text += f"\n\n## {heading}\n\n- {report_link}\n"

    updated = copy.deepcopy(entry)
    updated["report"] = report_relative
    updated["report_question"] = question
    updated["report_sources"] = sources
    entry.update(updated)
    atomic_write_batch(
        {
            report_path: report_text,
            card_path: card_text,
            path: json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        }
    )
    print(json.dumps(entry, ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--config", help="Override the pointer config path")
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Initialize a chosen Boundary root")
    init.add_argument("--root", required=True)
    init.add_argument("--language", choices=("zh", "en"), required=True)
    init.add_argument("--mode", choices=tuple(sorted(MODES)), required=True)
    init.add_argument("--timezone", default=detect_timezone())
    init.set_defaults(func=cmd_init)

    context = commands.add_parser("context", help="Show selection and active-card context")
    context.add_argument("--limit", type=int, default=30)
    context.set_defaults(func=cmd_context)

    configure = commands.add_parser("configure", help="Change language, mode, timezone, or root")
    configure.add_argument("--language", choices=("zh", "en"))
    configure.add_argument("--mode", choices=tuple(sorted(MODES)))
    configure.add_argument("--timezone")
    configure.add_argument("--root", help="Existing Boundary root containing v2 state")
    configure.set_defaults(func=cmd_configure)

    pick = commands.add_parser("pick", help="Pick a mode and primary domain")
    pick.add_argument(
        "--mode",
        choices=("default", "boundary", "wander", "alternate"),
        default="default",
    )
    pick.add_argument("--seed", type=int, help="Deterministic seed for tests")
    pick.set_defaults(func=cmd_pick)

    record = commands.add_parser("record", help="Persist a complete shown card")
    record.add_argument("--title", required=True)
    record.add_argument("--slug")
    record.add_argument("--question", required=True)
    record.add_argument("--summary", required=True)
    record.add_argument("--topic-key")
    record.add_argument("--domain", action="append", choices=DOMAINS, required=True)
    record.add_argument("--region", action="append", required=True)
    record.add_argument("--mode", choices=("boundary", "wander"), required=True)
    record.add_argument("--body", required=True, help="UTF-8 Markdown file containing the delivered card")
    record.add_argument("--sources", required=True, help="JSON file containing structured sources")
    record.set_defaults(func=cmd_record)

    feedback = commands.add_parser("feedback", help="Finalize a shown card or request a report for Known/New")
    feedback.add_argument("--id", required=True)
    feedback.add_argument("--value", choices=("known", "new", "deep", "skipped"), required=True)
    feedback.set_defaults(func=cmd_feedback)

    deep = commands.add_parser(
        "deep",
        help="Attach a verified report to a pending deep research request",
    )
    deep.add_argument("--id", required=True)
    deep.add_argument("--question")
    deep.add_argument("--body", required=True, help="UTF-8 Markdown deep research report")
    deep.add_argument("--sources", required=True, help="JSON file containing at least three sources")
    deep.set_defaults(func=cmd_deep)
    return root


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parser().parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

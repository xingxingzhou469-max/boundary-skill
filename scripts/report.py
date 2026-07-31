#!/usr/bin/env python3
"""Build, render, and approve a polished Boundary full-report PDF."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from xml.sax.saxutils import escape

try:
    from pypdf import PdfReader
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        KeepTogether,
        ListFlowable,
        ListItem,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Boundary PDF dependencies are missing. Install requirements-pdf.txt "
        "before generating a full report."
    ) from exc


NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#197C7A")
INK = colors.HexColor("#25313C")
MUTED = colors.HexColor("#647482")
PALE = colors.HexColor("#EAF3F2")
LINE = colors.HexColor("#CCD8DE")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def atomic_json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
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
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing report file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Expected a JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"Report field '{field}' must be non-empty text")
    return value.strip()


def validate_report(value: dict[str, Any]) -> dict[str, Any]:
    report = {
        "title": require_text(value.get("title"), "title"),
        "question": require_text(value.get("question"), "question"),
        "language": value.get("language"),
        "generated_at": require_text(value.get("generated_at"), "generated_at"),
        "summary": require_text(value.get("summary"), "summary"),
    }
    if report["language"] not in {"zh", "en"}:
        raise SystemExit("Report language must be 'zh' or 'en'")

    sections = value.get("sections")
    if not isinstance(sections, list) or not sections:
        raise SystemExit("Report requires at least one section")
    clean_sections: list[dict[str, Any]] = []
    for index, raw in enumerate(sections, start=1):
        if not isinstance(raw, dict):
            raise SystemExit(f"Section {index} must be an object")
        heading = require_text(raw.get("heading"), f"sections[{index}].heading")
        paragraphs = raw.get("paragraphs", [])
        bullets = raw.get("bullets", [])
        if not isinstance(paragraphs, list) or any(
            not isinstance(item, str) or not item.strip() for item in paragraphs
        ):
            raise SystemExit(f"Section {index} paragraphs must be non-empty strings")
        if not isinstance(bullets, list) or any(
            not isinstance(item, str) or not item.strip() for item in bullets
        ):
            raise SystemExit(f"Section {index} bullets must be non-empty strings")
        if not paragraphs and not bullets:
            raise SystemExit(f"Section {index} has no content")
        clean_sections.append(
            {
                "heading": heading,
                "paragraphs": [item.strip() for item in paragraphs],
                "bullets": [item.strip() for item in bullets],
            }
        )

    references = value.get("references")
    if not isinstance(references, list) or len(references) < 2:
        raise SystemExit("A full report requires at least two references")
    clean_references: list[dict[str, str]] = []
    for index, raw in enumerate(references, start=1):
        if not isinstance(raw, dict):
            raise SystemExit(f"Reference {index} must be an object")
        reference = {
            "title": require_text(raw.get("title"), f"references[{index}].title"),
            "url": require_text(raw.get("url"), f"references[{index}].url"),
            "publisher": require_text(
                raw.get("publisher"), f"references[{index}].publisher"
            ),
        }
        parsed = urlparse(reference["url"])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise SystemExit(f"Reference {index} has an invalid URL")
        clean_references.append(reference)

    report["sections"] = clean_sections
    report["references"] = clean_references
    return report


def font_names(language: str) -> tuple[str, str]:
    if language == "zh":
        name = "BoundaryCJK"
        if name not in pdfmetrics.getRegisteredFontNames():
            candidates = [
                os.environ.get("BOUNDARY_CJK_FONT"),
                "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "C:/Windows/Fonts/arialuni.ttf",
                "C:/Windows/Fonts/msyh.ttc",
            ]
            registered = False
            for candidate in candidates:
                if not candidate or not Path(candidate).is_file():
                    continue
                try:
                    pdfmetrics.registerFont(TTFont(name, candidate, subfontIndex=0))
                except Exception:
                    continue
                registered = True
                break
            if not registered:
                raise SystemExit(
                    "No embeddable Chinese font was found. Set BOUNDARY_CJK_FONT "
                    "to a TTF or TTC font with complete Chinese glyph coverage."
                )
            pdfmetrics.registerFontFamily(
                name,
                normal=name,
                bold=name,
                italic=name,
                boldItalic=name,
            )
        return name, name
    return "Helvetica", "Helvetica-Bold"


def styles_for(language: str) -> dict[str, ParagraphStyle]:
    normal_font, bold_font = font_names(language)
    base = getSampleStyleSheet()
    return {
        "label": ParagraphStyle(
            "BoundaryLabel",
            parent=base["Normal"],
            fontName=bold_font,
            fontSize=10,
            leading=13,
            textColor=TEAL,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "title": ParagraphStyle(
            "BoundaryTitle",
            parent=base["Title"],
            fontName=bold_font,
            fontSize=28,
            leading=36,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "question": ParagraphStyle(
            "BoundaryQuestion",
            parent=base["Normal"],
            fontName=normal_font,
            fontSize=13,
            leading=21,
            textColor=INK,
            alignment=TA_LEFT,
        ),
        "meta": ParagraphStyle(
            "BoundaryMeta",
            parent=base["Normal"],
            fontName=normal_font,
            fontSize=9,
            leading=12,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "BoundaryH1",
            parent=base["Heading1"],
            fontName=bold_font,
            fontSize=18,
            leading=24,
            textColor=NAVY,
            spaceBefore=12,
            spaceAfter=9,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "BoundaryH2",
            parent=base["Heading2"],
            fontName=bold_font,
            fontSize=13,
            leading=18,
            textColor=TEAL,
            spaceBefore=8,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "BoundaryBody",
            parent=base["BodyText"],
            fontName=normal_font,
            fontSize=10.5,
            leading=18,
            textColor=INK,
            spaceAfter=8,
        ),
        "toc": ParagraphStyle(
            "BoundaryToc",
            parent=base["BodyText"],
            fontName=normal_font,
            fontSize=11,
            leading=18,
            textColor=INK,
            leftIndent=8,
            spaceAfter=4,
        ),
        "reference": ParagraphStyle(
            "BoundaryReference",
            parent=base["BodyText"],
            fontName=normal_font,
            fontSize=8.5,
            leading=13,
            textColor=INK,
            spaceAfter=7,
        ),
    }


def paragraph_text(value: str) -> str:
    return escape(value).replace("\n", "<br/>")


def draw_first_page(canvas: Any, document: Any) -> None:
    canvas.saveState()
    canvas.setFillColor(TEAL)
    canvas.rect(0, A4[1] - 7 * mm, A4[0], 7 * mm, fill=1, stroke=0)
    canvas.restoreState()


def draw_later_pages(canvas: Any, document: Any) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, height - 15 * mm, width - 20 * mm, height - 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, height - 11.5 * mm, "BOUNDARY")
    canvas.drawRightString(width - 20 * mm, 11 * mm, str(document.page))
    canvas.restoreState()


def build_pdf(report: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = styles_for(report["language"])
    labels = (
        {
            "brand": "BOUNDARY | 完整研究报告",
            "question": "研究问题",
            "date": "生成日期",
            "contents": "目录",
            "summary": "执行摘要",
            "references": "完整参考文献",
        }
        if report["language"] == "zh"
        else {
            "brand": "BOUNDARY | FULL RESEARCH REPORT",
            "question": "Research question",
            "date": "Generated",
            "contents": "Contents",
            "summary": "Executive summary",
            "references": "Complete bibliography",
        }
    )

    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title=report["title"],
        author="Boundary",
        subject=report["question"],
    )
    story: list[Any] = [
        Spacer(1, 34 * mm),
        Paragraph(labels["brand"], styles["label"]),
        Paragraph(paragraph_text(report["title"]), styles["title"]),
        Spacer(1, 8 * mm),
    ]
    question_box = Table(
        [
            [Paragraph(labels["question"], styles["h2"])],
            [Paragraph(paragraph_text(report["question"]), styles["question"])],
        ],
        colWidths=[155 * mm],
        hAlign="CENTER",
    )
    question_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 10 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5 * mm),
            ]
        )
    )
    story.extend(
        [
            question_box,
            Spacer(1, 20 * mm),
            Paragraph(
                f'{labels["date"]}: {escape(report["generated_at"])}',
                styles["meta"],
            ),
            PageBreak(),
        ]
    )

    if len(report["sections"]) >= 4:
        story.append(Paragraph(labels["contents"], styles["h1"]))
        for number, section in enumerate(report["sections"], start=1):
            story.append(
                Paragraph(
                    f'{number:02d}  {paragraph_text(section["heading"])}',
                    styles["toc"],
                )
            )
        story.extend(
            [
                Paragraph(
                    f'{len(report["sections"]) + 1:02d}  {labels["references"]}',
                    styles["toc"],
                ),
                PageBreak(),
            ]
        )

    story.extend(
        [
            Paragraph(labels["summary"], styles["h1"]),
            Paragraph(paragraph_text(report["summary"]), styles["body"]),
        ]
    )
    for number, section in enumerate(report["sections"], start=1):
        heading = Paragraph(
            f'{number}. {paragraph_text(section["heading"])}',
            styles["h1"],
        )
        flows: list[Any] = [heading]
        flows.extend(
            Paragraph(paragraph_text(text), styles["body"])
            for text in section["paragraphs"]
        )
        if section["bullets"]:
            bullets = [
                ListItem(
                    Paragraph(paragraph_text(item), styles["body"]),
                    leftIndent=10,
                )
                for item in section["bullets"]
            ]
            flows.append(
                ListFlowable(
                    bullets,
                    bulletType="bullet",
                    start="circle",
                    leftIndent=18,
                    bulletColor=TEAL,
                )
            )
        story.extend(flows)

    story.append(Paragraph(labels["references"], styles["h1"]))
    for number, reference in enumerate(report["references"], start=1):
        url = escape(reference["url"], {'"': "&quot;"})
        text = (
            f'[{number}] {escape(reference["publisher"])}. '
            f'{escape(reference["title"])}. '
            f'<link href="{url}" color="#197C7A">{url}</link>'
        )
        story.append(Paragraph(text, styles["reference"]))

    document.build(story, onFirstPage=draw_first_page, onLaterPages=draw_later_pages)


def render_pdf(pdf: Path, render_dir: Path) -> list[Path]:
    executable = shutil.which("pdftoppm")
    if not executable:
        raise SystemExit("pdftoppm is required to visually validate Boundary PDFs")
    render_dir.mkdir(parents=True, exist_ok=True)
    for old_page in render_dir.glob("page-*.png"):
        old_page.unlink()
    prefix = render_dir / "page"
    result = subprocess.run(
        [executable, "-png", "-r", "144", str(pdf), str(prefix)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"Failed to render PDF: {result.stderr.strip()}")
    pages = sorted(render_dir.glob("page-*.png"))
    if not pages:
        raise SystemExit("PDF rendering produced no page images")
    return pages


def automated_pdf_checks(pdf: Path, rendered_pages: list[Path]) -> tuple[int, list[str]]:
    try:
        reader = PdfReader(str(pdf))
    except Exception as exc:
        raise SystemExit(f"Generated PDF could not be opened: {exc}") from exc
    page_count = len(reader.pages)
    if page_count < 2:
        raise SystemExit("A full report PDF must contain at least two pages")
    if page_count != len(rendered_pages):
        raise SystemExit("Rendered page count does not match the PDF")
    extracted = "".join((page.extract_text() or "") for page in reader.pages)
    if len(extracted.strip()) < 100:
        raise SystemExit("Generated PDF contains too little extractable text")
    if any(page.stat().st_size < 10_000 for page in rendered_pages):
        raise SystemExit("One or more rendered pages appear empty")
    return page_count, [
        "PDF opens successfully",
        "PDF contains at least two pages",
        "Every PDF page has a rendered PNG",
        "Rendered pages are non-empty",
        "Report text is extractable",
    ]


def cmd_build(args: argparse.Namespace) -> None:
    input_path = Path(args.input).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    render_dir = Path(args.render_dir).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()
    report = validate_report(load_json(input_path))
    build_pdf(report, output)
    rendered_pages = render_pdf(output, render_dir)
    page_count, checks = automated_pdf_checks(output, rendered_pages)
    manifest = {
        "version": 1,
        "pdf": str(output),
        "pdf_sha256": file_sha256(output),
        "page_count": page_count,
        "rendered_pages": [str(page) for page in rendered_pages],
        "automated_checks": checks,
        "built_at": now_iso(),
    }
    atomic_json_write(manifest_path, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def cmd_approve(args: argparse.Namespace) -> None:
    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest = load_json(manifest_path)
    pdf = Path(require_text(manifest.get("pdf"), "manifest.pdf"))
    if not pdf.is_file():
        raise SystemExit(f"Manifest PDF is missing: {pdf}")
    if file_sha256(pdf) != manifest.get("pdf_sha256"):
        raise SystemExit("PDF changed after rendering; rebuild and inspect it again")
    pages = manifest.get("rendered_pages")
    if not isinstance(pages, list) or not pages:
        raise SystemExit("Manifest contains no rendered pages")
    if any(not Path(page).is_file() for page in pages):
        raise SystemExit("One or more rendered pages are missing")
    if len(pages) != manifest.get("page_count"):
        raise SystemExit("Rendered page count no longer matches the manifest")
    manifest["visual_approved_at"] = now_iso()
    atomic_json_write(manifest_path, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build", help="Build and render a full report PDF")
    build.add_argument("--input", required=True, help="Structured report JSON")
    build.add_argument("--output", required=True, help="Final PDF path")
    build.add_argument("--render-dir", required=True, help="Temporary rendered-page directory")
    build.add_argument("--manifest", required=True, help="Validation manifest path")
    build.set_defaults(func=cmd_build)

    approve = commands.add_parser(
        "approve",
        help="Mark a rendered PDF approved after every page has been visually inspected",
    )
    approve.add_argument("--manifest", required=True)
    approve.set_defaults(func=cmd_approve)
    return root


def main() -> int:
    args = parser().parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

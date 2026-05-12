#!/usr/bin/env python3
"""Genera ricerca_sintomi_cronici.pdf da RICERCA_SINTOMI.md"""

import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.platypus.flowables import Flowable

MD_FILE  = "RICERCA_SINTOMI.md"
PDF_FILE = "ricerca_sintomi_cronici.pdf"

# ── Colori ────────────────────────────────────────────────────────────────
C_TITLE  = colors.HexColor("#1e50a0")
C_H2     = colors.HexColor("#143c82")
C_H3     = colors.HexColor("#283264")
C_ACCENT = colors.HexColor("#d0e6ff")
C_ROW0   = colors.HexColor("#f0f5ff")
C_ROW1   = colors.white
C_BORDER = colors.HexColor("#b4c8e6")
C_NOTE   = colors.HexColor("#646470")
C_WARN   = colors.HexColor("#b43c28")
C_TEXT   = colors.HexColor("#1e1e1e")


def md_to_rl(text: str) -> str:
    """Convert basic markdown inline to ReportLab XML."""
    # Escape XML special chars first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # **bold**
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # *italic*
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # `code`
    text = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", text)
    return text


def make_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["h1"] = ParagraphStyle("h1",
        parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=18,
        textColor=C_TITLE, backColor=C_ACCENT,
        spaceAfter=6, spaceBefore=4,
        leftIndent=4, leading=24)

    styles["h2"] = ParagraphStyle("h2",
        parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=13,
        textColor=C_H2, backColor=C_ACCENT,
        spaceBefore=12, spaceAfter=4,
        leftIndent=2, leading=18)

    styles["h3"] = ParagraphStyle("h3",
        parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=11,
        textColor=C_H3,
        spaceBefore=8, spaceAfter=3,
        leading=14)

    styles["body"] = ParagraphStyle("body",
        parent=base["Normal"],
        fontName="Helvetica", fontSize=10,
        textColor=C_TEXT,
        spaceAfter=2, leading=14)

    styles["bullet"] = ParagraphStyle("bullet",
        parent=base["Normal"],
        fontName="Helvetica", fontSize=10,
        textColor=C_TEXT,
        leftIndent=12, firstLineIndent=-8,
        spaceAfter=2, leading=13)

    styles["bullet2"] = ParagraphStyle("bullet2",
        parent=base["Normal"],
        fontName="Helvetica", fontSize=9,
        textColor=C_TEXT,
        leftIndent=22, firstLineIndent=-8,
        spaceAfter=2, leading=12)

    styles["quote"] = ParagraphStyle("quote",
        parent=base["Normal"],
        fontName="Helvetica-Oblique", fontSize=9,
        textColor=C_NOTE, backColor=colors.HexColor("#f0f5ff"),
        leftIndent=10, rightIndent=10,
        spaceBefore=4, spaceAfter=4, leading=13)

    styles["note"] = ParagraphStyle("note",
        parent=base["Normal"],
        fontName="Helvetica-Oblique", fontSize=8,
        textColor=C_NOTE,
        spaceAfter=6, leading=11)

    return styles


def parse_table(lines: list, start: int):
    """Return (headers, rows, next_index)."""
    headers, rows = [], []
    i = start
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r"^\|[-| :]+\|$", line):
            i += 1
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not headers:
                headers = cells
            else:
                rows.append(cells)
            i += 1
        else:
            break
    return headers, rows, i


def render_table(headers, rows, styles):
    col_count = len(headers)
    page_w = A4[0] - 36 * mm  # margins

    # Column widths: first col wider for 2-col tables
    if col_count == 2:
        col_widths = [page_w * 0.52, page_w * 0.48]
    else:
        col_widths = [page_w / col_count] * col_count

    header_style = ParagraphStyle("th",
        fontName="Helvetica-Bold", fontSize=8,
        textColor=colors.white, leading=11)
    cell_style = ParagraphStyle("td",
        fontName="Helvetica", fontSize=8,
        textColor=C_TEXT, leading=11)

    table_data = []
    # Header row
    table_data.append([Paragraph(md_to_rl(h), header_style) for h in headers])
    # Data rows
    for row in rows:
        table_data.append([Paragraph(md_to_rl(c), cell_style) for c in row])

    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_TITLE),
        ("GRID",        (0, 0), (-1, -1), 0.3, C_BORDER),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ])
    # Alternating row colors
    for r in range(1, len(table_data)):
        bg = C_ROW0 if r % 2 == 1 else C_ROW1
        ts.add("BACKGROUND", (0, r), (-1, r), bg)

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(ts)
    return t


def build_pdf(md_path: str, pdf_path: str):
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    styles = make_styles()
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm,  bottomMargin=18 * mm,
        title="Ricerca Clinica — Sintomi Cronici",
        author="Doctor_01",
    )

    story = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        # H1
        if re.match(r"^# [^#]", stripped):
            story.append(Paragraph(md_to_rl(stripped[2:]), styles["h1"]))
            story.append(Spacer(1, 4))
            i += 1

        # H2
        elif re.match(r"^## [^#]", stripped):
            story.append(Spacer(1, 6))
            story.append(Paragraph(md_to_rl(stripped[3:]), styles["h2"]))
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=C_H2, spaceAfter=4))
            i += 1

        # H3
        elif re.match(r"^### [^#]", stripped):
            story.append(Spacer(1, 4))
            story.append(Paragraph(md_to_rl(stripped[4:]), styles["h3"]))
            i += 1

        # HR
        elif stripped == "---":
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.3,
                                    color=C_BORDER, spaceAfter=4))
            i += 1

        # Blockquote
        elif stripped.startswith("> "):
            story.append(Paragraph(md_to_rl(stripped[2:]), styles["quote"]))
            i += 1

        # Table
        elif stripped.startswith("|"):
            headers, rows, i = parse_table(lines, i)
            if headers:
                story.append(Spacer(1, 4))
                story.append(render_table(headers, rows, styles))
                story.append(Spacer(1, 4))

        # Bullet level 2 (4+ spaces or 2 spaces)
        elif re.match(r"^  +[-*] ", raw):
            text = re.sub(r"^\s+[-*] ", "", raw)
            story.append(Paragraph("◦  " + md_to_rl(text), styles["bullet2"]))
            i += 1

        # Bullet level 1
        elif re.match(r"^[-*] ", stripped):
            text = re.sub(r"^[-*] ", "", stripped)
            story.append(Paragraph("•  " + md_to_rl(text), styles["bullet"]))
            i += 1

        # Blank
        elif stripped == "":
            story.append(Spacer(1, 3))
            i += 1

        # Italic-only line (disclaimer at bottom)
        elif stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            story.append(Paragraph(md_to_rl(stripped[1:-1]), styles["note"]))
            i += 1

        # Normal paragraph
        else:
            story.append(Paragraph(md_to_rl(stripped), styles["body"]))
            i += 1

    doc.build(story)
    print(f"PDF generato: {pdf_path}")


if __name__ == "__main__":
    build_pdf(MD_FILE, PDF_FILE)

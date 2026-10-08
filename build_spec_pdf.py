#!/usr/bin/env python3
"""
Builds a single, professionally formatted PDF that merges the content of:
  1. "Machine Specification.pdf"                      (commercial / package-output requirements)
  2. "Winding_Machine_Technical_Specifications.pdf"   (machine & bobbin technical data)

Bobbin drawings and the package photograph are the original raster images
extracted from the two source PDFs (see ./assets).

Output: Winding_Machines_Combined_Specification.pdf
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

# ---------------------------------------------------------------- design tokens
NAVY = colors.HexColor("#14263F")
NAVY_MID = colors.HexColor("#22405F")
ACCENT = colors.HexColor("#D2791E")
ACCENT_SOFT = colors.HexColor("#F8EADA")
GREY_BG = colors.HexColor("#F4F6F8")
GREY_LINE = colors.HexColor("#D8DEE6")
TEXT = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#6B7A8C")

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
BOTTOM_EXTRA = 5 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

DOC_TITLE = "Winding Machine Technical Specification"
DOC_SUB = "Soft Winding · Hard Winding · Sewing Thread"

PAD = 4.5          # default table cell padding (compact)
PAD_ROOMY = 6.0    # padding for the full-page comparison matrix

# ---------------------------------------------------------------- paragraph styles
_ss = getSampleStyleSheet()


def _p(name, **kw):
    base = dict(name=name, fontName="Helvetica", fontSize=9.5, leading=13.5,
                textColor=TEXT, spaceBefore=0, spaceAfter=0)
    base.update(kw)
    return ParagraphStyle(**base)


S = {
    "cover_kicker": _p("ck", fontName="Helvetica-Bold", fontSize=9, leading=12,
                       textColor=colors.white),
    "cover_title": _p("ct", fontName="Helvetica-Bold", fontSize=31, leading=36,
                      textColor=colors.white),
    "cover_sub": _p("cs", fontName="Helvetica", fontSize=12.5, leading=18,
                    textColor=colors.HexColor("#C5D3E2")),
    "cover_lead": _p("cl", fontSize=11, leading=17,
                     textColor=colors.HexColor("#AFC2D6")),
    "h1": _p("h1", fontName="Helvetica-Bold", fontSize=18, leading=22,
             textColor=NAVY, spaceAfter=2),
    "h1sub": _p("h1s", fontSize=10, leading=14, textColor=MUTED, spaceAfter=9),
    "h2": _p("h2", fontName="Helvetica-Bold", fontSize=11, leading=14,
             textColor=NAVY, spaceBefore=9, spaceAfter=4),
    "h3": _p("h3", fontName="Helvetica-Bold", fontSize=10, leading=13.5,
             textColor=NAVY_MID, spaceBefore=8, spaceAfter=3),
    "body": _p("body", alignment=TA_JUSTIFY, spaceAfter=6),
    "bullet": _p("bul", alignment=TA_JUSTIFY, leftIndent=11, bulletIndent=2,
                 spaceAfter=3.5),
    "caption": _p("cap", fontSize=8, leading=11, textColor=MUTED,
                  alignment=TA_CENTER, spaceBefore=3),
    "note": _p("note", fontSize=8.8, leading=12.5, textColor=MUTED,
               alignment=TA_JUSTIFY),
    "th": _p("th", fontName="Helvetica-Bold", fontSize=8, leading=10.5,
             textColor=colors.white),
    "td": _p("td", fontSize=8.8, leading=12),
    "td_b": _p("tdb", fontName="Helvetica-Bold", fontSize=8.8, leading=12,
               textColor=NAVY),
    "td_big": _p("tdbig", fontName="Helvetica-Bold", fontSize=12, leading=15,
                 textColor=NAVY),
    "badge": _p("badge", fontName="Helvetica-Bold", fontSize=8, leading=11,
                textColor=colors.white),
    "card_t": _p("cardt", fontName="Helvetica-Bold", fontSize=9.5, leading=12.5,
                 textColor=NAVY),
    "card_b": _p("cardb", fontSize=8.2, leading=11.5, textColor=MUTED),
}


def P(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    return [Paragraph(t, S["bullet"], bulletText="\u2022") for t in items]


# ---------------------------------------------------------------- table helpers
def spec_table(header, rows, col_widths, pad=PAD):
    """Header-row table with zebra striping."""
    data = [[Paragraph(h, S["th"]) for h in header]]
    for r in rows:
        data.append([c if hasattr(c, "wrap") else Paragraph(str(c), S["td"])
                     for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), GREY_BG))
    t.setStyle(TableStyle(style))
    return t


def kv_table(rows, label_w=52 * mm, total_w=None, pad=PAD):
    """Two-column label / value table."""
    total_w = total_w or CONTENT_W
    data = [[Paragraph(k, S["td_b"]),
             v if hasattr(v, "wrap") else Paragraph(str(v), S["td"])]
            for k, v in rows]
    t = Table(data, colWidths=[label_w, total_w - label_w], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
        ("BACKGROUND", (0, 0), (0, -1), GREY_BG),
        ("TOPPADDING", (0, 0), (-1, -1), pad + 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad + 1.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def stat_strip(items, width=CONTENT_W):
    """Row of big-number KPI cards."""
    n = len(items)
    cells = []
    for label, value in items:
        inner = Table(
            [[Paragraph(label.upper(), S["th"])],
             [Paragraph(value, S["td_big"])]],
            colWidths=[width / n - 3],
        )
        inner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), NAVY_MID),
            ("BACKGROUND", (0, 1), (0, 1), GREY_BG),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW", (0, 0), (0, 0), 1.2, ACCENT),
            ("BOX", (0, 1), (0, 1), 0.5, GREY_LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        cells.append(inner)
    outer = Table([cells], colWidths=[width / n] * n, hAlign="LEFT")
    outer.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return outer


def machine_cards(cards):
    """Three summary cards side by side (cover page)."""
    n = len(cards)
    cells = []
    for num, name, lines in cards:
        body = "<br/>".join(lines)
        inner = Table([[Paragraph(f'<font color="#D2791E">{num}</font> &nbsp; '
                                  f'{name}', S["card_t"])],
                       [Paragraph(body, S["card_b"])]],
                      colWidths=[CONTENT_W / n - 6])
        inner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.5, GREY_LINE),
            ("LINEABOVE", (0, 0), (0, 0), 2, NAVY),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (0, 0), 8),
            ("BOTTOMPADDING", (0, 0), (0, 0), 2),
            ("TOPPADDING", (0, 1), (0, 1), 2),
            ("BOTTOMPADDING", (0, 1), (0, 1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        cells.append(inner)
    outer = Table([cells], colWidths=[CONTENT_W / n] * n, hAlign="LEFT")
    outer.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return outer


def machine_header(number, title, strapline):
    badge = Table([[Paragraph(f"MACHINE {number}", S["badge"])]],
                  colWidths=[26 * mm])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    return [badge, Spacer(1, 6), P(title, "h1"), P(strapline, "h1sub")]


def fit_image(path, max_w, max_h=None):
    iw, ih = ImageReader(path).getSize()
    w, h = max_w, ih * (max_w / iw)
    if max_h and h > max_h:
        h, w = max_h, iw * (max_h / ih)
    return Image(path, width=w, height=h)


def figure(path, caption, max_w=None, max_h=None, frame_w=None):
    frame_w = frame_w or CONTENT_W
    img = fit_image(path, max_w or frame_w - 16, max_h)
    box = Table([[img], [Paragraph(caption, S["caption"])]],
                colWidths=[frame_w], hAlign="LEFT")
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.white),
        ("BOX", (0, 0), (0, 0), 0.5, GREY_LINE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (0, 0), 7),
        ("BOTTOMPADDING", (0, 0), (0, 0), 7),
        ("TOPPADDING", (0, 1), (0, 1), 3),
        ("BOTTOMPADDING", (0, 1), (0, 1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return box


def side_by_side(left, right, left_w):
    t = Table([[left, right]], colWidths=[left_w, CONTENT_W - left_w],
              hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 8),
        ("LEFTPADDING", (1, 0), (1, 0), 0),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def callout(title, body):
    t = Table([[Paragraph(title, S["td_b"])], [Paragraph(body, S["note"])]],
              colWidths=[CONTENT_W], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT_SOFT),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (0, 0), 6),
        ("BOTTOMPADDING", (0, 0), (0, 0), 2),
        ("TOPPADDING", (0, 1), (0, 1), 2),
        ("BOTTOMPADDING", (0, 1), (0, 1), 6),
    ]))
    return t


# ---------------------------------------------------------------- page furniture
def _footer(canv, doc):
    canv.saveState()
    canv.setFont("Helvetica", 7.5)
    canv.setFillColor(MUTED)
    canv.drawString(MARGIN, 11 * mm, DOC_TITLE)
    canv.drawRightString(PAGE_W - MARGIN, 11 * mm, f"Page {doc.page}")
    canv.setStrokeColor(GREY_LINE)
    canv.setLineWidth(0.5)
    canv.line(MARGIN, 14.5 * mm, PAGE_W - MARGIN, 14.5 * mm)
    canv.restoreState()


def draw_cover(canv, doc):
    canv.saveState()
    band_h = 122 * mm
    canv.setFillColor(NAVY)
    canv.rect(0, PAGE_H - band_h, PAGE_W, band_h, stroke=0, fill=1)
    canv.setStrokeColor(colors.HexColor("#2E4C6D"))
    canv.setLineWidth(1)
    for r in range(14, 92, 9):
        canv.circle(PAGE_W - 24 * mm, PAGE_H - band_h + 20 * mm, r,
                    stroke=1, fill=0)
    canv.setFillColor(ACCENT)
    canv.rect(0, PAGE_H - band_h, PAGE_W, 3.2 * mm, stroke=0, fill=1)
    canv.restoreState()
    _footer(canv, doc)


def draw_inner(canv, doc):
    canv.saveState()
    canv.setStrokeColor(GREY_LINE)
    canv.setLineWidth(0.5)
    canv.line(MARGIN, PAGE_H - 14 * mm, PAGE_W - MARGIN, PAGE_H - 14 * mm)
    canv.setFillColor(ACCENT)
    canv.rect(MARGIN, PAGE_H - 14 * mm, 16 * mm, 1.4, stroke=0, fill=1)
    canv.setFont("Helvetica", 7.5)
    canv.setFillColor(MUTED)
    canv.drawRightString(PAGE_W - MARGIN, PAGE_H - 12.3 * mm, DOC_SUB)
    canv.restoreState()
    _footer(canv, doc)


VOLT = "3PH (380–440 V AC) or 1PH (220–230 V AC) with PE &amp; N"


# ---------------------------------------------------------------- story
def build_story():
    st = []

    # ========================================================== COVER
    st.append(Spacer(1, 24 * mm))
    st.append(P("CONSOLIDATED TECHNICAL SPECIFICATION", "cover_kicker"))
    st.append(Spacer(1, 7))
    st.append(P("Winding Machines", "cover_title"))
    st.append(Spacer(1, 3))
    st.append(P("Soft Winding&nbsp; · &nbsp;Hard Winding&nbsp; · &nbsp;Sewing Thread",
                "cover_sub"))
    st.append(Spacer(1, 10))
    rule = Table([[""]], colWidths=[36 * mm], rowHeights=[2.2])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT)]))
    st.append(rule)
    st.append(Spacer(1, 12))
    st.append(P("Machine configuration, yarn compatibility, bobbin geometry and "
                "finished-package requirements for three winding machine types, "
                "consolidated from the two issued specification documents.",
                "cover_lead"))

    st.append(Spacer(1, 32 * mm))
    st.append(stat_strip([
        ("Machine types", "3"),
        ("Total spindles", "156"),
        ("Max winding speed", "1 000 m/min"),
        ("Supply frequency", "50 Hz"),
    ]))
    st.append(Spacer(1, 14))
    st.append(machine_cards([
        ("01", "Soft Winding", [
            "48 spindles", "Cotton · spun &amp; filament polyester",
            "Bobbin 160.40 mm · cylindrical",
            "Package Ø 160 mm · 1 kg",
            "0.30–0.40 g/cm³ · open build"]),
        ("02", "Hard Winding", [
            "60 spindles", "Cotton",
            "Bobbin 173.00 mm · conical",
            "Cone 150/180 mm · h 155 mm · 1 kg",
            "0.40–0.50 g/cm³ · dense build"]),
        ("03", "Sewing Thread", [
            "48 spindles", "Spun polyester (2- and 3-ply)",
            "Bobbin 114.00 mm · conical",
            "4 000 m / 100 g at 50/2",
            "Tension control + auto doffing"]),
    ]))
    st.append(Spacer(1, 14))
    st.append(kv_table([
        ("Compiled from", "<i>Machine Specification.pdf</i> &nbsp;+&nbsp; "
                          "<i>Winding_Machine_Technical_Specifications.pdf</i>"),
        ("Drawings", "Bobbin dimension drawings and the finished-package "
                     "photograph are reproduced from the source documents"),
        ("Units", "All linear dimensions in millimetres (mm) unless stated "
                  "otherwise"),
    ], label_w=32 * mm))

    st.append(NextPageTemplate("inner"))
    st.append(PageBreak())

    # ========================================================== 1 + 2
    st.append(P("1. Scope &amp; Machine Overview", "h1"))
    st.append(P("What this document covers", "h1sub"))
    st.append(P(
        "This specification consolidates the requirements for three distinct "
        "winding machines. Although all three convert yarn from a supply form "
        "onto a defined carrier, each serves a different downstream purpose and "
        "is therefore specified independently: the <b>soft winding machine</b> "
        "builds open, permeable packages intended for package dyeing; the "
        "<b>hard winding machine</b> builds dense, firm cones for storage, "
        "transport and onward processing; and the <b>sewing thread machine</b> "
        "builds precision, length-controlled cones of finished sewing thread.",
        "body"))
    st.append(P(
        "Sections 4 to 6 give the full per-machine data set, each with its "
        "dimensioned bobbin drawing. Section 7 restates the requirements for "
        "each machine type in narrative form, with the engineering intent "
        "behind each figure made explicit.", "body"))

    st.append(P("Contents", "h2"))
    st.append(spec_table(
        ["SECTION", "TITLE", "CONTENT"],
        [
            ["2", Paragraph("Common Electrical Specification", S["td_b"]),
             "Supply voltage, phases, protective conductors, frequency"],
            ["3", Paragraph("Comparison Matrix", S["td_b"]),
             "All three machines compared parameter by parameter"],
            ["4", Paragraph("Machine 01 — Soft Winding", S["td_b"]),
             "48 spindles · yarn counts · bobbin 160.40 mm · soft package targets"],
            ["5", Paragraph("Machine 02 — Hard Winding", S["td_b"]),
             "60 spindles · yarn counts · bobbin 173.00 mm · hard cone targets"],
            ["6", Paragraph("Machine 03 — Sewing Thread", S["td_b"]),
             "48 spindles · yarn counts · bobbin 114.00 mm · thread length targets"],
            ["7", Paragraph("Detailed Requirements by Machine Type", S["td_b"]),
             "Purpose, build, process, control and acceptance criteria per machine"],
            ["8", Paragraph("Notes on the Source Data", S["td_b"]),
             "Transcription correction and items requiring confirmation"],
        ],
        [18 * mm, 58 * mm, CONTENT_W - 76 * mm]))

    st.append(Spacer(1, 10))
    st.append(P("2. Common Electrical Specification", "h1"))
    st.append(P("Applies identically to all three machine types", "h1sub"))
    st.append(P(
        "All three machines share a single electrical supply specification. The "
        "machine shall be suitable for either a three-phase or a single-phase "
        "supply as installed, in both cases with protective earth and neutral "
        "conductors provided.", "body"))
    st.append(spec_table(
        ["SUPPLY ARRANGEMENT", "VOLTAGE", "CONDUCTORS", "FREQUENCY"],
        [
            [Paragraph("Three phase (3PH)", S["td_b"]), "380 – 440 V AC",
             "L1, L2, L3 + PE + N", "50 Hz"],
            [Paragraph("Single phase (1PH)", S["td_b"]), "220 – 230 V AC",
             "L + PE + N", "50 Hz"],
        ],
        [42 * mm, 38 * mm, 48 * mm, CONTENT_W - 128 * mm]))
    st.append(Spacer(1, 9))
    st.append(callout(
        "Installation note",
        "The supply arrangement (3PH or 1PH) must be confirmed per installation "
        "site before manufacture, as it affects drive selection, cabling and the "
        "protective device rating. Both options require PE and N to be brought "
        "to the machine terminal box."))

    # ========================================================== 3 MATRIX
    st.append(PageBreak())
    st.append(P("3. Comparison Matrix", "h1"))
    st.append(P("All three machines, parameter by parameter", "h1sub"))
    cw = [36 * mm] + [(CONTENT_W - 36 * mm) / 3] * 3
    st.append(spec_table(
        ["PARAMETER", "SOFT WINDING", "HARD WINDING", "SEWING THREAD"],
        [
            ["Primary application", "Package dyeing (intermediate package)",
             "Storage, transport and onward processing",
             "Finished sewing thread for direct use"],
            ["Number of spindles", Paragraph("<b>48</b>", S["td"]),
             Paragraph("<b>60</b>", S["td"]), Paragraph("<b>48</b>", S["td"])],
            ["Yarn compatibility",
             "Cotton; spun polyester; filament polyester", "Cotton",
             "Spun polyester"],
            ["Cotton count range", "10/1 – 50/1<br/>20/2 – 100/2",
             "10/1 – 50/1<br/>20/2 – 100/2", "—"],
            ["Polyester count range",
             "20/2 – 60/2 SSP (spun)<br/>50 D – 300 D (filament)", "—",
             "20/2 – 100/2 SSP<br/>16/3 – 80/3 SSP"],
            ["Carrier form", "Cylindrical, stepped ends",
             "Conical (tapered)", "Conical (tapered)"],
            ["Carrier length", "160.40 mm", "173.00 mm", "114.00 mm"],
            ["Carrier end diameters",
             "54.70 / 49.60 / 43.15 mm<br/>43.15 / 48.80 / 52.90 mm",
             "71.00 / 67.00 mm (large)<br/>37.00 / 26.00 mm (small)",
             "38.00 / 35.00 mm (large)<br/>28.00 / 12.60 mm (small)"],
            ["Finished package size", "Ø 160 mm",
             "Ø 150 mm top / Ø 180 mm base<br/>height 155 mm", "Not specified"],
            ["Finished package weight", "1 kg", "1 kg", "Not specified"],
            ["Target density",
             "0.30 – 0.35 g/cm³ (cotton)<br/>0.35 – 0.40 g/cm³ (polyester)",
             "0.40 – 0.50 g/cm³", "Not specified"],
            ["Length / weight target", "—", "—",
             "4 000 m per 100 g<br/>(50/2 spun)"],
            ["Maximum winding speed", "1 000 m/min", "1 000 m/min",
             "1 400 rpm"],
            ["Yarn tension control", "Not specified", "Not specified",
             Paragraph("<b>Required</b>", S["td"])],
            ["Automatic doffing / feeding", "Not specified", "Not specified",
             Paragraph("<b>Required</b>", S["td"])],
            ["Rated voltage",
             "3PH 380–440 V AC or<br/>1PH 220–230 V AC",
             "3PH 380–440 V AC or<br/>1PH 220–230 V AC",
             "3PH 380–440 V AC or<br/>1PH 220–230 V AC"],
            ["Supply frequency", "50 Hz", "50 Hz", "50 Hz"],
        ], cw, pad=PAD_ROOMY))
    st.append(Spacer(1, 7))
    st.append(P(
        "“Not specified” indicates the parameter was not stated in either source "
        "document for that machine; it is listed so that the gap is visible "
        "rather than assumed. “—” indicates the parameter does not apply to "
        "that machine. Carrier end diameters are given as stepped / stacked "
        "dimensions exactly as drawn.", "note"))

    # ========================================================== 4 SOFT
    st.append(PageBreak())
    st += machine_header(
        "01", "Soft Winding Machine",
        "48 spindles · open, permeable packages for package dyeing")
    st.append(stat_strip([
        ("Spindles", "48"),
        ("Package Ø", "160 mm"),
        ("Package weight", "1 kg"),
        ("Max speed", "1 000 m/min"),
    ]))

    st.append(P("4.1 Machine and electrical data", "h2"))
    st.append(spec_table(
        ["SPINDLES", "FREQUENCY", "RATED VOLTAGE"],
        [["48", "50 Hz", VOLT]],
        [24 * mm, 28 * mm, CONTENT_W - 52 * mm]))

    st.append(P("4.2 Yarn compatibility and count range", "h2"))
    st.append(spec_table(
        ["YARN TYPE", "COUNT RANGE"],
        [
            [Paragraph("Cotton yarn", S["td_b"]),
             "10/1 to 50/1 &nbsp;&amp;&nbsp; 20/2 to 100/2"],
            [Paragraph("Spun polyester", S["td_b"]), "20/2 to 60/2 SSP"],
            [Paragraph("Filament polyester", S["td_b"]), "50 D to 300 D"],
        ],
        [46 * mm, CONTENT_W - 46 * mm]))

    st.append(P("4.3 Finished package requirements", "h2"))
    st.append(spec_table(
        ["PARAMETER", "REQUIREMENT"],
        [
            [Paragraph("Finished package diameter", S["td_b"]), "160 mm"],
            [Paragraph("Finished package weight", S["td_b"]), "1 kg"],
            [Paragraph("Target package density — cotton", S["td_b"]),
             "0.30 – 0.35 g/cm³"],
            [Paragraph("Target package density — polyester", S["td_b"]),
             "0.35 – 0.40 g/cm³"],
            [Paragraph("Winding speed", S["td_b"]), "1 000 m/min (maximum)"],
        ],
        [68 * mm, CONTENT_W - 68 * mm]))

    st.append(P("4.4 Bobbin specification", "h2"))
    st.append(spec_table(
        ["OVERALL LENGTH", "MAIN BODY LENGTH", "END SECTIONS"],
        [["160.40 mm", "143.00 mm", "10.40 mm / 7.00 mm"]],
        [CONTENT_W / 3] * 3))
    st.append(Spacer(1, 3))
    st.append(spec_table(
        ["LEFT-END DIAMETERS", "RIGHT-END DIAMETERS", "CARRIER TYPE"],
        [["54.70 / 49.60 / 43.15 mm", "43.15 / 48.80 / 52.90 mm",
          "Soft winding bobbin"]],
        [CONTENT_W / 3] * 3))
    st.append(Spacer(1, 8))
    st.append(figure("assets/bobbin_soft.png",
                     "Figure 1 — Soft winding bobbin, dimensioned drawing (all "
                     "dimensions in mm). Reproduced from the source "
                     "specification.", max_h=88))

    # ========================================================== 5 HARD
    st.append(PageBreak())
    st += machine_header(
        "02", "Hard Winding Machine",
        "60 spindles · dense, firm cones for storage and onward processing")
    st.append(stat_strip([
        ("Spindles", "60"),
        ("Cone height", "155 mm"),
        ("Package weight", "1 kg"),
        ("Max speed", "1 000 m/min"),
    ]))

    st.append(P("5.1 Machine and electrical data", "h2"))
    st.append(spec_table(
        ["SPINDLES", "FREQUENCY", "RATED VOLTAGE"],
        [["60", "50 Hz", VOLT]],
        [24 * mm, 28 * mm, CONTENT_W - 52 * mm]))

    st.append(P("5.2 Yarn compatibility and count range", "h2"))
    st.append(spec_table(
        ["YARN TYPE", "COUNT RANGE"],
        [[Paragraph("Cotton yarn", S["td_b"]),
          "10/1 to 50/1 &nbsp;&amp;&nbsp; 20/2 to 100/2"]],
        [46 * mm, CONTENT_W - 46 * mm]))
    st.append(Spacer(1, 4))
    st.append(P("This machine is specified for cotton only. Polyester — spun or "
                "filament — is not within its stated compatibility range.",
                "note"))

    st.append(P("5.3 Finished package requirements", "h2"))
    pkg_w = 104 * mm
    pkg_table = spec_table(
        ["PARAMETER", "REQUIREMENT"],
        [
            [Paragraph("Package diameter — top", S["td_b"]), "150 mm"],
            [Paragraph("Package diameter — bottom", S["td_b"]), "180 mm"],
            [Paragraph("Package height", S["td_b"]), "155 mm"],
            [Paragraph("Package weight", S["td_b"]), "1 kg"],
            [Paragraph("Target hardness / density", S["td_b"]),
             "0.40 – 0.50 g/cm³"],
            [Paragraph("Winding speed", S["td_b"]),
             "1 000 m/min (max.)"],
        ],
        [56 * mm, pkg_w - 56 * mm])
    photo = figure("assets/package_photo.jpg",
                   "Figure 2 — Hard-wound finished package: 150 mm top Ø, "
                   "180 mm base Ø, 155 mm height.",
                   frame_w=CONTENT_W - pkg_w - 8, max_h=112)
    st.append(side_by_side(pkg_table, photo, pkg_w))

    st.append(P("5.4 Bobbin specification", "h2"))
    st.append(spec_table(
        ["OVERALL LENGTH", "LARGE-END DIAMETERS", "SMALL-END DIAMETERS"],
        [["173.00 mm", "71.00 / 67.00 mm", "37.00 / 26.00 mm"]],
        [CONTENT_W / 3] * 3))
    st.append(Spacer(1, 8))
    st.append(figure("assets/bobbin_hard.png",
                     "Figure 3 — Hard winding bobbin, dimensioned drawing (all "
                     "dimensions in mm). Reproduced from the source "
                     "specification.", max_h=92))

    # ========================================================== 6 SEWING
    st.append(PageBreak())
    st += machine_header(
        "03", "Sewing Thread Machine",
        "48 spindles · precision, length-controlled finished sewing thread")
    st.append(stat_strip([
        ("Spindles", "48"),
        ("Length / weight", "4 000 m / 100 g"),
        ("Max speed", "1 400 rpm"),
        ("Auto doffing", "Required"),
    ]))

    st.append(P("6.1 Machine and electrical data", "h2"))
    st.append(spec_table(
        ["SPINDLES", "FREQUENCY", "RATED VOLTAGE"],
        [["48", "50 Hz", VOLT]],
        [24 * mm, 28 * mm, CONTENT_W - 52 * mm]))

    st.append(P("6.2 Yarn compatibility and count range", "h2"))
    st.append(spec_table(
        ["YARN TYPE", "COUNT RANGE"],
        [[Paragraph("Spun polyester", S["td_b"]),
          "20/2 to 100/2 SSP &nbsp;&amp;&nbsp; 16/3 to 80/3 SSP"]],
        [46 * mm, CONTENT_W - 46 * mm]))

    st.append(P("6.3 Thread and process requirements", "h2"))
    st.append(spec_table(
        ["PARAMETER", "REQUIREMENT"],
        [
            [Paragraph("Thread length / weight", S["td_b"]),
             "4 000 m per 100 g &nbsp;(yarn count 50/2 spun)"],
            [Paragraph("Required winding speed", S["td_b"]),
             "1 400 rpm (maximum)"],
            [Paragraph("Yarn tension control", S["td_b"]),
             Paragraph("<b>Required</b>", S["td"])],
            [Paragraph("Automatic doffing / feeding", S["td_b"]),
             Paragraph("<b>Required</b>", S["td"])],
        ],
        [68 * mm, CONTENT_W - 68 * mm]))

    st.append(P("6.4 Bobbin specification", "h2"))
    st.append(spec_table(
        ["OVERALL LENGTH", "LARGE-END DIAMETERS", "SMALL-END DIAMETERS"],
        [["114.00 mm", "38.00 / 35.00 mm", "28.00 / 12.60 mm"]],
        [CONTENT_W / 3] * 3))
    st.append(Spacer(1, 8))
    st.append(figure("assets/bobbin_sewing.png",
                     "Figure 4 — Sewing thread bobbin, dimensioned drawing (all "
                     "dimensions in mm). Reproduced from the source "
                     "specification.", max_h=100))

    # ========================================================== 7 NARRATIVE
    st.append(PageBreak())
    st.append(P("7. Detailed Requirements by Machine Type", "h1"))
    st.append(P("Purpose, build, process behaviour and acceptance criteria",
                "h1sub"))
    st.append(P(
        "The preceding sections present the specification as tabulated data. "
        "This section states the same requirements in narrative form, with the "
        "engineering intent behind each figure made explicit. It introduces no "
        "new numeric requirements.", "body"))

    # --- 7.1 soft
    st.append(P("7.1 Soft Winding Machine", "h2"))
    st.append(P("Purpose and process role", "h3"))
    st.append(P(
        "The soft winding machine produces packages whose defining property is "
        "<b>permeability</b> rather than compactness. The package is an "
        "intermediate product: it is built specifically so that dye liquor can "
        "be forced through the full wound mass during package dyeing. Every "
        "requirement below follows from that single objective — the yarn must be "
        "laid down firmly enough to hold its shape through handling and loading "
        "into a dyeing carrier, yet loosely enough that liquor reaches the "
        "innermost layers at the same rate as the outermost ones.", "body"))
    st.append(P("Capacity and configuration", "h3"))
    st += bullets([
        "The machine shall be built with <b>48 winding spindles</b>, each "
        "independently threaded and each capable of being stopped without "
        "interrupting the remaining spindles.",
        "Electrical supply shall be <b>3PH 380–440 V AC or 1PH 220–230 V AC at "
        "50 Hz</b>, with protective earth and neutral provided.",
    ])
    st.append(P("Yarn compatibility", "h3"))
    st.append(P(
        "This is the most versatile of the three machines and shall handle three "
        "distinct fibre classes without mechanical reconfiguration beyond normal "
        "setting changes: <b>cotton</b> in counts 10/1 to 50/1 and 20/2 to "
        "100/2; <b>spun polyester</b> in counts 20/2 to 60/2 SSP; and "
        "<b>filament polyester</b> from 50 D to 300 D. The span from a coarse "
        "10/1 cotton to a fine 300 D filament is wide, so yarn-path components — "
        "guides, tensioners and traverse elements — shall be selected to run the "
        "full declared range without substitution.", "body"))
    st.append(P("Package build and density", "h3"))
    st.append(P(
        "The finished package shall be <b>160 mm in diameter</b> and weigh "
        "<b>1 kg</b>. Target density is fibre-dependent and is the primary "
        "quality acceptance criterion:", "body"))
    st += bullets([
        "<b>Cotton: 0.30 – 0.35 g/cm³.</b> Cotton swells appreciably when wet, "
        "so the dry wound density is held lower to leave room for that swelling "
        "without choking liquor flow.",
        "<b>Polyester: 0.35 – 0.40 g/cm³.</b> Polyester does not swell "
        "comparably, so a slightly firmer build is permitted — and is desirable "
        "for package stability.",
    ])
    st.append(Spacer(1, 4))
    st.append(P(
        "Density shall be uniform through the package. A package that meets the "
        "target as an average while varying materially between core and surface "
        "will dye unevenly and does not satisfy this specification.", "body"))
    st.append(P("Speed and carrier", "h3"))
    st.append(P(
        "Maximum winding speed shall be <b>1 000 m/min</b>. Yarn shall be wound "
        "onto the cylindrical stepped bobbin detailed in section 4.4: "
        "<b>160.40 mm</b> overall, with a <b>143.00 mm</b> main body and stepped "
        "end sections of 10.40 mm and 7.00 mm. The stepped ends (54.70 / 49.60 / "
        "43.15 mm at one end, 43.15 / 48.80 / 52.90 mm at the other) allow "
        "bobbins to nest and to locate positively on the dyeing carrier "
        "spindle.", "body"))

    # --- 7.2 hard
    st.append(P("7.2 Hard Winding Machine", "h2"))
    st.append(P("Purpose and process role", "h3"))
    st.append(P(
        "The hard winding machine has the opposite objective to the soft winder. "
        "Here the package is a <b>finished or near-finished</b> product, built "
        "for maximum yarn mass in minimum volume and for mechanical stability in "
        "storage, handling and transport. Liquor permeability is irrelevant; what "
        "matters is a firm, stable cone that will not collapse, telescope or "
        "shed layers when stacked, and that unwinds cleanly downstream.", "body"))
    st.append(P("Capacity and configuration", "h3"))
    st += bullets([
        "The machine shall be built with <b>60 winding spindles</b> — the "
        "highest spindle count of the three machines.",
        "Electrical supply shall be <b>3PH 380–440 V AC or 1PH 220–230 V AC at "
        "50 Hz</b>, with protective earth and neutral provided.",
    ])
    st.append(P("Yarn compatibility", "h3"))
    st.append(P(
        "The machine is specified for <b>cotton only</b>, in counts 10/1 to 50/1 "
        "and 20/2 to 100/2. Unlike the soft winder, no polyester capability is "
        "required. This narrower remit permits the yarn path and tension system "
        "to be optimised for the higher tension that hard winding demands.",
        "body"))
    st.append(P("Package build and hardness", "h3"))
    st.append(P(
        "The finished package is a <b>tapered cone</b>, not a cylinder, and shall "
        "be built to the following envelope: <b>150 mm diameter at the top, "
        "180 mm diameter at the base and 155 mm overall height</b>, at a "
        "finished weight of <b>1 kg</b>. Target hardness is "
        "<b>0.40 – 0.50 g/cm³</b> — between roughly 15 % and 65 % denser than "
        "the soft-wound equivalent. Achieving this reliably requires "
        "correspondingly higher and more tightly regulated winding tension, and "
        "traverse control good enough to hold square, stable cone edges at that "
        "density; soft or broken-down edges are the usual failure mode of an "
        "under-controlled hard winder.", "body"))
    st.append(P("Speed and carrier", "h3"))
    st.append(P(
        "Maximum winding speed shall be <b>1 000 m/min</b>, matching the soft "
        "winder. Yarn shall be wound onto the conical bobbin detailed in section "
        "5.4: <b>173.00 mm</b> overall — the longest carrier of the three — "
        "tapering from a large end of 71.00 / 67.00 mm to a small end of "
        "37.00 / 26.00 mm. That taper is what generates the finished cone "
        "profile, so carrier geometry and the 150 / 180 / 155 mm package "
        "envelope must be verified together rather than separately.", "body"))

    # --- 7.3 sewing
    st.append(P("7.3 Sewing Thread Machine", "h2"))
    st.append(P("Purpose and process role", "h3"))
    st.append(P(
        "The sewing thread machine winds <b>finished sewing thread</b> for sale "
        "and direct use in sewing operations. Its governing requirement is "
        "neither permeability nor density but <b>precision and repeatability</b>. "
        "A sewing thread package is consumed at high speed by a machine that "
        "cannot tolerate tension spikes, snarls or sloughing, and it is sold on "
        "a declared length. Both constraints drive the specification below.",
        "body"))
    st.append(P("Capacity and configuration", "h3"))
    st += bullets([
        "The machine shall be built with <b>48 winding spindles</b>.",
        "Electrical supply shall be <b>3PH 380–440 V AC or 1PH 220–230 V AC at "
        "50 Hz</b>, with protective earth and neutral provided.",
    ])
    st.append(P("Yarn compatibility", "h3"))
    st.append(P(
        "The machine is specified for <b>spun polyester</b> only, in counts "
        "20/2 to 100/2 SSP and 16/3 to 80/3 SSP. The inclusion of three-ply "
        "constructions (16/3 to 80/3) is significant: three-ply sewing threads "
        "are torque-prone, and the yarn path shall be arranged to wind them "
        "without introducing or releasing twist that would cause snarling at the "
        "point of use.", "body"))
    st.append(P("Length and weight control", "h3"))
    st.append(P(
        "The thread length-to-weight requirement is <b>4 000 m per 100 g</b> at "
        "a reference count of <b>50/2 spun</b> — equivalently 40 m per gram. "
        "This is the commercial basis on which the package is sold, so the "
        "machine shall provide length measurement and cut-off accurate enough to "
        "guarantee the declared length on every package, not merely on average "
        "across a batch.", "body"))
    st.append(P("Tension control", "h3"))
    st.append(P(
        "<b>Active yarn tension control is a mandatory requirement</b> for this "
        "machine. Consistent tension governs both the length-per-weight accuracy "
        "above and the thread's residual elongation and strength, which must not "
        "vary within a package or between packages. Open-loop or purely "
        "mechanical tensioning that drifts as the package builds does not meet "
        "this requirement.", "body"))
    st.append(P("Automation", "h3"))
    st.append(P(
        "<b>Automatic doffing and automatic feeding are mandatory "
        "requirements.</b> The machine shall eject completed packages and "
        "introduce empty carriers without manual intervention, and shall take up "
        "supply yarn automatically. Across 48 spindles this is what makes "
        "continuous unattended running practical; it also removes the "
        "package-to-package variation that manual doffing introduces at the "
        "start and end of each build.", "body"))
    st.append(P("Speed and carrier", "h3"))
    st.append(P(
        "Required winding speed is <b>1 400 rpm maximum</b>. Note that this "
        "figure is stated as a rotational speed, whereas the soft and hard "
        "winders are specified in linear terms (1 000 m/min) — see section 8.2. "
        "Yarn shall be wound onto the conical bobbin detailed in section 6.4: "
        "<b>114.00 mm</b> overall — the shortest carrier of the three — tapering "
        "from a large end of 38.00 / 35.00 mm to a small end of 28.00 / "
        "12.60 mm.", "body"))

    # ========================================================== 8 NOTES
    st.append(Spacer(1, 6))
    st.append(KeepTogether([
        P("8. Notes on the Source Data", "h1"),
        P("Transcription correction and items requiring confirmation", "h1sub"),
        P("The source data is reproduced as issued. Points identified during "
          "consolidation are recorded here rather than silently resolved.",
          "body"),
        P("8.1 Transcription correction applied", "h2"),
        spec_table(
            ["ITEM", "AS ISSUED", "AS PRESENTED HERE", "BASIS"],
            [
                ["Hard winder target density", "0.40 – .050 gm/cm³",
                 "0.40 – 0.50 g/cm³",
                 "“.050” is an evident typographical error; 0.050 g/cm³ would "
                 "be an order of magnitude <i>lower</i> than the soft-winding "
                 "target and inconsistent with a hard, dense package"],
            ],
            [32 * mm, 28 * mm, 30 * mm, CONTENT_W - 90 * mm]),
    ]))

    st.append(P("8.2 Items recommended for confirmation", "h2"))
    st += bullets([
        "<b>Speed units are inconsistent between machines.</b> The soft and hard "
        "winders are specified at 1 000 m/min (linear yarn speed); the sewing "
        "thread machine at 1 400 rpm (rotational speed). These are not directly "
        "comparable, and the rotational figure cannot be converted to a linear "
        "speed without a stated reference diameter. Confirm whether 1 400 rpm is "
        "the intended basis for the sewing thread machine.",
        "<b>The sewing thread package envelope is not specified.</b> No finished "
        "package diameter, height or weight is given for the sewing thread "
        "machine, although both other machines have a defined envelope and a "
        "1 kg finished weight.",
        "<b>Tension control and automatic doffing are stated only for the sewing "
        "thread machine.</b> Confirm whether these are genuinely not required on "
        "the soft and hard winders, or were simply not recorded for them.",
        "<b>Soft bobbin length and soft package diameter are both nominally "
        "160 mm.</b> These are independent dimensions — 160.40 mm is axial "
        "length, 160 mm is wound diameter — and the coincidence is not a "
        "relationship.",
        "<b>Density basis is not stated.</b> Confirm whether the target "
        "densities are to be measured on the wound yarn mass alone or on the "
        "gross package volume including the carrier, as the two give materially "
        "different figures.",
    ])

    st.append(P("8.3 Source documents", "h2"))
    st.append(spec_table(
        ["SOURCE FILE", "CONTRIBUTED CONTENT"],
        [
            [Paragraph("Machine Specification.pdf", S["td_b"]),
             "Finished-package requirements, target densities, winding speeds, "
             "thread length/weight, tension and auto-doffing. Package "
             "photograph (Figure 2)."],
            [Paragraph("Winding_Machine_Technical_Specifications.pdf",
                       S["td_b"]),
             "Machine configuration: spindle counts, electrical specification, "
             "yarn compatibility and count ranges, and all bobbin dimension "
             "drawings (Figures 1, 3 and 4)."],
        ],
        [58 * mm, CONTENT_W - 58 * mm]))
    st.append(Spacer(1, 6))
    st.append(callout(
        "End of document",
        "All values in sections 1 to 6 are reproduced unaltered, except as "
        "recorded in section 8.1."))
    return st


def main():
    out = "Winding_Machines_Combined_Specification.pdf"
    doc = BaseDocTemplate(
        out, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Winding Machine Technical Specification — "
              "Soft Winding, Hard Winding & Sewing Thread",
        author="MMS-ITS",
        subject="Consolidated winding machine specification",
        keywords="winding machine, soft winding, hard winding, sewing thread, "
                 "bobbin, yarn count, package density",
    )
    cover_frame = Frame(MARGIN, MARGIN, CONTENT_W, PAGE_H - 2 * MARGIN,
                        id="cover", leftPadding=0, rightPadding=0,
                        topPadding=0, bottomPadding=0)
    inner_frame = Frame(MARGIN, MARGIN + BOTTOM_EXTRA, CONTENT_W,
                        PAGE_H - 2 * MARGIN - 2 * BOTTOM_EXTRA, id="inner",
                        leftPadding=0, rightPadding=0, topPadding=0,
                        bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
        PageTemplate(id="inner", frames=[inner_frame], onPage=draw_inner),
    ])
    doc.build(build_story())
    print("wrote", out)


if __name__ == "__main__":
    main()

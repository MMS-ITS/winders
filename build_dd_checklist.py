#!/usr/bin/env python3
"""
Builds a brief technical compliance checklist for the seller to complete.

Scope is limited to the technical specification: electrical supply and the
three machines. 21 requirement lines, grouped so that each line is one
coherent technical requirement.

Each line is a mutually exclusive YES / NO AcroForm radio group plus a
free-text Remarks field, so the form can be completed in any PDF reader or
printed and filled in by hand.

Output: Winding_Machines_Seller_Due_Diligence_Checklist.pdf
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable,
                                Frame, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

# ---------------------------------------------------------------- design tokens
NAVY = colors.HexColor("#14263F")
NAVY_MID = colors.HexColor("#22405F")
ACCENT = colors.HexColor("#D2791E")
ACCENT_SOFT = colors.HexColor("#F8EADA")
GREY_BG = colors.HexColor("#F4F6F8")
GREY_LINE = colors.HexColor("#D8DEE6")
FIELD_BG = colors.HexColor("#FCFDFE")
TEXT = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#6B7A8C")

PAGE_W, PAGE_H = landscape(A4)          # 842 x 595
MARGIN = 15 * mm
BOTTOM_EXTRA = 4 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

DOC_TITLE = "Technical Compliance Checklist"
DOC_SUB = "Winding Machines · Soft Winding · Hard Winding · Sewing Thread"

# columns: # | requirement | yes | no | remarks
C_ITEM = 30
C_YN = 34
C_REQ = 328
C_REM = CONTENT_W - (C_ITEM + 2 * C_YN + C_REQ)
COLS = [C_ITEM, C_REQ, C_YN, C_YN, C_REM]


def _p(name, **kw):
    base = dict(name=name, fontName="Helvetica", fontSize=9, leading=12.5,
                textColor=TEXT, spaceBefore=0, spaceAfter=0)
    base.update(kw)
    return ParagraphStyle(**base)


S = {
    "kicker": _p("ck", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
                 textColor=colors.white),
    "title": _p("ct", fontName="Helvetica-Bold", fontSize=24, leading=28,
                textColor=colors.white),
    "sub": _p("cs", fontSize=11, leading=15,
              textColor=colors.HexColor("#C5D3E2")),
    "h2": _p("h2", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
             textColor=NAVY, spaceBefore=6, spaceAfter=4),
    "body": _p("body", spaceAfter=4),
    "bullet": _p("bul", fontSize=8.8, leading=12.5, leftIndent=11,
                 bulletIndent=2, spaceAfter=2.5),
    "note": _p("note", fontSize=8.2, leading=11.5, textColor=MUTED),
    "th": _p("th", fontName="Helvetica-Bold", fontSize=7.8, leading=10,
             textColor=colors.white),
    "td": _p("td", fontSize=9, leading=12.5),
    "td_b": _p("tdb", fontName="Helvetica-Bold", fontSize=8.8, leading=12,
               textColor=NAVY),
    "item": _p("item", fontName="Helvetica-Bold", fontSize=8.6, leading=11,
               textColor=NAVY_MID),
    "secbar": _p("sb", fontName="Helvetica-Bold", fontSize=9.5, leading=12.5,
                 textColor=colors.white),
    "fieldlbl": _p("fl", fontName="Helvetica-Bold", fontSize=8.4, leading=11,
                   textColor=NAVY),
}


def P(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    return [Paragraph(t, S["bullet"], bulletText="\u2022") for t in items]


# ---------------------------------------------------------------- form widgets
class Radio(Flowable):
    def __init__(self, group, value, size=11):
        Flowable.__init__(self)
        self.group, self.value = group, value
        self.width = self.height = size
        self.size = size

    def draw(self):
        self.canv.acroForm.radio(
            name=self.group, value=self.value, selected=False,
            x=0, y=0, size=self.size, shape="square", buttonStyle="cross",
            borderWidth=0.8, borderColor=NAVY_MID, fillColor=colors.white,
            textColor=NAVY, forceBorder=True, relative=True,
        )


class TextBox(Flowable):
    def __init__(self, name, width, height=15, multiline=True, fontsize=8.5):
        Flowable.__init__(self)
        self.name = name
        self.width, self.height = width, height
        self.multiline, self.fontsize = multiline, fontsize

    def draw(self):
        self.canv.acroForm.textfield(
            name=self.name, x=0, y=0, width=self.width, height=self.height,
            value="", fontSize=self.fontsize, fontName="Helvetica",
            borderWidth=0, borderColor=None, fillColor=None, textColor=TEXT,
            forceBorder=False, relative=True,
            fieldFlags="multiline" if self.multiline else "",
        )


# ---------------------------------------------------------------- tables
HEADER = ["#", "REQUIREMENT", "YES", "NO", "REMARKS / OBSERVATIONS"]
_counter = {"n": 0}


def section_bar(letter, title, subtitle=""):
    txt = f"SECTION {letter} &nbsp;—&nbsp; {title}"
    if subtitle:
        txt += (f'&nbsp;&nbsp;<font size="8" color="#C5D3E2">{subtitle}'
                f'</font>')
    t = Table([[Paragraph(txt, S["secbar"])]], colWidths=[CONTENT_W],
              hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY_MID),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def checklist_table(rows):
    data = [[Paragraph(h, S["th"]) for h in HEADER]]
    for code, req in rows:
        _counter["n"] += 1
        data.append([
            Paragraph(code, S["item"]),
            Paragraph(req, S["td"]),
            Radio(code, "yes"),
            Radio(code, "no"),
            TextBox(f"{code}_remarks", C_REM - 8, 20),
        ])
    t = Table(data, colWidths=COLS, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("ALIGN", (2, 0), (3, -1), "CENTER"),
        ("BACKGROUND", (2, 1), (3, -1), GREY_BG),
        ("LINEBEFORE", (2, 1), (2, -1), 0.8, NAVY_MID),
        ("LINEAFTER", (3, 1), (3, -1), 0.8, NAVY_MID),
        ("BACKGROUND", (4, 1), (4, -1), FIELD_BG),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
    ]
    t.setStyle(TableStyle(style))
    return t


def fields_row(pairs, label_ws, height=16):
    n = len(pairs)
    fw = (CONTENT_W - sum(label_ws)) / n
    cells, widths = [], []
    for (lbl, name), lw in zip(pairs, label_ws):
        cells.append(Paragraph(lbl, S["fieldlbl"]))
        widths.append(lw)
        cells.append(TextBox(name, fw - 12, height))
        widths.append(fw)
    t = Table([cells], colWidths=widths, hAlign="LEFT")
    style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(0, 2 * n, 2):
        style.append(("BACKGROUND", (i, 0), (i, 0), GREY_BG))
        style.append(("BACKGROUND", (i + 1, 0), (i + 1, 0), FIELD_BG))
    t.setStyle(TableStyle(style))
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
    canv.setFont("Helvetica", 7)
    canv.setFillColor(MUTED)
    canv.drawString(MARGIN, 9 * mm, DOC_TITLE)
    canv.drawRightString(PAGE_W - MARGIN, 9 * mm, f"Page {doc.page} of 3")
    canv.setStrokeColor(GREY_LINE)
    canv.setLineWidth(0.5)
    canv.line(MARGIN, 12 * mm, PAGE_W - MARGIN, 12 * mm)
    canv.restoreState()


def draw_cover(canv, doc):
    canv.saveState()
    band_h = 53 * mm
    canv.setFillColor(NAVY)
    canv.rect(0, PAGE_H - band_h, PAGE_W, band_h, stroke=0, fill=1)
    canv.setStrokeColor(colors.HexColor("#2E4C6D"))
    canv.setLineWidth(1)
    for r in range(10, 66, 8):
        canv.circle(PAGE_W - 28 * mm, PAGE_H - band_h + 13 * mm, r,
                    stroke=1, fill=0)
    canv.setFillColor(ACCENT)
    canv.rect(0, PAGE_H - band_h, PAGE_W, 2.4 * mm, stroke=0, fill=1)
    canv.restoreState()
    _footer(canv, doc)


def draw_inner(canv, doc):
    canv.saveState()
    canv.setStrokeColor(GREY_LINE)
    canv.setLineWidth(0.5)
    canv.line(MARGIN, PAGE_H - 11 * mm, PAGE_W - MARGIN, PAGE_H - 11 * mm)
    canv.setFillColor(ACCENT)
    canv.rect(MARGIN, PAGE_H - 11 * mm, 14 * mm, 1.3, stroke=0, fill=1)
    canv.setFont("Helvetica", 7)
    canv.setFillColor(MUTED)
    canv.drawRightString(PAGE_W - MARGIN, PAGE_H - 9.4 * mm, DOC_SUB)
    canv.restoreState()
    _footer(canv, doc)


# ---------------------------------------------------------------- requirements
SEC_A = [
    ("A1", "Electrical supply: <b>3PH 380–440 V AC</b> or "
           "<b>1PH 220–230 V AC</b>, with PE and N."),
    ("A2", "Supply frequency: <b>50 Hz</b>."),
]

SEC_B = [
    ("B1", "<b>48 winding spindles.</b>"),
    ("B2", "Yarn range: cotton <b>10/1–50/1</b> and <b>20/2–100/2</b>; spun "
           "polyester <b>20/2–60/2 SSP</b>; filament polyester "
           "<b>50 D–300 D</b>."),
    ("B3", "Finished package: <b>160 mm diameter</b>, <b>1 kg</b>."),
    ("B4", "Package density: <b>0.30–0.35 g/cm³</b> for cotton, "
           "<b>0.35–0.40 g/cm³</b> for polyester."),
    ("B5", "Winding speed: up to <b>1 000 m/min</b>."),
    ("B6", "Bobbin: <b>160.40 mm</b> overall (143.00 mm body), ends "
           "10.40 / 7.00 mm, diameters 54.70 / 49.60 / 43.15 mm and "
           "43.15 / 48.80 / 52.90 mm."),
]

SEC_C = [
    ("C1", "<b>60 winding spindles.</b>"),
    ("C2", "Yarn range: cotton <b>10/1–50/1</b> and <b>20/2–100/2</b>."),
    ("C3", "Finished cone: <b>150 mm top diameter</b>, <b>180 mm bottom "
           "diameter</b>, <b>155 mm height</b>, <b>1 kg</b>."),
    ("C4", "Package hardness / density: <b>0.40–0.50 g/cm³</b>."),
    ("C5", "Winding speed: up to <b>1 000 m/min</b>."),
    ("C6", "Bobbin: conical, <b>173.00 mm</b> overall, large end "
           "71.00 / 67.00 mm, small end 37.00 / 26.00 mm."),
]

SEC_D = [
    ("D1", "<b>48 winding spindles.</b>"),
    ("D2", "Yarn range: spun polyester <b>20/2–100/2 SSP</b> and "
           "<b>16/3–80/3 SSP</b>."),
    ("D3", "Thread length / weight: <b>4 000 m per 100 g</b> at count "
           "50/2 spun."),
    ("D4", "Winding speed: up to <b>1 400 rpm</b>."),
    ("D5", "<b>Yarn tension control provided.</b>"),
    ("D6", "<b>Automatic doffing and feeding provided.</b>"),
    ("D7", "Bobbin: conical, <b>114.00 mm</b> overall, large end "
           "38.00 / 35.00 mm, small end 28.00 / 12.60 mm."),
]


# ---------------------------------------------------------------- story
def build_story():
    st = []

    # ---------------------------------------------------------- header
    st.append(Spacer(1, 11 * mm))
    st.append(P("TO BE COMPLETED AND RETURNED BY THE SELLER", "kicker"))
    st.append(Spacer(1, 5))
    st.append(P("Technical Compliance Checklist", "title"))
    st.append(Spacer(1, 1))
    st.append(P("Winding Machines&nbsp; · &nbsp;Soft Winding&nbsp; · &nbsp;"
                "Hard Winding&nbsp; · &nbsp;Sewing Thread", "sub"))
    st.append(Spacer(1, 13 * mm))

    st += bullets([
        "Mark <b>YES</b> or <b>NO</b> on every line. Leave none blank.",
        "<b>YES</b> = the machine offered meets the requirement in full, as "
        "stated. Anything partial or conditional is <b>NO</b>.",
        "Explain every <b>NO</b> in <i>Remarks</i>, stating what is offered "
        "instead.",
    ])

    st.append(Spacer(1, 7))
    st.append(fields_row([("Company", "s_company"),
                          ("Contact", "s_contact")], [70, 70], 16))
    st.append(Spacer(1, 3))
    st.append(fields_row([("Offer ref.", "s_ref"), ("Date", "s_date")],
                         [70, 70], 16))

    st.append(Spacer(1, 11))
    st.append(NextPageTemplate("inner"))

    # ---------------------------------------------------------- sections
    def block(letter, title, subtitle, rows):
        return [CondPageBreak(130), section_bar(letter, title, subtitle),
                Spacer(1, 5), checklist_table(rows), Spacer(1, 11)]

    st += block("A", "Electrical Supply", "all three machines", SEC_A)
    st += block("B", "Soft Winding Machine", "48 spindles", SEC_B)
    st += block("C", "Hard Winding Machine", "60 spindles", SEC_C)
    st += block("D", "Sewing Thread Machine", "48 spindles", SEC_D)

    # ---------------------------------------------------------- declaration
    st.append(CondPageBreak(190))
    st.append(section_bar("E", "Declaration", "to be completed last"))
    st.append(Spacer(1, 8))
    st.append(P(f"I confirm that the {_counter['n']} responses above "
                f"accurately describe the machines offered, and that every "
                f"<b>NO</b> is explained in the corresponding Remarks field.",
                "body"))
    st.append(Spacer(1, 4))
    st.append(fields_row([("Name", "d_name"), ("Position", "d_position")],
                         [70, 70], 16))
    st.append(Spacer(1, 3))
    st.append(fields_row([("Signature", "d_signature"), ("Date", "d_date")],
                         [70, 70], 30))
    st.append(Spacer(1, 10))
    st.append(callout(
        "Note",
        "Requirements are taken from the consolidated document "
        "“Winding Machine Technical Specification — Soft Winding, Hard Winding "
        "&amp; Sewing Thread”. Technical scope only; commercial terms are not "
        "covered by this checklist."))
    return st


def main():
    out = "Winding_Machines_Seller_Due_Diligence_Checklist.pdf"
    doc = BaseDocTemplate(
        out, pagesize=landscape(A4),
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Technical Compliance Checklist — Winding Machines",
        author="MMS-ITS",
        subject="Seller technical compliance checklist for soft winding, "
                "hard winding and sewing thread machines",
        keywords="compliance checklist, winding machine, technical "
                 "specification",
    )
    cover = Frame(MARGIN, MARGIN, CONTENT_W, PAGE_H - 2 * MARGIN, id="cover",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    inner = Frame(MARGIN, MARGIN + BOTTOM_EXTRA, CONTENT_W,
                  PAGE_H - 2 * MARGIN - 2 * BOTTOM_EXTRA, id="inner",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover], onPage=draw_cover),
        PageTemplate(id="inner", frames=[inner], onPage=draw_inner),
    ])
    doc.build(build_story())
    print(f"wrote {out}  ({_counter['n']} requirement lines)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Builds a seller due-diligence / compliance checklist for the three winding
machines, derived line-by-line from Winding_Machines_Combined_Specification.pdf.

Every requirement line gives the seller a mutually exclusive YES / NO choice
(real AcroForm radio group) plus a free-text Remarks field, so the form can be
completed digitally in any PDF reader or printed and filled in by hand.

Output: Winding_Machines_Seller_Due_Diligence_Checklist.pdf
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
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

DOC_TITLE = "Seller Due-Diligence & Compliance Checklist"
DOC_SUB = "Winding Machines · Soft Winding · Hard Winding · Sewing Thread"

# column widths -------------------------------------------------------------
C_ITEM = 32
C_REF = 34
C_YN = 30
C_REQ = 296
C_REM = CONTENT_W - (C_ITEM + C_REF + 2 * C_YN + C_REQ)
COLS = [C_ITEM, C_REQ, C_REF, C_YN, C_YN, C_REM]


def _p(name, **kw):
    base = dict(name=name, fontName="Helvetica", fontSize=9, leading=12.5,
                textColor=TEXT, spaceBefore=0, spaceAfter=0)
    base.update(kw)
    return ParagraphStyle(**base)


S = {
    "cover_kicker": _p("ck", fontName="Helvetica-Bold", fontSize=8.5,
                       leading=11, textColor=colors.white),
    "cover_title": _p("ct", fontName="Helvetica-Bold", fontSize=25, leading=29,
                      textColor=colors.white),
    "cover_sub": _p("cs", fontSize=11, leading=15,
                    textColor=colors.HexColor("#C5D3E2")),
    "h1": _p("h1", fontName="Helvetica-Bold", fontSize=15, leading=19,
             textColor=NAVY, spaceAfter=2),
    "h1sub": _p("h1s", fontSize=9, leading=12.5, textColor=MUTED, spaceAfter=7),
    "h2": _p("h2", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
             textColor=NAVY, spaceBefore=8, spaceAfter=4),
    "body": _p("body", alignment=TA_JUSTIFY, spaceAfter=5),
    "bullet": _p("bul", fontSize=8.6, leading=12, leftIndent=11,
                 bulletIndent=2, spaceAfter=2.5),
    "note": _p("note", fontSize=8.2, leading=11.5, textColor=MUTED,
               alignment=TA_JUSTIFY),
    "th": _p("th", fontName="Helvetica-Bold", fontSize=7.6, leading=10,
             textColor=colors.white),
    "td": _p("td", fontSize=8.6, leading=11.5),
    "td_b": _p("tdb", fontName="Helvetica-Bold", fontSize=8.6, leading=11.5,
               textColor=NAVY),
    "ref": _p("ref", fontSize=7.6, leading=10, textColor=MUTED),
    "item": _p("item", fontName="Helvetica-Bold", fontSize=8.2, leading=11,
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
    """A single AcroForm radio button belonging to group `group`."""

    def __init__(self, group, value, size=10):
        Flowable.__init__(self)
        self.group, self.value = group, value
        self.width = self.height = size
        self.size = size

    def draw(self):
        self.canv.acroForm.radio(
            name=self.group, value=self.value, selected=False,
            x=0, y=0, size=self.size, shape="square", buttonStyle="cross",
            borderWidth=0.7, borderColor=NAVY_MID, fillColor=colors.white,
            textColor=NAVY, forceBorder=True, relative=True,
        )


class TextBox(Flowable):
    """A borderless AcroForm text field sized to its table cell."""

    def __init__(self, name, width, height=15, multiline=True, fontsize=8):
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


# ---------------------------------------------------------------- table helpers
HEADER = ["#", "REQUIREMENT", "SPEC REF", "YES", "NO",
          "REMARKS / OBSERVATIONS"]

_counter = {"n": 0}


def section_bar(letter, title, subtitle=""):
    txt = f"SECTION {letter} &nbsp;—&nbsp; {title}"
    if subtitle:
        txt += (f'&nbsp;&nbsp;<font size="8" color="#C5D3E2">'
                f'{subtitle}</font>')
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
    """rows: list of (code, requirement_html, spec_ref)."""
    data = [[Paragraph(h, S["th"]) for h in HEADER]]
    for code, req, ref in rows:
        _counter["n"] += 1
        data.append([
            Paragraph(code, S["item"]),
            Paragraph(req, S["td"]),
            Paragraph(ref, S["ref"]),
            Radio(code, "yes"),
            Radio(code, "no"),
            TextBox(f"{code}_remarks", C_REM - 8, 17),
        ])
    t = Table(data, colWidths=COLS, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        # yes / no columns
        ("ALIGN", (3, 0), (4, -1), "CENTER"),
        ("BACKGROUND", (3, 1), (4, -1), GREY_BG),
        ("LINEBEFORE", (3, 1), (3, -1), 0.8, NAVY_MID),
        ("LINEAFTER", (4, 1), (4, -1), 0.8, NAVY_MID),
        # remarks column
        ("BACKGROUND", (5, 1), (5, -1), FIELD_BG),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (2, -1), "CENTER"),
    ]
    t.setStyle(TableStyle(style))
    return t


def field_row(label, name, width, height=16, label_w=78):
    """Label + fillable text field, as a single-row table."""
    data = [[Paragraph(label, S["fieldlbl"]),
             TextBox(name, width - label_w - 12, height)]]
    t = Table(data, colWidths=[label_w, width - label_w], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (0, 0), GREY_BG),
        ("BACKGROUND", (1, 0), (1, 0), FIELD_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def fields_row(pairs, label_ws, height=16):
    """One table row of (label, fillable field) pairs spanning CONTENT_W."""
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


def two_col(left, right, gap=10):
    w = (CONTENT_W - gap) / 2
    t = Table([[left, right]], colWidths=[w + gap, w], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), gap),
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
    canv.setFont("Helvetica", 7)
    canv.setFillColor(MUTED)
    canv.drawString(MARGIN, 9 * mm, DOC_TITLE)
    canv.drawCentredString(PAGE_W / 2, 9 * mm,
                           "Seller: ______________________________")
    canv.drawRightString(PAGE_W - MARGIN, 9 * mm, f"Page {doc.page}")
    canv.setStrokeColor(GREY_LINE)
    canv.setLineWidth(0.5)
    canv.line(MARGIN, 12 * mm, PAGE_W - MARGIN, 12 * mm)
    canv.restoreState()


def draw_cover(canv, doc):
    canv.saveState()
    band_h = 52 * mm
    canv.setFillColor(NAVY)
    canv.rect(0, PAGE_H - band_h, PAGE_W, band_h, stroke=0, fill=1)
    canv.setStrokeColor(colors.HexColor("#2E4C6D"))
    canv.setLineWidth(1)
    for r in range(10, 70, 8):
        canv.circle(PAGE_W - 30 * mm, PAGE_H - band_h + 14 * mm, r,
                    stroke=1, fill=0)
    canv.setFillColor(ACCENT)
    canv.rect(0, PAGE_H - band_h, PAGE_W, 2.6 * mm, stroke=0, fill=1)
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
    ("A1", "Machine is suitable for a <b>three-phase supply, 380–440 V AC</b>, "
           "with protective earth (PE) and neutral (N).", "§2"),
    ("A2", "Machine is suitable for a <b>single-phase supply, 220–230 V AC</b>, "
           "with protective earth (PE) and neutral (N).", "§2"),
    ("A3", "Machine is rated for a <b>50 Hz</b> supply frequency.", "§2"),
    ("A4", "PE and N are brought to the machine terminal box in both supply "
           "arrangements.", "§2"),
    ("A5", "State the installed / connected electrical load per machine "
           "(kW) in Remarks.", "§2"),
]

SEC_B = [
    ("B1", "Machine is built with <b>48 winding spindles</b>.", "§4.1"),
    ("B2", "Each spindle is independently threaded and can be stopped "
           "without interrupting the remaining spindles.", "§7.1"),
    ("B3", "Winds <b>cotton yarn, counts 10/1 to 50/1</b>.", "§4.2"),
    ("B4", "Winds <b>cotton yarn, counts 20/2 to 100/2</b>.", "§4.2"),
    ("B5", "Winds <b>spun polyester, counts 20/2 to 60/2 SSP</b>.", "§4.2"),
    ("B6", "Winds <b>filament polyester, 50 D to 300 D</b>.", "§4.2"),
    ("B7", "Runs the full declared yarn range without substituting yarn-path "
           "components (guides, tensioners, traverse elements).", "§7.1"),
    ("B8", "Produces a finished package of <b>160 mm diameter</b>.", "§4.3"),
    ("B9", "Produces a finished package of <b>1 kg</b> weight.", "§4.3"),
    ("B10", "Achieves target package density <b>0.30 – 0.35 g/cm³ for "
            "cotton</b>.", "§4.3"),
    ("B11", "Achieves target package density <b>0.35 – 0.40 g/cm³ for "
            "polyester</b>.", "§4.3"),
    ("B12", "Density is <b>uniform between package core and surface</b>, not "
            "merely on average across the package.", "§7.1"),
    ("B13", "Achieves a winding speed of <b>1 000 m/min</b> (maximum).",
     "§4.3"),
    ("B14", "Accepts a bobbin of <b>160.40 mm overall length</b> with a "
            "<b>143.00 mm</b> main body.", "§4.4"),
    ("B15", "Accepts bobbin stepped end sections of <b>10.40 mm and "
            "7.00 mm</b>.", "§4.4"),
    ("B16", "Accepts left-end bobbin diameters <b>54.70 / 49.60 / "
            "43.15 mm</b>.", "§4.4"),
    ("B17", "Accepts right-end bobbin diameters <b>43.15 / 48.80 / "
            "52.90 mm</b>.", "§4.4"),
    ("B18", "Resulting package is suitable for <b>package dyeing</b> — dye "
            "liquor penetrates to the innermost layers at the same rate as "
            "the outermost.", "§7.1"),
]

SEC_C = [
    ("C1", "Machine is built with <b>60 winding spindles</b>.", "§5.1"),
    ("C2", "Winds <b>cotton yarn, counts 10/1 to 50/1</b>.", "§5.2"),
    ("C3", "Winds <b>cotton yarn, counts 20/2 to 100/2</b>.", "§5.2"),
    ("C4", "Produces a finished cone of <b>150 mm top diameter</b>.", "§5.3"),
    ("C5", "Produces a finished cone of <b>180 mm bottom diameter</b>.",
     "§5.3"),
    ("C6", "Produces a finished cone of <b>155 mm height</b>.", "§5.3"),
    ("C7", "Produces a finished package of <b>1 kg</b> weight.", "§5.3"),
    ("C8", "Achieves target hardness / density <b>0.40 – 0.50 g/cm³</b>.",
     "§5.3"),
    ("C9", "Achieves a winding speed of <b>1 000 m/min</b> (maximum).",
     "§5.3"),
    ("C10", "Accepts a conical bobbin of <b>173.00 mm overall length</b>.",
     "§5.4"),
    ("C11", "Accepts large-end bobbin diameters <b>71.00 / 67.00 mm</b>.",
     "§5.4"),
    ("C12", "Accepts small-end bobbin diameters <b>37.00 / 26.00 mm</b>.",
     "§5.4"),
    ("C13", "Tension system sustains and regulates the higher tension needed "
            "to reach 0.40 – 0.50 g/cm³.", "§7.2"),
    ("C14", "Traverse control holds <b>square, stable cone edges</b> at the "
            "target density (no soft or broken-down edges).", "§7.2"),
    ("C15", "Finished cone is stable in stacking, handling and transport — "
            "does not collapse, telescope or shed layers.", "§7.2"),
]

SEC_D = [
    ("D1", "Machine is built with <b>48 winding spindles</b>.", "§6.1"),
    ("D2", "Winds <b>spun polyester, counts 20/2 to 100/2 SSP</b>.", "§6.2"),
    ("D3", "Winds <b>spun polyester, counts 16/3 to 80/3 SSP</b> "
           "(three-ply).", "§6.2"),
    ("D4", "Winds three-ply thread <b>without introducing or releasing "
           "twist</b> that would cause snarling at the point of use.",
     "§7.3"),
    ("D5", "Achieves a thread length / weight of <b>4 000 m per 100 g</b> at "
           "yarn count 50/2 spun.", "§6.3"),
    ("D6", "Length measurement and cut-off guarantee the declared length on "
           "<b>every package</b>, not merely on batch average.", "§7.3"),
    ("D7", "Achieves a winding speed of <b>1 400 rpm</b> (maximum).", "§6.3"),
    ("D8", "<b>Active yarn tension control is provided</b> and does not drift "
           "as the package builds (not open-loop or purely mechanical).",
     "§6.3"),
    ("D9", "Tension is consistent <b>within a package and between "
           "packages</b>, preserving thread elongation and strength.",
     "§7.3"),
    ("D10", "<b>Automatic doffing is provided</b> — completed packages are "
            "ejected and empty carriers introduced without manual "
            "intervention.", "§6.3"),
    ("D11", "<b>Automatic feeding / yarn take-up is provided.</b>", "§6.3"),
    ("D12", "Accepts a conical bobbin of <b>114.00 mm overall length</b>.",
     "§6.4"),
    ("D13", "Accepts large-end bobbin diameters <b>38.00 / 35.00 mm</b>.",
     "§6.4"),
    ("D14", "Accepts small-end bobbin diameters <b>28.00 / 12.60 mm</b>.",
     "§6.4"),
]

SEC_E = [
    ("E1", "<b>Speed basis for the sewing thread machine.</b> Confirm that "
           "1 400 rpm is the correct basis, and state the equivalent linear "
           "speed in m/min together with the reference diameter used.",
     "§8.2"),
    ("E2", "<b>Sewing thread package envelope.</b> State the finished package "
           "diameter, height and weight for the sewing thread machine "
           "(not given in the issued documents).", "§8.2"),
    ("E3", "<b>Tension control on the soft and hard winders.</b> State "
           "whether active tension control is offered on these two machines, "
           "and whether it is standard or optional.", "§8.2"),
    ("E4", "<b>Automatic doffing on the soft and hard winders.</b> State "
           "whether automatic doffing / feeding is offered on these two "
           "machines, and whether standard or optional.", "§8.2"),
    ("E5", "<b>Density measurement basis.</b> State whether quoted densities "
           "are measured on the wound yarn mass alone or on gross package "
           "volume including the carrier.", "§8.2"),
    ("E6", "<b>Hard winder density.</b> Confirm the target is "
           "<b>0.40 – 0.50 g/cm³</b> (issued as “0.40 – .050 gm/cm³”, read as "
           "a typographical error).", "§8.1"),
]

SEC_F = [
    ("F1", "Machine footprint and installation layout drawings are provided.",
     "—"),
    ("F2", "Utility requirements are stated — compressed air, vacuum, "
           "extraction, cooling (as applicable).", "—"),
    ("F3", "Noise emission level is stated.", "—"),
    ("F4", "Applicable safety conformity is declared (e.g. CE marking) with "
           "the standards listed.", "—"),
    ("F5", "Fixed guarding, interlocks and emergency-stop circuits conform to "
           "the declared safety standard.", "—"),
    ("F6", "Operation and maintenance manuals are supplied in English.", "—"),
    ("F7", "Electrical schematics and a spare-parts list are supplied.", "—"),
    ("F8", "A recommended spare-parts package is quoted.", "—"),
    ("F9", "Installation and commissioning are included in the offer.", "—"),
    ("F10", "Operator and maintenance training is included in the offer.",
     "—"),
    ("F11", "Warranty period is stated.", "—"),
    ("F12", "Spare-parts availability period after delivery is stated.", "—"),
    ("F13", "Delivery lead time from order is stated.", "—"),
    ("F14", "A factory acceptance test is offered, including <b>sample "
            "packages wound to the specified density and dimensions</b> for "
            "approval before shipment.", "—"),
    ("F15", "Reference installations running comparable machines can be "
            "provided.", "—"),
    ("F16", "Any deviation from this specification is listed in full, with "
            "the technical reason and the proposed alternative.", "—"),
]


# ---------------------------------------------------------------- story
def build_story():
    st = []

    # ========================================================== COVER
    st.append(Spacer(1, 9 * mm))
    st.append(P("TO BE COMPLETED AND RETURNED BY THE SELLER", "cover_kicker"))
    st.append(Spacer(1, 6))
    st.append(P("Due-Diligence &amp; Compliance Checklist", "cover_title"))
    st.append(Spacer(1, 2))
    st.append(P("Winding Machines&nbsp; · &nbsp;Soft Winding&nbsp; · &nbsp;"
                "Hard Winding&nbsp; · &nbsp;Sewing Thread", "cover_sub"))
    st.append(Spacer(1, 20 * mm))

    st.append(P("How to complete this checklist", "h2"))
    st += bullets([
        "Mark <b>exactly one box — YES or NO — for every numbered line</b>. "
        "Leave no line blank.",
        "<b>YES</b> means the equipment offered meets the requirement in full, "
        "exactly as stated.",
        "<b>NO</b> means the requirement is not met, or is met only partially, "
        "conditionally, or by an alternative arrangement.",
        "Every <b>NO</b> must be explained in <i>Remarks</i>. State what is "
        "offered instead and the technical reason.",
        "Partial or conditional compliance is <b>NO</b>, not YES. A qualified "
        "YES will be read as a deviation.",
        "Section E items are <b>requests for information</b> — mark YES once "
        "the information is supplied in <i>Remarks</i>.",
        "Section F covers supply scope and support that the issued "
        "specification did not address; it is included so the commercial "
        "position is on record.",
        "Spec references (§) point to sections of the consolidated document "
        "<i>Winding Machine Technical Specification — Soft Winding, Hard "
        "Winding &amp; Sewing Thread</i>.",
    ])

    st.append(Spacer(1, 8))
    st.append(P("Seller identification", "h2"))
    LW = [92, 104]
    st.append(fields_row([("Company", "s_company"),
                          ("Offer / quote ref.", "s_ref")], LW, 17))
    st.append(Spacer(1, 3))
    st.append(fields_row([("Contact name", "s_contact"),
                          ("Position", "s_position")], LW, 17))
    st.append(Spacer(1, 3))
    st.append(fields_row([("Email / phone", "s_email"),
                          ("Date", "s_date")], LW, 17))
    st.append(Spacer(1, 3))
    st.append(fields_row([("Machine model(s) offered", "s_models"),
                          ("Country of manufacture", "s_origin")], LW, 17))

    st.append(NextPageTemplate("inner"))
    st.append(PageBreak())

    # ========================================================== SECTIONS
    def block(letter, title, subtitle, rows, lead=None):
        # never leave a section bar stranded at the foot of a page
        out = [CondPageBreak(135), section_bar(letter, title, subtitle),
               Spacer(1, 5)]
        if lead:
            out += [P(lead, "note"), Spacer(1, 5)]
        out.append(checklist_table(rows))
        out.append(Spacer(1, 10))
        return out

    st += block("A", "Common Electrical Specification",
                "applies to all three machines", SEC_A)
    st += block("B", "Machine 01 — Soft Winding", "48 spindles", SEC_B,
                "Open, permeable packages for package dyeing. Density and its "
                "uniformity are the primary acceptance criteria.")
    st += block("C", "Machine 02 — Hard Winding", "60 spindles", SEC_C,
                "Dense, firm cones for storage, transport and onward "
                "processing. Cotton only.")
    st += block("D", "Machine 03 — Sewing Thread", "48 spindles", SEC_D,
                "Precision, length-controlled cones of finished sewing "
                "thread. Tension control and automatic doffing are mandatory.")
    st += block("E", "Open Items Requiring the Seller's Position",
                "information requests", SEC_E,
                "These items were identified as gaps or inconsistencies in "
                "the issued specification. Answer each one in Remarks.")
    st += block("F", "Supply Scope, Documentation &amp; Support",
                "not covered by the issued specification", SEC_F,
                "These items are not stated in the issued documents. They are "
                "listed so that scope and support are confirmed in writing "
                "rather than assumed.")

    # ========================================================== SUMMARY
    total = _counter["n"]
    st.append(PageBreak())
    st.append(section_bar("G", "Summary &amp; Declaration",
                          "to be completed last"))
    st.append(Spacer(1, 8))
    st.append(P(f"Compliance summary &nbsp;<font size='8' color='#6B7A8C'>"
                f"({total} requirement lines in sections A to F)</font>",
                "h2"))
    st.append(fields_row([("Total YES", "sum_yes"),
                          ("Total NO", "sum_no"),
                          ("Lines with remarks", "sum_rem"),
                          ("Total deviations", "sum_dev")],
                         [58, 54, 90, 86], 17))

    st.append(Spacer(1, 10))
    st.append(P("Overall statement of deviations", "h2"))
    st.append(P("List every item marked NO, with the deviation offered and "
                "its technical justification. Continue on a separate sheet if "
                "required.", "note"))
    st.append(Spacer(1, 4))
    st.append(field_row("Summary", "dev_summary", CONTENT_W, height=66,
                        label_w=68))

    st.append(Spacer(1, 12))
    st.append(P("Declaration", "h2"))
    st.append(P("I confirm that the responses recorded in this checklist "
                "accurately describe the equipment offered; that every "
                "<b>NO</b> is explained in the corresponding Remarks field; "
                "and that no requirement marked <b>YES</b> is subject to an "
                "unstated qualification, condition or deviation.", "body"))
    st.append(Spacer(1, 2))
    st.append(fields_row([("Name", "d_name"), ("Position", "d_position")],
                         [92, 104], 17))
    st.append(Spacer(1, 3))
    st.append(fields_row([("Signature", "d_signature"),
                          ("Date", "d_date")], [92, 104], 32))
    st.append(Spacer(1, 3))
    st.append(field_row("Company stamp", "d_stamp", CONTENT_W, height=38,
                        label_w=92))

    st.append(Spacer(1, 10))
    st.append(callout(
        "Return instructions",
        "Return this checklist complete, together with the machine layout "
        "drawings, electrical schematics and the deviation list referred to in "
        "item F16. An incomplete checklist, or one with unexplained NO "
        "responses, cannot be evaluated."))
    return st


def main():
    out = "Winding_Machines_Seller_Due_Diligence_Checklist.pdf"
    doc = BaseDocTemplate(
        out, pagesize=landscape(A4),
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Seller Due-Diligence & Compliance Checklist — Winding Machines",
        author="MMS-ITS",
        subject="Seller compliance checklist for soft winding, hard winding "
                "and sewing thread machines",
        keywords="due diligence, compliance checklist, winding machine, "
                 "deviation list, vendor assessment",
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

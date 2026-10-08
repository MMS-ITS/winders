# Winding Machine Specifications

Consolidated technical specification for three winding machines: **soft winding**,
**hard winding** and **sewing thread**.

## Deliverables

| Document | Purpose |
|---|---|
| [`Winding_Machines_Combined_Specification.pdf`](Winding_Machines_Combined_Specification.pdf) | The specification — issued **to** the seller |
| [`Winding_Machines_Seller_Due_Diligence_Checklist.pdf`](Winding_Machines_Seller_Due_Diligence_Checklist.pdf) | Compliance checklist — completed **by** the seller and returned |

## Specification

**`Winding_Machines_Combined_Specification.pdf`** — 9-page A4 document combining both source specifications:

| Section | Content |
|---|---|
| 1 | Scope and machine overview |
| 2 | Common electrical specification |
| 3 | Full comparison matrix (all three machines, 17 parameters) |
| 4 | Machine 01 — Soft Winding (48 spindles, bobbin 160.40 mm) |
| 5 | Machine 02 — Hard Winding (60 spindles, bobbin 173.00 mm) |
| 6 | Machine 03 — Sewing Thread (48 spindles, bobbin 114.00 mm) |
| 7 | Detailed requirements per machine type, in narrative form |
| 8 | Notes on the source data |

All four figures (three dimensioned bobbin drawings and the finished-package
photograph) are the original images extracted from the source PDFs — not redrawn.

## Seller due-diligence checklist

**`Winding_Machines_Seller_Due_Diligence_Checklist.pdf`** — 8-page A4 landscape
form with **74 requirement lines**, each traced back to a section of the
specification. The seller marks **YES** (complies) or **NO** (does not comply)
and records remarks or observations.

| Section | Lines | Content |
|---|---|---|
| A | 5 | Common electrical specification |
| B | 18 | Machine 01 — Soft Winding |
| C | 15 | Machine 02 — Hard Winding |
| D | 14 | Machine 03 — Sewing Thread |
| E | 6 | Open items requiring the seller's position (the gaps flagged in §8.2) |
| F | 16 | Supply scope, documentation and support — not covered by the issued specification |
| G | — | Compliance summary, statement of deviations, signed declaration |

The PDF is a **fillable form**: YES/NO are mutually exclusive AcroForm radio
groups (74 groups) and every remarks box is a real text field (92 fields), so it
can be completed in any PDF reader or printed and filled in by hand.

Partial or conditional compliance counts as **NO** — this is stated in the
instructions so a qualified YES cannot be used to obscure a deviation.

## Sources

| File | Contributed |
|---|---|
| `Machine Specification.pdf` | Finished-package requirements, target densities, winding speeds, thread length/weight, tension and auto-doffing requirements, package photograph |
| `Winding_Machine_Technical_Specifications.pdf` | Spindle counts, electrical specification, yarn compatibility and count ranges, bobbin dimension drawings |

Every numeric value in sections 1–6 is reproduced from these two documents
without alteration, with one exception: the hard winder density was issued as
`0.40 – .050 gm/cm³` and is presented as `0.40 – 0.50 g/cm³`. This correction
and five items recommended for confirmation are recorded in section 8.

## Rebuilding

```bash
pip install reportlab pypdf pdfplumber pillow
python3 build_spec_pdf.py       # the specification
python3 build_dd_checklist.py   # the seller checklist
```

Both scripts lay the documents out with ReportLab and share the same design
tokens. `assets/` holds the figures extracted from the source PDFs.

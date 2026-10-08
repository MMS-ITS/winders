# Winding Machine Specifications

Consolidated technical specification for three winding machines: **soft winding**,
**hard winding** and **sewing thread**.

## Deliverable

**[`Winding_Machines_Combined_Specification.pdf`](Winding_Machines_Combined_Specification.pdf)** — 9-page A4 document combining both source specifications:

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
python3 build_spec_pdf.py
```

`build_spec_pdf.py` lays out the document with ReportLab; `assets/` holds the
figures extracted from the source PDFs.

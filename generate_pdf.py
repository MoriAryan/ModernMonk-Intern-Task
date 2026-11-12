"""
Convert report.md to report.pdf using markdown -> HTML -> PDF via a Python-only pipeline.
Uses fpdf2 since weasyprint needs GTK. Alternative: just call pandoc.
"""

import subprocess
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_MD = os.path.join(PROJECT_DIR, "report.md")
REPORT_PDF = os.path.join(PROJECT_DIR, "report.pdf")

# Use pandoc with xelatex
# We create a small LaTeX header to control formatting tightly
HEADER = os.path.join(PROJECT_DIR, "header.tex")

header_content = r"""
\usepackage{float}
\usepackage{graphicx}
\let\origfigure\figure
\let\endorigfigure\endfigure
\renewenvironment{figure}[1][htbp]{%
  \origfigure[H]
}{%
  \endorigfigure
}
\usepackage{enumitem}
\setlist{nosep, leftmargin=1.5em}
\setlength{\parskip}{4pt}
\setlength{\parindent}{0pt}
\usepackage{titlesec}
\titlespacing*{\section}{0pt}{12pt}{4pt}
\titlespacing*{\subsection}{0pt}{8pt}{3pt}
\titlespacing*{\subsubsection}{0pt}{6pt}{2pt}
\usepackage{caption}
\captionsetup{font=small, skip=4pt}
"""

with open(HEADER, "w", encoding="utf-8") as f:
    f.write(header_content)

cmd = [
    "pandoc", REPORT_MD,
    "-o", REPORT_PDF,
    "--pdf-engine=xelatex",
    "-V", "geometry:margin=1.8cm",
    "-V", "fontsize=10.5pt",
    "-V", "mainfont=Segoe UI",
    "-V", "monofont=Consolas",
    "-V", "linestretch=1.15",
    "-H", HEADER,
    "--highlight-style=tango",
]

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_DIR)
if result.returncode != 0:
    print(f"STDERR: {result.stderr}")
    sys.exit(1)

import pymupdf
doc = pymupdf.open(REPORT_PDF)
pages = len(doc)
doc.close()

size_kb = os.path.getsize(REPORT_PDF) / 1024
print(f"PDF: {REPORT_PDF}")
print(f"Pages: {pages}, Size: {size_kb:.0f} KB")

if pages > 15:
    print(f"WARNING: {pages} pages exceeds the 15-page limit!")
else:
    print("Page count OK.")

import pdfplumber
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "..", "ZBLS - FR.pdf")

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]
    table = page.extract_tables()[0]
    with open("table_dump.txt", "w", encoding="utf-8") as f:
        for r_idx, row in enumerate(table):
            f.write(f"Row {r_idx:02d}:\n")
            for c_idx, cell in enumerate(row):
                if cell is not None and cell != "":
                    f.write(f"  Col {c_idx:02d}: {repr(cell)}\n")
            f.write("\n")
print("Dumped table to table_dump.txt")

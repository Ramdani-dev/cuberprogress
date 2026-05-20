import pdfplumber
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "..", "ZBLS - FR.pdf")

with pdfplumber.open(PDF_PATH) as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"--- Page {i+1} ---")
        tables = page.extract_tables()
        print(f"Number of tables: {len(tables)}")
        for t_idx, table in enumerate(tables):
            print(f"  Table {t_idx+1} dimensions: {len(table)} rows x {len(table[0]) if table else 0} columns")
            # Print first few rows
            for r_idx, row in enumerate(table[:5]):
                print(f"    Row {r_idx}: {row[:10]}...")

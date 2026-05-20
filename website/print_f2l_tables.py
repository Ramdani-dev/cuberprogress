import pdfplumber
import os

PDF_PATH = "c:\\Users\\Ramdani\\3D Objects\\ZBMethods\\f2l-algorithms-different-slot-positions.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]
    tables = page.find_tables()
    print(f"Total tables on page 1: {len(tables)}")
    if tables:
        table = tables[0]
        print(f"Table dimensions: {len(table.rows)} rows, {len(table.rows[0].cells)} columns")
        # Print the first 10 rows
        for idx, row in enumerate(table.rows[:15]):
            row_text = [cell.text.strip().replace('\n', ' ') if cell and cell.text else "" for cell in row.cells]
            print(f"Row {idx+1}: {row_text}")

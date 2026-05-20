import pdfplumber
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "..", "ZBLS - FR.pdf")

def group_chars_into_lines(chars, y_tolerance=0.5):
    if not chars:
        return []
    # Sort chars by top
    chars = sorted(chars, key=lambda c: c['top'])
    lines = []
    current_line = [chars[0]]
    for c in chars[1:]:
        if c['top'] - current_line[-1]['top'] <= y_tolerance:
            current_line.append(c)
        else:
            lines.append(current_line)
            current_line = [c]
    lines.append(current_line)
    
    # Format lines
    formatted_lines = []
    for line in lines:
        line = sorted(line, key=lambda c: c['x0'])
        text = "".join(c['text'] for c in line).strip()
        text = " ".join(text.split())
        if text:
            formatted_lines.append(text)
    return formatted_lines

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]
    tables = page.find_tables()
    table = tables[0]
    
    # Row index 2, Col index 3
    cell = table.rows[2].cells[3]
    print(f"Cell bounding box: {cell}")
    
    if cell:
        x0, y0, x1, y1 = cell
        # Extract chars in cell
        cell_chars = [c for c in page.chars if x0 <= c['x0'] <= x1 and y0 <= c['top'] <= y1]
        algs = group_chars_into_lines(cell_chars)
        print("Extracted Algorithms:")
        for idx, alg in enumerate(algs):
            print(f"  {idx+1}: {repr(alg)}")

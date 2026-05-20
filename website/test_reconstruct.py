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
        # Sort characters by x0
        line = sorted(line, key=lambda c: c['x0'])
        text = "".join(c['text'] for c in line).strip()
        # Clean up double/multiple spaces
        text = " ".join(text.split())
        if text:
            formatted_lines.append(text)
    return formatted_lines

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]
    
    # We want to inspect F2L 1
    # Cell boundaries for (r=0, c=0):
    # x: [50, 154.7]
    # y: [69.6, 139.4]
    x_min, x_max = 50, 154.7
    y_min, y_max = 69.6, 139.4
    
    # Header height is about 10 points
    # F2L 1 header text is usually around y = 69.6 to 71.3
    # Sub-case area: y in [72.0, 139.4]
    
    # Let's divide y into 4 sub-case rows
    row_height = (y_max - 72.0) / 4
    x_mid = x_min + (x_max - x_min) / 2
    
    print(f"Cell width: {x_max - x_min:.2f}, x_mid: {x_mid:.2f}")
    
    for sr in range(4):
        sr_ymin = 72.0 + sr * row_height
        sr_ymax = sr_ymin + row_height
        print(f"\n--- Sub-Case Row {sr+1} (y: {sr_ymin:.2f} to {sr_ymax:.2f}) ---")
        
        # Left case chars
        left_chars = [c for c in page.chars if x_min <= c['x0'] < x_mid and sr_ymin <= c['top'] <= sr_ymax]
        left_algs = group_chars_into_lines(left_chars)
        print(f"  Left Case: {left_algs}")
        
        # Right case chars
        right_chars = [c for c in page.chars if x_mid <= c['x0'] <= x_max and sr_ymin <= c['top'] <= sr_ymax]
        right_algs = group_chars_into_lines(right_chars)
        print(f"  Right Case: {right_algs}")

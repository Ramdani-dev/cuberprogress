import pdfplumber
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "algorithm", "Anthony-Brooks-ZBLL.pdf")
OUTPUT_JSON_PATH = os.path.join(BASE, "algorithm", "zbll.json")

# X limits
X_LIMITS = [0, 155, 275, 396, 520, 640, 792]

# Y limits
Y_LIMITS_TOP = [80, 150, 230, 320, 410]
Y_LIMITS_BOT = [420, 500, 570]

# Subgroup categories mapped by page index (1-based)
ZBLL_SUBGROUPS = {
    1: "T-Shape",
    2: "U-Shape",
    3: "L-Shape",
    4: "H-Shape",
    5: "Pi-Shape",
    6: "S-Shape",
    7: "Anti-S Shape",
    8: "Dot",
    9: "Cross",
    10: "Corners Oriented",
}

def should_filter_line(text):
    t = text.lower()
    if "zbll algs by" in t:
        return True
    if "arranged by" in t:
        return True
    if "andy klise" in t:
        return True
    if "jabari nuruddin" in t:
        return True
    return False

def group_chars_into_lines(chars, y_tolerance=2.0):
    if not chars:
        return []
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
    
    formatted_lines = []
    for line in lines:
        line = sorted(line, key=lambda c: c['x0'])
        text = "".join(c['text'] for c in line).strip()
        text = " ".join(text.split())
        if text and not should_filter_line(text):
            formatted_lines.append(text)
    return formatted_lines

def extract_cell(page, x_min, x_max, y_min, y_max):
    cell_chars = [
        c for c in page.chars
        if x_min <= c['x0'] <= x_max and y_min <= c['top'] <= y_max
    ]
    return group_chars_into_lines(cell_chars)

def extract_zbll():
    results = []
    urutan_idx = 1
    
    with pdfplumber.open(PDF_PATH) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            category = ZBLL_SUBGROUPS.get(page_num, f"Page {page_num}")
            
            # We traverse the page horizontal row-by-row
            # 1. Top box (4 rows, 6 columns)
            for row_idx in range(4):
                y_min, y_max = Y_LIMITS_TOP[row_idx], Y_LIMITS_TOP[row_idx+1]
                for col_idx in range(6):
                    x_min, x_max = X_LIMITS[col_idx], X_LIMITS[col_idx+1]
                    algs = extract_cell(page, x_min, x_max, y_min, y_max)
                    if algs:
                        results.append({
                            "kategori": category,
                            "urutan": urutan_idx,
                            "algoritma": [" ".join(algs)]
                        })
                        urutan_idx += 1
                        
            # 2. Bottom box (2 rows, 6 columns)
            for row_idx in range(2):
                y_min, y_max = Y_LIMITS_BOT[row_idx], Y_LIMITS_BOT[row_idx+1]
                for col_idx in range(6):
                    x_min, x_max = X_LIMITS[col_idx], X_LIMITS[col_idx+1]
                    algs = extract_cell(page, x_min, x_max, y_min, y_max)
                    if algs:
                        results.append({
                            "kategori": category,
                            "urutan": urutan_idx,
                            "algoritma": [" ".join(algs)]
                        })
                        urutan_idx += 1
                        
    print(f"Extraction complete. Total cases extracted: {len(results)}")
    
    # Save to JSON matching the required format
    output_data = {
        "front_right_slot": results
    }
    
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved JSON to: {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    extract_zbll()

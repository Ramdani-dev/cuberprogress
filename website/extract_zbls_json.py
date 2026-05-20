import pdfplumber
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "..", "ZBLS - FR.pdf")
OUTPUT_JSON_PATH = os.path.join(BASE, "algorithm", "zbls.json")

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

def extract_algorithms_from_cell(page, cell):
    if not cell:
        return []
    x0, y0, x1, y1 = cell
    cell_chars = [c for c in page.chars if x0 <= c['x0'] <= x1 and y0 <= c['top'] <= y1]
    return group_chars_into_lines(cell_chars)

def main():
    results = []
    urutan = 1
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # --- Page 1: F2L 1 to F2L 40 ---
        page1 = pdf.pages[0]
        tables = page1.find_tables()
        if not tables:
            print("Error: No tables found on page 1")
            return
        table1 = tables[0]
        
        # 10 rows of F2L groups (each has 4 columns across)
        for group_idx in range(10):
            num_sub_rows = 4 if group_idx < 9 else 2
            
            # Loop through sub-case rows (normally 4, except group 9 has 2 rows)
            for sub_idx in range(num_sub_rows):
                # Loop through the 4 columns across the page
                for col_group in range(4):
                    # Check if this F2L case has a sub-case at sub_idx for the bottom cases
                    if group_idx == 9:
                        if col_group == 0 and sub_idx > 0:  # F2L 37 only has 1 subcase row
                            continue
                        if col_group == 3 and sub_idx > 0:  # F2L 40 only has 1 subcase row
                            continue
                            
                    f2l_case_num = group_idx * 4 + col_group + 1
                    kategori = f"F2L {f2l_case_num}"
                    
                    # Column indices for this F2L case:
                    if col_group == 0:
                        col_left, col_right = 1, 3
                    elif col_group == 1:
                        col_left, col_right = 6, 8
                    elif col_group == 2:
                        col_left, col_right = 11, 13
                    else:
                        col_left, col_right = 16, 18
                    
                    row_idx = 2 + 5 * group_idx + sub_idx
                    row = table1.rows[row_idx]
                    
                    # Left Case
                    left_cell = row.cells[col_left]
                    left_algs = extract_algorithms_from_cell(page1, left_cell)
                    results.append({
                        "kategori": kategori,
                        "urutan": urutan,
                        "algoritma": left_algs
                    })
                    urutan += 1
                    
                    # Right Case
                    right_cell = row.cells[col_right]
                    right_algs = extract_algorithms_from_cell(page1, right_cell)
                    results.append({
                        "kategori": kategori,
                        "urutan": urutan,
                        "algoritma": right_algs
                    })
                    urutan += 1

        # --- Page 2: F2L 41 ---
        page2 = pdf.pages[1]
        tables2 = page2.find_tables()
        if not tables2:
            print("Warning: No tables found on page 2")
        else:
            table2 = tables2[0]
            kategori = "F2L 41"
            
            row = table2.rows[1]
            
            # Left Case
            left_cell = row.cells[1]
            left_algs = extract_algorithms_from_cell(page2, left_cell)
            results.append({
                "kategori": kategori,
                "urutan": urutan,
                "algoritma": left_algs
            })
            urutan += 1
            
            # Right Case
            right_cell = row.cells[3]
            right_algs = extract_algorithms_from_cell(page2, right_cell)
            results.append({
                "kategori": kategori,
                "urutan": urutan,
                "algoritma": right_algs
            })
            urutan += 1

    # Verify and print statistics
    print(f"Total extracted subcases: {len(results)}")
    
    empty_cases = [r for r in results if not r["algoritma"]]
    print(f"Cases with 0 algorithms: {len(empty_cases)}")
    for ec in empty_cases[:10]:
        print(f"  Empty case: kategori={ec['kategori']}, urutan={ec['urutan']}")
        
    # Write to JSON
    output_data = {
        "front_right_slot": results
    }
    
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully wrote JSON to {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    main()

"""
Generate seed_data.json from the PNG images in the static/images directory.
Maps each image to a case entry with placeholder algorithms.
User can later fill in the actual algorithm notations.
"""
import os
import json
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")
OUTPUT = os.path.join(BASE_DIR, "data", "seed_data.json")

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)


def natural_sort_key(s):
    """Sort strings with embedded numbers naturally."""
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r'(\d+)', s)
    ]


def generate_cases():
    cases = []
    case_counter = {"F2L": 0, "ZBLL": 0, "ZBLS": 0}

    # ── F2L ────────────────────────────────────────────
    # Images: f2l-algorithms-different-slot-positions-page{P}-image{N}.png
    # Pages 1-8, sorted naturally
    f2l_dir = os.path.join(IMAGES_DIR, "f2l")
    f2l_pngs = sorted(
        [f for f in os.listdir(f2l_dir) if f.endswith(".png")],
        key=natural_sort_key
    )

    # F2L sub-groups based on PDF page structure
    f2l_subgroups = {
        1: "Basic Inserts (U-Layer Pair)",
        2: "Basic Inserts (Misoriented Pair)",
        3: "Corner in Slot (Edge in U)",
        4: "Edge in Slot (Corner in U)",
        5: "Both in Slot (Same Slot)",
        6: "Both in Slot (Different Slot)",
        7: "Special Cases",
        8: "Mirror / Inverse Cases",
    }

    for fname in f2l_pngs:
        page_match = re.search(r'page(\d+)-image(\d+)', fname)
        if not page_match:
            continue
        page = int(page_match.group(1))
        img_num = int(page_match.group(2))
        case_counter["F2L"] += 1
        idx = case_counter["F2L"]

        cases.append({
            "category": "F2L",
            "case_name": f"F2L Case {idx}",
            "sub_group": f2l_subgroups.get(page, f"Page {page}"),
            "image_url": f"/static/images/f2l/{fname}",
            "algorithms": [
                {"notation": "(algorithm here)", "label": "Main"},
                {"notation": "(alt algorithm)", "label": "Alt 1"},
            ]
        })

    # ── ZBLL ───────────────────────────────────────────
    # Images: Anthony-Brooks-ZBLL-page{P}-image{N}.png
    # Pages 1-10, sorted naturally
    zbll_dir = os.path.join(IMAGES_DIR, "zbll")
    zbll_pngs = sorted(
        [f for f in os.listdir(zbll_dir) if f.endswith(".png")],
        key=natural_sort_key
    )

    zbll_subgroups = {
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

    for fname in zbll_pngs:
        page_match = re.search(r'page(\d+)-image(\d+)', fname)
        if not page_match:
            continue
        page = int(page_match.group(1))
        img_num = int(page_match.group(2))
        case_counter["ZBLL"] += 1
        idx = case_counter["ZBLL"]

        cases.append({
            "category": "ZBLL",
            "case_name": f"ZBLL Case {idx}",
            "sub_group": zbll_subgroups.get(page, f"Page {page}"),
            "image_url": f"/static/images/zbll/{fname}",
            "algorithms": [
                {"notation": "(algorithm here)", "label": "Main"},
            ]
        })

    # ── ZBLS ───────────────────────────────────────────
    # Images: ZBLS - FR-page{P}-image{N}.png
    # Mostly page 1, a few on page 2
    zbls_dir = os.path.join(IMAGES_DIR, "zbls")
    zbls_pngs = sorted(
        [f for f in os.listdir(zbls_dir) if f.endswith(".png")],
        key=natural_sort_key
    )

    # ZBLS sub-groups estimated from PDF FR slot layout
    # Page 1 has ~298 images, organized in groups
    zbls_group_ranges = [
        (1, 36, "Edge Oriented"),
        (37, 72, "Edge Misoriented - Flip"),
        (73, 108, "Corner Twisted CW"),
        (109, 148, "Corner Twisted CCW"),
        (149, 200, "Both Misoriented A"),
        (201, 259, "Both Misoriented B"),
        (260, 298, "Special / Mirror"),
    ]

    for fname in zbls_pngs:
        page_match = re.search(r'page(\d+)-image(\d+)', fname)
        if not page_match:
            continue
        page = int(page_match.group(1))
        img_num = int(page_match.group(2))
        case_counter["ZBLS"] += 1
        idx = case_counter["ZBLS"]

        # Determine sub-group for ZBLS based on image number
        sub_group = f"Page {page}"
        if page == 1:
            for start, end, name in zbls_group_ranges:
                if start <= img_num <= end:
                    sub_group = name
                    break

        cases.append({
            "category": "ZBLS",
            "case_name": f"ZBLS Case {idx}",
            "sub_group": sub_group,
            "image_url": f"/static/images/zbls/{fname}",
            "algorithms": [
                {"notation": "(algorithm here)", "label": "Main"},
                {"notation": "(alt algorithm)", "label": "Alt 1"},
            ]
        })

    return cases


if __name__ == "__main__":
    cases = generate_cases()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)

    # Summary
    from collections import Counter
    cats = Counter(c["category"] for c in cases)
    print(f"Generated {len(cases)} cases total:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")
    print(f"Saved to: {OUTPUT}")

import os
import re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
ZBLL_DIR = os.path.join(BASE, "static", "images", "zbll")

pngs = [f for f in os.listdir(ZBLL_DIR) if f.endswith(".png")]
page_counts = Counter()

for f in pngs:
    match = re.search(r'page(\d+)-image', f)
    if match:
        page_counts[int(match.group(1))] += 1

for page in sorted(page_counts.keys()):
    print(f"Page {page}: {page_counts[page]} images")

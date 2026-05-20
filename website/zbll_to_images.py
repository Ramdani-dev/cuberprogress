import pdfplumber
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "algorithm", "Anthony-Brooks-ZBLL.pdf")
OUT_DIR = os.path.join(BASE, "..", "zbll_pages")
os.makedirs(OUT_DIR, exist_ok=True)

with pdfplumber.open(PDF_PATH) as pdf:
    for idx in range(min(2, len(pdf.pages))):
        page = pdf.pages[idx]
        img = page.to_image(resolution=200)
        img.save(os.path.join(OUT_DIR, f"page_{idx+1}.png"))
        print(f"Saved page_{idx+1}.png")

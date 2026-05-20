import pdfplumber
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "..", "ZBLS - FR.pdf")
OUT_PATH = os.path.join(BASE, "..", "zbls_pages", "bottom_cases.png")

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]
    img = page.to_image(resolution=400)
    pil_img = img.annotated
    w, h = pil_img.size
    
    # Bottom part of the page: from y=0.9 * h to h
    y1 = int(0.85 * h)
    y2 = h
    cropped = pil_img.crop((0, y1, w, y2))
    cropped.save(OUT_PATH)
    print(f"Saved bottom cases to {OUT_PATH}")

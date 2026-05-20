"""Convert ZBLS PDF pages to images for visual inspection."""
import pdfplumber
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "..", "ZBLS - FR.pdf")
OUT_DIR = os.path.join(BASE, "..", "zbls_pages")
os.makedirs(OUT_DIR, exist_ok=True)

with pdfplumber.open(PDF_PATH) as pdf:
    for i, page in enumerate(pdf.pages):
        img = page.to_image(resolution=300)
        img_path = os.path.join(OUT_DIR, f"page_{i+1}.png")
        img.save(img_path)
        print(f"Saved page {i+1} to {img_path}")

"""Extract ZBLS PDF with higher resolution and crop sections for readability."""
import pdfplumber
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "..", "ZBLS - FR.pdf")
OUT_DIR = os.path.join(BASE, "..", "zbls_pages")
os.makedirs(OUT_DIR, exist_ok=True)

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]
    # Get page dimensions
    print(f"Page width: {page.width}, height: {page.height}")
    
    # Render at very high resolution for readability
    img = page.to_image(resolution=600)
    img.save(os.path.join(OUT_DIR, "page_1_hires.png"))
    print("Saved high-res page 1")
    
    # Now let's crop specific sections of the page to read them
    # The page seems to be organized in a grid - let's try to crop individual sections
    pil_img = img.annotated  # Get PIL image
    w, h = pil_img.size
    print(f"Image size: {w}x{h}")
    
    # Let's crop the top portion to see the labels and first few cases
    # Top section - first 2 rows of cases
    sections = [
        ("top", 0, 0, w, h // 10),           # Header/first row area
        ("row1", 0, h//20, w, h // 6),        # First row of cases
        ("row2", 0, h//6, w, h // 4),         # Second row of cases
        ("section1", 0, 0, w//2, h//4),       # Top-left quarter
        ("section2", w//2, 0, w, h//4),       # Top-right quarter
    ]
    
    for name, x1, y1, x2, y2 in sections:
        cropped = pil_img.crop((x1, y1, x2, y2))
        cropped.save(os.path.join(OUT_DIR, f"page_1_{name}.png"))
        print(f"Saved {name} crop: ({x1},{y1})-({x2},{y2})")

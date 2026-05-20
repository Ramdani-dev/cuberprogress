"""Crop each F2L case group from the ZBLS PDF at high resolution."""
import pdfplumber
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "..", "ZBLS - FR.pdf")
OUT_DIR = os.path.join(BASE, "..", "zbls_cases")
os.makedirs(OUT_DIR, exist_ok=True)

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]
    img = page.to_image(resolution=400)
    pil_img = img.annotated
    w, h = pil_img.size
    print(f"Image size: {w}x{h}")
    
    # The page has rows of F2L case groups
    # From the layout, it looks like there are approximately:
    # - Header at top
    # - Then groups of F2L cases organized in rows across the page
    # Let me divide the page into horizontal strips to read each row
    
    # Let's divide the page into roughly 12 strips vertically  
    num_strips = 24
    strip_height = h // num_strips
    
    for i in range(num_strips):
        y1 = i * strip_height
        y2 = (i + 1) * strip_height
        cropped = pil_img.crop((0, y1, w, y2))
        cropped.save(os.path.join(OUT_DIR, f"strip_{i:02d}.png"))
    
    print(f"Saved {num_strips} strips")
    
    # Also save a larger crop of each F2L case column
    # Page seems to have approximately 5 columns, each with a case group
    # Let me crop each case group area more precisely
    # There seem to be about 5 columns across, each roughly w/5 wide
    col_width = w // 5
    
    # Save top header
    header = pil_img.crop((0, 0, w, 300))
    header.save(os.path.join(OUT_DIR, "header.png"))

import pdfplumber
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "..", "ZBLS - FR.pdf")

with pdfplumber.open(PDF_PATH) as pdf:
    for page_num, page in enumerate(pdf.pages):
        print(f"=== Page {page_num+1} ===")
        words = page.extract_words()
        f2l_words = [w for w in words if w['text'] == 'F2L']
        print(f"Number of 'F2L' words: {len(f2l_words)}")
        for w in f2l_words[:10]:
            print(f"  text={w['text']}, x0={w['x0']:.1f}, x1={w['x1']:.1f}, top={w['top']:.1f}, bottom={w['bottom']:.1f}")

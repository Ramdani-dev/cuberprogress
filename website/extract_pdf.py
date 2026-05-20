"""Extract text from all 3 PDFs to understand algorithm structure."""
import pdfplumber
import os, json

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE, "..")

# Extract F2L
print("="*60)
print("F2L PDF")
print("="*60)
with pdfplumber.open(os.path.join(PDF_DIR, "f2l-algorithms-different-slot-positions.pdf")) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            print(f"\n--- PAGE {i+1} ---")
            print(text[:3000])

print("\n\n")
print("="*60)
print("ZBLS PDF (first 3 pages)")
print("="*60)
with pdfplumber.open(os.path.join(PDF_DIR, "ZBLS - FR.pdf")) as pdf:
    for i, page in enumerate(pdf.pages[:3]):
        text = page.extract_text()
        if text:
            print(f"\n--- PAGE {i+1} ---")
            print(text[:3000])

print("\n\n")
print("="*60)
print("ZBLL PDF (first 3 pages)")
print("="*60)
with pdfplumber.open(os.path.join(PDF_DIR, "ZBLL Algorithms v2.57.pdf")) as pdf:
    for i, page in enumerate(pdf.pages[:3]):
        text = page.extract_text()
        if text:
            print(f"\n--- PAGE {i+1} ---")
            print(text[:3000])

import pdfplumber
import os

PDF_PATH = "c:\\Users\\Ramdani\\3D Objects\\ZBMethods\\f2l-algorithms-different-slot-positions.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    print(pdf.pages[0].extract_text()[:1000])

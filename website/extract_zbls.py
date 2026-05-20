"""Extract ZBLS PDF content with detailed text and table extraction."""
import pdfplumber
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE, "..", "ZBLS - FR.pdf")

with pdfplumber.open(PDF_PATH) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    for i, page in enumerate(pdf.pages):
        print(f"\n{'='*80}")
        print(f"PAGE {i+1}")
        print(f"{'='*80}")
        
        # Extract text
        text = page.extract_text()
        if text:
            print("\n--- TEXT ---")
            print(text)
        
        # Extract tables
        tables = page.extract_tables()
        if tables:
            print(f"\n--- TABLES ({len(tables)} found) ---")
            for j, table in enumerate(tables):
                print(f"\nTable {j+1}:")
                for row_idx, row in enumerate(table):
                    print(f"  Row {row_idx}: {row}")
        
        # Extract words with positions for understanding layout
        words = page.extract_words()
        if words:
            print(f"\n--- WORDS ({len(words)} found, showing first 50) ---")
            for w in words[:50]:
                print(f"  x0={w['x0']:.1f}, top={w['top']:.1f}, text='{w['text']}'")

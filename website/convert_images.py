"""Convert all TIFF images to PNG for browser compatibility."""
import os
from PIL import Image

BASE_DIR = os.path.join(os.path.dirname(__file__), "static", "images")

for category in ["f2l", "zbll", "zbls"]:
    cat_dir = os.path.join(BASE_DIR, category)
    if not os.path.isdir(cat_dir):
        continue
    
    tiff_files = [f for f in os.listdir(cat_dir) if f.lower().endswith(('.tiff', '.tif'))]
    print(f"\n[{category.upper()}] Converting {len(tiff_files)} TIFF files to PNG...")
    
    for i, filename in enumerate(sorted(tiff_files)):
        tiff_path = os.path.join(cat_dir, filename)
        png_name = os.path.splitext(filename)[0] + ".png"
        png_path = os.path.join(cat_dir, png_name)
        
        try:
            with Image.open(tiff_path) as img:
                # Convert to RGBA to handle transparency, then save as PNG
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img.save(png_path, 'PNG', optimize=True)
        except Exception as e:
            print(f"  ERROR converting {filename}: {e}")
        
        if (i + 1) % 50 == 0:
            print(f"  Converted {i + 1}/{len(tiff_files)}...")
    
    print(f"  Done: {len(tiff_files)} files converted.")

print("\n✅ All conversions complete!")

"""
extract_epub.py — Kinesiology taping textbook EPUB → dataset conversion

WHY EPUB extraction is fundamentally different from PDF:
EPUB is a ZIP archive containing HTML files. Images sit inside semantic
<section> and <div> elements with nearby <p> and <figcaption> tags.
The image-text mapping comes for free from the HTML structure —
no coordinate-based bbox matching needed.

Pipeline:
  EPUB (.zip) → unzip
    → parse HTML files (BeautifulSoup)
    → (1) chapter text .txt  (split by <h1>/<h2> or spine order)
    → (2) images .png/.jpg   (extract from OEBPS/images/ or equivalent)
    → (3) mapping JSON        (<img> tag's parent section provides context)

Usage:
  python extract_epub.py <path_to_epub> [output_dir]

Dependencies: beautifulsoup4, lxml
"""

# TODO: Implement when EPUB file is provided.
# Key steps:
# 1. zipfile.ZipFile(epub_path) → extract to temp dir
# 2. Parse META-INF/container.xml → find content.opf
# 3. Parse content.opf → get spine order (chapter sequence)
# 4. For each HTML in spine:
#    - Extract text (strip tags, keep structure)
#    - Find <img> tags → extract src path → copy image
#    - Record parent section text as surrounding_text
# 5. Build same mapping JSON format as extract_pdf.py

import sys

def main():
    print("[extract_epub] Not yet implemented. Provide EPUB file to complete.")
    print("See docstring for planned pipeline.")
    sys.exit(0)

if __name__ == "__main__":
    main()

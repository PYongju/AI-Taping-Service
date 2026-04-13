"""
extract_pdf.py — Kinesiology taping textbook PDF → dataset conversion

WHY PDF is coordinate-based (vs EPUB's semantic HTML):
PDF is a flat canvas. Text and images are positioned by (x, y) coordinates
with no structural relationship between them. Unlike EPUB where <img> sits
inside a <section>, a PDF image is just "draw this at (255, 436)."
So we infer image-text relationships by comparing bounding boxes (bboxes).

Pipeline:
  PDF → (1) chapter text .txt  (RAG retrieval chunks)
      → (2) content images .png (3D modeler taping references)
      → (3) anatomy page rasters .jpg (composite diagrams intact)
      → (4) mapping JSON (which image → which technique)

Usage:
  python extract_pdf.py <path_to_pdf> [output_dir]

Dependencies: PyMuPDF (fitz), Pillow
System: pdftoppm (poppler-utils)
"""

import fitz
import glob
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from PIL import Image


# ---------------------------------------------------------------------------
# CONFIG — tuned for this specific PDF (Gibbons, 3rd Ed.)
# Adapt thresholds if reusing on a different textbook.
# ---------------------------------------------------------------------------

# WHY these thresholds:
# This PDF has ~6,800 embedded images. Most are:
#   - <50px fragments: composite anatomy diagrams stored as dozens of tiny rasters
#   - 481x680: full-page z-library watermark/background layers
# Only images above MIN_DIM are actual content (taping photos, anatomy figures).
MIN_IMAGE_WIDTH = 150
MIN_IMAGE_HEIGHT = 150
BACKGROUND_SIZE = (481, 680)

# WHY 200 DPI:
# 150 DPI is readable but loses label text on anatomy diagrams.
# 300 DPI doubles file size for marginal gain. 200 is the sweet spot
# for the 3D modeler to read muscle names and taping paths.
RASTER_DPI = 200

# WHY detect anatomy pages by fragment count:
# Pages with >=10 tiny image fragments (<100px) contain composite
# anatomy diagrams that can't be extracted as single images.
# These pages MUST be rasterized to capture the composed diagram.
ANATOMY_FRAGMENT_THRESHOLD = 10

# Book page → PDF page offset (empirically determined).
# pdf_page_0indexed = book_page - 1 + PAGE_OFFSET
PAGE_OFFSET = 1

# WHY chapter-level chunking (not page-level):
# RAG retrieval works best with topically coherent chunks.
# A taping technique spans 2-3 pages — splitting at page boundaries
# would sever "apply Y-strip" from "with 15% stretch."
CHAPTERS = [
    ("frontmatter",     "Frontmatter",                                                     1,   4),
    ("preface",         "Preface",                                                         5,   8),
    ("acknowledgments", "Acknowledgments",                                                 9,   9),
    ("abbreviations",   "List of Abbreviations",                                          10,  10),
    ("glossary",        "Glossary of Commonly Used Anatomical Terms",                     11,  12),
    ("chapter_01",      "Chapter 1: Overview of Kinesiology Taping",                      13,  32),
    ("chapter_02",      "Chapter 2: Taping Techniques for the Lower Limbs",               33,  46),
    ("chapter_03",      "Chapter 3: Taping Techniques for the Knee Joint",                47,  56),
    ("chapter_04",      "Chapter 4: Taping Techniques for the Anterior/Posterior Thigh",  57,  62),
    ("chapter_05",      "Chapter 5: Taping Techniques for the Lower Back, Trunk, Pelvis", 63,  72),
    ("chapter_06",      "Chapter 6: Taping for the Upper Back, Neck, and Chest",          73,  80),
    ("chapter_07",      "Chapter 7: Taping Techniques for the Upper Limbs",               81,  86),
    ("chapter_08",      "Chapter 8: Taping Techniques for the Forearm, Hand, Wrist",      87,  94),
    ("chapter_09",      "Chapter 9: Taping Techniques to Control Edema (Swelling)",       95, 102),
    ("bibliography",    "Bibliography",                                                   103, 105),
]

# Noise patterns to strip from extracted text
NOISE_PATTERNS = [
    re.compile(r'^\d+\s+A Practical Guide to Kinesiology Taping.*$', re.MULTILINE),
    re.compile(r'^(?:Kinesiology Taping|Overview of|List of|Glossary|Preface|Acknowledgments|Bibliography).*?\d+\s*$', re.MULTILINE),
    re.compile(r'^\s*\d{1,3}\s*$', re.MULTILINE),
    re.compile(r'(?:Get more new versions ebooks|best ebook download Website).*$', re.MULTILINE | re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def book_to_pdf(book_page: int) -> int:
    return book_page - 1 + PAGE_OFFSET

def page_to_chapter(book_page: int) -> str:
    for ch_id, _, s, e in CHAPTERS:
        if s <= book_page <= e:
            return ch_id
    return "unknown"

def clean_text(text: str) -> str:
    for p in NOISE_PATTERNS:
        text = p.sub('', text)
    return re.sub(r'\n{3,}', '\n\n', text).strip()

def extract_headings(page_text: str) -> list:
    headings = re.findall(r'^([A-Z][A-Z\s/:\'()]+)$', page_text, re.MULTILINE)
    return [h.strip() for h in headings
            if not h.startswith('CHAPTER')
            and not h.startswith('KINESIOLOGY TAPING TECH')
            and len(h) > 5]


# ---------------------------------------------------------------------------
# STEP 1: Chapter text extraction
# ---------------------------------------------------------------------------

def extract_texts(doc, output_dir):
    print("=== Step 1: Chapter text extraction ===")
    text_dir = output_dir / "texts"
    text_dir.mkdir(parents=True, exist_ok=True)

    chapter_meta = []
    for ch_id, ch_title, book_start, book_end in CHAPTERS:
        pdf_start = book_to_pdf(book_start)
        pdf_end = book_to_pdf(book_end)

        pages_text = []
        for pi in range(pdf_start, min(pdf_end + 1, len(doc))):
            text = clean_text(doc[pi].get_text())
            if text:
                pages_text.append(text)

        full = '\n\n'.join(pages_text)
        (text_dir / f"{ch_id}.txt").write_text(full, encoding='utf-8')

        chapter_meta.append({
            "id": ch_id,
            "title": ch_title,
            "file": f"texts/{ch_id}.txt",
            "book_pages": f"{book_start}-{book_end}",
            "char_count": len(full),
        })
        print(f"  {ch_id:<20} {len(full):>6,} chars")

    return chapter_meta


# ---------------------------------------------------------------------------
# STEP 2: Embedded content image extraction
# ---------------------------------------------------------------------------

def extract_images(doc, output_dir):
    """
    WHY Pillow conversion is necessary:
    Many images are JPEG 2000 (jpx). Saving raw jpx bytes with a .png
    extension produces unreadable files. Pillow decodes jpx and
    re-encodes as actual PNG.
    """
    print("\n=== Step 2: Content image extraction ===")
    img_dir = output_dir / "images" / "embedded"
    img_dir.mkdir(parents=True, exist_ok=True)

    seen_xrefs = set()
    entries = []

    for pi in range(len(doc)):
        page = doc[pi]
        book_p = pi - PAGE_OFFSET + 1
        ch_id = page_to_chapter(book_p)

        page_text = clean_text(page.get_text())
        captions = re.findall(r'(Figure\s+\d+\.\d+\s+.*?)(?:\n|$)', page_text)
        headings = extract_headings(page_text)

        text_blocks = []
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:
                t = "".join(
                    span["text"]
                    for line in block["lines"]
                    for span in line["spans"]
                ).strip()
                if len(t) > 10:
                    text_blocks.append({"text": t, "y": block["bbox"][1]})

        for img_info in page.get_images(full=True):
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                data = doc.extract_image(xref)
            except Exception:
                continue

            w, h = data["width"], data["height"]
            if w < MIN_IMAGE_WIDTH or h < MIN_IMAGE_HEIGHT:
                continue
            if (w, h) == BACKGROUND_SIZE:
                continue

            fname = f"p{pi+1:03d}_xref{xref}.png"
            try:
                pil_img = Image.open(io.BytesIO(data["image"]))
                if pil_img.mode in ("CMYK", "YCbCr"):
                    pil_img = pil_img.convert("RGB")
                pil_img.save(img_dir / fname, "PNG")
            except Exception:
                with open(img_dir / fname, "wb") as f:
                    f.write(data["image"])

            surrounding = _find_surrounding_text(page, text_blocks)

            entries.append({
                "filename": f"images/embedded/{fname}",
                "type": "embedded",
                "source_chapter": ch_id,
                "page_pdf": pi + 1,
                "page_book": book_p,
                "dimensions": f"{w}x{h}",
                "section_headings": headings[:2],
                "figure_captions": captions[:2],
                "surrounding_text": surrounding,
            })

    print(f"  extracted {len(entries)} content images")
    return entries


def _find_surrounding_text(page, text_blocks):
    """
    WHY bbox proximity (not reading order):
    A caption might be above, below, or beside the image — layout varies.
    We find the largest image bbox on the page, then grab the 3 nearest
    text blocks by vertical distance. Catches captions + technique descriptions.
    """
    if not text_blocks:
        return ""

    img_bboxes = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] == 1:
            bw = block["bbox"][2] - block["bbox"][0]
            bh = block["bbox"][3] - block["bbox"][1]
            if bw > 100 and bh > 100:
                img_bboxes.append(block["bbox"])

    if img_bboxes:
        largest = max(img_bboxes, key=lambda b: (b[2]-b[0]) * (b[3]-b[1]))
        img_y = (largest[1] + largest[3]) / 2
        sorted_blocks = sorted(text_blocks, key=lambda b: abs(b["y"] - img_y))
        return " ".join(b["text"] for b in sorted_blocks[:3])[:400]

    return text_blocks[0]["text"][:400]


# ---------------------------------------------------------------------------
# STEP 3: Anatomy page rasterization
# ---------------------------------------------------------------------------

def identify_anatomy_pages(doc):
    """
    WHY fragment-count heuristic:
    Anatomy diagrams = 50–3000+ tiny raster fragments composed on-page.
    Extracting them individually gives useless 3x3px scraps.
    Only full-page rasterization captures the composed diagram.
    """
    pages = []
    for pi in range(len(doc)):
        page = doc[pi]
        small_count = 0
        for img in page.get_images(full=True):
            try:
                data = doc.extract_image(img[0])
            except Exception:
                continue
            w, h = data["width"], data["height"]
            if (w, h) == BACKGROUND_SIZE:
                continue
            if w < 100 and h < 100:
                small_count += 1
        if small_count >= ANATOMY_FRAGMENT_THRESHOLD:
            pages.append(pi + 1)
    return pages


def rasterize_anatomy(pdf_path, anatomy_pages, doc, output_dir):
    print("\n=== Step 3: Anatomy page rasterization ===")
    raster_dir = output_dir / "images" / "pages"
    raster_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    for pdf_p in anatomy_pages:
        pi = pdf_p - 1
        book_p = pi - PAGE_OFFSET + 1
        ch_id = page_to_chapter(book_p)

        prefix = str(raster_dir / f"anatomy_p{pdf_p:03d}")
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", str(RASTER_DPI),
             "-f", str(pdf_p), "-l", str(pdf_p), pdf_path, prefix],
            check=True, capture_output=True
        )

        page_text = clean_text(doc[pi].get_text())
        captions = re.findall(r'(Figure\s+\d+\.\d+\s+.*?)(?:\n|$)', page_text)
        headings = extract_headings(page_text)

        for f in sorted(glob.glob(f"{prefix}-*.jpg")):
            entries.append({
                "filename": f"images/pages/{os.path.basename(f)}",
                "type": "page_raster",
                "source_chapter": ch_id,
                "page_pdf": pdf_p,
                "page_book": book_p,
                "dpi": RASTER_DPI,
                "section_headings": headings[:3],
                "figure_captions": captions[:3],
                "surrounding_text": page_text[:500],
            })

    print(f"  rasterized {len(entries)} anatomy pages at {RASTER_DPI} DPI")
    return entries


# ---------------------------------------------------------------------------
# STEP 4: Mapping JSON
# ---------------------------------------------------------------------------

def build_mapping(chapter_meta, embedded, rasters, output_dir):
    """
    WHY this mapping exists:
    Without it, someone must manually classify 218 images:
    "which technique?" "which chapter?" "what muscle?"
    The mapping automates this by linking each image to its
    chapter, Figure caption, section heading, and surrounding text.
    """
    print("\n=== Step 4: Image-text mapping JSON ===")

    mapping = {
        "source": "A Practical Guide to Kinesiology Taping, 3rd Ed. (John Gibbons, 2024)",
        "isbn": "978-1-7182-2701-9",
        "extraction_note": (
            "PDF coordinate-based extraction. "
            "Embedded images via PyMuPDF + Pillow, "
            "composite anatomy diagrams via page rasterization (pdftoppm 200dpi)."
        ),
        "chapters": chapter_meta,
        "stats": {
            "total_images": len(embedded) + len(rasters),
            "embedded_content_images": len(embedded),
            "rasterized_anatomy_pages": len(rasters),
        },
        "images": embedded + rasters,
    }

    out_path = output_dir / "image_text_mapping.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"  saved: {out_path}")
    print(f"  entries: {mapping['stats']['total_images']}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <path_to_pdf> [output_dir]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output_pdf")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[extract_pdf] Input:  {pdf_path}")
    print(f"[extract_pdf] Output: {output_dir}\n")

    doc = fitz.open(pdf_path)
    print(f"Pages: {len(doc)}, Size: {os.path.getsize(pdf_path)/1e6:.1f} MB\n")

    chapter_meta = extract_texts(doc, output_dir)
    embedded = extract_images(doc, output_dir)
    anatomy_pages = identify_anatomy_pages(doc)
    rasters = rasterize_anatomy(pdf_path, anatomy_pages, doc, output_dir)
    doc.close()

    build_mapping(chapter_meta, embedded, rasters, output_dir)
    print(f"\n[extract_pdf] Done.")


if __name__ == "__main__":
    main()

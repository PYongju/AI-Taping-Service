# Kinesiology Taping Textbook → Dataset Preprocessing

Converts a kinesiology taping textbook (PDF or EPUB) into structured data for:
- **LLM RAG system**: chapter-level text chunks for retrieval-augmented generation
- **3D modeler**: reference images for reproducing taping paths on 3D mesh
- **Pipeline automation**: mapping JSON that links each image to its technique/chapter

## Pipeline Overview

```
EPUB/PDF
  │
  ├─→ Chapter Text (.txt)          ← RAG retrieval chunks
  │     Split by chapter/body region so each chunk is topically coherent.
  │     A query about "knee taping" retrieves the full knee chapter,
  │     not a fragment split mid-technique at a page boundary.
  │
  ├─→ Content Images (.png/.jpg)   ← 3D modeler references
  │     Taping photos: extracted as embedded images (original resolution)
  │     Anatomy diagrams: page rasterization (composite diagrams that
  │     exist as 50-3000 tiny fragments in the PDF, not as single images)
  │
  └─→ Mapping JSON                 ← Image-technique linkage
        Each image entry contains:
        - source_chapter (which body region)
        - figure_captions (e.g. "Figure 2.1 Plantar fascia...")
        - section_headings (e.g. "PLANTAR FASCIITIS/HEEL PAIN")
        - surrounding_text (nearest text by bbox proximity)
```

## Why PDF and EPUB Need Different Extractors

| Aspect | EPUB | PDF |
|--------|------|-----|
| Structure | HTML inside a ZIP — semantic tags | Flat coordinate canvas |
| Image-text link | `<img>` inside `<section>` — automatic | bbox proximity matching |
| Composite diagrams | Rendered as single `<img>` | 50-3000 tiny raster fragments |
| Chapter detection | Spine order + `<h1>`/`<h2>` tags | Text pattern matching (no TOC) |

## Usage

### PDF Extraction

```bash
python extract_pdf.py input.pdf output_pdf/
```

Output structure:
```
output_pdf/
├── texts/
│   ├── chapter_01.txt
│   ├── chapter_02.txt
│   └── ...
├── images/
│   ├── embedded/          # Content photos (PNG, original resolution)
│   │   ├── p034_xref435.png
│   │   └── ...
│   └── pages/             # Rasterized anatomy diagram pages (JPG, 200dpi)
│       ├── anatomy_p034-034.jpg
│       └── ...
└── image_text_mapping.json
```

### EPUB Extraction

```bash
python extract_epub.py input.epub output_epub/
```
*(Not yet implemented — awaiting EPUB file)*

## PDF-Specific Design Decisions

### Image filtering (why 190 out of 6,800)

The PDF contains ~6,800 embedded image objects:
- **~5,800 tiny fragments** (<50px): pieces of composite anatomy diagrams
- **~96 background layers** (481×680): z-library watermark/page backgrounds
- **~100 alpha masks** (smask): transparency data paired with backgrounds
- **~190 content images** (>150px): actual taping photos and anatomy figures

Only the 190 content images are extracted as embedded files.

### Anatomy page rasterization (why 28 additional JPGs)

Anatomy diagrams are stored as hundreds of positioned tiny raster fragments.
Extracting them individually produces useless 3×3px or 20×56px scraps.
Pages with ≥10 such fragments are identified and rasterized at 200 DPI
to capture the composed diagram as the author intended.

### Text noise removal

Stripped from extracted text:
- Running headers ("A Practical Guide to Kinesiology Taping..." on even pages)
- Section headers with page numbers (odd pages)
- Standalone page numbers
- z-library watermark text ("Get more new versions ebooks...")

### Chapter boundary detection

This PDF has no embedded TOC (Table of Contents) metadata.
Chapter boundaries are hardcoded from the printed table of contents,
with an empirically determined page offset (PDF page = book page + 1).

## Mapping JSON Schema

```json
{
  "source": "...",
  "isbn": "...",
  "chapters": [
    {
      "id": "chapter_02",
      "title": "Chapter 2: Taping Techniques for the Lower Limbs",
      "file": "texts/chapter_02.txt",
      "book_pages": "33-46",
      "char_count": 17617
    }
  ],
  "images": [
    {
      "filename": "images/embedded/p034_xref435.png",
      "type": "embedded",
      "source_chapter": "chapter_02",
      "page_pdf": 34,
      "page_book": 33,
      "dimensions": "658x439",
      "section_headings": ["PLANTAR FASCIITIS/HEEL PAIN/FAT PAD SYNDROME"],
      "figure_captions": ["Figure 2.1  Plantar fascia, showing the site of ..."],
      "surrounding_text": "..."
    }
  ]
}
```

## Requirements

- Python 3.8+
- PyMuPDF (`pip install PyMuPDF`)
- Pillow (`pip install Pillow`)
- poppler-utils (system package for `pdftoppm`)

```bash
pip install -r requirements.txt
# Also: sudo apt install poppler-utils
```

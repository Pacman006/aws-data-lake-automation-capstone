#!/usr/bin/env python3
"""Re-extract the original embedded PDF images (never redraws or alters them)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'assignment': ROOT / 'docs/source/capstone_assignment.pdf',
    'student-report': ROOT / 'docs/source/original_project_report.pdf',
}


def main():
    try:
        import fitz
    except ImportError as exc:
        raise SystemExit('Install PyMuPDF first: python -m pip install pymupdf') from exc
    dest = ROOT / 'docs/images/original'
    dest.mkdir(parents=True, exist_ok=True)
    inventory = []
    for label, path in SOURCES.items():
        pdf = fitz.open(path)
        for page_number, page in enumerate(pdf, 1):
            seen = set()
            number = 0
            for item in page.get_image_info(xrefs=True):
                xref = item['xref']
                if xref <= 0 or xref in seen or item['width'] < 260 or item['height'] < 110:
                    continue
                seen.add(xref)
                number += 1
                image = pdf.extract_image(xref)
                extension = image['ext'].lower()
                if extension not in ('png', 'jpg', 'jpeg'):
                    extension = 'png'
                filename = f'{label}_p{page_number:02d}_{number:02d}.{extension}'
                (dest / filename).write_bytes(image['image'])
                inventory.append({
                    'source': label, 'source_page': page_number,
                    'file': f'docs/images/original/{filename}',
                    'width': item['width'], 'height': item['height'],
                })
    (ROOT / 'docs/images/image_inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print('Re-extracted', len(inventory), 'images from the supplied PDFs.')


if __name__ == '__main__':
    main()

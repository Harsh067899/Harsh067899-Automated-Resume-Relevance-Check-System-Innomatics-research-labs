#!/usr/bin/env python3
"""Check annotations in the generated PDF"""

import fitz
import tempfile
import os

# Find the most recent annotated PDF
temp_dir = tempfile.gettempdir()
pdf_files = [f for f in os.listdir(temp_dir) if '_reviewed_' in f and f.endswith('.pdf')]

if pdf_files:
    latest_pdf = sorted(pdf_files, key=lambda x: os.path.getmtime(os.path.join(temp_dir, x)))[-1]
    pdf_path = os.path.join(temp_dir, latest_pdf)
    
    print(f'📄 Checking annotations in: {latest_pdf}')
    
    doc = fitz.open(pdf_path)
    total_annotations = 0
    
    for page_num, page in enumerate(doc):
        annotations = list(page.annots())
        page_annot_count = len(annotations)
        total_annotations += page_annot_count
        if page_annot_count > 0:
            print(f'   Page {page_num + 1}: {page_annot_count} annotations')
            for i, annot in enumerate(annotations):
                annot_type = annot.type[1] if hasattr(annot.type, '__getitem__') else str(annot.type)
                print(f'      {i+1}. Type: {annot_type}, Content: {annot.info.get("content", "No content")[:50]}...')
    
    print(f'📊 Total annotations found: {total_annotations}')
    doc.close()
    
    if total_annotations > 0:
        print('✅ PDF contains annotations - original system working!')
    else:
        print('⚠️ No annotations found in PDF')
        print('   This might be normal if text snippets were not found in the PDF')
else:
    print('❌ No reviewed PDFs found in temp directory')
    print(f'   Checked: {temp_dir}')
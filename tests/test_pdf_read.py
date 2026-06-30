import pdfplumber

pdf_path = '/Volumes/SanXiaoXing/Work/Invoice-OCR/docs/已合并_1-复制.pdf'

with pdfplumber.open(pdf_path) as pdf:
    print(f'Total pages: {len(pdf.pages)}')
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f'=== Page {i+1} ===')
        if text:
            print(text[:2000])
        else:
            print('No text extracted')
        print('\n' + '='*50 + '\n')

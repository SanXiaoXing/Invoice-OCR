import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.pdf_parser import PDFParser
from extractor.invoice_extractor import InvoiceExtractor


def test_qr_amount_extraction():
    """验证同程商旅确认单二维码金额提取"""
    parser = PDFParser()
    extractor = InvoiceExtractor()

    test_cases = [
        {
            'path': '/Volumes/SanXiaoXing/Work/Invoice-OCR/docs/闫兴(西安-西安高新锦业路轻居酒店)_2026-05-25_同程商旅_1782832624178.pdf',
            'expected_type': 'hotel',
            'expected_amount': 3261.0,
            'qr_prefix': 'etripHotel://'
        },
        {
            'path': '/Volumes/SanXiaoXing/Work/Invoice-OCR/docs/闫兴(西安北站北广场-西停车楼B1层-网约车上车点-西安高新锦业路轻居酒店)_2026-06-23_同程商旅_1782832637412.pdf',
            'expected_type': 'car',
            'expected_amount': 68.26,
            'qr_prefix': 'etripCar://'
        }
    ]

    for case in test_cases:
        pages = parser.extract_text_by_page(case['path'])
        qr_codes_by_page = parser.extract_qr_codes(case['path'])
        qr_map = {page_num: codes for page_num, codes in qr_codes_by_page}

        assert len(pages) == 1, f"{case['path']} 应只有一页"

        page_num, page_text = pages[0]
        qr_codes = qr_map.get(page_num, [])

        assert len(qr_codes) >= 1, f"{case['path']} 应识别到二维码"
        assert qr_codes[0].startswith(case['qr_prefix']), f"{case['path']} 二维码协议头不匹配"

        invoice_type = extractor.detect_invoice_type(page_text, qr_codes)
        assert invoice_type == case['expected_type'], f"期望类型 {case['expected_type']}, 实际 {invoice_type}"

        fields = extractor.extract_fields(page_text, invoice_type, qr_codes)
        assert fields.get('qr_amount') is True, f"{case['path']} 金额应来自二维码"
        assert abs(fields['amount'] - case['expected_amount']) < 0.01, \
            f"期望金额 {case['expected_amount']}, 实际 {fields['amount']}"

    print('All QR extraction tests passed!')


if __name__ == '__main__':
    test_qr_amount_extraction()

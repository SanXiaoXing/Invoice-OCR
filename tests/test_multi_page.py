import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser.pdf_parser import PDFParser
from src.extractor.invoice_extractor import InvoiceExtractor
from src.generator.report_generator import ReportGenerator

pdf_path = '/Volumes/SanXiaoXing/Work/Invoice-OCR/docs/已合并_1-复制.pdf'

print(f"=== 测试多页PDF处理: {pdf_path} ===")

pdf_parser = PDFParser()
extractor = InvoiceExtractor()

pages = pdf_parser.extract_text_by_page(pdf_path)
print(f"\nPDF共 {len(pages)} 页")

all_results = []
for page_num, page_text in pages:
    print(f"\n--- 第 {page_num} 页 ---")
    
    invoice_type = extractor.detect_invoice_type(page_text)
    print(f"发票类型: {invoice_type}")
    
    fields = extractor.extract_fields(page_text, invoice_type)
    print(f"提取字段: {fields}")
    
    all_results.append(fields)

print(f"\n=== 共识别 {len(all_results)} 张发票 ===")

for i, result in enumerate(all_results, 1):
    print(f"\n发票 {i}:")
    print(f"  类型: {result.get('type')}")
    print(f"  车次: {result.get('train_number')}")
    print(f"  出发站: {result.get('departure_station')}")
    print(f"  到达站: {result.get('arrival_station')}")
    print(f"  出发时间: {result.get('departure_time')}")
    print(f"  金额: ¥{result.get('amount')}")

print("\n=== 生成报销单 ===")
generator = ReportGenerator()
success = generator.generate_report(all_results, 'test_multi_report.xlsx')
print(f"报销单生成: {'成功' if success else '失败'}")

print("\n=== 测试完成 ===")

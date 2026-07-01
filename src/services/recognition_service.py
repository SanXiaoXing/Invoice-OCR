"""识别流程编排服务 — 处理文件列表，编排 PDF 解析与发票提取"""

import os
from typing import List, Dict, Callable, Optional
from src.parser.pdf_parser import PDFParser
from src.extractor.invoice_extractor import InvoiceExtractor
from src.utils.logger import logger


def process_files(file_paths: List[str], progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Dict]:
    """处理文件列表，返回识别结果

    Args:
        file_paths: 待处理的 PDF 文件路径列表
        progress_callback: 进度回调函数，参数为 (current, total)

    Returns:
        识别结果列表，每条记录包含 type/amount/filename 等字段
    """
    logger.info(f"[RecognitionService] 开始识别，共 {len(file_paths)} 个文件")
    pdf_parser = PDFParser()
    extractor = InvoiceExtractor()
    results = []

    total = len(file_paths)

    for i, file_path in enumerate(file_paths):
        logger.info(f"[RecognitionService] 处理文件 ({i + 1}/{total}): {os.path.basename(file_path)}")
        pages = pdf_parser.extract_text_by_page(file_path)
        qr_codes_by_page = pdf_parser.extract_qr_codes(file_path)
        qr_map = {page_num: codes for page_num, codes in qr_codes_by_page}

        if not pages:
            logger.warning(f"[RecognitionService] 文件无文本内容: {os.path.basename(file_path)}")
            if progress_callback:
                progress_callback(i + 1, total)
            continue

        for page_num, page_text in pages:
            qr_codes = qr_map.get(page_num, [])
            invoice_type = extractor.detect_invoice_type(page_text, qr_codes)
            fields = extractor.extract_fields(page_text, invoice_type, qr_codes)
            fields['filename'] = os.path.basename(file_path)
            fields['full_path'] = file_path
            fields['page_number'] = page_num
            results.append(fields)
            logger.info(f"[RecognitionService] 第 {page_num} 页识别结果: 类型={invoice_type}, 金额={fields.get('amount', '无')}")

        if progress_callback:
            progress_callback(i + 1, total)

    logger.info(f"[RecognitionService] 识别完成，共 {len(results)} 条记录")
    return results

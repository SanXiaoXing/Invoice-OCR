import pdfplumber
import os
from typing import List, Tuple
from pypdf import PdfWriter, PdfReader
from src.utils.logger import logger


class PDFParser:
    def __init__(self):
        pass

    def extract_text_by_page(self, pdf_path: str) -> list:
        """
        从PDF文件中按页提取文本，支持多页PDF中的多张发票

        Args:
            pdf_path: PDF文件路径

        Returns:
            每页文本的列表，格式: [(page_number, text), ...]
        """
        try:
            if not os.path.exists(pdf_path):
                logger.warning(f"[PDFParser] 文件不存在: {pdf_path}")
                return []

            logger.info(f"[PDFParser] 开始按页提取文本: {os.path.basename(pdf_path)}")
            pages = []
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        pages.append((i + 1, page_text.strip()))
            logger.info(f"[PDFParser] 文本提取完成，共 {len(pages)} 页: {os.path.basename(pdf_path)}")
            return pages
        except Exception as e:
            logger.error(f"[PDFParser] PDF按页解析错误: {e}")
            return []

    def extract_qr_codes(self, pdf_path: str, scale: int = 4) -> List[Tuple[int, List[str]]]:
        """
        从PDF页面中扫描并解码二维码

        针对同程商旅确认函中的二维码，将其渲染为高分辨率图像后使用
        OpenCV QRCodeDetector 进行识别。

        Args:
            pdf_path: PDF文件路径
            scale: 渲染缩放比例，值越大二维码识别率越高但耗时越长

        Returns:
            每页二维码内容列表，格式: [(page_number, [qr_data1, ...]), ...]
        """
        results = []

        try:
            import pypdfium2 as pdfium
            import cv2
            import numpy as np
        except ImportError as e:
            logger.error(f"[PDFParser] 二维码扫描依赖缺失: {e}")
            return results

        try:
            if not os.path.exists(pdf_path):
                logger.warning(f"[PDFParser] 文件不存在: {pdf_path}")
                return results

            logger.info(f"[PDFParser] 开始扫描二维码: {os.path.basename(pdf_path)}")
            detector = cv2.QRCodeDetector()
            pdf = pdfium.PdfDocument(pdf_path)

            for i, page in enumerate(pdf):
                qr_list = []
                try:
                    bitmap = page.render(scale=scale)
                    pil_image = bitmap.to_pil()
                    img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                    data, bbox, _ = detector.detectAndDecode(img)
                    if data:
                        qr_list.append(data)
                        logger.info(f"[PDFParser] 第 {i + 1} 页识别到二维码: {data}")
                    else:
                        logger.debug(f"[PDFParser] 第 {i + 1} 页未识别到二维码")
                except Exception as e:
                    logger.error(f"[PDFParser] 第 {i + 1} 页扫描出错: {e}")

                results.append((i + 1, qr_list))

            pdf.close()
            logger.info(f"[PDFParser] 二维码扫描完成: {os.path.basename(pdf_path)}")
        except Exception as e:
            logger.error(f"[PDFParser] PDF二维码提取错误: {e}")

        return results

    def merge_pdfs(self, file_paths: List[str], output_path: str) -> bool:
        """
        合并多个PDF文件为一个PDF

        Args:
            file_paths: 待合并的PDF文件路径列表
            output_path: 输出PDF文件路径

        Returns:
            合并成功返回True，失败返回False
        """
        if not file_paths:
            logger.warning("[PDFParser] 合并PDF：文件列表为空")
            return False

        try:
            writer = PdfWriter()
            for path in file_paths:
                if not os.path.exists(path):
                    logger.warning(f"[PDFParser] 合并PDF：文件不存在，跳过: {path}")
                    continue
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            logger.info(f"[PDFParser] PDF合并完成，共合并 {len(file_paths)} 个文件 → {output_path}")
            return True
        except Exception as e:
            logger.error(f"[PDFParser] PDF合并错误: {e}")
            return False

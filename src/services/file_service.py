"""文件操作服务 — 合并 PDF、导出报销单、打开文件夹等"""

import os
import subprocess
import sys
from typing import List, Dict
from src.parser.pdf_parser import PDFParser
from src.generator.report_generator import ReportGenerator
from src.utils.logger import logger


def open_containing_folder(path: str):
    """在系统文件管理器中打开文件所在目录并选中文件"""
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-R", path])
        elif sys.platform == "win32":
            subprocess.Popen(["explorer", f"/select,{path}"])
        else:
            subprocess.Popen(["xdg-open", os.path.dirname(path)])
    except Exception as e:
        logger.warning(f"[FileService] 打开文件夹失败: {e}")


def merge_pdfs(file_paths: List[str], output_path: str) -> bool:
    """合并多个 PDF 文件为一个

    Args:
        file_paths: 待合并的 PDF 文件路径列表
        output_path: 输出 PDF 文件路径

    Returns:
        合并成功返回 True
    """
    logger.info(f"[FileService] 开始合并 {len(file_paths)} 个PDF → {output_path}")
    parser = PDFParser()
    return parser.merge_pdfs(file_paths, output_path)


def export_report(invoice_data: List[Dict], output_path: str) -> bool:
    """导出报销单 Excel 表格

    Args:
        invoice_data: 识别结果列表
        output_path: 输出 Excel 文件路径

    Returns:
        导出成功返回 True
    """
    logger.info(f"[FileService] 开始导出报销单 → {output_path}")
    generator = ReportGenerator()
    return generator.generate_report(invoice_data, output_path)

"""测试PDF合并功能"""
import os
import tempfile
from pypdf import PdfReader, PdfWriter
from src.parser.pdf_parser import PDFParser


def _create_pdf(path, num_pages):
    """创建一个包含 num_pages 页的简单PDF"""
    writer = PdfWriter()
    for i in range(num_pages):
        writer.add_blank_page(width=595, height=842)  # A4
    with open(path, "wb") as f:
        writer.write(f)


class TestMergePdfs:
    def test_merge_multiple_pdfs_preserves_all_pages(self, tmp_path):
        """合并多个PDF时，输出文件应包含所有源PDF的页面"""
        # 创建3个PDF：2页、3页、1页
        pdf1 = tmp_path / "a.pdf"
        pdf2 = tmp_path / "b.pdf"
        pdf3 = tmp_path / "c.pdf"
        _create_pdf(str(pdf1), 2)
        _create_pdf(str(pdf2), 3)
        _create_pdf(str(pdf3), 1)

        output = tmp_path / "merged.pdf"
        parser = PDFParser()
        result = parser.merge_pdfs([str(pdf1), str(pdf2), str(pdf3)], str(output))

        assert result is True
        assert output.exists()
        reader = PdfReader(str(output))
        assert len(reader.pages) == 6  # 2 + 3 + 1

    def test_merge_single_file_produces_copy(self, tmp_path):
        """合并单个PDF时，输出应与源文件页数相同"""
        pdf1 = tmp_path / "single.pdf"
        _create_pdf(str(pdf1), 3)

        output = tmp_path / "merged.pdf"
        parser = PDFParser()
        result = parser.merge_pdfs([str(pdf1)], str(output))

        assert result is True
        assert output.exists()
        reader = PdfReader(str(output))
        assert len(reader.pages) == 3

    def test_merge_empty_list_returns_false(self, tmp_path):
        """文件列表为空时，合并应返回False"""
        output = tmp_path / "merged.pdf"
        parser = PDFParser()
        result = parser.merge_pdfs([], str(output))

        assert result is False

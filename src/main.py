import sys
import logging

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger


def main():
    # 配置主模块 logger，复用 invoice_ocr 的 handlers
    main_logger = logging.getLogger("Main")
    if not main_logger.handlers:
        main_logger.setLevel(logging.INFO)
        for h in logging.getLogger("invoice_ocr").handlers:
            main_logger.addHandler(h)

    main_logger.info("程序启动")
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

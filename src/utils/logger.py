"""日志工具模块"""
import logging
import os
import sys
from pathlib import Path
from datetime import datetime


def get_log_dir():
    """获取日志目录（支持打包后的场景）"""
    if getattr(sys, 'frozen', False):
        # nuitka 打包后，脚本所在目录
        # base_dir = Path(sys.executable).parent
        base_dir = Path(sys.argv[0]).parent
    else:
        # 开发环境，项目的 logs 目录
        base_dir = Path(__file__).parent.parent.parent
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir


def setup_logger(name: str = "invoice_ocr", level: int = logging.INFO):
    """配置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    log_dir = get_log_dir()
    log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"

    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 格式化
    formatter = logging.Formatter(
        "[%(levelname)s]%(asctime)s -[%(name)s]  -%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 默认日志记录器
logger = setup_logger()

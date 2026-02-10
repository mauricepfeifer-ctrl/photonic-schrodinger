import logging
import sys
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler

def get_logger(name: str, log_file: str = "empire.log", level=logging.INFO):
    """
    Returns a structured logger with:
    - Console output (Rich)
    - File output (Rotating JSON-like or standard format)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # 1. Console Handler (Rich)
    console_handler = RichHandler(rich_tracebacks=True, markup=True)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # 2. File Handler (Rotating)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3  # 5MB file size, 3 backups
    )
    file_fmt = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    )
    file_handler.setFormatter(file_fmt)
    file_handler.setLevel(logging.DEBUG)  # Log detailed debug info to file
    logger.addHandler(file_handler)

    return logger

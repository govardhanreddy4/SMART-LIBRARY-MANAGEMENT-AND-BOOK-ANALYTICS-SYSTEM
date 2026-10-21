"""Logging configuration with rotating file handler and console output."""

import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

# Add project root to path if needed
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import LOG_FILE_PATH, LOG_FORMAT, LOG_MAX_BYTES, LOG_BACKUP_COUNT


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure root logger with a rotating file handler and stdout stream."""
    root_logger = logging.getLogger("smart_library")
    root_logger.setLevel(level)

    # Avoid adding duplicate handlers on multiple calls
    if not root_logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)

        # Rotating file handler to prevent unbounded log growth
        file_handler = RotatingFileHandler(
            filename=str(LOG_FILE_PATH),
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the 'smart_library' namespace."""
    setup_logging()
    return logging.getLogger(f"smart_library.{name}")

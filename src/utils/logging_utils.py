"""Logging utility functions for setting up a dedicated logger with file and console handlers"""
import logging
from pathlib import Path

def setup_logger(log_path: Path):
    """
    Create and configure a dedicated logger for this run.
    Ensures:
    - no duplicate handlers
    - correct log file every run
    - console + file output
    
    Returns configured logger instance.
    """
    logger = logging.getLogger("ib_matchwise")  # dedicated logger
    logger.setLevel(logging.INFO)
    
    # Prevent propagation to root logger to avoid duplicates
    logger.propagate = False

    # IMPORTANT: Remove old handlers if re-running
    if logger.hasHandlers():
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    # --- File Handler ---
    try:
        fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        # If file handler fails, log warning to console handler only
        logger.warning(f"Could not create log file: {e}")

    return logger


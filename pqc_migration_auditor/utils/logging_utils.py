"""
Logging utilities for the PQC Migration Auditor.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str, verbose: bool = False) -> logging.Logger:
    """
    Set up a logger with appropriate formatting and level.

    Args:
        name: Logger name
        verbose: If True, set DEBUG level; otherwise INFO

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Avoid adding multiple handlers if logger already configured
    if logger.handlers:
        return logger

    # Console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)

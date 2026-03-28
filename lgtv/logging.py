"""Logging configuration for LG TV CLI."""

import logging
import os
import sys


# Create package logger
logger = logging.getLogger("lgtv")


def setup_logging(debug: bool = False, log_file: str = None):
    """Configure logging for the application.

    Args:
        debug: Enable debug logging
        log_file: Optional file path to write logs to
    """
    # Check environment variable for log level
    env_level = os.environ.get("LGTV_LOG_LEVEL", "").upper()

    if debug:
        level = logging.DEBUG
    elif env_level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        level = getattr(logging, env_level)
    else:
        level = logging.WARNING

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure root logger for the package
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Add stderr handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(level)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Don't propagate to root logger
    logger.propagate = False

    logger.debug("Logging initialized (level=%s)", logging.getLevelName(level))


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Optional name suffix for the logger (e.g., "config" -> "lgtv.config")

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"lgtv.{name}")
    return logger

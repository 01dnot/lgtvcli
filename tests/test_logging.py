"""Tests for lgtv.logging module."""

import logging
import os
from unittest.mock import patch

from lgtv.logging import setup_logging, get_logger


class TestSetupLogging:
    """Tests for setup_logging function."""

    def teardown_method(self):
        """Clean up logging after each test."""
        logger = logging.getLogger("lgtv")
        logger.handlers.clear()
        logger.setLevel(logging.WARNING)

    def test_setup_logging_default_level(self):
        """Default logging level is WARNING."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("LGTV_LOG_LEVEL", None)
            setup_logging()
            logger = logging.getLogger("lgtv")
            assert logger.level == logging.WARNING

    def test_setup_logging_debug_flag(self):
        """debug=True sets DEBUG level."""
        setup_logging(debug=True)
        logger = logging.getLogger("lgtv")
        assert logger.level == logging.DEBUG

    def test_setup_logging_env_debug(self, monkeypatch):
        """LGTV_LOG_LEVEL=DEBUG sets DEBUG level."""
        monkeypatch.setenv("LGTV_LOG_LEVEL", "DEBUG")
        setup_logging()
        logger = logging.getLogger("lgtv")
        assert logger.level == logging.DEBUG

    def test_setup_logging_env_info(self, monkeypatch):
        """LGTV_LOG_LEVEL=INFO sets INFO level."""
        monkeypatch.setenv("LGTV_LOG_LEVEL", "INFO")
        setup_logging()
        logger = logging.getLogger("lgtv")
        assert logger.level == logging.INFO

    def test_setup_logging_env_warning(self, monkeypatch):
        """LGTV_LOG_LEVEL=WARNING sets WARNING level."""
        monkeypatch.setenv("LGTV_LOG_LEVEL", "WARNING")
        setup_logging()
        logger = logging.getLogger("lgtv")
        assert logger.level == logging.WARNING

    def test_setup_logging_env_error(self, monkeypatch):
        """LGTV_LOG_LEVEL=ERROR sets ERROR level."""
        monkeypatch.setenv("LGTV_LOG_LEVEL", "ERROR")
        setup_logging()
        logger = logging.getLogger("lgtv")
        assert logger.level == logging.ERROR

    def test_setup_logging_env_critical(self, monkeypatch):
        """LGTV_LOG_LEVEL=CRITICAL sets CRITICAL level."""
        monkeypatch.setenv("LGTV_LOG_LEVEL", "CRITICAL")
        setup_logging()
        logger = logging.getLogger("lgtv")
        assert logger.level == logging.CRITICAL

    def test_setup_logging_env_invalid(self, monkeypatch):
        """Invalid LGTV_LOG_LEVEL defaults to WARNING."""
        monkeypatch.setenv("LGTV_LOG_LEVEL", "INVALID")
        setup_logging()
        logger = logging.getLogger("lgtv")
        assert logger.level == logging.WARNING

    def test_setup_logging_env_lowercase(self, monkeypatch):
        """LGTV_LOG_LEVEL is case insensitive."""
        monkeypatch.setenv("LGTV_LOG_LEVEL", "debug")
        setup_logging()
        logger = logging.getLogger("lgtv")
        assert logger.level == logging.DEBUG

    def test_setup_logging_debug_overrides_env(self, monkeypatch):
        """debug=True overrides LGTV_LOG_LEVEL."""
        monkeypatch.setenv("LGTV_LOG_LEVEL", "ERROR")
        setup_logging(debug=True)
        logger = logging.getLogger("lgtv")
        assert logger.level == logging.DEBUG

    def test_setup_logging_adds_stderr_handler(self):
        """setup_logging adds a stderr handler."""
        setup_logging()
        logger = logging.getLogger("lgtv")
        assert len(logger.handlers) >= 1
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    def test_setup_logging_with_file(self, tmp_path):
        """setup_logging adds file handler when log_file specified."""
        log_file = str(tmp_path / "test.log")
        setup_logging(log_file=log_file)
        logger = logging.getLogger("lgtv")
        assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

    def test_setup_logging_file_writes_logs(self, tmp_path):
        """File handler writes logs to file."""
        log_file = tmp_path / "test.log"
        setup_logging(debug=True, log_file=str(log_file))
        logger = logging.getLogger("lgtv")
        logger.debug("test message")

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        content = log_file.read_text()
        assert "test message" in content

    def test_setup_logging_clears_existing_handlers(self):
        """setup_logging removes existing handlers."""
        logger = logging.getLogger("lgtv")
        logger.addHandler(logging.StreamHandler())
        logger.addHandler(logging.StreamHandler())
        initial_count = len(logger.handlers)

        setup_logging()

        # Should have cleared old handlers and added new one
        assert len(logger.handlers) < initial_count + 1

    def test_setup_logging_no_propagate(self):
        """setup_logging sets propagate=False."""
        setup_logging()
        logger = logging.getLogger("lgtv")
        assert logger.propagate is False

    def test_setup_logging_formatter(self):
        """setup_logging uses correct log format."""
        setup_logging()
        logger = logging.getLogger("lgtv")
        handler = logger.handlers[0]
        formatter = handler.formatter
        assert formatter is not None
        # Format string should include level and name
        assert "%(levelname)" in formatter._fmt or "levelname" in str(formatter._fmt)


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_without_name(self):
        """get_logger() returns root lgtv logger."""
        logger = get_logger()
        assert logger.name == "lgtv"

    def test_get_logger_with_name(self):
        """get_logger(name) returns child logger."""
        logger = get_logger("config")
        assert logger.name == "lgtv.config"

    def test_get_logger_with_nested_name(self):
        """get_logger with dotted name creates nested logger."""
        logger = get_logger("commands.power")
        assert logger.name == "lgtv.commands.power"

    def test_get_logger_returns_logger_instance(self):
        """get_logger returns logging.Logger instance."""
        logger = get_logger("test")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_same_name_returns_same_logger(self):
        """Same name returns same logger instance."""
        logger1 = get_logger("test")
        logger2 = get_logger("test")
        assert logger1 is logger2

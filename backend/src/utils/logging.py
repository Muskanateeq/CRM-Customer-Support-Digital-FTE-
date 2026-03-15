"""
Custora Customer Success FTE - Structured Logging
Production-ready logging with correlation IDs and structured output
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from contextvars import ContextVar
import uuid

# Context variable for correlation ID (tracks requests across services)
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')


def get_correlation_id() -> str:
    """Get current correlation ID."""
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str = None):
    """Set correlation ID for current context."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    return correlation_id


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured JSON logging.

    Outputs logs in JSON format for easy parsing by log aggregators.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""

        # Base log structure
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': get_correlation_id(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        # Add source location in development
        if record.levelno >= logging.WARNING:
            log_data['source'] = {
                'file': record.pathname,
                'line': record.lineno,
                'function': record.funcName
            }

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for console output (development only).
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Format: [TIME] LEVEL - logger - message
        timestamp = datetime.utcnow().strftime('%H:%M:%S')
        correlation_id = get_correlation_id()

        formatted = (
            f"{color}[{timestamp}] {record.levelname:8s}{reset} "
            f"- {record.name:30s} - {record.getMessage()}"
        )

        if correlation_id:
            formatted += f" [cid: {correlation_id[:8]}]"

        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging(log_level: str = "INFO", environment: str = "development"):
    """
    Setup application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment (development, production)
    """

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Use structured JSON logging in production, colored in development
    if environment == "production":
        formatter = StructuredFormatter()
    else:
        formatter = ColoredFormatter()

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("aiokafka").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger with name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger: Configured logger
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds extra context to all log messages.

    Usage:
        logger = LoggerAdapter(logging.getLogger(__name__), {'customer_id': '123'})
        logger.info("Processing request")  # Will include customer_id in log
    """

    def process(self, msg, kwargs):
        """Add extra fields to log record."""
        if 'extra' not in kwargs:
            kwargs['extra'] = {}

        # Add adapter's extra fields
        if hasattr(self, 'extra'):
            kwargs['extra'].update(self.extra)

        # Store extra fields in record
        if kwargs['extra']:
            kwargs['extra']['extra_fields'] = kwargs['extra'].copy()

        return msg, kwargs

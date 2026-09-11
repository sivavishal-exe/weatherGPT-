import logging
import re
import sys
from typing import Any

# Sensitive pattern regexes for redacting secrets in logs
SENSITIVE_PATTERNS = [
    (re.compile(r'(api_key|token|password|secret|authorization)=["\']?[^"\'&\s]+["\']?', re.IGNORECASE), r'\1=***REDACTED***'),
    (re.compile(r'(Bearer\s+)[A-Za-z0-9\-\._~\+\/]+=*', re.IGNORECASE), r'\1***REDACTED***'),
]


class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive information like tokens, keys, and credentials from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, replacement in SENSITIVE_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        if record.args:
            cleaned_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, replacement in SENSITIVE_PATTERNS:
                        arg = pattern.sub(replacement, arg)
                cleaned_args.append(arg)
            record.args = tuple(cleaned_args)
        return True


def setup_logger(name: str = "weathergpt") -> logging.Logger:
    """Configures a secure, structured logger with redaction enabled."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logger()

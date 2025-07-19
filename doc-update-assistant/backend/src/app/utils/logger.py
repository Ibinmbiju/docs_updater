"""Centralized logging configuration for the application."""

import logging
import sys
from typing import Optional


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Set up a logger with consistent formatting and level."""
    logger = logging.getLogger(name)
    
    # Set level from parameter or default to INFO
    if level:
        log_level = level.upper()
    else:
        try:
            from ..config import settings
            log_level = settings.log_level.upper()
        except (ImportError, AttributeError):
            log_level = "INFO"
    
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


# App-wide loggers
app_logger = setup_logger("docs_assistant.app", "INFO")
api_logger = setup_logger("docs_assistant.api", "INFO")
processor_logger = setup_logger("docs_assistant.processor", "INFO")
ai_logger = setup_logger("docs_assistant.ai", "INFO")
"""Centralized logging configuration for the application."""

import logging
import os
import sys


def get_debug_logger(name: str) -> logging.Logger:
    """Get a logger that respects the DEBUG_LOGGING environment variable.
    
    Args:
        name: The name of the logger (typically __name__)
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Check if DEBUG_LOGGING environment variable is set to true
    debug_enabled = os.getenv("DEBUG_LOGGING", "").lower() in ("true", "1", "yes")
    
    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    
    # Set level based on environment variable
    logger.setLevel(logging.DEBUG if debug_enabled else logging.WARNING)
    
    return logger


def is_debug_enabled() -> bool:
    """Check if debug logging is enabled via environment variable.
    
    Returns:
        True if DEBUG_LOGGING is set to true/1/yes, False otherwise
    """
    return os.getenv("DEBUG_LOGGING", "").lower() in ("true", "1", "yes")

"""
Logging Configuration
Structured logging configuration for the Healthcare Operations Assistant
"""

import logging
import sys
from datetime import datetime
import os


def setup_logger(name: str = "healthcare_ops") -> logging.Logger:
    """
    Setup and configure logger with structured formatting
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler with detailed format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(detailed_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional - if logs directory exists)
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    if os.path.exists(log_dir):
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f'healthcare_ops_{datetime.now().strftime("%Y%m%d")}.log')
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()

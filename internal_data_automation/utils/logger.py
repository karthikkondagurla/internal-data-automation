import logging
import os
import sys
from pathlib import Path

def setup_logger(name: str = "internal_data_automation", log_file: str = "logs/pipeline.log", level: str = "INFO") -> logging.Logger:
    """
    Sets up a logger that logs to both console and a file.
    
    Args:
        name: Name of the logger.
        log_file: Path to the log file.
        level: Logging level (e.g., "INFO", "DEBUG").
        
    Returns:
        Configured logger instance.
    """
    # specific log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger
        
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    try:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file logging: {e}")
        
    return logger

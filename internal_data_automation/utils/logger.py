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

    # CloudWatch Handler (if configured)
    # We check if 'cloudwatch_config' is passed in extra args or handle it outside.
    # For simplicity, we can pass it as an argument or handle it in the caller.
    # However, to match the signature, we might need to rely on the caller adding the handler.
    # To keep this function focused, we will just return the logger here.
        
    return logger

def add_cloudwatch_handler(logger: logging.Logger, log_group: str, log_stream_name: str):
    """
    Adds a CloudWatch log handler to the existing logger.
    """
    try:
        from internal_data_automation.utils.aws_utils import CloudWatchLogHandler
        cw_handler = CloudWatchLogHandler(log_group=log_group, log_stream_name=log_stream_name)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        cw_handler.setFormatter(formatter)
        logger.addHandler(cw_handler)
    except Exception as e:
        logger.error(f"Failed to add CloudWatch handler: {e}")

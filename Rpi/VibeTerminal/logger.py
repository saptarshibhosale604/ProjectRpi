"""
Logger for VibeTerminal
Centralized logging management
"""

import logging
import os
from datetime import datetime
from config import CONFIG


class Logger:
    """Handles all logging for the application"""
    
    def __init__(self):
        self.log_dir = CONFIG["log_dir"]
        self.log_level = CONFIG["log_level"]
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure logging to file and console"""
        os.makedirs(self.log_dir, exist_ok=True)
        
        log_file = os.path.join(
            self.log_dir,
            f'vibeterminal-{datetime.now().strftime("%Y-%m-%d")}.log'
        )
        
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                # logging.StreamHandler()  # Also log to console
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def log(self, msg, level="INFO"):
        """Log a message"""
        getattr(self.logger, level.lower())(msg)
    
    def info(self, msg):
        """Log info message"""
        self.logger.info(msg)
    
    def error(self, msg):
        """Log error message"""
        self.logger.error(msg)
    
    def warning(self, msg):
        """Log warning message"""
        self.logger.warning(msg)
    
    def debug(self, msg):
        """Log debug message"""
        self.logger.debug(msg)

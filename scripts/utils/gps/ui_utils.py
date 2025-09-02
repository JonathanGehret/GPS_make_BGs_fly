#!/usr/bin/env python3
"""
User Interface Utilities

Functions for consistent user interaction and messaging.
"""

import logging


def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


class UserInterface:
    """Utilities for consistent user interaction"""
    
    @staticmethod
    def print_header(title: str, width: int = 80):
        """Print a formatted header"""
        print("\n" + "=" * width)
        print(f"{title:^{width}}")
        print("=" * width)
    
    @staticmethod
    def print_section(title: str, width: int = 50):
        """Print a formatted section header"""
        print(f"\n{title}")
        print("-" * width)
    
    @staticmethod
    def print_success(message: str):
        """Print a success message"""
        print(f"✅ {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Print a warning message"""
        print(f"⚠️  {message}")
    
    @staticmethod
    def print_error(message: str):
        """Print an error message"""
        print(f"❌ {message}")
    
    @staticmethod
    def print_info(message: str):
        """Print an info message"""
        print(f"ℹ️  {message}")


# Create default logger instance
logger = setup_logging()

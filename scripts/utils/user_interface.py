"""
User Interface Module

Utilities for consistent user interaction and terminal output formatting.
"""


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


# ===========================
# EXCEPTION CLASSES
# ===========================

class GPSVisualizationError(Exception):
    """Base exception for GPS visualization errors"""
    pass


class DataLoadError(GPSVisualizationError):
    """Raised when data loading fails"""
    pass


class ValidationError(GPSVisualizationError):
    """Raised when data validation fails"""
    pass


class VisualizationError(GPSVisualizationError):
    """Raised when visualization creation fails"""
    pass

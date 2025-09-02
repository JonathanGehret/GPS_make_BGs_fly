#!/usr/bin/env python3
"""
Proximity Analysis GUI Package

Modular proximity analysis GUI components for better maintainability and organization.
"""

# Import main components
from .config import ProximityGUIConfig
from .i18n_handler import ProximityI18nHandler
from .event_handlers import ProximityEventHandler
from .ui_builder import ProximityUIBuilder

# Version info
__version__ = "1.0.0"
__author__ = "GPS Vulture Visualization Project"

# Export main components
__all__ = [
    'ProximityGUIConfig',
    'ProximityI18nHandler', 
    'ProximityEventHandler',
    'ProximityUIBuilder'
]

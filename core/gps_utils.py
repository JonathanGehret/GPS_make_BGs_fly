#!/usr/bin/env python3
"""
GPS Utils - Backwards Compatibility Module

This module maintains backwards compatibility by importing from the new modular GPS utilities.
All functionality has been moved to scripts/utils/gps/ for better organization.

For new code, consider importing directly from scripts.utils.gps instead:
    from scripts.utils.gps import DataLoader, VisualizationHelper, etc.
"""

# Import everything from the new modular GPS package for backwards compatibility
from utils.gps import *

# Note: This file should eventually be deprecated in favor of direct imports from utils.gps

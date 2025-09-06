#!/usr/bin/env python3
"""
Test script for precipitation overlay coloring functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.data.trail_system import TrailSystem
from utils.user_interface import UserInterface

def test_precipitation_coloring():
    """Test the precipitation-based coloring functionality"""
    print("Testing precipitation-based coloring...")

    # Create trail system instance
    ui = UserInterface()
    trail_system = TrailSystem(ui)

    # Test color function with different precipitation values
    test_values = [0, 0.1, 0.5, 2.0, 5.0, 10.0]

    print("Precipitation color mapping:")
    for precip in test_values:
        color = trail_system._get_precipitation_color(precip)
        print(f"  {precip} mm/h -> {color}")

    print("✅ Precipitation coloring test completed!")
    return True

if __name__ == "__main__":
    test_precipitation_coloring()

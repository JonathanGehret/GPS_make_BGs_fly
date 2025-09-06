#!/usr/bin/env python3
"""
Test script for timezone-aware precipitation data matching
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from core.animation.live_map_animator import LiveMapAnimator

def test_timezone_matching():
    """Test timezone conversion and timestamp matching"""
    print("Testing timezone-aware precipitation matching...")

    # Create a mock animator instance
    animator = LiveMapAnimator()

    # Create mock API data (simulating Open-Meteo response)
    mock_data = {
        'hourly': {
            'time': [
                '2025-09-05T10:00', '2025-09-05T11:00', '2025-09-05T12:00',
                '2025-09-05T13:00', '2025-09-05T14:00', '2025-09-05T15:00'
            ],
            'precipitation': [0.0, 0.5, 1.2, 0.8, 0.0, 0.0]
        }
    }

    # Test timestamps in UTC (simulating GPS data)
    # Note: Precipitation at T represents rain during [T, T+1)
    test_cases = [
        ('2025-09-05 08:30:00 UTC', 0.0),  # Berlin 10:30 -> matches 10:00 precipitation
        ('2025-09-05 09:15:00 UTC', 0.5),  # Berlin 11:15 -> matches 11:00 precipitation
        ('2025-09-05 10:45:00 UTC', 1.2),  # Berlin 12:45 -> matches 12:00 precipitation
        ('2025-09-05 11:20:00 UTC', 0.8),  # Berlin 13:20 -> matches 13:00 precipitation
        ('2025-09-05 12:10:00 UTC', 0.0),  # Berlin 14:10 -> matches 14:00 precipitation
    ]

    print("Testing UTC to Berlin timezone conversion:")
    for utc_str, expected in test_cases:
        utc_timestamp = pd.to_datetime(utc_str, utc=True)
        result = animator.get_precipitation_for_timestamp(mock_data, utc_timestamp)
        status = "✅" if abs(result - expected) < 0.01 else "❌"
        print(f"  {status} {utc_str} -> {result} mm/h (expected: {expected} mm/h)")

    print("✅ Timezone matching test completed!")
    return True

if __name__ == "__main__":
    test_timezone_matching()

#!/usr/bin/env python3
"""
Test script for precipitation overlay functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.animation.live_map_animator import LiveMapAnimator
import pandas as pd

def test_precipitation_api():
    """Test the precipitation API fetching functionality"""
    print("Testing precipitation API functionality...")

    # Create a mock animator instance
    animator = LiveMapAnimator()

    # Test coordinates (somewhere in Germany/Austria for the vulture project)
    lat, lon = 47.5, 13.0  # Approximate location
    # Use recent dates for testing
    start_date = "2024-09-01"
    end_date = "2024-09-02"

    try:
        data = animator.fetch_precipitation_data(lat, lon, start_date, end_date)
        if data:
            print("✅ API call successful!")
            print(f"   Data keys: {list(data.keys())}")
            if 'hourly' in data:
                hourly = data['hourly']
                if 'time' in hourly and 'precipitation' in hourly:
                    times = hourly['time']
                    precipitations = hourly['precipitation']
                    print(f"   Time points: {len(times)}")
                    print(f"   Precipitation values: {len(precipitations)}")
                    print(f"   Sample data: {list(zip(times[:3], precipitations[:3]))}")
                else:
                    print("   ⚠️ Missing hourly time/precipitation data")
            else:
                print("   ⚠️ Missing hourly data")
        else:
            print("❌ API call failed or returned no data")
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

    # Test timestamp matching
    try:
        # Use a timestamp that should be in the returned data
        test_timestamp = pd.Timestamp("2025-08-30 12:00:00", tz='UTC')
        if data:
            precip = animator.get_precipitation_for_timestamp(data, test_timestamp)
            print(f"✅ Timestamp matching: {precip} mm/h for {test_timestamp}")
        else:
            print("⚠️ Skipping timestamp test due to API failure")
    except Exception as e:
        print(f"❌ Timestamp test failed: {e}")
        return False

    print("Test completed!")
    return True

if __name__ == "__main__":
    test_precipitation_api()

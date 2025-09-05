#!/usr/bin/env python3
"""
Test script to debug proximity analysis issues
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        from core.gps_utils import DataLoader, get_numbered_output_path
        print("✅ core.gps_utils imports successful")
    except Exception as e:
        print(f"❌ core.gps_utils import failed: {e}")
        return False
    
    try:
        from core.analysis.proximity_engine import ProximityEngine
        print("✅ proximity_engine import successful")
    except Exception as e:
        print(f"❌ proximity_engine import failed: {e}")
        return False
    
    try:
        from utils.proximity_plots import ProximityVisualizer
        print("✅ proximity_plots import successful")
    except Exception as e:
        print(f"❌ proximity_plots import failed: {e}")
        return False
    
    return True

def test_data_loading():
    """Test data loading"""
    print("\nTesting data loading...")
    
    try:
        from core.gps_utils import DataLoader
        
        data_folder = "assets/data"
        data_loader = DataLoader(data_folder)
        csv_files = data_loader.find_csv_files()
        
        print(f"Found {len(csv_files)} CSV files: {csv_files}")
        
        if csv_files:
            dataframes = data_loader.load_all_csv_files()
            print(f"Loaded {len(dataframes)} dataframes")
            for i, df in enumerate(dataframes):
                vulture_id = df['vulture_id'].iloc[0] if 'vulture_id' in df.columns else f"Vulture_{i+1}"
                print(f"  - {vulture_id}: {len(df)} records")
            return dataframes
        else:
            print("❌ No CSV files found")
            return None
            
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_proximity_analysis(dataframes):
    """Test proximity analysis"""
    print("\nTesting proximity analysis...")
    
    try:
        from core.analysis.proximity_engine import ProximityEngine
        
        engine = ProximityEngine()
        engine.load_dataframes(dataframes)
        engine.proximity_threshold_km = 10.0  # Increased from 2.0
        engine.min_duration_minutes = 1.0     # Decreased from 5.0
        
        print(f"Engine configured: threshold={engine.proximity_threshold_km}km, min_duration={engine.min_duration_minutes}min")
        
        events = engine.analyze_proximity()
        print(f"Found {len(events)} proximity events")
        
        if events:
            stats = engine.calculate_statistics()
            print(f"Statistics: {stats.total_events} events, {stats.unique_pairs} pairs")
            return events, stats
        else:
            print("⚠️ No proximity events found")
            return None, None
            
    except Exception as e:
        print(f"❌ Proximity analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def main():
    """Main test function"""
    print("🔍 Debug Proximity Analysis Issues")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed - aborting")
        return
    
    # Test data loading
    dataframes = test_data_loading()
    if not dataframes:
        print("\n❌ Data loading failed - aborting")
        return
    
    # Test proximity analysis
    events, stats = test_proximity_analysis(dataframes)
    if events:
        print(f"\n✅ Analysis successful: {len(events)} events found")
    else:
        print(f"\n⚠️ Analysis completed but no events found")
    
    print("\n🎯 Debug test completed")

if __name__ == "__main__":
    main()

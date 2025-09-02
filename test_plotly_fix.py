#!/usr/bin/env python3
"""
Quick test to verify the Plotly template error is fixed
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_plotly_config():
    """Test that the slider configuration is valid for Plotly"""
    print("🔧 Testing Fixed Plotly Configuration")
    print("=" * 40)
    
    try:
        from scripts.utils.enhanced_timeline_labels import create_enhanced_slider_config
        
        # Create test time data
        test_times = [
            "01.01.2024 10:00:00",
            "01.01.2024 11:00:00", 
            "01.01.2024 12:00:00"
        ]
        
        # Test with prominent display - this should NOT use 'template'
        print("Creating slider config with prominent display...")
        slider_config = create_enhanced_slider_config(
            test_times, 
            enable_prominent_display=True
        )
        
        # Verify no invalid properties
        currentvalue = slider_config['currentvalue']
        valid_properties = {'prefix', 'suffix', 'font', 'visible', 'xanchor', 'offset'}
        
        for prop in currentvalue.keys():
            if prop not in valid_properties:
                print(f"❌ Invalid property found: {prop}")
                return False
        
        # Check that we don't have the problematic 'template' property
        if 'template' in currentvalue:
            print("❌ Invalid 'template' property still present!")
            return False
        
        print("✅ All properties are valid for Plotly")
        print(f"✅ Font size: {currentvalue['font']['size']}px")
        print(f"✅ Font family: {currentvalue['font']['family']}")
        print(f"✅ Font color: {currentvalue['font']['color']}")
        print(f"✅ Prefix: '{currentvalue['prefix']}'")
        print(f"✅ Offset: {currentvalue['offset']}px")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_plotly_config()
    if success:
        print("\n🎉 Fix successful! No more Plotly template errors.")
        print("The prominent time display now uses valid Plotly properties.")
    else:
        print("\n⚠️ Issue still exists - check the implementation.")

#!/usr/bin/env python3
"""
Test Animation UI Stability
Tests for slider disappearing and button jumping issues
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_ui_stability():
    """Test UI stability fixes"""
    print("🎯 Testing Animation UI Stability Fixes")
    print("=" * 45)
    
    try:
        # Test 1: Slider Configuration Stability
        print("\n1. Testing Slider Configuration...")
        from scripts.utils.enhanced_timeline_labels import create_enhanced_slider_config
        
        test_times = [
            "15.06.2024 08:00:00",
            "15.06.2024 08:30:00", 
            "15.06.2024 09:00:00"
        ]
        
        slider_config = create_enhanced_slider_config(test_times, enable_prominent_display=True)
        
        # Check slider has all required properties
        required_props = ['active', 'currentvalue', 'x', 'y', 'len', 'steps', 'visible']
        for prop in required_props:
            if prop not in slider_config:
                print(f"   ❌ Missing required property: {prop}")
                return False
        
        # Check slider is visible
        if not slider_config.get('visible', True):
            print("   ❌ Slider visibility set to False")
            return False
        
        print(f"   ✅ Slider config complete ({len(slider_config['steps'])} steps)")
        print(f"   ✅ Slider visibility: {slider_config['visible']}")
        
        # Test 2: Button Positioning Stability
        print("\n2. Testing Button Positioning...")
        from scripts.utils.animation_state_manager import AnimationStateManager
        
        manager = AnimationStateManager(frame_duration=500)
        updatemenus = manager.create_enhanced_updatemenus(
            include_speed_controls=True,
            frame_duration=500
        )
        
        if len(updatemenus) != 2:
            print(f"   ❌ Expected 2 updatemenus, got: {len(updatemenus)}")
            return False
        
        main_controls = updatemenus[0]
        speed_controls = updatemenus[1]
        
        # Check positioning doesn't overlap
        main_y = main_controls['y']
        speed_y = speed_controls['y']
        
        if abs(speed_y - main_y) < 0.08:  # Too close, might overlap
            print(f"   ❌ Controls too close: main={main_y}, speed={speed_y}")
            return False
        
        # Check fixed positioning elements
        if 'pad' not in main_controls:
            print("   ❌ Main controls missing padding for stability")
            return False
        
        if 'pad' not in speed_controls:
            print("   ❌ Speed controls missing padding for stability")
            return False
        
        print(f"   ✅ Main controls at y={main_y} with padding")
        print(f"   ✅ Speed controls at y={speed_y} with padding")
        print(f"   ✅ Safe separation: {abs(speed_y - main_y):.2f}")
        
        # Test 3: Step Args Validation
        print("\n3. Testing Step Args Structure...")
        steps = slider_config['steps']
        first_step = steps[0]
        
        # Check args structure
        args = first_step['args']
        if not isinstance(args, list) or len(args) != 2:
            print(f"   ❌ Invalid args structure: {args}")
            return False
        
        frame_list = args[0]
        if not isinstance(frame_list, list):
            print(f"   ❌ Frame should be in list: {frame_list}")
            return False
        
        config = args[1]
        if 'frame' not in config or 'mode' not in config:
            print(f"   ❌ Missing frame config: {config}")
            return False
        
        print("   ✅ Step args structure valid")
        print(f"   ✅ Step mode: {config['mode']}")
        print(f"   ✅ Step frame duration: {config['frame']['duration']}")
        
        print("\n" + "=" * 45)
        print("🎉 UI Stability Tests Passed!")
        
        print("\n📋 Stability Improvements:")
        print("   ✅ Slider visibility explicitly set to True")
        print("   ✅ Button positioning with safe separation")
        print("   ✅ Fixed padding to prevent jumping")
        print("   ✅ Robust step args extraction")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_positioning_guide():
    """Show the positioning layout"""
    print("\n\n📐 Control Layout Guide:")
    print("=" * 30)
    print("┌─────────────────────────┐")
    print("│                         │")
    print("│   [0.25x][0.5x][1x]     │  ← Speed controls (y=0.15)")
    print("│   [2.0x][5.0x]          │")
    print("│                         │")
    print("│                         │")
    print("│ [▶️ Play][⏸️ Pause]      │  ← Main controls (y=0.02)")
    print("│ [⏮️ Restart]            │")
    print("│ ═══════════════════════ │  ← Slider (y=0.08)")
    print("│ 🕒 15.06.2024 08:30:00  │")
    print("└─────────────────────────┘")
    print("\nSeparation: 0.13 (safe distance)")

if __name__ == "__main__":
    success = test_ui_stability()
    show_positioning_guide()
    
    if success:
        print("\n\n🚀 UI Should Now Be Stable!")
        print("   • Slider won't disappear")
        print("   • Speed buttons won't jump")
        print("   • Controls have proper spacing")
    else:
        print("\n⚠️  Issues detected - check output above")

#!/usr/bin/env python3
"""
Test Playback Speed Controls

Quick test to verify the new playback speed functionality works correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

import tkinter as tk
from utils.animation_controls import AnimationControlsFrame

def test_animation_controls():
    """Test the animation controls with playback speed"""
    print("🧪 Testing Animation Controls with Playback Speed")
    
    # Create a test window
    root = tk.Tk()
    root.title("Animation Controls Test")
    root.geometry("600x400")
    
    # Create the animation controls frame
    controls = AnimationControlsFrame(
        parent_frame=root,
        include_time_buffer=True,
        include_encounter_limit=True,
        data_folder="data"
    )
    
    # Test getting configuration
    config = controls.get_config()
    print(f"✅ Default configuration: {config}")
    
    # Test setting configuration
    test_config = {
        'trail_length': 3.5,
        'time_step': '5m',
        'playback_speed': 2.5,
        'time_buffer': 1.5,
        'limit_encounters': 10
    }
    
    controls.set_config(test_config)
    new_config = controls.get_config()
    print(f"✅ Updated configuration: {new_config}")
    
    # Test frame duration calculation
    print(f"✅ Frame duration at 1.0x speed: {controls.get_frame_duration(600)}ms (should be 600ms)")
    print(f"✅ Frame duration at 2.0x speed: {controls.get_frame_duration(600)}ms (should be ~300ms)")
    
    print("\n🎉 Animation Controls Test Complete!")
    print("You can now adjust the playback speed slider to test the functionality.")
    print("Close this window to end the test.")
    
    # Run the GUI
    root.mainloop()

if __name__ == "__main__":
    test_animation_controls()

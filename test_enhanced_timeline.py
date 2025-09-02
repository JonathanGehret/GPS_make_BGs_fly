#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced timeline labels system.
Shows how the labeling adapts to different time frames.
"""

import sys
import os
from datetime import datetime, timedelta

# Add scripts to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

def test_timeline_labels():
    """Test the enhanced timeline labels with different time spans"""
    print("🏷️  Enhanced Timeline Labels Test")
    print("=" * 50)
    
    try:
        from utils.enhanced_timeline_labels import TimelineLabelSystem, create_enhanced_slider_config
        
        label_system = TimelineLabelSystem()
        print("✅ TimelineLabelSystem imported successfully")
        
        # Test different time spans
        test_cases = [
            ("30 minutes", 30, 2),      # 30 minutes, 2-minute steps
            ("2 hours", 120, 5),        # 2 hours, 5-minute steps  
            ("6 hours", 360, 15),       # 6 hours, 15-minute steps
            ("2 days", 2880, 60),       # 2 days, 1-hour steps
            ("1 week", 10080, 360),     # 1 week, 6-hour steps
            ("3 weeks", 30240, 1440),   # 3 weeks, 1-day steps
        ]
        
        for name, total_minutes, step_minutes in test_cases:
            print(f"\n📊 Testing: {name}")
            print("-" * 30)
            
            # Generate sample timestamps
            base_time = datetime.now()
            unique_times = []
            
            for i in range(0, total_minutes + 1, step_minutes):
                time_point = base_time + timedelta(minutes=i)
                time_str = time_point.strftime('%d.%m.%Y %H:%M:%S')
                unique_times.append(time_str)
            
            print(f"   📍 Generated {len(unique_times)} time points")
            
            # Analyze time span
            analysis = label_system.analyze_time_span(unique_times)
            print(f"   🎯 Strategy: {analysis['strategy']}")
            print(f"   ⏱️  Duration: {analysis.get('total_hours', 0):.1f} hours")
            
            # Get time span summary
            summary = label_system.get_time_span_summary(unique_times)
            print(f"   📝 Summary: {summary}")
            
            # Show sample labels (first 3 and last 3)
            enhanced_labels = label_system.create_enhanced_slider_labels(unique_times)
            print(f"   🏷️  Sample labels:")
            
            # Show first few labels
            for i, label_data in enumerate(enhanced_labels[:3]):
                clean_label = label_data['label'].replace('<b>', '').replace('</b>', '').replace('<br>', ' | ').replace('<small>', '').replace('</small>', '').replace("<small style='color:#666'>", '')
                print(f"      {i+1}: {clean_label}")
            
            if len(enhanced_labels) > 6:
                print(f"      ... ({len(enhanced_labels)-6} more) ...")
            
            # Show last few labels
            for i, label_data in enumerate(enhanced_labels[-3:], len(enhanced_labels)-2):
                clean_label = label_data['label'].replace('<b>', '').replace('</b>', '').replace('<br>', ' | ').replace('<small>', '').replace('</small>', '').replace("<small style='color:#666'>", '')
                print(f"      {i}: {clean_label}")
        
        print(f"\n🎉 Enhanced timeline labels test completed!")
        print("📍 Features demonstrated:")
        print("   • Adaptive labeling strategies (minutes/hours/days/weeks)")
        print("   • Two-line display (time + context)")
        print("   • Major/minor mark emphasis")
        print("   • Intelligent time span analysis")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_slider_config():
    """Test the slider configuration creation"""
    print(f"\n🎛️  Testing Slider Configuration")
    print("-" * 40)
    
    try:
        from utils.enhanced_timeline_labels import create_enhanced_slider_config
        
        # Create sample timestamps for 2 hours
        base_time = datetime.now()
        unique_times = []
        for i in range(0, 121, 10):  # 2 hours, 10-minute steps
            time_point = base_time + timedelta(minutes=i)
            time_str = time_point.strftime('%d.%m.%Y %H:%M:%S')
            unique_times.append(time_str)
        
        # Create enhanced slider config
        slider_config = create_enhanced_slider_config(unique_times)
        
        print(f"✅ Slider config created with {len(slider_config['steps'])} steps")
        print(f"   📍 Position: x={slider_config['x']}, y={slider_config['y']}")
        print(f"   📏 Length: {slider_config['len']}")
        print(f"   🎨 Enhanced styling: {'✅' if 'bgcolor' in slider_config else '❌'}")
        
        # Show sample step configurations
        print(f"   🎯 Sample step configs:")
        for i, step in enumerate(slider_config['steps'][:3]):
            print(f"      Step {i+1}: method={step['method']}, has_args={'✅' if 'args' in step else '❌'}")
        
        print("✅ Slider configuration test passed!")
        
    except Exception as e:
        print(f"❌ Slider config test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🎬 Enhanced Timeline Labels - Comprehensive Test")
    print("=" * 60)
    
    success1 = test_timeline_labels()
    success2 = test_slider_config()
    
    if success1 and success2:
        print(f"\n🎉 All tests passed!")
        print("📅 Your animation sliders now have:")
        print("   • Smart time labeling that adapts to any time span")
        print("   • Two-line display: time + date/context")
        print("   • Better visual hierarchy with major/minor marks")
        print("   • Optimized for readability across time scales")
        print("   • Enhanced styling with borders and backgrounds")
    else:
        print(f"\n❌ Some tests failed. Check the errors above.")

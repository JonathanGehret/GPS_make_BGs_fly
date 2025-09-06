"""
Mobiimport sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gps_utils import DataLoader, ensure_output_directories
from utils.mobile_interface import MobileInterface
from utils.performance_optimizer import PerformanceOptimizer
from core.animation.mobile_animation_engine import MobileAnimationEngine
import pandas as pd
import os
import tkinter as tk
from tkinter import messagebox
import platform
import subprocess
import webbrowseron - Main Script

Streamlined entry point for mobile-optimized GPS animation using modular architecture.
This script has been refactored from the original 513-line version to use
dedicated modules for better maintainability.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.gps_utils import DataLoader, ensure_output_directories
from utils.mobile_interface import MobileInterface
from utils.performance_optimizer import PerformanceOptimizer
from core.animation.mobile_animation_engine import MobileAnimationEngine
import pandas as pd
import os
import tkinter as tk
from tkinter import messagebox
import platform
import subprocess
import webbrowser


def show_mobile_completion_popup(output_path):
    """Show a completion popup with options to open folder and HTML file"""
    try:
        # Create popup dialog
        root = tk.Tk()
        root.title("Mobile Animation Complete")
        root.geometry("500x200")
        root.resizable(False, False)
        
        # Center the dialog
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Success message
        tk.Label(main_frame, text="✅", font=("Arial", 24)).pack(pady=(0, 10))
        tk.Label(main_frame, text="Mobile Animation Created Successfully!", 
                font=("Arial", 12, "bold")).pack(pady=(0, 5))
        
        # File info
        output_folder = os.path.dirname(output_path)
        filename = os.path.basename(output_path)
        tk.Label(main_frame, text=f"📁 Output: {output_folder}", 
                font=("Arial", 9)).pack(pady=(0, 2))
        tk.Label(main_frame, text=f"📄 File: {filename}", 
                font=("Arial", 9), fg="blue").pack(pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        # Open folder button
        tk.Button(button_frame, text="📁 Open Folder", 
                 command=lambda: open_output_folder(output_folder)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Open HTML button
        tk.Button(button_frame, text="🌐 Open HTML", 
                 command=lambda: open_html_file(output_path)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        tk.Button(button_frame, text="Close", 
                 command=root.destroy).pack(side=tk.LEFT)
        
        # Focus and bindings
        root.focus_set()
        root.bind('<Return>', lambda e: root.destroy())
        root.bind('<Escape>', lambda e: root.destroy())
        
        # Start the GUI
        root.mainloop()
        
    except Exception as e:
        print(f"Warning: Could not show completion popup: {e}")


def open_output_folder(folder_path):
    """Open the output folder in the system file manager"""
    try:
        if os.path.exists(folder_path):
            system = platform.system()
            
            if system == "Windows":
                subprocess.run(['explorer', folder_path], check=True)
            elif system == "Darwin":
                subprocess.run(['open', folder_path], check=True)
            else:
                subprocess.run(['xdg-open', folder_path], check=True)
            
            print(f"📁 Opened output folder: {folder_path}")
        else:
            messagebox.showerror("Error", f"Folder not found: {folder_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open folder: {e}")


def open_html_file(html_file_path):
    """Open the generated HTML file in the default browser"""
    try:
        if html_file_path and os.path.exists(html_file_path):
            webbrowser.open(f"file://{os.path.abspath(html_file_path)}")
            print(f"🌐 Opened HTML file: {html_file_path}")
        else:
            messagebox.showerror("Error", f"HTML file not found: {html_file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open HTML file: {e}")


def main():
    """Main mobile animation workflow"""
    mobile_ui = MobileInterface()
    
    try:
        # Initialize components
        mobile_ui.display_mobile_welcome()
        
        # Ensure output directories exist
        ensure_output_directories()
        
        # Load GPS data
        mobile_ui.ui.print_section("📁 LOADING DATA")
        data_loader = DataLoader()
        dataframes = data_loader.load_all_csv_files()
        
        if not dataframes:
            mobile_ui.ui.print_error("No GPS data found!")
            return False
        
        print(f"Loaded {len(dataframes)} GPS data files")
        
        # Use default mobile optimization (Fast - Mobile Optimal)
        selected_time_step = 120  # 120 seconds = 2 minutes
        print(f"📱 Using default mobile optimization: {selected_time_step}s time steps")
        
        # Process data with selected optimization
        mobile_ui.ui.print_section("⚡ PROCESSING DATA")
        optimizer = PerformanceOptimizer()
        processed_dataframes = []
        
        for i, df in enumerate(dataframes):
            print(f"   📱 Processing file {i+1}/{len(dataframes)}...")
            
            # Apply time step filtering for mobile optimization
            filtered_df = optimizer.filter_by_time_step(df, selected_time_step)
            
            if len(filtered_df) > 0:
                # Add vulture ID if not present
                if 'vulture_id' not in filtered_df.columns:
                    filtered_df = filtered_df.copy()
                    filtered_df['vulture_id'] = f'Vulture {i+1:02d}'
                
                processed_dataframes.append(filtered_df)
                print(f"      ✅ {len(filtered_df):,} points retained")
            else:
                print("      ⚠️ No data after filtering")
        
        if not processed_dataframes:
            mobile_ui.ui.print_error("No data remaining after mobile optimization!")
            return False
        
        # Combine processed data
        combined_data = pd.concat(processed_dataframes, ignore_index=True)
        total_points = len(combined_data)
        
        print(f"📱 Total mobile-optimized points: {total_points:,}")
        
        # Initialize mobile animation engine
        mobile_ui.ui.print_section("🎬 MOBILE ANIMATION SETUP")
        
        # Use default mobile configuration values
        mobile_height = 500
        mobile_zoom = 13
        mobile_marker_size = 12
        playback_speed = 1.0
        
        print(f"📱 Using default configuration:")
        print(f"   📐 Height: {mobile_height}px")
        print(f"   🔍 Zoom: {mobile_zoom}")
        print(f"   📏 Marker size: {mobile_marker_size}px")
        print(f"   ⚡ Playback speed: {playback_speed}x")
        
        # Get mobile performance mode from GUI setting (environment variable)
        perf_mode_env = os.environ.get('PERFORMANCE_MODE', '0')
        performance_enabled = perf_mode_env == '1'
        
        print(f"   🚀 Performance mode: {'Enabled' if performance_enabled else 'Disabled'}")
        
        # Set environment variables for consistency
        os.environ['PERFORMANCE_MODE'] = '1' if performance_enabled else '0'
        os.environ['PLAYBACK_SPEED'] = str(playback_speed)

        animation_engine = MobileAnimationEngine(
            mobile_height=mobile_height,
            mobile_zoom=mobile_zoom,
            mobile_marker_size=mobile_marker_size
        )
        
        # Load processed data
        animation_engine.load_processed_data(combined_data)
        
        # Create mobile visualization
        output_path = animation_engine.create_mobile_visualization()
        
        if output_path:
            # Display completion information
            mobile_ui.display_mobile_completion(output_path)
            
            # Show animation info
            info = animation_engine.get_animation_info()
            print("\n📊 Animation Details:")
            print(f"   📱 Total GPS points: {info['total_points']:,}")
            print(f"   🦅 Vultures tracked: {info['unique_vultures']}")
            print(f"   🎬 Animation frames: {info['animation_frames']:,}")
            print(f"   ⏱️ Time span: {info['time_span_hours']:.1f} hours")
            print(f"   📏 Marker size: {info['marker_size']}px (touch-friendly)")
            print(f"   📐 Height: {info['mobile_height']}px (mobile-optimized)")
            
            mobile_ui.ui.print_success("✅ Mobile animation completed successfully!")
            
            # Show completion popup if running in GUI mode
            if os.environ.get('GUI_MODE') == '1':
                show_mobile_completion_popup(output_path)
            
            return True
        else:
            mobile_ui.ui.print_error("Mobile visualization creation failed")
            return False
        
    except KeyboardInterrupt:
        mobile_ui.ui.print_warning("\n⚠️ Operation interrupted by user")
        return False
    except Exception as e:
        mobile_ui.ui.print_error(f"Mobile animation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

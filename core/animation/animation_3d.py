"""
3D Animation - Main Script

Entry point for 3D GPS visualization with real terrain data.
Uses modular architecture with downloadable elevation models.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.gps_utils import DataLoader, ensure_output_directories
from utils.user_interface import UserInterface
from utils.performance_optimizer import PerformanceOptimizer
from core.data.elevation_data_manager import ElevationDataManager
from core.animation.animation_3d_engine import Animation3DEngine
import pandas as pd
import os
import tkinter as tk
from tkinter import messagebox
import platform
import subprocess
import webbrowser


def _parse_time_step_from_gui(time_step_str: str) -> int:
    """Parse time step from GUI format to seconds"""
    time_step_str = time_step_str.lower().strip()
    
    # Handle different GUI formats
    if time_step_str.endswith('seconds') or time_step_str.endswith('second'):
        return int(time_step_str.split()[0])
    elif time_step_str.endswith('minutes') or time_step_str.endswith('minute'):
        return int(time_step_str.split()[0]) * 60
    elif time_step_str.endswith('hours') or time_step_str.endswith('hour'):
        return int(time_step_str.split()[0]) * 3600
    elif time_step_str.endswith('s'):
        return int(time_step_str[:-1])
    elif time_step_str.endswith('m'):
        return int(time_step_str[:-1]) * 60
    elif time_step_str.endswith('h'):
        return int(time_step_str[:-1]) * 3600
    else:
        # Default to seconds if no unit specified
        return int(time_step_str)


def show_3d_completion_popup(output_path):
    """Show a completion popup with options to open folder and HTML file"""
    try:
        # Create popup dialog
        root = tk.Tk()
        root.title("3D Animation Complete")
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
        tk.Label(main_frame, text="3D Animation Created Successfully!", 
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
    """Main 3D animation workflow"""
    ui = UserInterface()
    
    try:
        # Initialize system
        ui.print_header("🏔️ 3D GPS VISUALIZATION WITH REAL TERRAIN", 80)
        ensure_output_directories()
        
        # Load GPS data
        ui.print_section("📁 LOADING GPS DATA")
        
        # Use custom data directory from GUI if available
        custom_data_dir = os.environ.get('GPS_DATA_DIR')
        if custom_data_dir and os.path.exists(custom_data_dir):
            data_loader = DataLoader(custom_data_dir)
            ui.print_success(f"Using GUI data directory: {custom_data_dir}")
        else:
            data_loader = DataLoader()
            
        dataframes = data_loader.load_all_csv_files()
        
        if not dataframes:
            ui.print_error("No GPS data found!")
            return False
        
        print(f"Loaded {len(dataframes)} GPS data files")
        
        # Initialize components
        elevation_manager = ElevationDataManager()
        animation_engine = Animation3DEngine(elevation_manager)
        
        # Check for GUI environment variables
        terrain_quality_env = os.environ.get('TERRAIN_QUALITY', '100')
        time_step_env = os.environ.get('TIME_STEP')
        show_elevation_env = os.environ.get('SHOW_ELEVATION', 'true')
        show_markers_env = os.environ.get('SHOW_MARKERS', 'true')
        playback_speed_env = os.environ.get('PLAYBACK_SPEED', '1.0')
        
        # Configure playback speed
        try:
            playback_speed = float(playback_speed_env)
            animation_engine.set_playback_speed(playback_speed)
        except Exception:
            ui.print_warning(f"Invalid playback speed: {playback_speed_env}, using default 1.0x")
            animation_engine.set_playback_speed(1.0)
        
        # Show available regions and get user choice
        ui.print_section("🗺️ TERRAIN REGION SELECTION")
        elevation_manager.list_available_regions()
        
        # Get region selection - use default for GUI mode
        if os.environ.get('OUTPUT_DIR'):  # GUI mode
            region_choice = "berchtesgaden_full"  # Default recommended region for GUI
            ui.print_success(f"Using default region for GUI mode: {region_choice}")
        else:
            # Get region selection from user
            region_choice = ui.get_user_input(
                "Select region (berchtesgaden_full recommended)", 
                "berchtesgaden_full", 
                str
            )
        
        # Get terrain resolution - use GUI value if available
        try:
            terrain_quality_str = terrain_quality_env.lower()
            # Convert quality string to resolution number
            if terrain_quality_str == "low":
                resolution_choice = 150
            elif terrain_quality_str == "medium":
                resolution_choice = 100
            elif terrain_quality_str == "high":
                resolution_choice = 50
            else:
                resolution_choice = int(terrain_quality_env)
            ui.print_success(f"Using GUI terrain quality: {terrain_quality_str} ({resolution_choice})")
        except (ValueError, TypeError):
            resolution_choice = 100  # Default to medium quality
            ui.print_success(f"Using default terrain quality: medium ({resolution_choice})")
        
        if resolution_choice < 20 or resolution_choice > 200:
            ui.print_warning("Resolution should be between 20-200, using 100")
            resolution_choice = 100
        
        # Setup terrain data
        terrain_success = animation_engine.setup_terrain(
            region_name=region_choice,
            resolution=resolution_choice,
            force_download=False
        )
        
        if not terrain_success:
            ui.print_error("Failed to setup terrain data")
            return False
        
        # Get performance optimization for GPS data
        ui.print_section("⚡ GPS DATA OPTIMIZATION")
        optimizer = PerformanceOptimizer()
        
        # Use GUI time step if available
        if time_step_env:
            try:
                # Convert from GUI format (e.g., "5 minutes") to seconds
                time_step = _parse_time_step_from_gui(time_step_env)
                ui.print_success(f"Using GUI time step: {time_step_env} ({time_step}s)")
            except Exception:
                ui.print_warning(f"Invalid time step from GUI: {time_step_env}, falling back to manual selection")
                time_step = 120  # Default to 2 minutes
                ui.print_success(f"Using default time step: 2 minutes ({time_step}s)")
        else:
            time_step = 120  # Default to 2 minutes
            ui.print_success(f"Using default time step: 2 minutes ({time_step}s)")
        
        # Process GPS data
        ui.print_section("🔄 PROCESSING GPS DATA")
        processed_dataframes = []
        
        for i, df in enumerate(dataframes):
            print(f"   📊 Processing file {i+1}/{len(dataframes)}...")
            
            # Apply time step filtering
            filtered_df = optimizer.filter_by_time_step(df, time_step)
            
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
            ui.print_error("No data remaining after filtering!")
            return False
        
        # Combine processed data
        combined_data = pd.concat(processed_dataframes, ignore_index=True)
        print(f"📊 Total GPS points for 3D visualization: {len(combined_data):,}")
        
        # Load data into animation engine
        animation_engine.load_processed_data(combined_data)
        
        # Get animation type choice - default to static for GUI
        if os.environ.get('OUTPUT_DIR'):  # GUI mode
            animation_type = 'static'  # Default for GUI usage
            ui.print_success("Using static 3D paths for GUI mode")
        else:
            animation_type = 'full'  # Default to full animation for independent testing
            ui.print_success("Using full 3D animation for independent testing")
        
        # Create 3D visualization
        output_path = animation_engine.create_3d_visualization(animation_type)
        
        if output_path:
            # Display completion information
            ui.print_section("✅ 3D VISUALIZATION COMPLETE")
            
            # Show detailed information
            info = animation_engine.get_3d_info()
            print("📊 3D Visualization Details:")
            print(f"   🏔️ Terrain: {info.get('terrain_region', 'N/A')}")
            print(f"   📐 Terrain resolution: {info.get('terrain_resolution', 'N/A')}")
            print(f"   🗻 Terrain elevation: {info.get('terrain_elevation_range', 'N/A')}")
            print(f"   📏 Terrain area: {info.get('terrain_area_km2', 0):.1f} km²")
            print(f"   📱 GPS points: {info.get('total_points', 0):,}")
            print(f"   🦅 Vultures: {info.get('unique_vultures', 0)}")
            print(f"   ⏱️ Time span: {info.get('time_span_hours', 0):.1f} hours")
            print(f"   🎬 Animation type: {animation_type}")
            print(f"   💾 Output: {output_path}")
            
            ui.print_success("🏔️ 3D terrain visualization ready!")
            
            # Show completion popup if running in GUI mode
            if os.environ.get('GUI_MODE') == '1':
                show_3d_completion_popup(output_path)
            
            return True
        else:
            ui.print_error("3D visualization creation failed")
            return False
    
    except KeyboardInterrupt:
        ui.print_warning("\n⚠️ Operation interrupted by user")
        return False
    except Exception as e:
        ui.print_error(f"3D animation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Launch Manager for GPS Animation Suite
Handles launching different animation modes with proper configuration
"""

import os
import subprocess
import sys


class AnimationLauncher:
    """Manages launching of different animation scripts with configuration"""
    
    def __init__(self, get_language_func):
        self.get_language = get_language_func
        
    def launch_selected_mode(self, mode_manager, folder_manager, settings_manager, status_callback=None):
        """Launch based on selected mode"""
        try:
            mode_key = mode_manager.get_selected_mode_key()
            mode_info = mode_manager.get_selected_mode_info()
            
            if status_callback:
                status_callback(f"Launching {mode_info['name']}...")
            
            if mode_key == "2d_live_map":
                # Use existing LaunchManager for 2D maps
                try:
                    from components.launch_manager import LaunchManager
                    launch_manager = LaunchManager(self.get_language)
                    result = launch_manager.launch_map(folder_manager, settings_manager)
                    status = "2D Live Map launched!" if result else "2D Live Map launch failed"
                except ImportError:
                    result = self.launch_script(mode_info['script'], folder_manager, settings_manager)
                    status = f"{mode_info['name']} launched!" if result else f"{mode_info['name']} launch failed"
            else:
                # For mobile_animation and 3d_animation
                result = self.launch_script(mode_info['script'], folder_manager, settings_manager)
                status = f"{mode_info['name']} launched!" if result else f"{mode_info['name']} launch failed"
            
            if status_callback:
                status_callback(status)
            
            return result
            
        except Exception as e:
            print(f"Launch error: {e}")
            if status_callback:
                status_callback(f"Launch error: {str(e)}")
            return False
    
    def launch_script(self, script_name, folder_manager, settings_manager):
        """Launch a script with proper configuration"""
        try:
            # Validate folders first
            issues = folder_manager.validate_folders()
            if issues:
                print(f"Folder validation issues: {issues}")
                return False
            
            # Get configuration
            config = settings_manager.get_config()
            data_folder = folder_manager.get_data_folder()
            output_folder = folder_manager.get_output_folder()
            
            script_path = os.path.join("scripts", script_name)
            # Check if script exists in scripts directory, otherwise try core/animation
            if not os.path.exists(script_path):
                script_path = os.path.join("core", "animation", script_name)
            
            if os.path.exists(script_path):
                print(f"Launching {script_path} with configuration:")
                print(f"  Data folder: {data_folder}")
                print(f"  Output folder: {output_folder}")
                print(f"  Trail length: {config['trail_length']} hours")
                print(f"  Time step: {config['time_step']}")
                print(f"  Performance mode: {config['performance_mode']}")
                print(f"  Online map mode: {config.get('online_map_mode', True)}")
                
                # Set environment variables for configuration
                env = os.environ.copy()
                env['GPS_DATA_DIR'] = data_folder
                env['OUTPUT_DIR'] = output_folder
                env['TRAIL_LENGTH_HOURS'] = str(config['trail_length'])
                env['TIME_STEP'] = config['time_step']
                env['PLAYBACK_SPEED'] = str(config.get('playback_speed', 1.0))
                env['PERFORMANCE_MODE'] = '1' if config['performance_mode'] else '0'
                env['EXPORT_MP4'] = '1' if config.get('export_mp4', False) else '0'
                print(f"  Setting EXPORT_MP4={env['EXPORT_MP4']}")
                env['ONLINE_MAP_MODE'] = '1' if config.get('online_map_mode', True) else '0'
                print(f"  Setting ONLINE_MAP_MODE={env['ONLINE_MAP_MODE']}")
                env['ENABLE_PRECIPITATION'] = '1' if config.get('enable_precipitation', False) else '0'
                print(f"  Setting ENABLE_PRECIPITATION={env['ENABLE_PRECIPITATION']}")
                env['GUI_MODE'] = '1'  # Indicate we're running from GUI
                # Include optional animation time range if provided by settings_manager
                # SettingsManager may expose them as attributes or the config may include them.
                start_time = None
                end_time = None
                try:
                    # Prefer explicit attributes if present
                    if hasattr(settings_manager, 'animation_start_time'):
                        start_time = getattr(settings_manager, 'animation_start_time')
                    if hasattr(settings_manager, 'animation_end_time'):
                        end_time = getattr(settings_manager, 'animation_end_time')
                except Exception:
                    start_time = None
                    end_time = None

                # Fallback to config dict
                if start_time is None:
                    start_time = config.get('animation_start_time') if isinstance(config, dict) else None
                if end_time is None:
                    end_time = config.get('animation_end_time') if isinstance(config, dict) else None

                if start_time:
                    env['ANIMATION_START_TIME'] = str(start_time)
                if end_time:
                    env['ANIMATION_END_TIME'] = str(end_time)
                
                # Launch the script with environment variables
                subprocess.Popen([sys.executable, script_path], env=env)
                return True
            else:
                print(f"Script not found: {script_path}")
                return False
        except Exception as e:
            print(f"Error launching script: {e}")
            return False

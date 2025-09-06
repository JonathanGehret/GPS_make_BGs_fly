from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, List

import pandas as pd
import plotly.express as px

from utils.user_interface import UserInterface
from utils.performance_optimizer import PerformanceOptimizer
from utils.html_injection import inject_fullscreen
from utils.animation_builders import (
    build_color_map,
    create_base_figure,
    apply_standard_layout,
    apply_controls_and_slider,
    attach_frames,
)
from core.data.trail_system import TrailSystem
from core.gps_utils import (
    get_numbered_output_path,
    ensure_output_directories,
    logger,
    DataLoader,
    VisualizationHelper,
)
from core.export.video_export import export_animation_video
from core.export.browser_video_export import export_animation_video_browser
from utils.lod import LODConfig, apply_lod
from utils.offline_tiles import ensure_offline_style_for_bounds


class LiveMapAnimator:
    """Orchestrates the live map animation workflow."""

    def __init__(self):
        self.ui = UserInterface()

        # Use custom data directory from GUI if available
        custom_data_dir = os.environ.get('GPS_DATA_DIR')
        if custom_data_dir and os.path.exists(custom_data_dir):
            self.data_loader = DataLoader(custom_data_dir)
            self.ui.print_success(f"Using GUI data directory: {custom_data_dir}")
        else:
            self.data_loader = DataLoader()

        self.optimizer = PerformanceOptimizer()
        self.viz_helper = VisualizationHelper()
        self.trail_system = TrailSystem(self.ui)

        # Configuration
        self.selected_time_step: Optional[int] = None
        self.dataframes: List[pd.DataFrame] = []
        self.combined_data: Optional[pd.DataFrame] = None
        self.base_animation_speed = 800  # ms per frame at 1x speed for 2D maps
        self.playback_speed = 1.0
        self.performance_mode = os.environ.get('PERFORMANCE_MODE', '0') == '1'
        self.export_mp4 = os.environ.get('EXPORT_MP4', '0') == '1'
        self.export_mp4_browser = os.environ.get('EXPORT_MP4_BROWSER', '0') == '1'
        # Check GUI online map mode setting first (takes precedence)
        online_gui = os.environ.get('ONLINE_MAP_MODE')
        if online_gui:
            # ONLINE_MAP_MODE='1' means online (checkbox checked), so offline_map = False
            # ONLINE_MAP_MODE='0' means offline (checkbox unchecked), so offline_map = True
            self.offline_map = online_gui.lower() in ('0', 'false', 'no')
            print(f"🗺️ GUI map mode: ONLINE_MAP_MODE={online_gui}, offline_map={self.offline_map}")
        else:
            # Fall back to legacy environment variables if GUI setting not present
            self.offline_map = os.environ.get('OFFLINE_MAP', '0') == '1'
            # Also check GUI-specific offline map setting
            if not self.offline_map:
                offline_gui = os.environ.get('OFFLINE_MAP_GUI')
                if offline_gui and offline_gui.lower() in ('1', 'true', 'yes'):
                    self.offline_map = True
            print(f"🗺️ No ONLINE_MAP_MODE set, using legacy settings: offline_map={self.offline_map}")
        self.offline_map_download = os.environ.get('OFFLINE_MAP_DOWNLOAD', '1') == '1'
        self.tiles_dir = (
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'tiles_cache')
            if os.environ.get('TILES_DIR') is None
            else os.environ.get('TILES_DIR')
        )
        self.tile_server_url = os.environ.get('TILE_SERVER_URL', 'https://tile.openstreetmap.org/{z}/{x}/{y}.png')

        # Precipitation overlay settings
        self.enable_precipitation = os.environ.get('ENABLE_PRECIPITATION', '0') == '1'
        self.precipitation_cache = {}  # Cache for API responses

        # Read playback speed from environment if available (from GUI)
        playback_speed_env = os.environ.get('PLAYBACK_SPEED')
        if playback_speed_env:
            try:
                self.playback_speed = float(playback_speed_env)
                self.playback_speed = max(0.1, min(10.0, self.playback_speed))
                print(f"🎬 Using GUI playback speed: {self.playback_speed:.1f}x")
            except Exception:
                print(f"⚠️ Invalid playback speed from GUI: {playback_speed_env}, using default 1.0x")

    def set_playback_speed(self, speed_multiplier: float) -> None:
        self.playback_speed = max(0.1, min(10.0, speed_multiplier))
        print(f"🎬 2D Animation playback speed set to {self.playback_speed:.1f}x")

    def get_frame_duration(self) -> int:
        return max(50, int(self.base_animation_speed / self.playback_speed))

    def fetch_precipitation_data(self, lat: float, lon: float, start_date: str, end_date: str) -> dict:
        """Fetch hourly precipitation data from Open-Meteo API"""
        import requests
        
        cache_key = f"{lat:.4f}_{lon:.4f}_{start_date}_{end_date}"
        if cache_key in self.precipitation_cache:
            return self.precipitation_cache[cache_key]
        
        try:
            # Use past_days parameter for historical data
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                "&hourly=precipitation"
                "&timezone=Europe/Berlin"
                "&past_days=7"  # Get last 7 days of data
            )
            
            self.ui.print_info(f"🌧️ Fetching precipitation data for {lat:.4f}, {lon:.4f}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.precipitation_cache[cache_key] = data
            return data
            
        except Exception as e:
            self.ui.print_warning(f"Failed to fetch precipitation data: {e}")
            return None

    def get_precipitation_for_timestamp(self, data: dict, timestamp: pd.Timestamp) -> float:
        """Get precipitation value for a specific timestamp"""
        if not data or 'hourly' not in data:
            return 0.0
        
        times = data['hourly'].get('time', [])
        precipitations = data['hourly'].get('precipitation', [])
        
        if not times or not precipitations:
            return 0.0
        
        # Find the closest hour
        target_time = timestamp.replace(minute=0, second=0, microsecond=0)
        target_str = target_time.strftime('%Y-%m-%dT%H:%M')
        
        for i, time_str in enumerate(times):
            if time_str.startswith(target_str):
                return precipitations[i]
        
        return 0.0

    def _parse_time_step_from_gui(self, time_step_str: str) -> int:
        s = time_step_str.lower().strip()
        if s.endswith('seconds') or s.endswith('second'):
            return int(s.split()[0])
        elif s.endswith('minutes') or s.endswith('minute'):
            return int(s.split()[0]) * 60
        elif s.endswith('hours') or s.endswith('hour'):
            return int(s.split()[0]) * 3600
        elif s.endswith('s'):
            return int(s[:-1])
        elif s.endswith('m'):
            return int(s[:-1]) * 60
        elif s.endswith('h'):
            return int(s[:-1]) * 3600
        else:
            return int(s)

    def run(self) -> bool:
        try:
            self.ui.print_header("🦅 BEARDED VULTURE GPS VISUALIZATION", 80)
            print("Live Map Animation with Performance Optimization")
            if self.enable_precipitation:
                print("🌧️ Precipitation overlay enabled - fetching weather data from Open-Meteo")
            print()
            if self.performance_mode:
                self.ui.print_success("Performance mode: ON (line+head + adaptive LOD)")
            else:
                self.ui.print_info("Performance mode: OFF (fading markers)")
            if self.export_mp4 or self.export_mp4_browser:
                mode = "Browser" if (self.export_mp4_browser or self.offline_map) else "Offline"
                self.ui.print_info(f"Video export enabled ({mode}): MP4 will be created")

            # Ask user about offline map capability
            if not self.offline_map:  # Only ask if not already set via environment
                # Check if we're running in GUI mode (no stdin available)
                import sys
                is_gui_mode = not sys.stdin.isatty() or os.environ.get('GUI_MODE') == '1'
                
                if is_gui_mode:
                    # In GUI mode, don't ask - use the setting from environment
                    print(f"🗺️ GUI mode detected - using {'offline' if self.offline_map else 'online'} maps")
                else:
                    # CLI mode - ask for user input
                    self.ui.print_section("🗺️ MAP CONFIGURATION")
                    print("Choose map mode:")
                    print("1. Online maps (default - requires internet connection)")
                    print("2. Offline maps (downloads tiles for offline viewing)")
                    print()
                    while True:
                        try:
                            choice = input("Enter your choice (1 or 2): ").strip()
                            if choice == "1":
                                self.offline_map = False
                                break
                            elif choice == "2":
                                self.offline_map = True
                                self.ui.print_success("Offline map mode enabled - tiles will be downloaded")
                                break
                            else:
                                print("Please enter 1 or 2.")
                        except (EOFError, KeyboardInterrupt):
                            # Handle cases where input is not available
                            print("Input not available, using online maps (default)")
                            self.offline_map = False
                            break

            # Data analysis
            if not self.analyze_data():
                return False
            if not self.configure_performance():
                return False
            if not self.configure_trail_system():
                return False
            if not self.process_data():
                return False
            if not self.create_visualization():
                return False

            self.show_completion_summary()
            return True
        except KeyboardInterrupt:
            self.ui.print_info("\nOperation cancelled by user")
            return False
        except Exception as e:
            self.ui.print_error(f"Unexpected error: {e}")
            logger.exception("Unexpected error in main workflow")
            return False

    def analyze_data(self) -> bool:
        self.ui.print_section("📊 DATA ANALYSIS")
        try:
            csv_files = self.data_loader.find_csv_files()
            if not csv_files:
                self.ui.print_error("No CSV files found in data directory!")
                self.ui.print_info("Please add GPS data files to the 'data/' folder")
                return False
            total_points = 0
            print(f"Found {len(csv_files)} GPS data file(s):")

            # Check for an optional time window to limit data (set by GUI)
            time_window_start = os.environ.get('TIME_WINDOW_START')
            time_window_end = os.environ.get('TIME_WINDOW_END')
            start_ts = None
            end_ts = None
            if time_window_start:
                try:
                    start_ts = pd.to_datetime(time_window_start, utc=True)
                    self.ui.print_info(f"Applying time window start: {start_ts.isoformat()}")
                except Exception:
                    self.ui.print_warning(f"Invalid TIME_WINDOW_START: {time_window_start}")
            if time_window_end:
                try:
                    end_ts = pd.to_datetime(time_window_end, utc=True)
                    self.ui.print_info(f"Applying time window end: {end_ts.isoformat()}")
                except Exception:
                    self.ui.print_warning(f"Invalid TIME_WINDOW_END: {time_window_end}")

            for i, csv_file in enumerate(csv_files, 1):
                try:
                    df = self.data_loader.load_single_csv(csv_file)
                    if df is not None:
                        # If a time window was provided, attempt to filter by the Timestamp [UTC] column
                        if (start_ts is not None) or (end_ts is not None):
                            if 'Timestamp [UTC]' in df.columns:
                                try:
                                    ts = pd.to_datetime(df['Timestamp [UTC]'], utc=True)
                                    df['Timestamp [UTC]'] = ts
                                    mask = pd.Series(True, index=df.index)
                                    if start_ts is not None:
                                        mask &= ts >= start_ts
                                    if end_ts is not None:
                                        mask &= ts <= end_ts
                                    df = df[mask]
                                except Exception:
                                    self.ui.print_warning(f"Could not apply time window filter to {Path(csv_file).name}")
                            else:
                                self.ui.print_warning(f"No 'Timestamp [UTC]' column to filter in {Path(csv_file).name}")

                        points = len(df)
                        total_points += points
                        print(f"    {i}. {Path(csv_file).name:<25} ({points:4d} GPS points)")
                        self.dataframes.append(df)
                except Exception as e:
                    self.ui.print_warning(f"Could not analyze {Path(csv_file).name}: {e}")
            if not self.dataframes:
                self.ui.print_error("No valid GPS data found!")
                return False
            print(f"\n📈 Total GPS points available: {total_points}")
            return True
        except Exception as e:
            self.ui.print_error(f"Failed to analyze data: {e}")
            return False

    def configure_performance(self) -> bool:
        time_step_env = os.environ.get('TIME_STEP')
        if time_step_env:
            try:
                self.selected_time_step = self._parse_time_step_from_gui(time_step_env)
                self.ui.print_success(f"Using GUI time step: {time_step_env} ({self.selected_time_step}s)")
                return True
            except Exception:
                self.ui.print_warning(f"Invalid time step from GUI: {time_step_env}, falling back to manual selection")
        self.ui.print_info("Using default 1 minute time step for testing")
        self.selected_time_step = 60
        return True

    def configure_trail_system(self) -> bool:
        try:
            trail_length = self.trail_system.select_trail_length()
            if trail_length is False:
                return False
            self.trail_system.trail_length_minutes = trail_length
            return True
        except Exception as e:
            self.ui.print_error(f"Failed to configure trail system: {e}")
            return False

    def process_data(self) -> bool:
        self.ui.print_section("🔄 DATA PROCESSING")
        print(f"Applying {self.selected_time_step/60:.1f} minute time step filter...")
        print()
        try:
            processed: List[pd.DataFrame] = []
            for i, df in enumerate(self.dataframes):
                filename = df['source_file'].iloc[0] if 'source_file' in df.columns else f"File {i+1}"
                print(f"   📁 Processing {filename}...")
                original_count = len(df)
                filtered_df = self.optimizer.filter_by_time_step(df, self.selected_time_step)
                filtered_count = len(filtered_df)
                if filtered_count == 0:
                    self.ui.print_warning(f"No data points remain after filtering {filename}")
                    continue
                reduction = ((original_count - filtered_count) / original_count * 100) if original_count > 0 else 0
                print(f"   ✅ Filtered: {original_count} → {filtered_count} points ({reduction:.1f}% reduction)")
                filtered_df = filtered_df.copy()
                filtered_df['color'] = px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)]
                
                # Add precipitation data if enabled
                if self.enable_precipitation:
                    print(f"   🌧️ Adding precipitation data for {filename}...")
                    filtered_df = self._add_precipitation_data(filtered_df)
                
                processed.append(filtered_df)
            if not processed:
                self.ui.print_error("No data remained after processing!")
                return False
            self.combined_data = pd.concat(processed, ignore_index=True)
            total_points = len(self.combined_data)
            rating = self.optimizer.get_performance_rating(total_points)
            print(f"\n✅ Total processed data points: {total_points}")
            print(f"⚡ Expected performance: {rating}")
            return True
        except Exception as e:
            self.ui.print_error(f"Failed to process data: {e}")
            return False

    def _add_precipitation_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add precipitation data to the dataframe"""
        if df.empty:
            return df
        
        # Get date range for API call
        start_date = df['Timestamp [UTC]'].min().strftime('%Y-%m-%d')
        end_date = df['Timestamp [UTC]'].max().strftime('%Y-%m-%d')
        
        # Get unique coordinates (to minimize API calls)
        coords = df[['Latitude', 'Longitude']].drop_duplicates()
        
        # Fetch precipitation data for each unique coordinate
        precipitation_data = {}
        for _, row in coords.iterrows():
            lat, lon = row['Latitude'], row['Longitude']
            data = self.fetch_precipitation_data(lat, lon, start_date, end_date)
            if data:
                precipitation_data[(lat, lon)] = data
        
        # Add precipitation column
        df = df.copy()
        df['precipitation_mm'] = 0.0
        
        # Match each point to precipitation data
        for idx, row in df.iterrows():
            lat, lon = row['Latitude'], row['Longitude']
            timestamp = row['Timestamp [UTC]']
            
            coord_key = (lat, lon)
            if coord_key in precipitation_data:
                precip = self.get_precipitation_for_timestamp(precipitation_data[coord_key], timestamp)
                df.at[idx, 'precipitation_mm'] = precip
        
        return df

    def create_visualization(self, base_name: str = 'live_map_animation') -> bool:
        if self.combined_data is None or len(self.combined_data) == 0:
            return False
        self.ui.print_section("🎬 VISUALIZATION CREATION")
        print("Creating interactive live map animation...")
        try:
            df = self.combined_data.copy()
            df['timestamp_str'] = df['Timestamp [UTC]'].dt.strftime('%d.%m.%Y %H:%M:%S')
            df['timestamp_display'] = df['Timestamp [UTC]'].dt.strftime('%d.%m %H:%M')
            df = df.sort_values('Timestamp [UTC]')
            vulture_ids = df['vulture_id'].unique()
            color_map = build_color_map(vulture_ids)
            map_cfg = self.viz_helper.calculate_map_bounds(df, padding_percent=0.1)
            center_lat = map_cfg['center']['lat']
            center_lon = map_cfg['center']['lon']
            zoom_level = map_cfg['zoom']
            lat_min, lat_max = df['Latitude'].min(), df['Latitude'].max()
            lon_min, lon_max = df['Longitude'].min(), df['Longitude'].max()
            strategy = "line_head" if self.performance_mode else "markers_fade"
            fig = create_base_figure(vulture_ids, color_map, strategy=strategy)
            unique_times = sorted(df['timestamp_str'].unique())
            full_df_for_video = df.copy()
            if self.performance_mode:
                lod_cfg = LODConfig(
                    max_points_per_track=20_000,
                    target_points_per_min=600,
                    rdp_epsilon_meters=5.0,
                    use_rdp=True,
                )
                per_vulture = []
                for vid in vulture_ids:
                    seg = df[df['vulture_id'] == vid].copy()
                    if len(seg) > lod_cfg.max_points_per_track:
                        seg = apply_lod(seg, 'Timestamp [UTC]', 'Latitude', 'Longitude', lod_cfg)
                        seg['timestamp_str'] = seg['Timestamp [UTC]'].dt.strftime('%d.%m.%Y %H:%M:%S')
                        seg['timestamp_display'] = seg['Timestamp [UTC]'].dt.strftime('%d.%m %H:%M')
                    per_vulture.append(seg)
                df = pd.concat(per_vulture, ignore_index=True)
                unique_times = sorted(df['timestamp_str'].unique())
            attach_frames(
                fig,
                trail_system=self.trail_system,
                df=df,
                vulture_ids=vulture_ids,
                color_map=color_map,
                unique_times=unique_times,
                enable_prominent_time_display=False,
                strategy=strategy,
            )
            map_style = "open-street-map"
            if self.offline_map:
                try:
                    map_style = ensure_offline_style_for_bounds(
                        lat_min=float(lat_min),
                        lat_max=float(lat_max),
                        lon_min=float(lon_min),
                        lon_max=float(lon_max),
                        zoom_level=zoom_level,
                        tiles_dir=self.tiles_dir,
                        download=self.offline_map_download,
                        zoom_pad=1,
                        tile_url_template=self.tile_server_url,
                        tiles_href="./tiles_cache" if os.path.isabs(self.tiles_dir) else self.tiles_dir,
                    )
                    print(f"🗺️ Using offline tiles from: {self.tiles_dir}")
                except Exception as te:
                    self.ui.print_warning(f"Offline map setup failed, using online tiles: {te}")
                    map_style = "open-street-map"
            apply_standard_layout(fig, center_lat=center_lat, center_lon=center_lon, zoom_level=zoom_level, map_style=map_style)
            apply_controls_and_slider(
                fig,
                unique_times=unique_times,
                frame_duration_ms=self.get_frame_duration(),
                center_lat=center_lat,
                center_lon=center_lon,
                zoom_level=zoom_level,
                include_speed_controls=True,
            )
            # Precipitation / rain radar feature removed per user request.
            filename = self.trail_system.get_output_filename(base_name=base_name, bird_names=list(vulture_ids))
            output_path = get_numbered_output_path(filename)
            config = {
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToAdd': [
                    'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'
                ],
                'modeBarButtonsToRemove': ['sendDataToCloud'],
                'responsive': False,
                'scrollZoom': True,
                'doubleClick': 'reset',
                'showTips': True,
            }
            html_string = fig.to_html(config=config)
            html_string = inject_fullscreen(html_string)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_string)
            if self.offline_map:
                try:
                    html_dir = os.path.dirname(output_path)
                    tiles_dst = os.path.join(html_dir, 'tiles_cache')
                    if not os.path.exists(tiles_dst):
                        import shutil
                        # Copy tiles to HTML directory for offline viewing
                        if os.path.exists(self.tiles_dir):
                            shutil.copytree(self.tiles_dir, tiles_dst, dirs_exist_ok=True)
                            self.ui.print_success(f"Offline tiles copied to: {tiles_dst}")
                        else:
                            self.ui.print_warning(f"Source tiles directory not found: {self.tiles_dir}")
                except Exception as ce:
                    self.ui.print_warning(f"Could not copy offline tiles next to HTML: {ce}")
            self.ui.print_success("✨ Interactive live map animation created with custom fullscreen support!")
            print(f"📁 Saved: {output_path}")
            print("🎯 Fullscreen: Click the '⛶ Fullscreen' button in the controls to view entire interface fullscreen")
            print("📱 Features: All controls, slider, and map included in fullscreen mode")
            if self.export_mp4 or self.export_mp4_browser:
                try:
                    # Use browser export for video export (to capture map tiles)
                    use_browser = self.export_mp4_browser or self.offline_map or self.export_mp4
                    if use_browser:
                        map_type = 'offline' if self.offline_map else 'online'
                        self.ui.print_info(f"Video export: Using browser capture (includes {map_type} map tiles)")
                        try:
                            mp4_path = export_animation_video_browser(
                                html_path=str(output_path),
                                out_basename=str(Path(output_path).with_suffix('')),
                                fps=30,
                                width=1280,
                                height=720,
                                quality_crf=20,
                                headless=True,
                            )
                            print(f"🎬 Wrote video (browser capture with tiles): {mp4_path}")
                        except Exception as be:
                            self.ui.print_warning(f"Browser video export failed, falling back to offline export: {be}")
                            fig_full = create_base_figure(vulture_ids, color_map, strategy="markers_fade")
                            full_times = sorted(full_df_for_video['timestamp_str'].unique())
                            attach_frames(
                                fig_full,
                                trail_system=self.trail_system,
                                df=full_df_for_video,
                                vulture_ids=vulture_ids,
                                color_map=color_map,
                                unique_times=full_times,
                                enable_prominent_time_display=False,
                                strategy="markers_fade",
                            )
                            mp4_path = export_animation_video(
                                fig_full,
                                str(Path(output_path).with_suffix('')),
                                fps=30,
                                width=1280,
                                height=720,
                                quality_crf=20,
                            )
                            print(f"🎬 Wrote video (offline fallback): {mp4_path}")
                    else:
                        self.ui.print_info("Video export: Using offline rendering (no map tiles)")
                        fig_full = create_base_figure(vulture_ids, color_map, strategy="markers_fade")
                        full_times = sorted(full_df_for_video['timestamp_str'].unique())
                        attach_frames(
                            fig_full,
                            trail_system=self.trail_system,
                            df=full_df_for_video,
                            vulture_ids=vulture_ids,
                            color_map=color_map,
                            unique_times=full_times,
                            enable_prominent_time_display=False,
                            strategy="markers_fade",
                        )
                        mp4_path = export_animation_video(
                            fig_full,
                            str(Path(output_path).with_suffix('')),
                            fps=30,
                            width=1280,
                            height=720,
                            quality_crf=20,
                        )
                        print(f"🎬 Wrote video: {mp4_path}")
                except Exception as ve:
                    self.ui.print_warning(f"Video export failed: {ve}")
            return True
        except Exception as e:
            self.ui.print_error(f"Error creating visualization: {str(e)}")
            return False

    def show_completion_summary(self):
        self.ui.print_section("🎉 COMPLETION SUMMARY")
        print("Your optimized GPS visualization is ready!")
        print()
        print("🎯 Features:")
        print("   • Fullscreen mode: Click ⛶ button in the top-right corner")
        print("   • Interactive controls: Pan, zoom, select, and reset view")
        print("   • Smooth animation: No jumping or layout shifts")
        print("   • Professional quality: Fixed layout and stable positioning")
        if self.offline_map:
            print("   • Offline capability: Map tiles downloaded for offline viewing")
        print()
        print("💡 Performance Tips:")
        print("   • Use larger time steps (10m+) for older computers")
        print("   • Use smaller time steps (1-2m) for detailed analysis")
        print("   • The visualization will load much faster now!")
        print()
        print("🎮 Controls:")
        print("   • ▶ Play/Pause: Control animation playback")
        print("   • ⛶ Fullscreen: Immersive viewing experience")
        print("   • 🖱️ Hover: Detailed information for each point")
        print("   • 🔍 Zoom/Pan: Navigate the map interactively")
        if self.offline_map:
            print()
            print("🗺️ Offline Usage:")
            print("   • Start local server: python3 -m http.server 8000")
            print("   • Open in browser: http://localhost:8000/[filename].html")
            print("   • No internet connection required for map viewing")


def run_live_map_cli() -> int:
    """Thin CLI wrapper for the LiveMapAnimator."""
    try:
        ensure_output_directories()
        animator = LiveMapAnimator()
        success = animator.run()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Critical error: {e}")
        logger.exception("Critical error in main")
        return 1

"""
Visualization Manager

Handles the creation and configuration of interactive map visualizations.
"""

from pathlib import Path
import pandas as pd

from utils.user_interface import UserInterface
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
    VisualizationHelper,
)
from core.export.video_export import export_animation_video
from core.export.browser_video_export import export_animation_video_browser
from utils.lod import LODConfig, apply_lod
from utils.offline_tiles import ensure_offline_style_for_bounds


class VisualizationManager:
    """Manages the creation and configuration of map visualizations."""

    def __init__(self, ui: UserInterface):
        self.ui = ui
        self.viz_helper = VisualizationHelper()

    def create_visualization(self, combined_data: pd.DataFrame, trail_system: TrailSystem,
                           enable_precipitation: bool, enable_precipitation_heatmap: bool,
                           offline_map: bool, tiles_dir: str, tile_server_url: str,
                           offline_map_download: bool, base_animation_speed: float,
                           playback_speed: float, performance_mode: bool,
                           export_mp4: bool, export_mp4_browser: bool,
                           base_name: str = 'live_map_animation') -> bool:

        if combined_data is None or len(combined_data) == 0:
            return False

        self.ui.print_section("🎬 VISUALIZATION CREATION")
        print("Creating interactive live map animation...")

        try:
            df = combined_data.copy()
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

            strategy = "line_head" if performance_mode else "markers_fade"
            fig = create_base_figure(vulture_ids, color_map, strategy=strategy)
            unique_times = sorted(df['timestamp_str'].unique())
            full_df_for_video = df.copy()

            if performance_mode:
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
                trail_system=trail_system,
                df=df,
                vulture_ids=vulture_ids,
                color_map=color_map,
                unique_times=unique_times,
                enable_prominent_time_display=False,
                strategy=strategy,
                enable_precipitation_overlay=enable_precipitation,
            )

            map_style = "open-street-map"
            if offline_map:
                try:
                    map_style = ensure_offline_style_for_bounds(
                        lat_min=float(lat_min),
                        lat_max=float(lat_max),
                        lon_min=float(lon_min),
                        lon_max=float(lon_max),
                        zoom_level=zoom_level,
                        tiles_dir=tiles_dir,
                        download=offline_map_download,
                        zoom_pad=1,
                        tile_url_template=tile_server_url,
                        tiles_href="./tiles_cache" if Path(tiles_dir).is_absolute() else tiles_dir,
                    )
                    print(f"🗺️ Using offline tiles from: {tiles_dir}")
                except Exception as te:
                    self.ui.print_warning(f"Offline map setup failed, using online tiles: {te}")
                    map_style = "open-street-map"

            apply_standard_layout(fig, center_lat=center_lat, center_lon=center_lon,
                                zoom_level=zoom_level, map_style=map_style)

            frame_duration_ms = max(50, int(base_animation_speed / playback_speed))
            apply_controls_and_slider(
                fig,
                unique_times=unique_times,
                frame_duration_ms=frame_duration_ms,
                center_lat=center_lat,
                center_lon=center_lon,
                zoom_level=zoom_level,
                include_speed_controls=True,
            )

            filename = trail_system.get_output_filename(base_name=base_name, bird_names=list(vulture_ids))
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

            if offline_map:
                try:
                    html_dir = Path(output_path).parent
                    tiles_dst = html_dir / 'tiles_cache'
                    if not tiles_dst.exists():
                        import shutil
                        if Path(tiles_dir).exists():
                            shutil.copytree(tiles_dir, tiles_dst, dirs_exist_ok=True)
                            self.ui.print_success(f"Offline tiles copied to: {tiles_dst}")
                        else:
                            self.ui.print_warning(f"Source tiles directory not found: {tiles_dir}")
                except Exception as ce:
                    self.ui.print_warning(f"Could not copy offline tiles next to HTML: {ce}")

            self.ui.print_success("✨ Interactive live map animation created with custom fullscreen support!")
            print(f"📁 Saved: {output_path}")
            print("🎯 Fullscreen: Click the '⛶ Fullscreen' button in the controls to view entire interface fullscreen")
            print("📱 Features: All controls, slider, and map included in fullscreen mode")

            if export_mp4 or export_mp4_browser:
                self._export_video(fig, full_df_for_video, vulture_ids, color_map, unique_times,
                                 trail_system, enable_precipitation, offline_map, export_mp4_browser,
                                 export_mp4, output_path)

            return True

        except Exception as e:
            self.ui.print_error(f"Error creating visualization: {str(e)}")
            return False

    def _export_video(self, fig, full_df_for_video, vulture_ids, color_map, unique_times,
                     trail_system, enable_precipitation, offline_map, export_mp4_browser,
                     export_mp4, output_path):
        """Handle video export functionality"""
        try:
            use_browser = export_mp4_browser or offline_map or export_mp4
            if use_browser:
                map_type = 'offline' if offline_map else 'online'
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
                    self._export_video_fallback(full_df_for_video, vulture_ids, color_map,
                                              unique_times, trail_system, enable_precipitation,
                                              output_path)
            else:
                self.ui.print_info("Video export: Using offline rendering (no map tiles)")
                self._export_video_fallback(full_df_for_video, vulture_ids, color_map,
                                          unique_times, trail_system, enable_precipitation,
                                          output_path)
        except Exception as ve:
            self.ui.print_warning(f"Video export failed: {ve}")

    def _export_video_fallback(self, full_df_for_video, vulture_ids, color_map, unique_times,
                              trail_system, enable_precipitation, output_path):
        """Fallback video export using offline rendering"""
        fig_full = create_base_figure(vulture_ids, color_map, strategy="markers_fade")
        full_times = sorted(full_df_for_video['timestamp_str'].unique())
        attach_frames(
            fig_full,
            trail_system=trail_system,
            df=full_df_for_video,
            vulture_ids=vulture_ids,
            color_map=color_map,
            unique_times=full_times,
            enable_prominent_time_display=False,
            strategy="markers_fade",
            enable_precipitation_overlay=enable_precipitation,
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

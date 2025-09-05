"""
3D User Interface Module

Specialized UI components for 3D GPS visualization with terrain data.
Extends base UserInterface with 3D-specific features.
"""

from utils.user_interface import UserInterface
from core.elevation_data_manager import ElevationDataManager


class UserInterface3D(UserInterface):
    """
    Extended user interface specifically for 3D visualization features.
    Provides terrain selection, 3D settings, and specialized prompts.
    """
    
    def __init__(self):
        super().__init__()
        self.elevation_manager = None
    
    def set_elevation_manager(self, elevation_manager: ElevationDataManager):
        """Set the elevation manager for terrain operations"""
        self.elevation_manager = elevation_manager
    
    def show_3d_welcome(self):
        """Display 3D-specific welcome message"""
        self.print_header("🏔️ 3D GPS VISUALIZATION WITH REAL TERRAIN", 80)
        print("This tool creates stunning 3D visualizations of GPS flight paths")
        print("overlaid on real elevation data from the Austrian Alps region.")
        print()
        print("Features:")
        print("  🗻 Real terrain elevation data")
        print("  💾 Intelligent terrain caching")
        print("  🎬 Interactive 3D animations")
        print("  📊 Multiple visualization modes")
        print("  🦅 Multi-vulture flight tracking")
        print()
    
    def get_terrain_region_choice(self) -> str:
        """
        Interactive terrain region selection with detailed information.
        
        Returns:
            str: Selected region name
        """
        self.print_section("🗺️ TERRAIN REGION SELECTION")
        
        if self.elevation_manager:
            regions = self.elevation_manager.list_available_regions()
            
            print("Available terrain regions:")
            print()
            
            region_info = {
                'berchtesgaden_full': {
                    'description': 'Complete Berchtesgaden area (recommended)',
                    'coverage': 'Berchtesgaden National Park + surrounding Alps',
                    'size': 'Large (30+ km²)',
                    'download_time': '2-5 minutes'
                },
                'berchtesgaden_core': {
                    'description': 'Core Berchtesgaden peaks',
                    'coverage': 'Central high peaks and valleys',
                    'size': 'Medium (15+ km²)',
                    'download_time': '1-3 minutes'
                },
                'tennengebirge': {
                    'description': 'Tennengebirge mountain range',
                    'coverage': 'Tennengebirge plateau and peaks',
                    'size': 'Large (25+ km²)',
                    'download_time': '2-4 minutes'
                },
                'salzburg_area': {
                    'description': 'Salzburg and Saalfelden region',
                    'coverage': 'Bischofshofen, Saalfelden surroundings',
                    'size': 'Large (40+ km²)',
                    'download_time': '3-6 minutes'
                }
            }
            
            for i, region in enumerate(regions, 1):
                info = region_info.get(region, {})
                print(f"  {i}. {region}")
                print(f"     📝 {info.get('description', 'No description')}")
                print(f"     🗺️ Coverage: {info.get('coverage', 'Unknown')}")
                print(f"     📏 Size: {info.get('size', 'Unknown')}")
                print(f"     ⏱️ Download time: {info.get('download_time', 'Unknown')}")
                print()
            
            # Get user choice
            while True:
                try:
                    choice = input("Select region number (or name): ").strip()
                    
                    # Try as number first
                    try:
                        region_num = int(choice)
                        if 1 <= region_num <= len(regions):
                            return regions[region_num - 1]
                    except ValueError:
                        pass
                    
                    # Try as region name
                    if choice in regions:
                        return choice
                    
                    # Try partial match
                    matches = [r for r in regions if choice.lower() in r.lower()]
                    if len(matches) == 1:
                        return matches[0]
                    
                    print(f"Invalid choice. Please select 1-{len(regions)} or region name.")
                    
                except KeyboardInterrupt:
                    raise
                except Exception:
                    print("Invalid input. Please try again.")
        else:
            # Fallback if no elevation manager
            return self.get_user_input(
                "Enter terrain region name", 
                "berchtesgaden_full", 
                str
            )
    
    def get_terrain_resolution(self) -> int:
        """
        Get terrain resolution with guidance on quality vs speed.
        
        Returns:
            int: Resolution value (grid points per dimension)
        """
        self.print_section("🔧 TERRAIN RESOLUTION SETTINGS")
        
        print("Terrain resolution affects visualization quality and download time:")
        print()
        print("  📊 Resolution Guide:")
        print("     50  - Fast download, basic terrain (30 seconds)")
        print("     100 - Good balance, recommended (1-2 minutes)")
        print("     150 - High detail, slower download (3-5 minutes)")
        print("     200 - Maximum detail, longest download (5+ minutes)")
        print()
        print("  💡 Tips:")
        print("     • Higher resolution = more detailed terrain")
        print("     • Lower resolution = faster processing")
        print("     • Resolution affects download time significantly")
        print()
        
        while True:
            try:
                resolution = self.get_user_input(
                    "Select resolution (50-200)", 
                    "100", 
                    int
                )
                
                if 20 <= resolution <= 300:
                    if resolution < 50:
                        self.print_warning("Very low resolution - terrain may look blocky")
                    elif resolution > 200:
                        self.print_warning("Very high resolution - download may take 10+ minutes")
                    
                    return resolution
                else:
                    print("Resolution must be between 20-300")
                    
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                raise
    
    def get_3d_animation_type(self) -> str:
        """
        Get animation type with detailed explanations.
        
        Returns:
            str: Animation type ('full' or 'static')
        """
        self.print_section("🎬 3D VISUALIZATION MODE")
        
        print("Choose your 3D visualization style:")
        print()
        print("  1. 🎮 Full Animation")
        print("     • Interactive time slider")
        print("     • Play/pause controls")
        print("     • Watch vultures move over terrain")
        print("     • Best for time-based analysis")
        print()
        print("  2. 📊 Static 3D View")
        print("     • All flight paths shown together")
        print("     • Faster rendering")
        print("     • Good for route comparison")
        print("     • Best for spatial analysis")
        print()
        
        while True:
            try:
                choice = self.get_user_input("Select mode (1 or 2)", "1", int)
                
                if choice == 1:
                    return 'full'
                elif choice == 2:
                    return 'static'
                else:
                    print("Please enter 1 or 2")
                    
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                raise
    
    def show_3d_progress(self, stage: str, details: str = ""):
        """Show 3D-specific progress updates"""
        stages = {
            'terrain_check': '🔍 Checking cached terrain data',
            'terrain_download': '⬇️ Downloading elevation data',
            'terrain_process': '🏔️ Processing terrain surface',
            'gps_process': '📱 Processing GPS coordinates',
            'render_3d': '🎨 Rendering 3D visualization',
            'save_output': '💾 Saving 3D visualization'
        }
        
        message = stages.get(stage, stage)
        if details:
            message += f" - {details}"
        
        print(f"   {message}")
    
    def show_3d_completion_info(self, info: dict, output_path: str):
        """Display comprehensive 3D completion information"""
        self.print_section("✅ 3D VISUALIZATION COMPLETE")
        
        print("📊 3D Visualization Summary:")
        print(f"   🏔️ Terrain Region: {info.get('terrain_region', 'N/A')}")
        print(f"   📐 Resolution: {info.get('terrain_resolution', 'N/A')} points")
        print(f"   🗻 Elevation Range: {info.get('terrain_elevation_range', 'N/A')}")
        print(f"   📏 Terrain Area: {info.get('terrain_area_km2', 0):.1f} km²")
        print(f"   📱 GPS Points: {info.get('total_points', 0):,}")
        print(f"   🦅 Vultures Tracked: {info.get('unique_vultures', 0)}")
        print(f"   ⏱️ Time Span: {info.get('time_span_hours', 0):.1f} hours")
        print(f"   🎬 Mode: {info.get('animation_type', 'N/A').title()}")
        print(f"   💾 Output File: {output_path}")
        print()
        
        self.show_3d_usage_tips()
    
    def show_3d_usage_tips(self):
        """Show tips for using 3D visualizations"""
        print("📋 3D Visualization Controls:")
        print("   🖱️ Mouse Controls:")
        print("      • Drag: Rotate 3D view")
        print("      • Scroll: Zoom in/out")
        print("      • Double-click: Reset view")
        print()
        print("   🎮 Interactive Features:")
        print("      • Hover over paths: View vulture details")
        print("      • Click terrain: Elevation information")
        print("      • Use time controls: Animate through time")
        print()
        print("   💡 Viewing Tips:")
        print("      • Start with overview, then zoom to areas of interest")
        print("      • Try different angles to see elevation changes")
        print("      • Use animation to follow individual vultures")
        print()
    
    def confirm_terrain_download(self, region: str, resolution: int, estimated_time: str) -> bool:
        """
        Confirm terrain download with time estimate.
        
        Args:
            region: Region name
            resolution: Resolution setting
            estimated_time: Estimated download time
            
        Returns:
            bool: True if user confirms download
        """
        print("📋 Download Summary:")
        print(f"   🗺️ Region: {region}")
        print(f"   📐 Resolution: {resolution} points")
        print(f"   ⏱️ Estimated time: {estimated_time}")
        print()
        
        return self.get_user_confirmation(
            "Proceed with terrain download?",
            default=True
        )

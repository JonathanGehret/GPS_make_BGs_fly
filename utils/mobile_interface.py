"""
Mobile User Interface Module

Provides mobile-optimized user interaction methods and display utilities
specifically designed for mobile GPS visualization workflows.
"""

from typing import Optional, Dict, Any
from utils.user_interface import UserInterface
from utils.performance_optimizer import PerformanceOptimizer


class MobileInterface:
    """Mobile-optimized user interface utilities"""
    
    def __init__(self):
        self.ui = UserInterface()
        self.optimizer = PerformanceOptimizer()
    
    def display_mobile_welcome(self) -> None:
        """Display mobile-optimized welcome screen"""
        self.ui.print_header("📱 VULTURE GPS - MOBILE OPTIMIZER", 60)
        print("Mobile-Optimized Flight Path Visualization")
        print()
        print("Mobile Features:")
        print("  📱 Touch-friendly controls")
        print("  🔍 Larger markers for easy selection")
        print("  ⚡ Optimized for mobile performance")
        print("  📊 Compact interface design")
        print()
    
    def display_mobile_performance_options(self, dataframes) -> Optional[int]:
        """
        Display mobile-optimized performance options
        
        Args:
            dataframes: List of GPS dataframes
            
        Returns:
            Selected time step in seconds, or None if cancelled
        """
        if not dataframes:
            return None
        
        self.ui.print_section("📱 MOBILE PERFORMANCE")
        print("Choose optimization level for mobile device:")
        print()
        
        # Get performance options using the optimizer
        options = self.optimizer.get_performance_options(dataframes)
        
        # Display mobile-optimized options
        for key, option in options.items():
            point_count = self.optimizer.estimate_final_points(dataframes, option["seconds"])
            emoji = self._get_mobile_performance_emoji(point_count)
            speed = self._get_mobile_speed_description(point_count)
            
            print(f"  {key}. {emoji} {option['name']}")
            print(f"     📊 ~{point_count:,} points | ⏱️ {option['seconds']}s steps")
            print(f"     📱 {speed}")
            print()
        
        print("  0. ⚡ Custom time step")
        print()
        
        return self._get_mobile_user_choice(options)
    
    def _get_mobile_performance_emoji(self, point_count: int) -> str:
        """Get mobile-appropriate emoji for point count"""
        if point_count <= 500:
            return "🚀"  # Ultra fast
        elif point_count <= 1500:
            return "⚡"  # Fast
        elif point_count <= 3000:
            return "📱"  # Mobile optimal
        elif point_count <= 5000:
            return "⚠️"   # Caution
        else:
            return "🐌"  # Slow
    
    def _get_mobile_speed_description(self, point_count: int) -> str:
        """Get mobile-specific speed description"""
        if point_count <= 500:
            return "Ultra smooth on all mobile devices"
        elif point_count <= 1500:
            return "Smooth on most mobile devices"
        elif point_count <= 3000:
            return "Good performance on modern phones"
        elif point_count <= 5000:
            return "May be slow on older phones"
        else:
            return "Recommended for desktop only"
    
    def _get_mobile_user_choice(self, options: Dict[str, Any]) -> Optional[int]:
        """
        Get user choice with mobile-friendly prompts
        
        Args:
            options: Available performance options
            
        Returns:
            Selected time step in seconds, or None if cancelled
        """
        while True:
            try:
                choice = input("📱 Select mobile optimization level (1-4, 0 for custom): ").strip()
                
                if not choice:
                    continue
                
                choice_num = int(choice)
                
                if choice_num == 0:
                    # Custom time step
                    custom_step = input("⏱️ Enter custom time step (seconds, recommended: 30-300): ").strip()
                    if custom_step:
                        custom_seconds = int(custom_step)
                        if 1 <= custom_seconds <= 3600:
                            return custom_seconds
                        else:
                            print("⚠️ Please enter a value between 1 and 3600 seconds")
                    continue
                
                elif 1 <= choice_num <= len(options):
                    selected = list(options.values())[choice_num - 1]
                    
                    # Show mobile performance preview
                    estimated_points = self.optimizer.estimate_final_points(
                        [], selected["seconds"]  # Will be calculated properly in main script
                    )
                    print(f"\n📱 Selected: {selected['name']}")
                    print(f"   ⚡ Performance: {self._get_mobile_speed_description(estimated_points)}")
                    
                    confirm = input("   ✅ Confirm selection? (y/N): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        return selected["seconds"]
                    
                else:
                    print("⚠️ Please select a number between 0-4")
                    
            except ValueError:
                print("⚠️ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n⚠️ Operation cancelled")
                return None
    
    def display_mobile_completion(self, output_path: str) -> None:
        """
        Display mobile-optimized completion message
        
        Args:
            output_path: Path to the generated visualization
        """
        self.ui.print_section("📱 MOBILE OPTIMIZATION COMPLETE")
        print("Mobile-optimized visualization created successfully!")
        print()
        print("📱 Mobile Features:")
        print("   🔍 Touch-friendly interface")
        print("   📊 Optimized performance")
        print(f"   💾 Saved to: {output_path}")
        print()
        print("📋 Mobile Usage Tips:")
        print("   • Use touch gestures to zoom and pan")
        print("   • Tap markers for vulture details")
        print("   • Use the play button to start animation")
        print("   • Pinch to zoom in/out")
        print()
        self.ui.print_success("Ready for mobile viewing! 📱")
    
    def get_mobile_input(self, prompt: str, default: str, value_type=str):
        """
        Mobile-friendly input with clear prompts
        
        Args:
            prompt: Input prompt message
            default: Default value
            value_type: Type conversion function
            
        Returns:
            User input converted to specified type
        """
        mobile_prompt = f"📱 {prompt} [{default}]: "
        return self.ui.get_user_input(mobile_prompt, default, value_type)

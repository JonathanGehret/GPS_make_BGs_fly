"""
Proximity Analysis - Main Script

Streamlined entry point for proximity analysis using modular architecture.
This script has been refactored from the original 832-line version to use
dedicated modules for better maintainability.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gps_utils import get_numbered_output_path, DataLoader
from utils.user_interface import UserInterface
from core.proximity_engine import ProximityEngine
from visualization.proximity_plots import ProximityVisualizer


def main():
    """Main proximity analysis workflow"""
    ui = UserInterface()
    
    # Initialize components
    ui.print_header("🔍 PROXIMITY ANALYSIS")
    
    try:
        # Load GPS data
        ui.print_section("📁 LOADING DATA")
        data_loader = DataLoader()
        dataframes = data_loader.load_all_csv_files()
        
        if not dataframes:
            ui.print_error("No GPS data found!")
            return False
        
        print(f"Loaded {len(dataframes)} GPS data files")
        
        # Initialize proximity engine
        proximity_engine = ProximityEngine()
        proximity_engine.load_dataframes(dataframes)
        
        # Configure analysis parameters
        print("\n⚙️  Configure proximity analysis:")
        proximity_threshold = ui.get_user_input(
            "Enter proximity threshold in kilometers", 
            "0.5", 
            float
        )
        time_threshold = ui.get_user_input(
            "Enter time threshold in minutes", 
            "5", 
            int
        )
        
        # Set parameters directly
        proximity_engine.proximity_threshold_km = proximity_threshold
        proximity_engine.min_duration_minutes = time_threshold
        
        # Run proximity analysis
        ui.print_section("🔍 ANALYZING PROXIMITY")
        events = proximity_engine.analyze_proximity()
        
        if not events:
            ui.print_warning("No proximity events found with current parameters")
            ui.print_info("Try increasing the proximity threshold or check your data")
            return True  # Still a successful run, just no events found
        
        ui.print_success(f"Found {len(events)} proximity events!")
        
        # Calculate statistics
        statistics = proximity_engine.calculate_statistics()
        
        # Create visualizations
        visualizer = ProximityVisualizer()
        visualizer.display_statistics(statistics)
        visualizer.create_all_visualizations(events, statistics)
        
        # Export results
        ui.print_section("💾 EXPORTING RESULTS")
        events_df = proximity_engine.get_events_dataframe()
        
        # Save events data
        output_path = get_numbered_output_path('proximity_events', 'analysis')
        # Change extension to CSV
        output_path = output_path.replace('.html', '.csv')
        events_df.to_csv(output_path, index=False)
        print(f"Events data saved to: {output_path}")
        
        ui.print_success("✅ Proximity analysis completed successfully!")
        return True
        
    except KeyboardInterrupt:
        ui.print_warning("\n⚠️  Analysis interrupted by user")
        return False
    except Exception as e:
        ui.print_error(f"Analysis failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

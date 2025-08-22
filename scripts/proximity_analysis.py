"""
Proximity Analysis - Main Script

Streamlined entry point for proximity analysis using modular architecture.
This script has been refactored from the original 832-line version to use
dedicated modules for better maintainability.
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gps_utils import get_numbered_output_path, DataLoader
from utils.user_interface import UserInterface
from core.proximity_engine import ProximityEngine
from visualization.proximity_plots import ProximityVisualizer
from animate_live_map import LiveMapAnimator


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
        
        # Ask user if they want to generate encounter maps
        print("\n🎬 Generate live map animations for proximity encounters?")
        print("This will create professional animated maps showing vulture interactions.")
        response = ui.get_user_input(
            "Generate encounter animations?", 
            "y/n", 
            str
        )
        
        generate_animations = response.lower().strip() in ['y', 'yes']
        
        if generate_animations:
            ui.print_section("🎬 CREATING ENCOUNTER ANIMATIONS")
            success = create_encounter_animations(events, proximity_engine.gps_data, ui)
            if not success:
                ui.print_warning("Encounter animation creation failed, continuing with standard analysis...")
        
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


def create_encounter_animations(events, gps_data, ui):
    """
    Create live map animations for proximity encounters
    
    Args:
        events: List of proximity events
        gps_data: Combined GPS data DataFrame
        ui: User interface for messaging
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Group events into encounters (events within 60 minutes of each other)
        encounters = group_proximity_events(events)
        
        if not encounters:
            ui.print_warning("No encounter groups found")
            return False
        
        ui.print_info(f"Found {len(encounters)} encounter group(s) to animate")
        
        # Get time buffer for animations
        print("\n⏱️  How much GPS data should be included around each encounter?")
        time_buffer = ui.get_user_input(
            "Time buffer in hours (before/after encounter)", 
            "1.0", 
            float
        )
        
        animated_count = 0
        
        for i, encounter in enumerate(encounters, 1):
            try:
                ui.print_info(f"Creating animation for encounter {i}/{len(encounters)}...")
                
                # Create encounter dataset
                encounter_data = create_encounter_dataset(
                    encounter, gps_data, time_buffer
                )
                
                if encounter_data is None or len(encounter_data) == 0:
                    ui.print_warning(f"No GPS data found for encounter {i}, skipping...")
                    continue
                
                # Create LiveMapAnimator with encounter data
                animator = LiveMapAnimator()
                animator.dataframes = encounter_data
                animator.combined_data = pd.concat(encounter_data, ignore_index=True)
                
                # Configure for encounter animation
                animator.selected_time_step = 30  # 30 second intervals for detail
                animator.trail_system.trail_length_minutes = 10  # 10 minute trails
                
                # Create the visualization
                success = animator.create_visualization()
                
                if success:
                    animated_count += 1
                    duration = encounter['duration_minutes']
                    vultures = ', '.join(encounter['vultures'])
                    ui.print_success(f"Encounter {i} animated: {vultures} ({duration:.1f} min)")
                else:
                    ui.print_warning(f"Failed to animate encounter {i}")
                    
            except Exception as e:
                ui.print_error(f"Error animating encounter {i}: {e}")
                continue
        
        if animated_count > 0:
            ui.print_success(f"Successfully created {animated_count} encounter animations!")
            return True
        else:
            ui.print_warning("No encounter animations were created")
            return False
            
    except Exception as e:
        ui.print_error(f"Encounter animation failed: {e}")
        return False


def group_proximity_events(events, gap_threshold_minutes=60):
    """
    Group proximity events into encounters based on time gaps
    
    Args:
        events: List of proximity events
        gap_threshold_minutes: Maximum gap between events to consider them part of same encounter
        
    Returns:
        List of encounter dictionaries
    """
    if not events:
        return []
    
    import pandas as pd
    
    # Convert events to DataFrame for easier processing
    events_data = []
    for event in events:
        events_data.append({
            'timestamp': event.timestamp,
            'vulture1': event.vulture1,
            'vulture2': event.vulture2,
            'distance_km': event.distance_km,
            'lat1': event.lat1,
            'lon1': event.lon1,
            'lat2': event.lat2,
            'lon2': event.lon2
        })
    
    events_df = pd.DataFrame(events_data)
    events_df = events_df.sort_values('timestamp')
    
    encounters = []
    current_encounter = None
    gap_threshold = pd.Timedelta(minutes=gap_threshold_minutes)
    
    for _, event in events_df.iterrows():
        if current_encounter is None:
            # Start new encounter
            current_encounter = {
                'start_time': event['timestamp'],
                'end_time': event['timestamp'],
                'events': [event.to_dict()],
                'vultures': set([event['vulture1'], event['vulture2']])
            }
        else:
            # Check if this event is close enough to the current encounter
            time_gap = event['timestamp'] - current_encounter['end_time']
            
            if time_gap <= gap_threshold:
                # Add to current encounter
                current_encounter['end_time'] = event['timestamp']
                current_encounter['events'].append(event.to_dict())
                current_encounter['vultures'].update([event['vulture1'], event['vulture2']])
            else:
                # Finish current encounter and start new one
                current_encounter['vultures'] = list(current_encounter['vultures'])
                current_encounter['duration_minutes'] = (
                    current_encounter['end_time'] - current_encounter['start_time']
                ).total_seconds() / 60
                current_encounter['num_events'] = len(current_encounter['events'])
                
                # Calculate center point
                lats = [e['lat1'] for e in current_encounter['events']] + [e['lat2'] for e in current_encounter['events']]
                lons = [e['lon1'] for e in current_encounter['events']] + [e['lon2'] for e in current_encounter['events']]
                current_encounter['center_lat'] = sum(lats) / len(lats)
                current_encounter['center_lon'] = sum(lons) / len(lons)
                
                encounters.append(current_encounter)
                
                # Start new encounter
                current_encounter = {
                    'start_time': event['timestamp'],
                    'end_time': event['timestamp'],
                    'events': [event.to_dict()],
                    'vultures': set([event['vulture1'], event['vulture2']])
                }
    
    # Don't forget the last encounter
    if current_encounter is not None:
        current_encounter['vultures'] = list(current_encounter['vultures'])
        current_encounter['duration_minutes'] = (
            current_encounter['end_time'] - current_encounter['start_time']
        ).total_seconds() / 60
        current_encounter['num_events'] = len(current_encounter['events'])
        
        # Calculate center point
        lats = [e['lat1'] for e in current_encounter['events']] + [e['lat2'] for e in current_encounter['events']]
        lons = [e['lon1'] for e in current_encounter['events']] + [e['lon2'] for e in current_encounter['events']]
        current_encounter['center_lat'] = sum(lats) / len(lats)
        current_encounter['center_lon'] = sum(lons) / len(lons)
        
        encounters.append(current_encounter)
    
    return encounters


def create_encounter_dataset(encounter, gps_data, time_buffer_hours):
    """
    Create filtered GPS datasets for a specific encounter
    
    Args:
        encounter: Encounter dictionary
        gps_data: Combined GPS DataFrame
        time_buffer_hours: Hours of data to include before/after
        
    Returns:
        List of DataFrames for the encounter period
    """
    import pandas as pd
    
    buffer_time = pd.Timedelta(hours=time_buffer_hours)
    start_time = encounter['start_time'] - buffer_time
    end_time = encounter['end_time'] + buffer_time
    
    encounter_dataframes = []
    vultures_involved = set(encounter['vultures'])
    
    # Filter the combined GPS data by time
    time_mask = (gps_data['timestamp'] >= start_time) & (gps_data['timestamp'] <= end_time)
    filtered_data = gps_data[time_mask].copy()
    
    # Split by vulture and create separate DataFrames for LiveMapAnimator
    for vulture_id in vultures_involved:
        vulture_data = filtered_data[filtered_data['vulture_id'] == vulture_id].copy()
        
        if not vulture_data.empty:
            # Convert to LiveMapAnimator expected column format
            vulture_data = vulture_data.rename(columns={
                'timestamp': 'Timestamp [UTC]',
                'latitude': 'Latitude',
                'longitude': 'Longitude'
            })
            
            # Add required columns for LiveMapAnimator
            vulture_data['source_file'] = f'encounter_{vulture_id}.csv'
            
            # Ensure Height column exists (even if empty)
            if 'Height' not in vulture_data.columns:
                if 'altitude' in vulture_data.columns:
                    vulture_data['Height'] = vulture_data['altitude']
                else:
                    vulture_data['Height'] = None
            
            encounter_dataframes.append(vulture_data)
    
    return encounter_dataframes


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

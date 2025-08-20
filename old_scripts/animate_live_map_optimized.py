#!/usr/bin/env python3
"""
Enhanced Live Map Animation with Performance Optimization
Features:
- Pre-loading configuration interface for time step filtering
- Dramatic performance improvement for large datasets
- Flexible time resolution from 1 second to 60 minutes
- Progress indicator during data processing
- Automatic data point count estimation
"""

import pandas as pd
import plotly.express as px
import os
import glob

def get_time_step_options():
    """Define available time step options with descriptions"""
    return {
        "1s": {"seconds": 1, "label": "1 second (Ultra-high detail)", "description": "Every GPS point"},
        "30s": {"seconds": 30, "label": "30 seconds (Very high detail)", "description": "High resolution"},
        "1m": {"seconds": 60, "label": "1 minute (High detail)", "description": "Default recommendation"},
        "2m": {"seconds": 120, "label": "2 minutes (Medium detail)", "description": "Good balance"},
        "5m": {"seconds": 300, "label": "5 minutes (Medium detail)", "description": "Faster loading"},
        "10m": {"seconds": 600, "label": "10 minutes (Low detail)", "description": "Quick overview"},
        "20m": {"seconds": 1200, "label": "20 minutes (Very low detail)", "description": "Fast loading"},
        "30m": {"seconds": 1800, "label": "30 minutes (Ultra-low detail)", "description": "Fastest loading"},
        "60m": {"seconds": 3600, "label": "1 hour (Summary only)", "description": "Major points only"}
    }

def estimate_data_points(file_paths, time_step_seconds):
    """Estimate the number of data points after filtering"""
    total_original = 0
    total_filtered = 0
    
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path, sep=';')
            df = df[df['display'] == 1]
            original_count = len(df)
            total_original += original_count
            
            # Quick estimate based on time span
            if len(df) > 1:
                df['Timestamp [UTC]'] = pd.to_datetime(df['Timestamp [UTC]'], format='%d.%m.%Y %H:%M:%S')
                time_span = (df['Timestamp [UTC]'].max() - df['Timestamp [UTC]'].min()).total_seconds()
                estimated_filtered = max(1, int(time_span / time_step_seconds))
                total_filtered += min(estimated_filtered, original_count)
            else:
                total_filtered += original_count
                
        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
            
    return total_original, total_filtered

def filter_data_by_time_step(df, time_step_seconds):
    """Filter dataframe to include only points at specified time intervals"""
    if len(df) == 0:
        return df
    
    # Convert timestamp to datetime
    df = df.copy()
    df['Timestamp [UTC]'] = pd.to_datetime(df['Timestamp [UTC]'], format='%d.%m.%Y %H:%M:%S')
    df = df.sort_values('Timestamp [UTC]')
    
    # If time step is very small (1 second), return all points
    if time_step_seconds <= 1:
        return df
    
    # Filter by time intervals
    filtered_data = []
    last_time = None
    
    for _, row in df.iterrows():
        current_time = row['Timestamp [UTC]']
        
        if last_time is None or (current_time - last_time).total_seconds() >= time_step_seconds:
            filtered_data.append(row)
            last_time = current_time
    
    return pd.DataFrame(filtered_data)

def show_configuration_interface():
    """Display configuration options and get user selection"""
    print("\n" + "="*80)
    print("🦅 BEARDED VULTURE GPS VISUALIZATION - PERFORMANCE OPTIMIZER")
    print("="*80)
    print("\nChoose time step resolution for optimal performance:")
    print("(Larger time steps = faster loading, fewer details)")
    print()
    
    options = get_time_step_options()
    
    # Find available CSV files
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    csv_files = [f for f in csv_files if not f.endswith('.gitkeep')]
    
    if not csv_files:
        print("❌ No CSV files found in data directory!")
        return None, None
    
    print(f"📊 Found {len(csv_files)} data file(s):")
    for i, file_path in enumerate(csv_files, 1):
        filename = os.path.basename(file_path)
        print(f"   {i}. {filename}")
    print()
    
    # Display options with data point estimates
    print("⚡ PERFORMANCE OPTIONS:")
    print("-" * 50)
    
    for key, option in options.items():
        original_points, filtered_points = estimate_data_points(csv_files, option["seconds"])
        reduction_percent = ((original_points - filtered_points) / original_points * 100) if original_points > 0 else 0
        
        performance_rating = "🔥" if filtered_points < 50 else "🚀" if filtered_points < 200 else "⚡" if filtered_points < 500 else "🐌"
        
        print(f"{key:3s}) {option['label']:25s} {performance_rating}")
        print(f"     {option['description']:25s} → ~{filtered_points:4d} points ({reduction_percent:5.1f}% reduction)")
        print()
    
    # Get user selection
    while True:
        choice = input("Enter your choice (1s, 2m, 5m, etc.) or 'q' to quit: ").strip().lower()
        
        if choice == 'q':
            return None, None
        
        if choice in options:
            selected = options[choice]
            original_points, filtered_points = estimate_data_points(csv_files, selected["seconds"])
            
            print(f"\n✅ Selected: {selected['label']}")
            print(f"📊 Estimated data points: {filtered_points} (reduced from {original_points})")
            
            if filtered_points > 1000:
                print("⚠️  Warning: Still many data points. Consider a larger time step for better performance.")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            
            return selected["seconds"], csv_files
        
        print("❌ Invalid choice. Please enter a valid option (e.g., '1m', '5m', '10m')")

def load_and_process_data(csv_files, time_step_seconds):
    """Load and process all CSV files with time step filtering"""
    print(f"\n🔄 Processing data with {time_step_seconds/60:.1f} minute intervals...")
    
    all_data = []
    colors = px.colors.qualitative.Set1
    
    for i, file_path in enumerate(csv_files):
        print(f"   📁 Loading {os.path.basename(file_path)}...")
        
        try:
            # Load data
            df = pd.read_csv(file_path, sep=';')
            df = df[df['display'] == 1]
            
            if len(df) == 0:
                print(f"   ⚠️  No valid data points in {os.path.basename(file_path)}")
                continue
            
            # Apply time step filtering
            original_count = len(df)
            df = filter_data_by_time_step(df, time_step_seconds)
            filtered_count = len(df)
            
            print(f"   ✅ Filtered: {original_count} → {filtered_count} points ({filtered_count/original_count*100:.1f}%)")
            
            # Add metadata
            filename = os.path.basename(file_path)
            vulture_name = filename.replace('.csv', '').replace('_', ' ').title()
            
            df['vulture'] = vulture_name
            df['color'] = colors[i % len(colors)]
            df['file_index'] = i
            
            all_data.append(df)
            
        except Exception as e:
            print(f"   ❌ Error processing {os.path.basename(file_path)}: {e}")
    
    if not all_data:
        print("❌ No valid data loaded!")
        return None
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n✅ Total data points loaded: {len(combined_df)}")
    
    return combined_df

def create_optimized_animation(df):
    """Create the optimized live map animation"""
    print("🎬 Creating optimized animation...")
    
    # Convert timestamp back to string for animation
    df['timestamp_str'] = df['Timestamp [UTC]'].dt.strftime('%d.%m.%Y %H:%M:%S')
    df['timestamp_short'] = df['Timestamp [UTC]'].dt.strftime('%d.%m %H:%M')
    
    # Create animation
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color="vulture",
        size_max=8,
        animation_frame="timestamp_str",
        hover_name="vulture",
        hover_data={
            "timestamp_str": ":timestamp",
            "Latitude": ":.6f",
            "Longitude": ":.6f", 
            "Height": ":altitude",
            "vulture": False,
            "timestamp_short": False
        },
        labels={
            "timestamp_str": "Date/Time",
            "Latitude": "Latitude",
            "Longitude": "Longitude",
            "Height": "Altitude (m)"
        },
        mapbox_style="open-street-map",
        height=600,
        title="🦅 Bearded Vulture GPS Flight Paths - Optimized Performance"
    )
    
    # Optimize layout for performance
    fig.update_layout(
        mapbox=dict(
            center=dict(
                lat=df['Latitude'].mean(),
                lon=df['Longitude'].mean()
            ),
            zoom=12
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        margin=dict(l=0, r=100, t=50, b=0),
        font=dict(size=12)
    )
    
    # Update animation settings for better performance
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 500
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 200
    
    # Update slider labels to show timestamps
    for i, frame in enumerate(fig.frames):
        if i < len(df['timestamp_short'].unique()):
            frame.layout.annotations = [
                dict(
                    text=f"Time: {df['timestamp_short'].iloc[i]}",
                    x=0.5, y=1.05,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=14, color="black")
                )
            ]
    
    return fig

def main():
    """Main function with configuration interface"""
    try:
        # Show configuration interface
        time_step_seconds, csv_files = show_configuration_interface()
        
        if time_step_seconds is None:
            print("👋 Goodbye!")
            return
        
        # Load and process data
        df = load_and_process_data(csv_files, time_step_seconds)
        
        if df is None:
            print("❌ No data to visualize!")
            return
        
        # Create animation
        fig = create_optimized_animation(df)
        
        # Save output
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'flight_paths_optimized.html')
        
        print("💾 Saving optimized visualization...")
        fig.write_html(output_file)
        
        print("\n🎉 SUCCESS!")
        print(f"📁 Optimized visualization saved to: {output_file}")
        print(f"⚡ Performance: {len(df)} data points")
        print(f"🕒 Time resolution: {time_step_seconds/60:.1f} minutes")
        print("\n💡 Tips:")
        print("   - Use larger time steps for faster loading on older laptops")
        print("   - Use smaller time steps for detailed analysis")
        print("   - The visualization will load much faster now!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

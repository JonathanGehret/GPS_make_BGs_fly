#!/usr/bin/env python3
"""
Mobile-Optimized Live Map Animation with Performance Optimization
Features:
- Pre-loading configuration interface for time step filtering
- Optimized for mobile devices and small screens
- Touch-friendly controls and compact layout
- Dramatic performance improvement for large datasets
"""

import pandas as pd
import plotly.express as px
import os
import glob

def get_time_step_options():
    """Define available time step options with mobile-friendly descriptions"""
    return {
        "1s": {"seconds": 1, "label": "1 second", "description": "Every GPS point (may be slow)"},
        "30s": {"seconds": 30, "label": "30 seconds", "description": "Very detailed"},
        "1m": {"seconds": 60, "label": "1 minute", "description": "Recommended default"},
        "2m": {"seconds": 120, "label": "2 minutes", "description": "Good balance"},
        "5m": {"seconds": 300, "label": "5 minutes", "description": "Faster loading"},
        "10m": {"seconds": 600, "label": "10 minutes", "description": "Quick overview"},
        "20m": {"seconds": 1200, "label": "20 minutes", "description": "Fast loading"},
        "30m": {"seconds": 1800, "label": "30 minutes", "description": "Fastest loading"}
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
    
    df = df.copy()
    df['Timestamp [UTC]'] = pd.to_datetime(df['Timestamp [UTC]'], format='%d.%m.%Y %H:%M:%S')
    df = df.sort_values('Timestamp [UTC]')
    
    if time_step_seconds <= 1:
        return df
    
    filtered_data = []
    last_time = None
    
    for _, row in df.iterrows():
        current_time = row['Timestamp [UTC]']
        
        if last_time is None or (current_time - last_time).total_seconds() >= time_step_seconds:
            filtered_data.append(row)
            last_time = current_time
    
    return pd.DataFrame(filtered_data)

def show_mobile_configuration():
    """Display mobile-friendly configuration options"""
    print("\n" + "="*60)
    print("🦅 VULTURE GPS - MOBILE PERFORMANCE OPTIMIZER")
    print("="*60)
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    csv_files = [f for f in csv_files if not f.endswith('.gitkeep')]
    
    if not csv_files:
        print("❌ No CSV files found!")
        return None, None
    
    print(f"📊 Found {len(csv_files)} data file(s)")
    print()
    
    options = get_time_step_options()
    
    print("⚡ PERFORMANCE OPTIONS:")
    print("-" * 40)
    
    for key, option in options.items():
        original_points, filtered_points = estimate_data_points(csv_files, option["seconds"])
        
        # Mobile-friendly performance indicators
        if filtered_points < 50:
            speed = "🔥 Ultra Fast"
        elif filtered_points < 100:
            speed = "🚀 Very Fast"
        elif filtered_points < 300:
            speed = "⚡ Fast"
        else:
            speed = "🐌 Slower"
        
        print(f"{key:3s}) {option['label']:12s} {speed}")
        print(f"     ~{filtered_points:3d} points - {option['description']}")
        print()
    
    while True:
        choice = input("Choose option (1m, 5m, etc.) or 'q': ").strip().lower()
        
        if choice == 'q':
            return None, None
        
        if choice in options:
            selected = options[choice]
            original_points, filtered_points = estimate_data_points(csv_files, selected["seconds"])
            
            print(f"\n✅ Selected: {selected['label']}")
            print(f"📊 Data points: {filtered_points}")
            
            # Mobile-specific warning for performance
            if filtered_points > 500:
                print("⚠️  Warning: May be slow on mobile!")
                confirm = input("Continue? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            
            return selected["seconds"], csv_files
        
        print("❌ Invalid choice. Try again.")

def load_and_process_data(csv_files, time_step_seconds):
    """Load and process data with mobile optimization"""
    print("\n🔄 Processing for mobile...")
    
    all_data = []
    colors = px.colors.qualitative.Set1
    
    for i, file_path in enumerate(csv_files):
        print(f"   📁 {os.path.basename(file_path)}...")
        
        try:
            df = pd.read_csv(file_path, sep=';')
            df = df[df['display'] == 1]
            
            if len(df) == 0:
                continue
            
            original_count = len(df)
            df = filter_data_by_time_step(df, time_step_seconds)
            filtered_count = len(df)
            
            print(f"   ✅ {original_count} → {filtered_count} points")
            
            filename = os.path.basename(file_path)
            vulture_name = filename.replace('.csv', '').replace('_', ' ').title()
            
            df['vulture'] = vulture_name
            df['color'] = colors[i % len(colors)]
            
            all_data.append(df)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if not all_data:
        return None
    
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n✅ Total points: {len(combined_df)}")
    
    return combined_df

def create_mobile_animation(df):
    """Create mobile-optimized animation"""
    print("🎬 Creating mobile animation...")
    
    # Mobile-friendly timestamp formatting
    df['timestamp_str'] = df['Timestamp [UTC]'].dt.strftime('%d.%m.%Y %H:%M:%S')
    df['timestamp_mobile'] = df['Timestamp [UTC]'].dt.strftime('%d.%m %H:%M')
    
    # Create mobile-optimized animation
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color="vulture",
        size_max=12,  # Larger markers for touch
        animation_frame="timestamp_str",
        hover_name="vulture",
        hover_data={
            "timestamp_mobile": ":Time",
            "Latitude": ":.4f",
            "Longitude": ":.4f", 
            "Height": ":Altitude (m)",
            "vulture": False,
            "timestamp_str": False
        },
        mapbox_style="open-street-map",
        height=500,  # Mobile-friendly height
        title="🦅 Vulture GPS - Mobile Optimized"
    )
    
    # Mobile-optimized layout
    fig.update_layout(
        mapbox=dict(
            center=dict(
                lat=df['Latitude'].mean(),
                lon=df['Longitude'].mean()
            ),
            zoom=13  # Higher zoom for mobile detail
        ),
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend for mobile
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.9)",
            font=dict(size=10)
        ),
        margin=dict(l=10, r=10, t=40, b=60),
        font=dict(size=11),
        title=dict(
            font=dict(size=14),
            x=0.5,
            xanchor='center'
        )
    )
    
    # Optimize animation for mobile performance
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 800
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 300
    
    # Mobile-friendly controls
    fig.update_layout(
        updatemenus=[dict(
            type="buttons",
            direction="left",
            buttons=list([
                dict(label="▶", method="animate", args=[None, {
                    "frame": {"duration": 800, "redraw": True},
                    "transition": {"duration": 300},
                    "fromcurrent": True
                }]),
                dict(label="⏸", method="animate", args=[[None], {
                    "frame": {"duration": 0, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 0}
                }])
            ]),
            pad={"r": 10, "t": 87},
            showactive=False,
            x=0.01,
            xanchor="left",
            y=0.02,
            yanchor="bottom"
        )]
    )
    
    # Mobile-friendly slider
    fig.update_layout(
        sliders=[dict(
            active=0,
            yanchor="top",
            xanchor="left",
            currentvalue=dict(
                font=dict(size=12),
                prefix="Time: ",
                visible=True,
                xanchor="right"
            ),
            transition=dict(duration=300, easing="cubic-in-out"),
            pad=dict(b=10, t=50),
            len=0.9,
            x=0.05,
            y=0,
            steps=[]
        )]
    )
    
    return fig

def main():
    """Main function for mobile optimization"""
    try:
        # Mobile configuration
        time_step_seconds, csv_files = show_mobile_configuration()
        
        if time_step_seconds is None:
            print("👋 Goodbye!")
            return
        
        # Process data
        df = load_and_process_data(csv_files, time_step_seconds)
        
        if df is None:
            print("❌ No data to visualize!")
            return
        
        # Create mobile animation
        fig = create_mobile_animation(df)
        
        # Save mobile-optimized output
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'flight_paths_mobile_optimized.html')
        
        print("💾 Saving mobile visualization...")
        fig.write_html(output_file)
        
        print("\n🎉 MOBILE SUCCESS!")
        print(f"📱 Mobile visualization: {output_file}")
        print(f"⚡ Optimized: {len(df)} data points")
        print(f"🕒 Time step: {time_step_seconds/60:.1f} minutes")
        print("\n📱 Mobile Features:")
        print("   ✅ Touch-friendly controls")
        print("   ✅ Larger markers for fingers")
        print("   ✅ Optimized for small screens")
        print("   ✅ Fast loading performance")
        
    except KeyboardInterrupt:
        print("\n👋 Cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()

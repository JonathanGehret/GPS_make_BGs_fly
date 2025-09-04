#!/usr/bin/env python3
"""
Enhanced Timeline Labels System

Provides intelligent time labeling for animation sliders that adapts to different
time frames (minutes, hours, days, weeks) with two-line display for better clarity.
"""

import pandas as pd
from typing import List, Dict


class TimelineLabelSystem:
    """Intelligent timeline labeling system for animation sliders"""
    
    def __init__(self):
        self.timezone_offset = 0  # Can be configured for local time display
    
    def analyze_time_span(self, unique_times: List[str]) -> Dict:
        """
        Analyze the time span to determine optimal labeling strategy
        
        Args:
            unique_times: List of time strings in format '%d.%m.%Y %H:%M:%S'
            
        Returns:
            Dict with time span analysis and labeling recommendations
        """
        if not unique_times or len(unique_times) < 2:
            return {'strategy': 'single_point', 'total_duration': 0}
        
        # Convert to datetime objects
        times = [pd.to_datetime(time_str, format='%d.%m.%Y %H:%M:%S') for time_str in unique_times]
        times.sort()
        
        start_time = times[0]
        end_time = times[-1]
        total_duration = (end_time - start_time).total_seconds()
        
        # Determine strategy based on duration
        minutes = total_duration / 60
        hours = minutes / 60
        days = hours / 24
        
        if minutes <= 90:  # Less than 1.5 hours
            strategy = 'minutes'
            major_step = 10 if minutes <= 30 else 15 if minutes <= 60 else 30
            minor_step = 5 if minutes <= 30 else 10
        elif hours <= 12:  # Less than 12 hours
            strategy = 'hours'
            major_step = 1 if hours <= 6 else 2
            minor_step = 30  # minutes
        elif days <= 3:  # Less than 3 days
            strategy = 'hours'
            major_step = 6 if days <= 1 else 12
            minor_step = 60  # minutes
        elif days <= 14:  # Less than 2 weeks
            strategy = 'days'
            major_step = 1 if days <= 7 else 2
            minor_step = 6  # hours
        else:  # Weeks or longer
            strategy = 'weeks'
            major_step = 1 if days <= 28 else 2
            minor_step = 1  # days
        
        return {
            'strategy': strategy,
            'total_duration': total_duration,
            'start_time': start_time,
            'end_time': end_time,
            'total_minutes': minutes,
            'total_hours': hours,
            'total_days': days,
            'major_step': major_step,
            'minor_step': minor_step,
            'frame_count': len(unique_times)
        }
    
    def create_enhanced_slider_labels(self, unique_times: List[str]) -> List[Dict]:
        """
        Create enhanced two-line labels for animation slider
        
        Args:
            unique_times: List of time strings in format '%d.%m.%Y %H:%M:%S'
            
        Returns:
            List of enhanced label dictionaries for Plotly slider
        """
        analysis = self.analyze_time_span(unique_times)
        
        if analysis['strategy'] == 'single_point':
            return self._create_single_point_labels(unique_times)
        
        strategy = analysis['strategy']
        
        if strategy == 'minutes':
            return self._create_minute_labels(unique_times, analysis)
        elif strategy == 'hours':
            return self._create_hour_labels(unique_times, analysis)
        elif strategy == 'days':
            return self._create_day_labels(unique_times, analysis)
        elif strategy == 'weeks':
            return self._create_week_labels(unique_times, analysis)
        else:
            return self._create_fallback_labels(unique_times)
    
    def _create_single_point_labels(self, unique_times: List[str]) -> List[Dict]:
        """Create labels for single time point"""
        return [{
            'args': [[time_str], dict(mode="immediate", transition=dict(duration=300))],
            'label': self._format_single_time(time_str),
            'method': 'animate'
        } for time_str in unique_times]
    
    def _create_minute_labels(self, unique_times: List[str], analysis: Dict) -> List[Dict]:
        """Create labels for minute-scale animations"""
        labels = []
        times = [pd.to_datetime(time_str, format='%d.%m.%Y %H:%M:%S') for time_str in unique_times]
        start_time = analysis['start_time']
        
        for i, (time_str, time_obj) in enumerate(zip(unique_times, times)):
            elapsed_minutes = (time_obj - start_time).total_seconds() / 60
            
            # First line: time, second line: elapsed minutes
            time_label = time_obj.strftime('%H:%M:%S')
            elapsed_label = f"+{elapsed_minutes:.0f}min"
            
            # Show major marks more prominently  
            if elapsed_minutes % analysis['major_step'] == 0 or i == 0 or i == len(unique_times) - 1:
                label = f"{time_label}\n{elapsed_label}"  # Two lines, no HTML
            else:
                label = f"{time_label}\n{elapsed_label}"  # Consistent formatting
            
            labels.append({
                'args': [[time_str], dict(mode="immediate", transition=dict(duration=300))],
                'label': label,
                'method': 'animate'
            })
        
        return labels
    
    def _create_hour_labels(self, unique_times: List[str], analysis: Dict) -> List[Dict]:
        """Create labels for hour-scale animations"""
        labels = []
        times = [pd.to_datetime(time_str, format='%d.%m.%Y %H:%M:%S') for time_str in unique_times]
        start_time = analysis['start_time']
        
        for i, (time_str, time_obj) in enumerate(zip(unique_times, times)):
            elapsed_hours = (time_obj - start_time).total_seconds() / 3600
            
            # First line: time, second line: day if multi-day
            time_label = time_obj.strftime('%H:%M')
            
            if analysis['total_days'] > 1:
                day_label = time_obj.strftime('%d.%m')
                if elapsed_hours >= 24:
                    day_label += f" (+{elapsed_hours/24:.0f}d)"
            else:
                day_label = f"+{elapsed_hours:.1f}h"
            
            # Show major marks more prominently
            if time_obj.hour % analysis['major_step'] == 0 or i == 0 or i == len(unique_times) - 1:
                label = f"{time_label}\n{day_label}"  # Two lines, no HTML
            else:
                label = f"{time_label}\n{day_label}"  # Consistent formatting
            
            labels.append({
                'args': [[time_str], dict(mode="immediate", transition=dict(duration=300))],
                'label': label,
                'method': 'animate'
            })
        
        return labels
    
    def _create_day_labels(self, unique_times: List[str], analysis: Dict) -> List[Dict]:
        """Create labels for day-scale animations"""
        labels = []
        times = [pd.to_datetime(time_str, format='%d.%m.%Y %H:%M:%S') for time_str in unique_times]
        start_time = analysis['start_time']
        
        for i, (time_str, time_obj) in enumerate(zip(unique_times, times)):
            elapsed_days = (time_obj - start_time).total_seconds() / 86400
            
            # First line: date, second line: time or day name
            date_label = time_obj.strftime('%d.%m')
            
            if analysis['total_days'] <= 7:
                time_label = time_obj.strftime('%H:%M')
            else:
                time_label = time_obj.strftime('%a')  # Weekday name
                if elapsed_days >= 7:
                    time_label += f" (Week {elapsed_days/7:.0f})"
            
            # Show major marks more prominently  
            if time_obj.day % analysis['major_step'] == 0 or i == 0 or i == len(unique_times) - 1:
                label = f"{date_label}\n{time_label}"  # Two lines, no HTML
            else:
                label = f"{date_label}\n{time_label}"  # Consistent formatting
            
            labels.append({
                'args': [[time_str], dict(mode="immediate", transition=dict(duration=300))],
                'label': label,
                'method': 'animate'
            })
        
        return labels
    
    def _create_week_labels(self, unique_times: List[str], analysis: Dict) -> List[Dict]:
        """Create labels for week-scale animations"""
        labels = []
        times = [pd.to_datetime(time_str, format='%d.%m.%Y %H:%M:%S') for time_str in unique_times]
        start_time = analysis['start_time']
        
        for i, (time_str, time_obj) in enumerate(zip(unique_times, times)):
            elapsed_weeks = (time_obj - start_time).total_seconds() / (86400 * 7)
            
            # First line: week info, second line: date
            week_info = f"Week {elapsed_weeks:.0f}" if elapsed_weeks >= 1 else "Week 1"
            date_label = time_obj.strftime('%d.%m.%Y')
            
            # Show major marks more prominently
            if int(elapsed_weeks) % analysis['major_step'] == 0 or i == 0 or i == len(unique_times) - 1:
                label = f"{week_info}\n{date_label}"  # Two lines, no HTML
            else:
                label = f"{week_info}\n{date_label}"  # Consistent formatting
            
            labels.append({
                'args': [[time_str], dict(mode="immediate", transition=dict(duration=300))],
                'label': label,
                'method': 'animate'
            })
        
        return labels
    
    def _create_fallback_labels(self, unique_times: List[str]) -> List[Dict]:
        """Create fallback labels for edge cases"""
        return [{
            'args': [[time_str], dict(mode="immediate", transition=dict(duration=300))],
            'label': self._format_single_time(time_str),
            'method': 'animate'
        } for time_str in unique_times]
    
    def _format_single_time(self, time_str: str) -> str:
        """Format a single time for display"""
        try:
            time_obj = pd.to_datetime(time_str, format='%d.%m.%Y %H:%M:%S')
            return f"{time_obj.strftime('%H:%M')}\n{time_obj.strftime('%d.%m.%Y')}"  # No HTML
        except Exception:
            return time_str
    
    def get_time_span_summary(self, unique_times: List[str]) -> str:
        """
        Get a human-readable summary of the time span
        
        Args:
            unique_times: List of time strings
            
        Returns:
            Human-readable time span description
        """
        analysis = self.analyze_time_span(unique_times)
        
        if analysis['strategy'] == 'single_point':
            return "Single time point"
        
        strategy = analysis['strategy']
        
        if strategy == 'minutes':
            return f"Animation spans {analysis['total_minutes']:.0f} minutes"
        elif strategy == 'hours':
            if analysis['total_hours'] < 2:
                return f"Animation spans {analysis['total_minutes']:.0f} minutes"
            else:
                return f"Animation spans {analysis['total_hours']:.1f} hours"
        elif strategy == 'days':
            if analysis['total_days'] < 2:
                return f"Animation spans {analysis['total_hours']:.0f} hours"
            else:
                return f"Animation spans {analysis['total_days']:.1f} days"
        elif strategy == 'weeks':
            weeks = analysis['total_days'] / 7
            return f"Animation spans {weeks:.1f} weeks"
        
        return f"Animation spans {len(unique_times)} time points"


def create_enhanced_slider_config(unique_times: List[str], 
                                 position_y: float = 0.02, 
                                 position_x: float = 0.1, 
                                 length: float = 0.8,
                                 enable_prominent_display: bool = False) -> Dict:
    """
    Create enhanced slider configuration for Plotly animations
    
    Args:
        unique_times: List of time strings in format '%d.%m.%Y %H:%M:%S'
        position_y: Y position of slider (0-1)
        position_x: X position of slider (0-1)
        length: Length of slider (0-1)
        enable_prominent_display: Whether to enable prominent date/time display
        
    Returns:
        Enhanced slider configuration dict for Plotly
    """
    label_system = TimelineLabelSystem()
    enhanced_labels = label_system.create_enhanced_slider_labels(unique_times)
    
    # Create robust slider steps with improved animation handling
    improved_steps = []
    for step in enhanced_labels:
        # Extract frame name safely
        frame_name = step['args'][0][0] if isinstance(step['args'][0], list) else step['args'][0]
        
        improved_step = {
            'args': [[frame_name], {
                "frame": {"duration": 0, "redraw": True},  # Enable immediate redraw
                "mode": "immediate",
                "transition": {"duration": 0}
            }],
            'label': step['label'],
            'method': 'animate',
            'execute': True  # Ensure step execution
        }
        improved_steps.append(improved_step)
    
    # Enhanced current value display with prominent styling
    if enable_prominent_display:
        current_value_config = {
            'prefix': '🕒 ',
            'suffix': '',
            'font': {
                'size': 18,
                'family': 'Arial Black, Arial, sans-serif',
                'color': '#2c3e50'
            },
            'visible': True,
            'xanchor': 'center',
            'offset': 25  # Higher offset to avoid overlap with controls
        }
    else:
        current_value_config = {
            'prefix': '🕒 Time: ',
            'font': {'size': 12},
            'visible': True,
            'xanchor': 'center',
            'offset': 20  # Consistent spacing
        }
    
    return {
        'active': 0,
        'currentvalue': current_value_config,
        'x': position_x,
        'y': position_y,
        'len': length,
        'steps': improved_steps,
        'transition': {'duration': 250},  # Slightly faster transitions
        'tickcolor': 'rgba(0,0,0,0.4)',
        'bordercolor': 'rgba(0,0,0,0.4)',
        'borderwidth': 2,
        'bgcolor': 'rgba(255,255,255,0.9)',
        # Enhanced slider styling with valid properties only
        'pad': {'t': 20, 'b': 20},
        'minorticklen': 4,  # Valid property
        'tickwidth': 2,
        'visible': True  # Ensure slider stays visible
    }

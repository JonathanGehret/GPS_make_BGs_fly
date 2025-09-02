#!/usr/bin/env python3
"""
Directory and File Management Utilities

Handles output directory creation and file path management.
"""

import os
from .constants import VISUALIZATIONS_DIR, ANALYSIS_DIR


def ensure_output_directories():
    """Create output directories if they don't exist"""
    for directory in [VISUALIZATIONS_DIR, ANALYSIS_DIR]:
        os.makedirs(directory, exist_ok=True)


def get_output_path(filename: str, output_type: str = 'visualizations') -> str:
    """
    Get the full path for an output file
    
    Args:
        filename: Name of the output file
        output_type: 'visualizations' or 'analysis'
        
    Returns:
        Full path to the output file
    """
    if output_type == 'visualizations':
        base_dir = VISUALIZATIONS_DIR
    elif output_type == 'analysis':
        base_dir = ANALYSIS_DIR
    else:
        raise ValueError(f"Unknown output_type: {output_type}")
    
    ensure_output_directories()
    return os.path.join(base_dir, filename)


def get_numbered_output_path(base_filename: str, output_type: str = 'visualizations') -> str:
    """
    Get the full path for an output file with consecutive numbering
    
    This function automatically finds the next available number and creates
    a filename like: base_name_01.html, base_name_02.html, etc.
    
    Args:
        base_filename: Base name of the output file (without extension)
        output_type: 'visualizations' or 'analysis'
        
    Returns:
        Full path to the numbered output file
    """
    # Check for custom output directory from GUI
    custom_output_dir = os.environ.get('OUTPUT_DIR')
    if custom_output_dir and os.path.exists(custom_output_dir):
        base_dir = custom_output_dir
        extension = '.html'
    elif output_type == 'visualizations':
        base_dir = VISUALIZATIONS_DIR
        extension = '.html'
    elif output_type == 'analysis':
        base_dir = ANALYSIS_DIR
        extension = '.html'
    else:
        raise ValueError(f"Unknown output_type: {output_type}")
    
    ensure_output_directories()
    
    # Ensure custom directory exists if specified
    if custom_output_dir and not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
    
    # Find the next available number
    existing_numbers = []
    
    if os.path.exists(base_dir):
        for file in os.listdir(base_dir):
            if file.startswith(base_filename) and file.endswith(extension):
                # Extract number from filename like "base_name_03.html"
                try:
                    # Remove base filename and extension
                    remaining = file[len(base_filename):]
                    if remaining.startswith('_') and remaining.endswith(extension):
                        number_part = remaining[1:-len(extension)]  # Remove _ and .html
                        if number_part.isdigit():
                            existing_numbers.append(int(number_part))
                except (ValueError, IndexError):
                    continue
    
    # Find next available number
    next_number = 1
    if existing_numbers:
        next_number = max(existing_numbers) + 1
    
    # Create numbered filename
    numbered_filename = f"{base_filename}_{next_number:02d}{extension}"
    
    return os.path.join(base_dir, numbered_filename)

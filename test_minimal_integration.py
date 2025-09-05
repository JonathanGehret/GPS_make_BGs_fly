#!/usr/bin/env python3
"""
Minimal integration test - build up GUI step by step to isolate segfault
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path
gui_path = os.path.join(os.path.dirname(__file__), "gui")
sys.path.insert(0, gui_path)

try:
    from components.folder_manager import FolderManager
    print("✓ Successfully imported FolderManager")
except ImportError as e:
    print(f"✗ Failed to import FolderManager: {e}")
    sys.exit(1)

def test_step_1_basic_window():
    """Test 1: Basic window creation"""
    print("Test 1: Creating basic window...")
    root = tk.Tk()
    root.title("Test Step 1")
    root.geometry("400x300")
    print("✓ Basic window created")
    root.destroy()
    print("✓ Basic window destroyed safely")

def test_step_2_with_frame():
    """Test 2: Window with frame"""
    print("Test 2: Creating window with frame...")
    root = tk.Tk()
    root.title("Test Step 2")
    root.geometry("400x300")
    
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    print("✓ Window with frame created")
    root.destroy()
    print("✓ Window with frame destroyed safely")

def test_step_3_with_folder_manager_creation():
    """Test 3: Create FolderManager object (no GUI setup)"""
    print("Test 3: Creating FolderManager object...")
    root = tk.Tk()
    root.title("Test Step 3")
    root.geometry("400x300")
    
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create a grid container for FolderManager
    folder_container = ttk.Frame(main_frame)
    folder_container.pack(fill=tk.X, pady=10)
    folder_container.columnconfigure(0, weight=1)
    
    def get_language():
        return 'en'
    
    # Just create the object, don't call setup_ui yet
    folder_manager = FolderManager(folder_container, get_language)
    print("✓ FolderManager object created")
    
    root.destroy()
    print("✓ Window with FolderManager object destroyed safely")

def test_step_4_with_folder_manager_setup():
    """Test 4: Create FolderManager and call setup_ui"""
    print("Test 4: Creating FolderManager with setup_ui...")
    root = tk.Tk()
    root.title("Test Step 4")
    root.geometry("400x300")
    
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create a grid container for FolderManager
    folder_container = ttk.Frame(main_frame)
    folder_container.pack(fill=tk.X, pady=10)
    folder_container.columnconfigure(0, weight=1)
    
    def get_language():
        return 'en'
    
    def on_data_folder_changed(directory):
        print(f"Data folder changed: {directory}")
    
    # Create object and setup UI
    folder_manager = FolderManager(folder_container, get_language)
    folder_manager.set_data_folder_callback(on_data_folder_changed)
    folder_manager.setup_ui()
    print("✓ FolderManager setup_ui completed")
    
    root.destroy()
    print("✓ Window with FolderManager setup destroyed safely")

def main():
    """Run all tests step by step"""
    print("=== Minimal Integration Testing ===")
    
    try:
        test_step_1_basic_window()
        print()
        
        test_step_2_with_frame()
        print()
        
        test_step_3_with_folder_manager_creation()
        print()
        
        test_step_4_with_folder_manager_setup()
        print()
        
        print("✓ All tests passed! FolderManager integration is working.")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

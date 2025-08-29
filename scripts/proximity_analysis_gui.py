#!/usr/bin/env python3
"""
Proximity Analysis GUI Application

Professional graphical interface for vulture proximity analysis.
Makes the analysis accessible to non-technical users through an intuitive interface.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import webbrowser
from pathlib import Path
import pandas as pd

# Add the scripts directory to the Python path
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from utils.animation_controls import AnimationControlsFrame
except ImportError:
    AnimationControlsFrame = None  # Fallback if import fails

try:
    from gps_utils import DataLoader
except ImportError:
    # Try alternative import path for bundled executable
    try:
        from scripts.gps_utils import DataLoader
    except ImportError:
        print("❌ ERROR: Could not import DataLoader from gps_utils")
        DataLoader = None

try:
    from core.proximity_engine import ProximityEngine
except ImportError:
    print("❌ ERROR: Could not import ProximityEngine")
    ProximityEngine = None

try:
    from visualization.proximity_plots import ProximityVisualizer
except ImportError:
    print("❌ ERROR: Could not import ProximityVisualizer")
    ProximityVisualizer = None

try:
    from animate_live_map import LiveMapAnimator
except ImportError:
    print("❌ ERROR: Could not import LiveMapAnimator")
    LiveMapAnimator = None

try:
    from proximity_analysis import group_proximity_events, parse_time_step
except ImportError:
    print("❌ ERROR: Could not import proximity analysis functions")
    group_proximity_events = None
    parse_time_step = None

try:
    from i18n import get_translator, t
except ImportError:
    print("❌ ERROR: Could not import i18n")
    get_translator = None
    t = None


class ProximityAnalysisGUI:
    """Professional GUI for Vulture Proximity Analysis"""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize translator
        self.translator = get_translator()
        
        self.root.title(self.translator.t("app_title"))
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Analysis state
        self.data_folder = tk.StringVar(value="data")
        self.output_folder = tk.StringVar(value="visualizations")
        self.proximity_threshold = tk.DoubleVar(value=2.0)
        self.time_threshold = tk.IntVar(value=5)
        self.generate_animations = tk.BooleanVar(value=False)
        self.time_buffer = tk.DoubleVar(value=2.0)
        self.trail_length = tk.DoubleVar(value=2.0)
        self.time_step = tk.StringVar(value="1m")
        self.limit_encounters = tk.IntVar(value=0)
        
        # Results storage
        self.results = {}
        self.output_files = []
        
        # Thread management
        self.analysis_thread = None
        self.log_queue = queue.Queue()
        
        self.setup_ui()
        self.check_log_queue()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title with language switcher
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        title_frame.columnconfigure(0, weight=1)
        
        self.title_label = ttk.Label(title_frame, text=self.translator.t("app_title"), 
                                    font=('Arial', 16, 'bold'))
        self.title_label.grid(row=0, column=0)
        
        # Language switcher dropdown (same style as other GUIs)
        lang_frame = ttk.Frame(title_frame)
        lang_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Label(lang_frame, text="🌐", font=("Arial", 12)).grid(row=0, column=0, padx=(0, 3))
        
        self.lang_var = tk.StringVar(value=self.translator.get_current_language())
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                 values=["en", "de"], state="readonly", width=6)
        lang_combo.grid(row=0, column=1)
        lang_combo.bind("<<ComboboxSelected>>", self.change_language_dropdown)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        
        # Setup tabs
        self.setup_data_tab()
        self.setup_analysis_tab()
        self.setup_animation_tab()
        self.setup_results_tab()
        self.setup_log_tab()
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        self.run_button = ttk.Button(button_frame, text=self.translator.t("btn_run"), 
                                    command=self.run_analysis, style='Accent.TButton')
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text=self.translator.t("btn_stop"), 
                                     command=self.stop_analysis, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_results_button = ttk.Button(button_frame, text=self.translator.t("btn_open_results"), 
                                             command=self.open_results_folder)
        self.open_results_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.help_button = ttk.Button(button_frame, text=self.translator.t("btn_help"), 
                                     command=self.show_help)
        self.help_button.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value=self.translator.t("status_ready"))
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Ensure all UI elements use the correct initial language
        self.update_ui_text()
        
    def change_language_dropdown(self, event=None):
        """Change language from dropdown selection"""
        new_lang = self.lang_var.get()
        self.translator.set_language(new_lang)
        self.translator.save_language_preference(new_lang)
        
        # Update all UI text
        self.update_ui_text()
    
    def switch_language(self):
        """Switch between German and English (legacy method for compatibility)"""
        current_lang = self.translator.get_current_language()
        new_lang = "en" if current_lang == "de" else "de"
        
        self.lang_var.set(new_lang)  # Update dropdown
        self.translator.set_language(new_lang)
        self.translator.save_language_preference(new_lang)
        
        # Update all UI text
        self.update_ui_text()
        
    def update_ui_text(self):
        """Update all UI elements with current language"""
        try:
            # Update window title
            self.root.title(self.translator.t("app_title"))
            
            # Update main title
            self.title_label.config(text=self.translator.t("app_title"))
            
            # Update tab names
            self.notebook.tab(0, text=self.translator.t("tab_data"))
            self.notebook.tab(1, text=self.translator.t("tab_analysis"))
            self.notebook.tab(2, text=self.translator.t("tab_animation"))
            self.notebook.tab(3, text=self.translator.t("tab_results"))
            self.notebook.tab(4, text=self.translator.t("tab_log"))
            
            # Update button texts
            self.run_button.config(text=self.translator.t("btn_run"))
            self.stop_button.config(text=self.translator.t("btn_stop"))
            self.open_results_button.config(text=self.translator.t("btn_open_results"))
            self.help_button.config(text=self.translator.t("btn_help"))
            
            # Update status
            current_status = self.status_var.get()
            if "Ready" in current_status or "Bereit" in current_status:
                self.status_var.set(self.translator.t("status_ready"))
            elif "Running" in current_status or "Führe" in current_status:
                self.status_var.set(self.translator.t("status_running"))
            elif "completed" in current_status or "abgeschlossen" in current_status:
                self.status_var.set(self.translator.t("status_completed"))
            
            # Update other UI elements
            self.update_data_tab_text()
            self.update_analysis_tab_text()
            self.update_animation_tab_text()
            self.update_results_tab_text()
            self.update_log_tab_text()
            self.update_button_texts()
            
            # Update additional browse button
            if hasattr(self, 'browse_output_button'):
                self.browse_output_button.config(text=self.translator.t("btn_browse"))
            
        except Exception:
            pass  # Gracefully handle any UI update errors
    
    def update_data_tab_text(self):
        """Update data tab text elements"""
        try:
            self.data_folder_label.config(text=self.translator.t("label_data_folder"))
            self.browse_button.config(text=self.translator.t("btn_browse"))
            self.data_preview_label.config(text=self.translator.t("label_data_preview"))
            self.refresh_button.config(text=self.translator.t("btn_refresh"))
        except Exception:
            pass
    
    def update_analysis_tab_text(self):
        """Update analysis tab text elements"""
        try:
            self.analysis_params_label.config(text=self.translator.t("label_analysis_params"))
            self.param_frame.config(text=self.translator.t("group_detection_params"))
            self.proximity_threshold_label.config(text=self.translator.t("label_proximity_threshold"))
            self.time_threshold_label.config(text=self.translator.t("label_time_threshold"))
            self.options_frame.config(text=self.translator.t("group_analysis_options"))
            self.animations_checkbox.config(text=self.translator.t("check_generate_animations"))
            self.help_frame.config(text=self.translator.t("group_parameter_guide"))
            
            # Update help text
            help_text = f"""
        {self.translator.t("help_proximity")}
        {self.translator.t("help_time")}
        {self.translator.t("help_animations")}
        """
            self.help_text_label.config(text=help_text)
        except Exception:
            pass
    
    def update_animation_tab_text(self):
        """Update animation tab text elements"""
        # This will be implemented when we update the animation tab
        pass
    
    def update_results_tab_text(self):
        """Update results tab text elements"""
        try:
            self.results_title_label.config(text=self.translator.t("label_analysis_results"))
            self.files_frame.config(text=self.translator.t("group_generated_files"))
            self.open_file_button.config(text=self.translator.t("btn_open"))
            self.show_folder_button.config(text=self.translator.t("btn_show_folder"))
        except Exception:
            pass

    def update_log_tab_text(self):
        """Update log tab text elements"""
        try:
            self.log_title_label.config(text=self.translator.t("label_analysis_log"))
            self.clear_log_button.config(text=self.translator.t("btn_clear_log"))
            self.save_log_button.config(text=self.translator.t("btn_save_log"))
        except Exception:
            pass
    
    def update_button_texts(self):
        """Update button texts"""
        # This will be implemented for additional buttons
        pass
        
    def setup_data_tab(self):
        """Setup data configuration tab"""
        data_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(data_frame, text=self.translator.t("tab_data"))
        
        # Data folder selection
        self.data_folder_label = ttk.Label(data_frame, text=self.translator.t("label_data_folder"), 
                                          font=('Arial', 11, 'bold'))
        self.data_folder_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        folder_frame = ttk.Frame(data_frame)
        folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.data_folder, width=50)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_button = ttk.Button(folder_frame, text=self.translator.t("btn_browse"), 
                                       command=self.browse_folder)
        self.browse_button.grid(row=0, column=1)
        
        # Output folder selection
        self.output_folder_label = ttk.Label(data_frame, text="Output Folder:", 
                                           font=('Arial', 11, 'bold'))
        self.output_folder_label.grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        
        output_folder_frame = ttk.Frame(data_frame)
        output_folder_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        output_folder_frame.columnconfigure(0, weight=1)
        
        self.output_folder_entry = ttk.Entry(output_folder_frame, textvariable=self.output_folder, width=50)
        self.output_folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_output_button = ttk.Button(output_folder_frame, text=self.translator.t("btn_browse"), 
                                              command=self.browse_output_folder)
        self.browse_output_button.grid(row=0, column=1)
        
        # Data preview
        self.data_preview_label = ttk.Label(data_frame, text=self.translator.t("label_data_preview"), 
                                           font=('Arial', 11, 'bold'))
        self.data_preview_label.grid(row=4, column=0, sticky=tk.W, pady=(15, 5))
        
        self.data_preview = scrolledtext.ScrolledText(data_frame, height=15, width=70)
        self.data_preview.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        data_frame.rowconfigure(5, weight=1)
        data_frame.columnconfigure(0, weight=1)
        
        self.refresh_button = ttk.Button(data_frame, text=self.translator.t("btn_refresh"), 
                                        command=self.refresh_data_preview)
        self.refresh_button.grid(row=6, column=0, pady=(10, 0))
        
    def setup_analysis_tab(self):
        """Setup analysis parameters tab"""
        analysis_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(analysis_frame, text=self.translator.t("tab_analysis"))
        
        # Proximity threshold
        self.analysis_params_label = ttk.Label(analysis_frame, text=self.translator.t("label_analysis_params"), 
                                              font=('Arial', 11, 'bold'))
        self.analysis_params_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        self.param_frame = ttk.LabelFrame(analysis_frame, text=self.translator.t("group_detection_params"), padding="15")
        self.param_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.proximity_threshold_label = ttk.Label(self.param_frame, text=self.translator.t("label_proximity_threshold"))
        self.proximity_threshold_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        proximity_scale = ttk.Scale(self.param_frame, from_=0.1, to=10.0, 
                                   variable=self.proximity_threshold, orient=tk.HORIZONTAL)
        proximity_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(0, 10))
        self.proximity_label = ttk.Label(self.param_frame, text="2.0 km")
        self.proximity_label.grid(row=0, column=2, pady=(0, 10))
        proximity_scale.configure(command=self.update_proximity_label)
        
        self.time_threshold_label = ttk.Label(self.param_frame, text=self.translator.t("label_time_threshold"))
        self.time_threshold_label.grid(row=1, column=0, sticky=tk.W)
        time_scale = ttk.Scale(self.param_frame, from_=1, to=60, 
                              variable=self.time_threshold, orient=tk.HORIZONTAL)
        time_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        self.time_label = ttk.Label(self.param_frame, text="5 min")
        self.time_label.grid(row=1, column=2)
        time_scale.configure(command=self.update_time_label)
        
        self.param_frame.columnconfigure(1, weight=1)
        
        # Analysis options
        self.options_frame = ttk.LabelFrame(analysis_frame, text=self.translator.t("group_analysis_options"), padding="15")
        self.options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.animations_checkbox = ttk.Checkbutton(self.options_frame, text=self.translator.t("check_generate_animations"), 
                                                  variable=self.generate_animations,
                                                  command=self.toggle_animation_options)
        self.animations_checkbox.grid(row=0, column=0, sticky=tk.W)
        
        # Help text
        self.help_frame = ttk.LabelFrame(analysis_frame, text=self.translator.t("group_parameter_guide"), padding="15")
        self.help_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        help_text = f"""
        {self.translator.t("help_proximity")}
        {self.translator.t("help_time")}
        {self.translator.t("help_animations")}
        """
        self.help_text_label = ttk.Label(self.help_frame, text=help_text, justify=tk.LEFT)
        self.help_text_label.grid(row=0, column=0, sticky=tk.W)
        
        analysis_frame.columnconfigure(0, weight=1)
        
    def setup_animation_tab(self):
        """Setup animation parameters tab using shared controls"""
        animation_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(animation_frame, text=self.translator.t("tab_animation"))
        
        # Animation settings header
        ttk.Label(animation_frame, text="Animation Configuration:", 
                 font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        # Create shared animation controls with all options
        if AnimationControlsFrame:
            self.animation_controls = AnimationControlsFrame(
                animation_frame, 
                include_time_buffer=True,  # Proximity analysis needs time buffer
                include_encounter_limit=True,  # Proximity analysis needs encounter limiting
                data_folder=self.data_folder  # Pass data folder for point count calculations
            )
            
            # Set initial values to match our variables
            self.animation_controls.time_buffer.set(self.time_buffer.get())
            self.animation_controls.trail_length.set(self.trail_length.get())
            self.animation_controls.time_step.set(self.time_step.get())
            self.animation_controls.limit_encounters.set(self.limit_encounters.get())
            
            # Create bindings to keep our variables synchronized
            self.animation_controls.time_buffer.trace('w', self._sync_time_buffer)
            self.animation_controls.trail_length.trace('w', self._sync_trail_length)
            self.animation_controls.time_step.trace('w', self._sync_time_step)
            self.animation_controls.limit_encounters.trace('w', self._sync_limit_encounters)
            
        else:
            # Fallback: create basic controls manually if import failed
            self.create_fallback_animation_controls(animation_frame)
        
        animation_frame.columnconfigure(0, weight=1)
    
    def _sync_time_buffer(self, *args):
        """Sync time buffer variable with animation controls"""
        if hasattr(self, 'animation_controls'):
            self.time_buffer.set(self.animation_controls.time_buffer.get())
    
    def _sync_trail_length(self, *args):
        """Sync trail length variable with animation controls"""
        if hasattr(self, 'animation_controls'):
            self.trail_length.set(self.animation_controls.trail_length.get())
    
    def _sync_time_step(self, *args):
        """Sync time step variable with animation controls"""
        if hasattr(self, 'animation_controls'):
            self.time_step.set(self.animation_controls.time_step.get())
    
    def _sync_limit_encounters(self, *args):
        """Sync limit encounters variable with animation controls"""
        if hasattr(self, 'animation_controls'):
            self.limit_encounters.set(self.animation_controls.limit_encounters.get())
        
    def setup_results_tab(self):
        """Setup results display tab"""
        results_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(results_frame, text=self.translator.t("tab_results"))
        
        # Results summary
        self.results_title_label = ttk.Label(results_frame, text="Analysis Results:", 
                 font=('Arial', 11, 'bold'))
        self.results_title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, width=70)
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Output files
        self.files_frame = ttk.LabelFrame(results_frame, text="Generated Files", padding="10")
        self.files_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.files_listbox = tk.Listbox(self.files_frame, height=6)
        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.files_listbox.bind('<Double-1>', self.open_selected_file)
        
        files_buttons = ttk.Frame(self.files_frame)
        files_buttons.grid(row=0, column=1, sticky=(tk.N))
        
        self.open_file_button = ttk.Button(files_buttons, text="📂 Open", 
                  command=self.open_selected_file)
        self.open_file_button.pack(pady=(0, 5))
        self.show_folder_button = ttk.Button(files_buttons, text="📁 Show in Folder", 
                  command=self.show_in_folder)
        self.show_folder_button.pack()
        
        self.files_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
    def setup_log_tab(self):
        """Setup log display tab"""
        log_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(log_frame, text=self.translator.t("tab_log"))
        
        self.log_title_label = ttk.Label(log_frame, text="Analysis Log:", 
                 font=('Arial', 11, 'bold'))
        self.log_title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25, width=80)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_buttons = ttk.Frame(log_frame)
        log_buttons.grid(row=2, column=0, pady=(10, 0))
        
        self.clear_log_button = ttk.Button(log_buttons, text="🗑 Clear Log", 
                  command=self.clear_log)
        self.clear_log_button.pack(side=tk.LEFT, padx=(0, 10))
        self.save_log_button = ttk.Button(log_buttons, text="💾 Save Log", 
                  command=self.save_log)
        self.save_log_button.pack(side=tk.LEFT)
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
    def update_proximity_label(self, value):
        """Update proximity threshold label"""
        self.proximity_label.config(text=f"{float(value):.1f} km")
        
    def update_time_label(self, value):
        """Update time threshold label"""
        self.time_label.config(text=f"{int(float(value))} min")
        
    def update_buffer_label(self, value):
        """Update time buffer label"""
        self.buffer_label.config(text=f"{float(value):.1f} hours")
        
    def update_trail_label(self, value):
        """Update trail length label"""
        self.trail_label.config(text=f"{float(value):.1f} hours")
        
    def update_limit_label(self, value):
        """Update encounter limit label"""
        limit = int(float(value))
        self.limit_label.config(text="No limit" if limit == 0 else f"{limit} encounters")
        
    def toggle_animation_options(self):
        """Enable/disable animation tab based on checkbox"""
        if self.generate_animations.get():
            self.notebook.tab(2, state='normal')  # Enable animation tab
        else:
            self.notebook.tab(2, state='disabled')  # Disable animation tab
            
    def browse_folder(self):
        """Browse for data folder"""
        folder = filedialog.askdirectory(title="Select GPS Data Folder", 
                                        initialdir=self.data_folder.get())
        if folder:
            self.data_folder.set(folder)
            self.refresh_data_preview()
            # Update point count in animation controls
            if hasattr(self, 'animation_controls'):
                self.animation_controls.update_data_folder(self.data_folder)
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder", 
                                        initialdir=self.output_folder.get())
        if folder:
            self.output_folder.set(folder)
            
    def refresh_data_preview(self):
        """Refresh the data preview"""
        self.data_preview.delete(1.0, tk.END)
        
        try:
            folder = self.data_folder.get()
            if not os.path.exists(folder):
                self.data_preview.insert(tk.END, self.translator.t("error_no_data", folder) + "\n")
                return
                
            csv_files = list(Path(folder).glob("*.csv"))
            
            if not csv_files:
                self.data_preview.insert(tk.END, self.translator.t("error_no_csv", folder) + "\n")
                return
                
            self.data_preview.insert(tk.END, self.translator.t("preview_folder", folder) + "\n")
            self.data_preview.insert(tk.END, self.translator.t("preview_found_files", len(csv_files)) + "\n\n")
            
            total_points = 0
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    points = len(df)
                    total_points += points
                    self.data_preview.insert(tk.END, self.translator.t("preview_file_ok", csv_file.name, points) + "\n")
                except Exception as e:
                    self.data_preview.insert(tk.END, self.translator.t("preview_file_error", csv_file.name, e) + "\n")
            
            self.data_preview.insert(tk.END, f"\n{self.translator.t('preview_total_points', total_points)}\n")
            
            if total_points > 100000:
                self.data_preview.insert(tk.END, f"\n{self.translator.t('error_large_dataset')}\n")
                
        except Exception as e:
            self.data_preview.insert(tk.END, self.translator.t("error_reading_folder", e) + "\n")
            
    def log(self, message):
        """Add message to log queue"""
        self.log_queue.put(message)
        
    def check_log_queue(self):
        """Check for new log messages"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, f"{message}\n")
                self.log_text.see(tk.END)
                self.root.update_idletasks()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_log_queue)
            
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        
    def save_log(self):
        """Save log to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Log File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Log saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {e}")
                
    def run_analysis(self):
        """Run the proximity analysis in a separate thread"""
        if self.analysis_thread and self.analysis_thread.is_alive():
            messagebox.showwarning("Warning", "Analysis is already running!")
            return
            
        # Validate inputs
        if not os.path.exists(self.data_folder.get()):
            messagebox.showerror("Error", "Please select a valid data folder!")
            return
            
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.files_listbox.delete(0, tk.END)
        self.output_files.clear()
        self.clear_log()
        
        # Update UI state
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running proximity analysis...")
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self._run_analysis_worker)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
    def stop_analysis(self):
        """Stop the running analysis"""
        if self.analysis_thread and self.analysis_thread.is_alive():
            # Note: This is a graceful stop - the thread will finish current operation
            self.log("🛑 Stop requested by user...")
            self.status_var.set("Stopping analysis...")
            
    def _run_analysis_worker(self):
        """Worker function for analysis thread"""
        try:
            self.log("🚀 Starting Vulture Proximity Analysis...")
            self.log(f"📁 Data folder: {self.data_folder.get()}")
            
            # Load data
            self.log("📊 Loading GPS data...")
            data_loader = DataLoader()
            data_loader.data_folder = self.data_folder.get()
            
            dataframes = data_loader.load_all_csv_files()
            
            if not dataframes:
                self.log("❌ No GPS data found!")
                return False
                
            self.log(f"✅ Loaded {len(dataframes)} GPS data files")
            
            # Initialize proximity engine
            proximity_engine = ProximityEngine()
            proximity_engine.load_dataframes(dataframes)
            
            # Set parameters
            proximity_engine.proximity_threshold_km = self.proximity_threshold.get()
            proximity_engine.min_duration_minutes = self.time_threshold.get()
            
            self.log(f"⚙️  Proximity threshold: {self.proximity_threshold.get()} km")
            self.log(f"⚙️  Time threshold: {self.time_threshold.get()} minutes")
            
            # Run proximity analysis
            self.log("🔍 Analyzing proximity events...")
            events = proximity_engine.analyze_proximity()
            
            if not events:
                self.log("⚠️  No proximity events found with current parameters")
                self.log("💡 Try increasing the proximity threshold or check your data")
                self._update_results("No proximity events found")
                return True
                
            self.log(f"✅ Found {len(events)} proximity events!")
            
            # Generate encounters animations if requested
            if self.generate_animations.get():
                self.log("🎬 Creating encounter animations...")
                self._create_animations(events, proximity_engine.gps_data)
            
            # Calculate statistics
            self.log("📊 Calculating statistics...")
            statistics = proximity_engine.calculate_statistics()
            
            # Create visualizations
            self.log("📈 Creating visualizations...")
            visualizer = ProximityVisualizer()
            visualizer.create_all_visualizations(events, statistics)
            
            # Export results
            self.log("💾 Exporting results...")
            events_df = proximity_engine.get_events_dataframe()
            
            from gps_utils import get_numbered_output_path
            output_path = get_numbered_output_path('proximity_events', 'analysis')
            output_path = output_path.replace('.html', '.csv')
            events_df.to_csv(output_path, index=False)
            self.output_files.append(output_path)
            self.log(f"📄 Events data saved to: {output_path}")
            
            # Update results display
            self._update_results_display(statistics, events)
            
            self.log("🎉 Proximity analysis completed successfully!")
            return True
            
        except Exception as e:
            self.log(f"❌ Analysis failed: {e}")
            return False
        finally:
            # Reset UI state
            self.root.after(0, self._analysis_finished)
            
    def _create_animations(self, events, gps_data):
        """Create encounter animations"""
        try:
            # Group events into encounters
            encounters = group_proximity_events(events)
            
            if not encounters:
                self.log("⚠️  No encounter groups found")
                return
                
            self.log(f"🎬 Found {len(encounters)} encounter group(s) to animate")
            
            # Apply encounter limit if set
            limit = self.limit_encounters.get()
            if limit > 0 and limit < len(encounters):
                encounters = encounters[:limit]
                self.log(f"⚡ Limited to first {limit} encounters for performance")
            
            # Parse time step
            time_step_seconds = parse_time_step(self.time_step.get())
            if time_step_seconds is None:
                time_step_seconds = 60  # Default to 1 minute
                
            animated_count = 0
            
            for i, encounter in enumerate(encounters, 1):
                try:
                    self.log(f"🎨 Creating animation for encounter {i}/{len(encounters)}...")
                    
                    # Create encounter dataset
                    from proximity_analysis import create_encounter_dataset
                    encounter_data = create_encounter_dataset(
                        encounter, gps_data, self.time_buffer.get()
                    )
                    
                    if encounter_data is None or len(encounter_data) == 0:
                        self.log(f"⚠️  No GPS data found for encounter {i}, skipping...")
                        continue
                    
                    # Create LiveMapAnimator with encounter data
                    animator = LiveMapAnimator()
                    animator.dataframes = encounter_data
                    animator.combined_data = pd.concat(encounter_data, ignore_index=True)
                    
                    # Configure for encounter animation
                    animator.selected_time_step = time_step_seconds
                    animator.trail_system.trail_length_minutes = self.trail_length.get() * 60
                    
                    # Create encounter-specific filename
                    base_name = f'encounter_{i}'
                    
                    # Create the visualization
                    success = animator.create_visualization(base_name=base_name)
                    
                    if success:
                        animated_count += 1
                        duration = encounter['duration_minutes']
                        vultures = ', '.join(encounter['vultures'])
                        self.log(f"✅ Encounter {i} animated: {vultures} ({duration:.1f} min)")
                        
                        # Add to output files list
                        # Note: Would need to get the actual output path from animator
                        
                    else:
                        self.log(f"⚠️  Failed to animate encounter {i}")
                        
                except KeyboardInterrupt:
                    self.log(f"⚠️  Animation interrupted at encounter {i}")
                    break
                except Exception as e:
                    self.log(f"❌ Error animating encounter {i}: {e}")
                    continue
            
            if animated_count > 0:
                self.log(f"🎉 Successfully created {animated_count} encounter animations!")
            else:
                self.log("⚠️  No encounter animations were created")
                
        except Exception as e:
            self.log(f"❌ Animation creation failed: {e}")
            
    def _update_results_display(self, statistics, events):
        """Update the results display"""
        try:
            results_text = f"""
🦅 VULTURE PROXIMITY ANALYSIS RESULTS
{'='*50}

📊 SUMMARY STATISTICS:
• Total proximity events: {statistics.total_events:,}
• Unique vulture pairs: {statistics.unique_pairs}
• Average distance: {statistics.average_distance_km:.2f} km
• Closest encounter: {statistics.closest_distance_km:.2f} km
• Total proximity time: {statistics.total_duration_hours:.1f} hours
• Most active pair: {statistics.most_active_pair}
• Peak activity hour: {statistics.peak_activity_hour}:00

🦅 EVENTS BY VULTURE:
"""
            for vulture, count in statistics.events_by_vulture.items():
                results_text += f"• {vulture}: {count} events\n"
                
            results_text += "\n⏰ EVENTS BY HOUR:\n"
            for hour in sorted(statistics.events_by_hour.keys()):
                count = statistics.events_by_hour[hour]
                results_text += f"• {hour:02d}:00: {count} events\n"
                
            # Update results in main thread
            self.root.after(0, lambda: self.results_text.insert(tk.END, results_text))
            
        except Exception as e:
            self.log(f"❌ Error updating results display: {e}")
            
    def _update_results(self, message):
        """Update results with a simple message"""
        self.root.after(0, lambda: self.results_text.insert(tk.END, message))
        
    def _analysis_finished(self):
        """Called when analysis is finished"""
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Analysis completed")
        
        # Update file list
        for file_path in self.output_files:
            self.files_listbox.insert(tk.END, os.path.basename(file_path))
            
    def open_selected_file(self, event=None):
        """Open the selected file"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.output_files):
                file_path = self.output_files[index]
                try:
                    webbrowser.open(f"file://{os.path.abspath(file_path)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file: {e}")
                    
    def show_in_folder(self):
        """Show selected file in folder"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.output_files):
                file_path = self.output_files[index]
                try:
                    folder_path = os.path.dirname(file_path)
                    self._open_file_manager(folder_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open folder: {e}")
                    
    def open_results_folder(self):
        """Open the results folder"""
        try:
            results_folder = os.path.join(os.path.dirname(__file__), '..', 'visualizations')
            results_folder = os.path.abspath(results_folder)
            self._open_file_manager(results_folder)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open results folder: {e}")
    
    def _open_file_manager(self, path):
        """Open system file manager at the specified path"""
        import platform
        import subprocess
        
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(['explorer', path])
            elif system == "Darwin":  # macOS
                subprocess.run(['open', path])
            else:  # Linux and other Unix-like systems
                subprocess.run(['xdg-open', path])
        except Exception:
            # Fallback to webbrowser if system file manager fails
            webbrowser.open(f"file://{path}")
            
    def show_help(self):
        """Show help dialog"""
        help_text = """
🦅 Vulture Proximity Analysis - Help

OVERVIEW:
This application analyzes GPS tracking data to identify when vultures are in close proximity to each other.

TABS:
📁 Data: Select your GPS data folder and preview files
⚙️ Analysis: Configure proximity detection parameters  
🎬 Animation: Configure encounter animation settings
📊 Results: View analysis results and statistics
📝 Log: Monitor analysis progress and messages

QUICK START:
1. Select your GPS data folder in the Data tab
2. Adjust proximity and time thresholds in Analysis tab
3. Optionally enable encounter animations
4. Click "Run Analysis" to start

TIPS:
• Use larger proximity thresholds for initial exploration
• Enable animations only for smaller datasets initially
• Check the log for detailed progress information
• Results are saved in the visualizations folder

For more information, visit the project documentation.
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Vulture Proximity Analysis")
        help_window.geometry("600x500")
        help_window.configure(bg='#f0f0f0')
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)


def main():
    """Main entry point for GUI application"""
    root = tk.Tk()
    ProximityAnalysisGUI(root)
    
    # Set window icon if available
    try:
        # You could add an icon file here
        # root.iconbitmap('vulture_icon.ico')
        pass
    except Exception:
        pass
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()

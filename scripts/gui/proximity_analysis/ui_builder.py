#!/usr/bin/env python3
"""
Proximity Analysis GUI - UI Layout Builder

Handles the creation and layout of all GUI components.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext


class ProximityUIBuilder:
    """Builds the UI layout for the Proximity Analysis GUI"""
    
    def __init__(self, config, event_handler, i18n_handler):
        self.config = config
        self.event_handler = event_handler
        self.i18n_handler = i18n_handler
    
    def setup_ui(self):
        """Set up the main user interface"""
        self._create_header()
        self._create_main_content()
        self._create_footer()
        
        # Update UI text with current language
        if self.i18n_handler:
            self.i18n_handler.update_ui_text()
    
    def _create_header(self):
        """Create the header with title and language selector"""
        # Header frame
        header_frame = ttk.Frame(self.config.root)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        # Title
        self.config.title_label = ttk.Label(
            header_frame, 
            text="Vulture Proximity Analysis", 
            font=('Arial', 16, 'bold')
        )
        self.config.title_label.pack(side='left')
        
        # Language selector
        lang_frame = ttk.Frame(header_frame)
        lang_frame.pack(side='right')
        
        ttk.Label(lang_frame, text="Language:").pack(side='left', padx=(0, 5))
        
        self.config.language_var = tk.StringVar(value="English")
        self.config.language_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.config.language_var,
            values=["English", "Deutsch"],
            state="readonly",
            width=10
        )
        self.config.language_dropdown.pack(side='left')
        self.config.language_dropdown.bind('<<ComboboxSelected>>', self.i18n_handler.change_language_dropdown)
    
    def _create_main_content(self):
        """Create the main content area with tabs"""
        # Create notebook for tabs
        self.config.notebook = ttk.Notebook(self.config.root)
        self.config.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self._create_data_tab()
        self._create_analysis_tab()
        self._create_animation_tab()
        self._create_results_tab()
        self._create_log_tab()
    
    def _create_footer(self):
        """Create the footer with controls and status"""
        # Footer frame
        footer_frame = ttk.Frame(self.config.root)
        footer_frame.pack(fill='x', padx=10, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(footer_frame)
        button_frame.pack(side='left')
        
        self.config.run_button = ttk.Button(
            button_frame,
            text="Run Analysis",
            command=self.event_handler.run_analysis,
            style='Accent.TButton'
        )
        self.config.run_button.pack(side='left', padx=(0, 5))
        
        self.config.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.event_handler.stop_analysis,
            state='disabled'
        )
        self.config.stop_button.pack(side='left', padx=(0, 5))
        
        self.config.open_results_button = ttk.Button(
            button_frame,
            text="Open Results",
            command=self.event_handler.open_results_folder
        )
        self.config.open_results_button.pack(side='left', padx=(0, 5))
        
        self.config.help_button = ttk.Button(
            button_frame,
            text="Help",
            command=self.event_handler.show_help
        )
        self.config.help_button.pack(side='left')
        
        # Status and progress
        status_frame = ttk.Frame(footer_frame)
        status_frame.pack(side='right', fill='x', expand=True)
        
        # Status label
        status_label = ttk.Label(status_frame, textvariable=self.config.status_var)
        status_label.pack(side='right', padx=(10, 0))
        
        # Progress bar
        self.config.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.config.progress_var,
            mode='indeterminate'
        )
        self.config.progress_bar.pack(side='right', padx=(10, 5), fill='x', expand=True)
    
    def _create_data_tab(self):
        """Create the data configuration tab"""
        data_frame = ttk.Frame(self.config.notebook)
        self.config.notebook.add(data_frame, text="Data")
        
        # Data folder selection
        folder_frame = ttk.LabelFrame(data_frame, text="Data Folder", padding=10)
        folder_frame.pack(fill='x', padx=10, pady=5)
        
        folder_path_frame = ttk.Frame(folder_frame)
        folder_path_frame.pack(fill='x')
        
        ttk.Entry(
            folder_path_frame,
            textvariable=self.config.data_folder,
            state='readonly'
        ).pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            folder_path_frame,
            text="Browse",
            command=self.event_handler.browse_folder
        ).pack(side='right', padx=(5, 0))
        
        # Data preview
        preview_frame = ttk.LabelFrame(data_frame, text="Data Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Preview table
        columns = ('File', 'Vulture ID', 'Records')
        self.config.data_preview = ttk.Treeview(preview_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.config.data_preview.heading(col, text=col)
            self.config.data_preview.column(col, width=150)
        
        # Scrollbar for preview
        preview_scroll = ttk.Scrollbar(preview_frame, orient='vertical', command=self.config.data_preview.yview)
        self.config.data_preview.configure(yscrollcommand=preview_scroll.set)
        
        self.config.data_preview.pack(side='left', fill='both', expand=True)
        preview_scroll.pack(side='right', fill='y')
        
        # Refresh button
        ttk.Button(
            preview_frame,
            text="Refresh",
            command=self.event_handler.refresh_data_preview
        ).pack(pady=(10, 0))
        
        # Initial data refresh
        self.event_handler.refresh_data_preview()
    
    def _create_analysis_tab(self):
        """Create the analysis configuration tab"""
        analysis_frame = ttk.Frame(self.config.notebook)
        self.config.notebook.add(analysis_frame, text="Analysis")
        
        # Analysis parameters
        params_frame = ttk.LabelFrame(analysis_frame, text="Analysis Parameters", padding=10)
        params_frame.pack(fill='x', padx=10, pady=5)
        
        # Proximity threshold
        proximity_frame = ttk.Frame(params_frame)
        proximity_frame.pack(fill='x', pady=2)
        
        ttk.Label(proximity_frame, text="Proximity Threshold (meters):").pack(side='left')
        proximity_scale = ttk.Scale(
            proximity_frame,
            from_=0.5,
            to=10.0,
            variable=self.config.proximity_threshold,
            orient='horizontal',
            command=self._update_proximity_label
        )
        proximity_scale.pack(side='left', fill='x', expand=True, padx=(10, 5))
        
        self.proximity_label = ttk.Label(proximity_frame, text=f"{self.config.proximity_threshold.get():.1f}m")
        self.proximity_label.pack(side='right')
        
        # Time threshold
        time_frame = ttk.Frame(params_frame)
        time_frame.pack(fill='x', pady=2)
        
        ttk.Label(time_frame, text="Time Threshold (minutes):").pack(side='left')
        time_scale = ttk.Scale(
            time_frame,
            from_=1,
            to=30,
            variable=self.config.time_threshold,
            orient='horizontal',
            command=self._update_time_label
        )
        time_scale.pack(side='left', fill='x', expand=True, padx=(10, 5))
        
        self.time_label = ttk.Label(time_frame, text=f"{self.config.time_threshold.get()}min")
        self.time_label.pack(side='right')
        
        # Output folder selection
        output_frame = ttk.LabelFrame(analysis_frame, text="Output Folder", padding=10)
        output_frame.pack(fill='x', padx=10, pady=5)
        
        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill='x')
        
        ttk.Entry(
            output_path_frame,
            textvariable=self.config.output_folder,
            state='readonly'
        ).pack(side='left', fill='x', expand=True)
        
        self.config.browse_output_button = ttk.Button(
            output_path_frame,
            text="Browse",
            command=self.event_handler.browse_output_folder
        )
        self.config.browse_output_button.pack(side='right', padx=(5, 0))
    
    def _create_animation_tab(self):
        """Create the animation configuration tab"""
        animation_frame = ttk.Frame(self.config.notebook)
        self.config.notebook.add(animation_frame, text="Animation")
        
        # Animation options
        anim_frame = ttk.LabelFrame(animation_frame, text="Animation Options", padding=10)
        anim_frame.pack(fill='x', padx=10, pady=5)
        # Note: animation/map generation is now performed on-demand after analysis
        info_label = ttk.Label(
            anim_frame,
            text="Map/animation generation is available after analysis in the Results tab.",
            wraplength=600
        )
        info_label.pack(anchor='w', pady=(0, 8))
        
        # Animation parameters (enabled when animations are enabled)
        self.anim_params_frame = ttk.Frame(anim_frame)
        self.anim_params_frame.pack(fill='x', pady=(10, 0))
        
        # Time buffer
        buffer_frame = ttk.Frame(self.anim_params_frame)
        buffer_frame.pack(fill='x', pady=2)
        
        ttk.Label(buffer_frame, text="Time Buffer (minutes):").pack(side='left')
        buffer_scale = ttk.Scale(
            buffer_frame,
            from_=0.5,
            to=10.0,
            variable=self.config.time_buffer,
            orient='horizontal',
            command=self._update_buffer_label
        )
        buffer_scale.pack(side='left', fill='x', expand=True, padx=(10, 5))
        
        self.buffer_label = ttk.Label(buffer_frame, text=f"{self.config.time_buffer.get():.1f}min")
        self.buffer_label.pack(side='right')
        
        # Trail length
        trail_frame = ttk.Frame(self.anim_params_frame)
        trail_frame.pack(fill='x', pady=2)
        
        ttk.Label(trail_frame, text="Trail Length (minutes):").pack(side='left')
        trail_scale = ttk.Scale(
            trail_frame,
            from_=0.5,
            to=10.0,
            variable=self.config.trail_length,
            orient='horizontal',
            command=self._update_trail_label
        )
        trail_scale.pack(side='left', fill='x', expand=True, padx=(10, 5))
        
        self.trail_label = ttk.Label(trail_frame, text=f"{self.config.trail_length.get():.1f}min")
        self.trail_label.pack(side='right')
        
        # Time step
        timestep_frame = ttk.Frame(self.anim_params_frame)
        timestep_frame.pack(fill='x', pady=2)
        
        ttk.Label(timestep_frame, text="Time Step:").pack(side='left')
        time_step_combo = ttk.Combobox(
            timestep_frame,
            textvariable=self.config.time_step,
            values=["30s", "1m", "2m", "5m", "10m"],
            state="readonly",
            width=10
        )
        time_step_combo.pack(side='left', padx=(10, 0))
        
        # Limit encounters
        limit_frame = ttk.Frame(self.anim_params_frame)
        limit_frame.pack(fill='x', pady=2)
        
        ttk.Label(limit_frame, text="Limit Encounters (0 = no limit):").pack(side='left')
        limit_scale = ttk.Scale(
            limit_frame,
            from_=0,
            to=50,
            variable=self.config.limit_encounters,
            orient='horizontal',
            command=self._update_limit_label
        )
        limit_scale.pack(side='left', fill='x', expand=True, padx=(10, 5))
        
        self.limit_label = ttk.Label(limit_frame, text=str(self.config.limit_encounters.get()))
        self.limit_label.pack(side='right')
    
    def _create_results_tab(self):
        """Create the results display tab"""
        results_frame = ttk.Frame(self.config.notebook)
        self.config.notebook.add(results_frame, text="Results")
        
        # Results display
        results_display_frame = ttk.LabelFrame(results_frame, text="Analysis Results", padding=10)
        results_display_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Results tree
        columns = ('Metric', 'Value')
        self.config.results_tree = ttk.Treeview(results_display_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.config.results_tree.heading(col, text=col)
            self.config.results_tree.column(col, width=200)
        
        # Scrollbar for results
        results_scroll = ttk.Scrollbar(results_display_frame, orient='vertical', command=self.config.results_tree.yview)
        self.config.results_tree.configure(yscrollcommand=results_scroll.set)
        
        self.config.results_tree.pack(side='left', fill='both', expand=True)
        results_scroll.pack(side='right', fill='y')
        
        # Bind double-click to open file
        self.config.results_tree.bind('<Double-1>', self.event_handler.open_selected_file)
        
        # Results actions
        results_actions_frame = ttk.Frame(results_frame)
        results_actions_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(
            results_actions_frame,
            text="Show in Folder",
            command=self.event_handler.show_in_folder
        ).pack(side='left', padx=(0, 5))

        ttk.Button(
            results_actions_frame,
            text="View Timeline",
            command=self.event_handler.view_timeline
        ).pack(side='left', padx=(0, 5))

        ttk.Button(
            results_actions_frame,
            text="Generate Map (Time Range)",
            command=self.event_handler.generate_map_for_timeframe
        ).pack(side='left', padx=(0, 5))
    
    def _create_log_tab(self):
        """Create the log display tab"""
        log_frame = ttk.Frame(self.config.notebook)
        self.config.notebook.add(log_frame, text="Log")
        
        # Log display
        log_display_frame = ttk.LabelFrame(log_frame, text="Analysis Log", padding=10)
        log_display_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Log text area
        self.config.log_text = scrolledtext.ScrolledText(
            log_display_frame,
            state='disabled',
            wrap='word',
            height=20
        )
        self.config.log_text.pack(fill='both', expand=True)
        
        # Log actions
        log_actions_frame = ttk.Frame(log_frame)
        log_actions_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(
            log_actions_frame,
            text="Clear Log",
            command=self.event_handler.clear_log
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            log_actions_frame,
            text="Save Log",
            command=self.event_handler.save_log
        ).pack(side='left')
    
    def _update_proximity_label(self, value):
        """Update proximity threshold label"""
        self.proximity_label.config(text=f"{float(value):.1f}m")
    
    def _update_time_label(self, value):
        """Update time threshold label"""
        self.time_label.config(text=f"{int(float(value))}min")
    
    def _update_buffer_label(self, value):
        """Update time buffer label"""
        self.buffer_label.config(text=f"{float(value):.1f}min")
    
    def _update_trail_label(self, value):
        """Update trail length label"""
        self.trail_label.config(text=f"{float(value):.1f}min")
    
    def _update_limit_label(self, value):
        """Update limit encounters label"""
        self.limit_label.config(text=str(int(float(value))))

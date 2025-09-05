#!/usr/bin/env python3
"""
GPS Live Map 2D Clean GUI - New Modular version using helper classes
"""

import tkinter as tk
import os
import sys
from datetime import datetime

# Add paths for importing components
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.extend([current_dir, parent_dir])

# Import helper modules
from helpers.scrollable_frame import ScrollableFrame
from helpers.mode_manager import ModeManager
from helpers.point_calculator import PointCalculator
from helpers.gui_sections import GUISections
from helpers.launcher import AnimationLauncher

print("Successfully imported modular components")


class ScrollableGUI:
    """Main GPS Animation Suite GUI using modular helper classes"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPS Animation Suite")
        self.root.geometry("600x700")
        
        # Language setting
        self.language = os.environ.get('GPS_ANALYSIS_LANGUAGE', 'en')
        
        # Initialize helper components
        self.mode_manager = ModeManager()
        self.point_calculator = PointCalculator()
        self.gui_sections = GUISections(self.get_language)
        self.launcher = AnimationLauncher(self.get_language)
        
        # Component references
        self.folder_manager = None
        self.data_preview = None
        self.settings_manager = None
        self.status_var = None
        
        self.setup_gui()
        self.center_window()
    
    def get_language(self):
        """Get current language"""
        return self.language
    
    def setup_gui(self):
        """Setup the complete GUI using helper classes"""
        # Create scrollable frame
        scrollable_frame = ScrollableFrame(self.root)
        content_frame = scrollable_frame.get_content_frame()
        
        # Status variable
        self.status_var = tk.StringVar(value="Ready")
        
        # Set up mode manager callback
        self.mode_manager.set_status_callback(self.update_status)
        
        # Create all GUI sections
        self.gui_sections.create_title_section(content_frame, self.mode_manager)
        self.gui_sections.create_status_section(content_frame, self.status_var)
        
        # Create folders section with callback
        self.folder_manager = self.gui_sections.create_folders_section(
            content_frame, 
            self.on_data_folder_changed
        )
        
        # Create data preview section
        self.data_preview = self.gui_sections.create_data_preview_section(
            content_frame, 
            self.folder_manager.data_folder
        )
        
        # Set up point calculator
        self.point_calculator.set_data_folder_var(self.folder_manager.data_folder)
        
        # Create settings section
        self.settings_manager = self.gui_sections.create_settings_section(
            content_frame, 
            self.point_calculator
        )

        # Create animation time range section (start / end)
        # These fields are added here rather than in GUISections to keep
        # this feature local and avoid modifying many helper files.
        self.start_time_var = tk.StringVar(value="")
        self.end_time_var = tk.StringVar(value="")
        self.use_full_range_var = tk.BooleanVar(value=True)
        self.create_time_range_section(content_frame)

        # Create buttons section
        self.gui_sections.create_buttons_section(
            content_frame,
            self.launch_selected_mode,
            self.root.destroy
        )
    
    def on_data_folder_changed(self, directory):
        """Callback when data folder changes"""
        print(f"Data folder changed to: {directory}")
        if self.status_var:
            self.status_var.set(f"Data folder: {directory}")
        
        # Refresh data preview when folder changes
        if self.data_preview:
            self.data_preview.refresh_preview()
            self.update_status()
        
        # Update point count calculation
        self.point_calculator.update_point_count_calculation()

        # Try to update start/end time defaults based on detected data
        try:
            self._update_time_defaults()
        except Exception:
            # non-fatal: continue without forcing a UI change
            pass
    
    def update_status(self):
        """Update status based on folder manager state"""
        if not self.data_preview:
            return
        
        file_count = self.data_preview.get_file_count()
        if file_count > 0:
            total_points = self.data_preview.get_total_points()
            mode_info = self.mode_manager.get_selected_mode_info()
            self.status_var.set(f"Ready | {file_count} files, {total_points} points | Mode: {mode_info['name']}")
        else:
            self.status_var.set("No GPS data files found")
    
    def launch_selected_mode(self):
        """Launch the selected animation mode"""
        def status_callback(message):
            if self.status_var:
                self.status_var.set(message)
                self.root.update()
        # Provide animation time range into settings_manager for the
        # AnimationLauncher to pick up. We add these attributes dynamically
        # so existing helper classes don't need to change.
        if self.settings_manager is not None:
            try:
                # If "use full range" is checked, clear entries so launcher
                # can interpret it as default/full range.
                if self.use_full_range_var.get():
                    setattr(self.settings_manager, 'animation_start_time', None)
                    setattr(self.settings_manager, 'animation_end_time', None)
                else:
                    setattr(self.settings_manager, 'animation_start_time', self.start_time_var.get())
                    setattr(self.settings_manager, 'animation_end_time', self.end_time_var.get())
            except Exception:
                # ignore failures here; launcher should handle missing data
                pass

        self.launcher.launch_selected_mode(
            self.mode_manager,
            self.folder_manager,
            self.settings_manager,
            status_callback
        )

    def create_time_range_section(self, parent):
        """Create GUI controls for animation start and end time."""
        frame = tk.LabelFrame(parent, text="Animation Time Range")
        frame.pack(fill=tk.X, padx=6, pady=6)

        # Start time
        start_label = tk.Label(frame, text="Start time:")
        start_label.grid(row=0, column=0, sticky=tk.W, padx=4, pady=2)
        self.start_entry = tk.Entry(frame, textvariable=self.start_time_var, width=30)
        self.start_entry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=2)
        # Inline error label
        self.start_error_label = tk.Label(frame, text="", fg="red", font=(None, 8))
        self.start_error_label.grid(row=0, column=2, sticky=tk.W, padx=6)

        # End time
        end_label = tk.Label(frame, text="End time:")
        end_label.grid(row=1, column=0, sticky=tk.W, padx=4, pady=2)
        self.end_entry = tk.Entry(frame, textvariable=self.end_time_var, width=30)
        self.end_entry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=2)
        # Inline error label
        self.end_error_label = tk.Label(frame, text="", fg="red", font=(None, 8))
        self.end_error_label.grid(row=1, column=2, sticky=tk.W, padx=6)

        # Use full detected range checkbox
        cb = tk.Checkbutton(frame, text="Use full data time range", variable=self.use_full_range_var, command=self._on_use_full_range_toggled)
        cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=4, pady=4)

        # Try to prefill or set UI based on checkbox state
        # Bind validation and editing hooks
        self.start_entry.bind('<FocusOut>', lambda e: self._validate_time_entry('start'))
        self.end_entry.bind('<FocusOut>', lambda e: self._validate_time_entry('end'))
        # On key press in either entry, uncheck full-range so user edits mean manual range
        self.start_entry.bind('<KeyRelease>', self._on_time_edited)
        self.end_entry.bind('<KeyRelease>', self._on_time_edited)

        try:
            # Initialize fields according to checkbox default (populate if checked)
            self._on_use_full_range_toggled()
        except Exception:
            pass

    def _on_use_full_range_toggled(self):
        """Toggle UI when use_full_range checkbox is changed."""
        if self.use_full_range_var.get():
            # Populate fields with detected range and disable manual entry
            try:
                detected = None
                if hasattr(self, 'data_preview') and self.data_preview is not None:
                    detected = getattr(self.data_preview, 'get_time_range', lambda: None)()
                if detected and isinstance(detected, (list, tuple)) and len(detected) >= 2:
                    start, end = detected[0], detected[1]
                    if isinstance(start, datetime):
                        self.start_time_var.set(start.isoformat(sep=' '))
                    else:
                        self.start_time_var.set(str(start))
                    if isinstance(end, datetime):
                        self.end_time_var.set(end.isoformat(sep=' '))
                    else:
                        self.end_time_var.set(str(end))
                else:
                    # fallback: clear
                    self.start_time_var.set("")
                    self.end_time_var.set("")
            except Exception:
                self.start_time_var.set("")
                self.end_time_var.set("")

            # Keep entries editable but re-run validation to clear or set errors
            try:
                self._validate_time_entry('start')
                self._validate_time_entry('end')
            except Exception:
                pass
        else:
            # Re-populate with detected values if present
            try:
                self._update_time_defaults(populate_if_missing=True)
            except Exception:
                pass
            # enable entries for manual editing
            try:
                self.start_entry.config(state='normal')
                self.end_entry.config(state='normal')
            except Exception:
                pass

    def _on_time_edited(self, event=None):
        """Handler for key edits inside time entry fields: uncheck full-range."""
        try:
            if self.use_full_range_var.get():
                self.use_full_range_var.set(False)
                # enable entries (they already are) and clear any errors until focus-out
                try:
                    self.start_entry.config(state='normal')
                    self.end_entry.config(state='normal')
                except Exception:
                    pass
        except Exception:
            pass

    def _parse_time_str(self, s):
        """Try parsing a time string into datetime. Returns datetime or None."""
        if not s or not s.strip():
            return None
        s = s.strip()
        fmts = ['%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']
        for fmt in fmts:
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        # fallback: try ISO parsing
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None

    def _validate_time_entry(self, which):
        """Validate an entry ('start' or 'end') and show inline error if invalid."""
        try:
            # Read and parse the typed value
            if which == 'start':
                s = self.start_time_var.get()
                dt = self._parse_time_str(s)
                if dt is None and s.strip():
                    self.start_error_label.config(text='Invalid time')
                    return False

                # If we have a detected data range, ensure the start is within bounds
                try:
                    detected = None
                    if hasattr(self, 'data_preview') and self.data_preview is not None:
                        detected = getattr(self.data_preview, 'get_time_range', lambda: None)()
                    if detected and isinstance(detected, (list, tuple)) and len(detected) >= 2 and dt is not None:
                        data_start, data_end = detected[0], detected[1]
                        # normalize detected to datetime if they are strings
                        if not isinstance(data_start, datetime):
                            data_start = self._parse_time_str(str(data_start))
                        if not isinstance(data_end, datetime):
                            data_end = self._parse_time_str(str(data_end))
                        if data_start and dt < data_start:
                            self.start_error_label.config(text='Before data start')
                            return False
                        if data_end and dt > data_end:
                            self.start_error_label.config(text='After data end')
                            return False
                except Exception:
                    # tolerate any detection failures and fall back to basic parsing
                    pass

                # Cross-field validation: if end is present, ensure start <= end
                try:
                    other_s = self.end_time_var.get()
                    other_dt = self._parse_time_str(other_s) if other_s and other_s.strip() else None
                    if other_dt is not None and dt is not None and dt > other_dt:
                        self.start_error_label.config(text='After end')
                        return False
                except Exception:
                    pass

                self.start_error_label.config(text='')
                return True

            elif which == 'end':
                s = self.end_time_var.get()
                dt = self._parse_time_str(s)
                if dt is None and s.strip():
                    self.end_error_label.config(text='Invalid time')
                    return False

                # Bounds check against detected data range if available
                try:
                    detected = None
                    if hasattr(self, 'data_preview') and self.data_preview is not None:
                        detected = getattr(self.data_preview, 'get_time_range', lambda: None)()
                    if detected and isinstance(detected, (list, tuple)) and len(detected) >= 2 and dt is not None:
                        data_start, data_end = detected[0], detected[1]
                        if not isinstance(data_start, datetime):
                            data_start = self._parse_time_str(str(data_start))
                        if not isinstance(data_end, datetime):
                            data_end = self._parse_time_str(str(data_end))
                        if data_end and dt > data_end:
                            self.end_error_label.config(text='After data end')
                            return False
                        if data_start and dt < data_start:
                            self.end_error_label.config(text='Before data start')
                            return False
                except Exception:
                    pass

                # Cross-field validation: if start is present, ensure start <= end
                try:
                    other_s = self.start_time_var.get()
                    other_dt = self._parse_time_str(other_s) if other_s and other_s.strip() else None
                    if other_dt is not None and dt is not None and dt < other_dt:
                        self.end_error_label.config(text='Before start')
                        return False
                except Exception:
                    pass

                self.end_error_label.config(text='')
                return True
        except Exception:
            return False

    def _update_time_defaults(self, populate_if_missing=False):
        """Attempt to detect data time range and populate start/end fields.

        This function tries to call helper methods on `data_preview` or
        `point_calculator` if they exist. It tolerantly falls back if those
        helpers don't expose a time-range API.
        """
        detected = None

        # Try common method names on data_preview
        if hasattr(self, 'data_preview') and self.data_preview is not None:
            for name in ('get_time_range', 'get_time_bounds', 'time_range'):
                fn = getattr(self.data_preview, name, None)
                if callable(fn):
                    try:
                        detected = fn()
                        break
                    except Exception:
                        detected = None

        # Fallback to point_calculator helpers
        if detected is None and hasattr(self, 'point_calculator') and self.point_calculator is not None:
            for name in ('get_time_range', 'get_time_bounds'):
                fn = getattr(self.point_calculator, name, None)
                if callable(fn):
                    try:
                        detected = fn()
                        break
                    except Exception:
                        detected = None

        # Detected should be a (start, end) tuple with datetime or string values
        if detected and isinstance(detected, (list, tuple)) and len(detected) >= 2:
            start, end = detected[0], detected[1]
            # Normalize datetimes to ISO strings if needed
            try:
                if isinstance(start, datetime):
                    start_str = start.isoformat(sep=' ')
                else:
                    start_str = str(start)
                if isinstance(end, datetime):
                    end_str = end.isoformat(sep=' ')
                else:
                    end_str = str(end)
            except Exception:
                start_str, end_str = str(start), str(end)

            # Populate fields only if checkbox is unchecked or populate_if_missing
            if (not self.use_full_range_var.get()) or populate_if_missing:
                if not self.start_time_var.get():
                    self.start_time_var.set(start_str)
                if not self.end_time_var.get():
                    self.end_time_var.set(end_str)

    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def run(self):
        """Start the GUI"""
        # Initial data refresh
        if self.data_preview:
            self.data_preview.refresh_preview()
            self.update_status()
        
        # Initial point count calculation
        self.point_calculator.update_point_count_calculation()
        
        self.root.mainloop()


def main():
    print("Starting modular GPS Animation Suite...")
    app = ScrollableGUI()
    app.run()
    print("GUI closed.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Launch Component for 2D Live Map GUI
Handles the actual map launching and process management
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import platform
import webbrowser


class LaunchManager:
    """Manages the launching of 2D live map animations"""
    
    def __init__(self, language_callback=None):
        self.get_language = language_callback or (lambda: 'en')
    
    def launch_map(self, folder_manager, settings_manager):
        """Launch the 2D live map with current configuration"""
        # Validate folders first
        issues = folder_manager.validate_folders()
        if issues:
            language = self.get_language()
            title = "Fehler" if language == "de" else "Error"
            # Check if main window still exists before showing dialog
            try:
                messagebox.showerror(title, "\n".join(issues))
            except tk.TclError:
                # Window was destroyed, just print the error
                print(f"GUI Error: {'; '.join(issues)}")
            return False
        
        # Get configuration
        config = settings_manager.get_config()
        data_folder = folder_manager.get_data_folder()
        output_folder = folder_manager.get_output_folder()
        
        # Find the animation script (now implemented under core/animation)
        script_path = os.path.join(os.path.dirname(__file__), "..", "..", "core", "animation", "animate_live_map.py")
        if not os.path.exists(script_path):
            language = self.get_language()
            if language == "de":
                error_msg = f"Skript nicht gefunden: {script_path}"
            else:
                error_msg = f"Script not found: {script_path}"
            try:
                messagebox.showerror("Fehler" if language == "de" else "Error", error_msg)
            except tk.TclError:
                print(f"GUI Error: {error_msg}")
            return False
        
        try:
            # Set environment variables for configuration
            env = os.environ.copy()
            env['GPS_DATA_DIR'] = data_folder
            env['OUTPUT_DIR'] = output_folder
            env['TRAIL_LENGTH_HOURS'] = str(config['trail_length'])
            env['TIME_STEP'] = config['time_step']
            env['PLAYBACK_SPEED'] = str(config.get('playback_speed', 1.0))
            env['PERFORMANCE_MODE'] = '1' if config['performance_mode'] else '0'
            env['EXPORT_MP4'] = '1' if config.get('export_mp4', False) else '0'
            env['ONLINE_MAP_MODE'] = '1' if config.get('online_map_mode', True) else '0'
            # (Precipitation overlay removed)
            
            # Set time window if provided by GUI
            start_time = getattr(settings_manager, 'animation_start_time', None)
            end_time = getattr(settings_manager, 'animation_end_time', None)
            if start_time:
                env['TIME_WINDOW_START'] = str(start_time)
            if end_time:
                env['TIME_WINDOW_END'] = str(end_time)
            
            # Launch the animation script
            language = self.get_language()
            if language == "de":
                print("🚀 Starte 2D Live Karte...")
            else:
                print("🚀 Launching 2D Live Map...")
            
            success, html_file_path = self._run_animation_script(script_path, env)
            
            if success:
                try:
                    offline_mode_used = env.get('ONLINE_MAP_MODE') == '0'
                    self._show_success_dialog(output_folder, html_file_path, offline_mode_used)
                except tk.TclError:
                    # Window was destroyed, just print success message
                    print(f"Animation completed successfully. Output: {output_folder}")
                return True
            else:
                return False
                
        except Exception as e:
            language = self.get_language()
            error_msg = f"Fehler beim Starten: {str(e)}" if language == "de" else f"Error launching: {str(e)}"
            try:
                messagebox.showerror("Fehler" if language == "de" else "Error", error_msg)
            except tk.TclError:
                print(f"GUI Error: {error_msg}")
            return False
    
    def _run_animation_script(self, script_path, env):
        """Run the animation script and wait for completion"""
        try:
            # Determine Python executable
            if getattr(sys, '_MEIPASS', False):
                # In bundle mode
                bundle_dir = sys._MEIPASS
                possible_python_paths = [
                    os.path.join(bundle_dir, 'python'),
                    os.path.join(bundle_dir, 'python3'),
                    'python3',
                    'python'
                ]
                
                python_exe = None
                for py_path in possible_python_paths:
                    if os.path.exists(py_path) or py_path in ['python3', 'python']:
                        python_exe = py_path
                        break
                
                if not python_exe:
                    python_exe = sys.executable
            else:
                # Development mode - try to use virtual environment if available
                venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.venv', 'bin', 'python')
                if os.path.exists(venv_python):
                    python_exe = venv_python
                    print(f"🐍 Using virtual environment Python: {python_exe}")
                else:
                    python_exe = sys.executable
            
            # Set GUI mode
            env['GUI_MODE'] = '1'
            
            # Run the script synchronously
            print(f"🚀 Launching animation script: {script_path}")
            process = subprocess.run([python_exe, script_path], env=env, 
                                   capture_output=True, text=True, timeout=600)
            
            # Parse output for HTML file path
            html_file_path = None
            if process.stdout:
                for line in process.stdout.split('\n'):
                    if 'Saved:' in line and '.html' in line:
                        html_file_path = line.split('Saved: ')[-1].strip()
                        break
            
            if process.returncode == 0:
                return True, html_file_path
            else:
                language = self.get_language()
                error_msg = process.stderr if process.stderr else "Unknown error"
                full_error = f"Script execution failed:\n{error_msg}"
                try:
                    messagebox.showerror("Fehler" if language == "de" else "Error", 
                                       "Skript-Ausführung fehlgeschlagen:\n{error_msg}" if language == "de" else full_error)
                except tk.TclError:
                    print(f"GUI Error: {full_error}")
                return False, None
                
        except subprocess.TimeoutExpired:
            language = self.get_language()
            error_msg = "Zeitüberschreitung beim Erstellen der Animation (10 Minuten)" if language == "de" else "Timeout while creating animation (10 minutes)"
            try:
                messagebox.showerror("Fehler" if language == "de" else "Error", error_msg)
            except tk.TclError:
                print(f"GUI Error: {error_msg}")
            return False, None
        except Exception as e:
            language = self.get_language()
            error_msg = f"Fehler beim Erstellen der Animation: {e}" if language == "de" else f"Error creating animation: {e}"
            try:
                messagebox.showerror("Fehler" if language == "de" else "Error", error_msg)
            except tk.TclError:
                print(f"GUI Error: {error_msg}")
            return False, None
    
    def _show_success_dialog(self, output_folder, html_file_path=None, offline_mode_used=False):
        """Show a success dialog with options to open output"""
        language = self.get_language()
        
        # Create custom dialog
        dialog = tk.Toplevel()
        if language == "de":
            dialog.title("Erfolg")
            message = "2D Live Karte erfolgreich erstellt!"
            folder_text = f"Ausgabeordner: {output_folder}"
            open_folder_btn_text = "📁 Ordner öffnen"
            open_html_btn_text = "🌐 HTML öffnen"
            close_btn_text = "Schließen"
        else:
            dialog.title("Success")
            message = "2D Live Map created successfully!"
            folder_text = f"Output folder: {output_folder}"
            open_folder_btn_text = "📁 Open Folder"
            open_html_btn_text = "🌐 Open HTML"
            close_btn_text = "Close"
        
        dialog.geometry("550x250")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Success message
        tk.Label(main_frame, text="✅", font=("Arial", 24)).pack(pady=(0, 10))
        tk.Label(main_frame, text=message, font=("Arial", 12, "bold")).pack(pady=(0, 5))
        tk.Label(main_frame, text=folder_text, font=("Arial", 9)).pack(pady=(0, 10))
        
        # HTML file info
        if html_file_path:
            html_filename = os.path.basename(html_file_path)
            if language == "de":
                html_text = f"HTML-Datei: {html_filename}"
            else:
                html_text = f"HTML file: {html_filename}"
            tk.Label(main_frame, text=html_text, font=("Arial", 9), fg="blue").pack(pady=(0, 10))
            
            # Add offline mode info only when offline mode was used
            if offline_mode_used:
                if language == "de":
                    offline_text = "Offline-Modus: Lokaler Server wird automatisch gestartet"
                else:
                    offline_text = "Offline mode: Local server will start automatically"
                tk.Label(main_frame, text=offline_text, font=("Arial", 8), fg="green").pack(pady=(0, 10))
        else:
            tk.Label(main_frame, text="", font=("Arial", 2)).pack(pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        # Open folder button
        tk.Button(button_frame, text=open_folder_btn_text, 
                 command=lambda: self._open_output_folder(output_folder)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Open HTML button
        if html_file_path:
            if offline_mode_used:
                tk.Button(button_frame, text=open_html_btn_text, 
                         command=lambda: self._open_html_with_server(html_file_path, output_folder)).pack(side=tk.LEFT, padx=(0, 10))
            else:
                tk.Button(button_frame, text=open_html_btn_text, 
                         command=lambda: self._open_html_file(html_file_path)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        tk.Button(button_frame, text=close_btn_text, command=dialog.destroy).pack(side=tk.LEFT)
        
        # Focus and bindings
        dialog.focus_set()
        dialog.bind('<Return>', lambda e: dialog.destroy())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def _open_output_folder(self, folder_path):
        """Open the output folder in the system file manager"""
        try:
            if os.path.exists(folder_path):
                system = platform.system()
                
                if system == "Windows":
                    subprocess.run(['explorer', folder_path], check=True)
                elif system == "Darwin":
                    subprocess.run(['open', folder_path], check=True)
                else:
                    subprocess.run(['xdg-open', folder_path], check=True)
                
                print(f"📁 Opened output folder: {folder_path}")
            else:
                language = self.get_language()
                error_msg = f"Ordner nicht gefunden: {folder_path}" if language == "de" else f"Folder not found: {folder_path}"
                try:
                    messagebox.showerror("Fehler" if language == "de" else "Error", error_msg)
                except tk.TclError:
                    print(f"GUI Error: {error_msg}")
        except Exception as e:
            language = self.get_language()
            error_msg = f"Fehler beim Öffnen des Ordners: {e}" if language == "de" else f"Failed to open folder: {e}"
            try:
                messagebox.showerror("Fehler" if language == "de" else "Error", error_msg)
            except tk.TclError:
                print(f"GUI Error: {error_msg}")
    
    def _open_html_file(self, html_file_path):
        """Open the generated HTML file in the default browser"""
        try:
            if html_file_path and os.path.exists(html_file_path):
                webbrowser.open(f"file://{os.path.abspath(html_file_path)}")
                print(f"🌐 Opened HTML file: {html_file_path}")
            else:
                language = self.get_language()
                error_msg = f"HTML-Datei nicht gefunden: {html_file_path}" if language == "de" else f"HTML file not found: {html_file_path}"
                try:
                    messagebox.showerror("Fehler" if language == "de" else "Error", error_msg)
                except tk.TclError:
                    print(f"GUI Error: {error_msg}")
        except Exception as e:
            language = self.get_language()
            error_msg = f"Fehler beim Öffnen der HTML-Datei: {e}" if language == "de" else f"Failed to open HTML file: {e}"
            try:
                messagebox.showerror("Fehler" if language == "de" else "Error", error_msg)
            except tk.TclError:
                print(f"GUI Error: {error_msg}")
    
    def _open_html_with_server(self, html_file_path, output_folder):
        """Open the generated HTML file with a local HTTP server for offline viewing"""
        try:
            if html_file_path and os.path.exists(html_file_path):
                # Start HTTP server in background
                import threading
                import http.server
                import socketserver
                
                # Find an available port
                port = 8000
                while port < 8100:
                    try:
                        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler):
                            break
                    except OSError:
                        port += 1
                
                # Create server in output folder
                os.chdir(output_folder)
                
                def start_server():
                    try:
                        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
                            print(f"🌐 Local server started on http://localhost:{port}")
                            httpd.serve_forever()
                    except Exception as e:
                        print(f"Server error: {e}")
                
                # Start server in background thread
                server_thread = threading.Thread(target=start_server, daemon=True)
                server_thread.start()
                
                # Wait a moment for server to start
                import time
                time.sleep(0.5)
                
                # Open HTML file with localhost URL
                html_filename = os.path.basename(html_file_path)
                localhost_url = f"http://localhost:{port}/{html_filename}"
                webbrowser.open(localhost_url)
                print(f"🌐 Opened offline HTML: {localhost_url}")
                
                language = self.get_language()
                if language == "de":
                    server_msg = f"Lokaler Server gestartet: http://localhost:{port}"
                else:
                    server_msg = f"Local server started: http://localhost:{port}"
                print(server_msg)
                
            else:
                language = self.get_language()
                error_msg = f"HTML-Datei nicht gefunden: {html_file_path}" if language == "de" else f"HTML file not found: {html_file_path}"
                try:
                    messagebox.showerror("Fehler" if language == "de" else "Error", error_msg)
                except tk.TclError:
                    print(f"GUI Error: {error_msg}")
        except Exception as e:
            language = self.get_language()
            error_msg = f"Fehler beim Öffnen der HTML-Datei: {e}" if language == "de" else f"Failed to open HTML file: {e}"
            try:
                messagebox.showerror("Fehler" if language == "de" else "Error", error_msg)
            except tk.TclError:
                print(f"GUI Error: {error_msg}")

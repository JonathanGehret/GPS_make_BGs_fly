#!/usr/bin/env python3
"""
GPS Analysis Suite - Auto Update System

Handles version checking and automatic updates for the GPS Analysis Suite.
"""

import os
import sys
import requests
import subprocess
import tempfile
import zipfile
import shutil
from pathlib import Path
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import messagebox

class UpdateManager:
    """Manages automatic updates for GPS Analysis Suite"""

    def __init__(self, current_version="1.0.0"):
        self.current_version = current_version
        self.repo_owner = "JonathanGehret"
        self.repo_name = "GPS_make_BGs_fly"
        self.github_api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        self.download_url = f"https://github.com/{self.repo_owner}/{self.repo_name}/archive/main.zip"

        # Get project root
        if getattr(sys, '_MEIPASS', False):
            # Running in PyInstaller bundle
            self.project_root = Path(sys._MEIPASS).parent
        else:
            # Running in development
            self.project_root = Path(__file__).parent.parent

    def get_latest_version(self):
        """Get the latest version from GitHub"""
        try:
            response = requests.get(f"{self.github_api_url}/releases/latest", timeout=10)
            if response.status_code == 200:
                release_data = response.json()
                return release_data['tag_name'], release_data['body']
            else:
                # Fallback: get latest commit info
                response = requests.get(f"{self.github_api_url}/commits/main", timeout=10)
                if response.status_code == 200:
                    commit_data = response.json()
                    return commit_data['sha'][:8], "Latest development version"
        except Exception as e:
            print(f"Failed to check for updates: {e}")
        return None, None

    def is_update_available(self):
        """Check if an update is available"""
        latest_version, _ = self.get_latest_version()
        if latest_version:
            return latest_version != self.current_version
        return False

    def download_update(self, progress_callback=None):
        """Download the latest version"""
        try:
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded_size += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            progress_callback(progress)

                return temp_file.name

        except Exception as e:
            print(f"Failed to download update: {e}")
            return None

    def install_update(self, zip_path, progress_callback=None):
        """Install the downloaded update"""
        try:
            # Create backup directory
            backup_dir = self.project_root / "backup"
            backup_dir.mkdir(exist_ok=True)

            # Extract update to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Find the extracted folder (GitHub zip includes repo name)
                extracted_dir = Path(temp_dir) / f"{self.repo_name}-main"

                if not extracted_dir.exists():
                    # Try alternative naming
                    extracted_dir = Path(temp_dir) / self.repo_name
                    if not extracted_dir.exists():
                        extracted_dir = Path(temp_dir)

                # Backup current version
                current_backup = backup_dir / f"backup_{self.current_version}"
                if self.project_root.exists():
                    shutil.copytree(self.project_root, current_backup, dirs_exist_ok=True)

                # Update files (skip certain directories)
                skip_dirs = {'.git', '__pycache__', '.venv', 'backup', 'node_modules'}

                for item in extracted_dir.rglob('*'):
                    if item.is_file():
                        # Skip certain directories
                        skip = False
                        for parent in item.parents:
                            if parent.name in skip_dirs:
                                skip = True
                                break

                        if not skip:
                            relative_path = item.relative_to(extracted_dir)
                            target_path = self.project_root / relative_path

                            # Create parent directories
                            target_path.parent.mkdir(parents=True, exist_ok=True)

                            # Copy file
                            shutil.copy2(item, target_path)

                            if progress_callback:
                                progress_callback(f"Updating: {relative_path}")

            # Clean up
            os.unlink(zip_path)

            return True

        except Exception as e:
            print(f"Failed to install update: {e}")
            return False

    def show_update_dialog(self, parent=None):
        """Show update dialog to user"""
        latest_version, release_notes = self.get_latest_version()

        if not latest_version:
            messagebox.showwarning("Update Check", "Unable to check for updates. Please try again later.")
            return

        if latest_version == self.current_version:
            messagebox.showinfo("Update Check", f"You have the latest version ({self.current_version})!")
            return

        # Create update dialog
        dialog = tk.Toplevel(parent) if parent else tk.Tk()
        dialog.title("Update Available")
        dialog.geometry("500x400")
        dialog.resizable(False, False)

        # Center the dialog
        dialog.transient(parent)
        dialog.grab_set()

        # Title
        title_label = ttk.Label(dialog, text="🦅 GPS Analysis Suite Update",
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Version info
        version_frame = ttk.Frame(dialog)
        version_frame.pack(fill='x', padx=20, pady=5)

        ttk.Label(version_frame, text=f"Current version: {self.current_version}").pack(anchor='w')
        ttk.Label(version_frame, text=f"Latest version: {latest_version}").pack(anchor='w')

        # Release notes
        notes_frame = ttk.LabelFrame(dialog, text="What's New", padding=10)
        notes_frame.pack(fill='both', expand=True, padx=20, pady=10)

        notes_text = tk.Text(notes_frame, wrap='word', height=8)
        scrollbar = ttk.Scrollbar(notes_frame, orient='vertical', command=notes_text.yview)
        notes_text.configure(yscrollcommand=scrollbar.set)

        notes_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        if release_notes:
            notes_text.insert('1.0', release_notes)
        else:
            notes_text.insert('1.0', "No release notes available.")

        notes_text.config(state='disabled')

        # Progress bar (initially hidden)
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(dialog, variable=progress_var, maximum=100)
        progress_bar.pack(fill='x', padx=20, pady=(0, 10))
        progress_bar.pack_forget()  # Hide initially

        # Status label
        status_label = ttk.Label(dialog, text="")
        status_label.pack(pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))

        def update_now():
            # Hide buttons, show progress
            update_button.pack_forget()
            skip_button.pack_forget()
            progress_bar.pack(fill='x', padx=20, pady=(0, 10))

            def progress_callback(value):
                if isinstance(value, int):
                    progress_var.set(value)
                    status_label.config(text=f"Downloading... {value}%")
                else:
                    status_label.config(text=value)
                dialog.update()

            # Download and install
            status_label.config(text="Downloading update...")
            zip_path = self.download_update(progress_callback)

            if zip_path:
                status_label.config(text="Installing update...")
                if self.install_update(zip_path, progress_callback):
                    status_label.config(text="✅ Update completed! Please restart the application.")
                    ttk.Button(button_frame, text="Restart Now",
                              command=lambda: restart_application()).pack(pady=5)
                else:
                    status_label.config(text="❌ Update failed. Please try again later.")
                    ttk.Button(button_frame, text="Close",
                              command=dialog.destroy).pack(pady=5)
            else:
                status_label.config(text="❌ Download failed. Please try again later.")
                ttk.Button(button_frame, text="Close",
                          command=dialog.destroy).pack(pady=5)

        def skip_update():
            dialog.destroy()

        def restart_application():
            # Restart the application
            python = sys.executable
            script = sys.argv[0]
            subprocess.Popen([python, script])
            sys.exit(0)

        update_button = ttk.Button(button_frame, text="Update Now", command=update_now)
        update_button.pack(side='left', padx=(0, 10))

        skip_button = ttk.Button(button_frame, text="Skip", command=skip_update)
        skip_button.pack(side='right')

        # Wait for dialog
        dialog.wait_window()

def check_for_updates(current_version="1.0.0", show_dialog=True, parent=None):
    """Convenience function to check for updates"""
    updater = UpdateManager(current_version)

    if show_dialog:
        updater.show_update_dialog(parent)
    else:
        return updater.is_update_available()

if __name__ == "__main__":
    # Test the update system
    updater = UpdateManager()
    print(f"Current version: {updater.current_version}")
    print(f"Update available: {updater.is_update_available()}")

    latest_version, notes = updater.get_latest_version()
    if latest_version:
        print(f"Latest version: {latest_version}")
        print(f"Release notes: {notes[:100]}...")
    else:
        print("Could not fetch latest version")

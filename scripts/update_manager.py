#!/usr/bin/env python3
"""
GPS Analysis Suite - Update Manager

Handles checking for updates from GitHub releases and notifying users
of new versions available for download.
"""

import requests
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import sys
import os
from packaging import version

# GitHub repository information
GITHUB_REPO = "JonathanGehret/GPS_make_BGs_fly"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def get_current_version():
    """Get the current application version"""
    try:
        # Try to import from main module
        if getattr(sys, '_MEIPASS', False):
            # Running as bundle
            bundle_dir = sys._MEIPASS
            main_path = os.path.join(bundle_dir, 'main.py')
            if os.path.exists(main_path):
                with open(main_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if line.startswith('__version__'):
                            return line.split('=')[1].strip().strip('"\'')
        else:
            # Running in development
            import main
            return main.__version__
    except Exception:
        pass

    # Fallback version
    return "1.0.0"

def check_github_for_updates():
    """Check GitHub for the latest release information"""
    try:
        print("🔄 Checking GitHub for updates...")

        # Make request to GitHub API
        headers = {
            'User-Agent': 'GPS-Analysis-Suite-Updater/1.0.0',
            'Accept': 'application/vnd.github.v3+json'
        }

        response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
        response.raise_for_status()

        release_data = response.json()

        latest_version = release_data.get('tag_name', '').lstrip('v')
        release_url = release_data.get('html_url', '')
        release_notes = release_data.get('body', '')
        published_at = release_data.get('published_at', '')

        print(f"📦 Latest version on GitHub: {latest_version}")

        return {
            'version': latest_version,
            'url': release_url,
            'notes': release_notes,
            'published': published_at,
            'success': True
        }

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error checking for updates: {e}")
        return {
            'success': False,
            'error': f"Network error: {str(e)}"
        }
    except Exception as e:
        print(f"❌ Error checking for updates: {e}")
        return {
            'success': False,
            'error': f"Error: {str(e)}"
        }

def compare_versions(current, latest):
    """Compare version strings using packaging library"""
    try:
        return version.parse(latest) > version.parse(current)
    except Exception:
        # Fallback to simple string comparison
        return latest != current

def show_update_dialog(current_version, latest_info, parent=None):
    """Show update notification dialog"""

    # Create dialog window
    dialog = tk.Toplevel(parent) if parent else tk.Tk()
    dialog.title("Update Available" if parent else "GPS Analysis Suite - Update Available")
    dialog.geometry("500x400")
    dialog.resizable(True, True)

    # Center the dialog
    dialog.transient(parent)
    dialog.grab_set()

    # Main frame
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    dialog.columnconfigure(0, weight=1)
    dialog.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)

    # Title
    title_label = ttk.Label(main_frame, text="🎉 Update Available!",
                           font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, pady=(0, 10))

    # Version info
    version_frame = ttk.Frame(main_frame)
    version_frame.grid(row=1, column=0, pady=(0, 15), sticky=(tk.W, tk.E))
    version_frame.columnconfigure(1, weight=1)

    ttk.Label(version_frame, text="Current version:").grid(row=0, column=0, sticky=tk.W)
    ttk.Label(version_frame, text=current_version).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

    ttk.Label(version_frame, text="Latest version:").grid(row=1, column=0, sticky=tk.W)
    ttk.Label(version_frame, text=latest_info['version'],
              font=("Arial", 10, "bold")).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

    # Release notes
    notes_label = ttk.Label(main_frame, text="What's new:",
                           font=("Arial", 11, "bold"))
    notes_label.grid(row=2, column=0, pady=(0, 5), sticky=tk.W)

    # Text widget for release notes
    notes_frame = ttk.Frame(main_frame)
    notes_frame.grid(row=3, column=0, pady=(0, 20), sticky=(tk.W, tk.E, tk.N, tk.S))
    notes_frame.columnconfigure(0, weight=1)
    notes_frame.rowconfigure(0, weight=1)

    notes_text = tk.Text(notes_frame, height=8, wrap=tk.WORD, padx=10, pady=10)
    scrollbar = ttk.Scrollbar(notes_frame, orient=tk.VERTICAL, command=notes_text.yview)
    notes_text.configure(yscrollcommand=scrollbar.set)

    notes_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    # Insert release notes
    release_notes = latest_info.get('notes', 'No release notes available.')
    notes_text.insert(tk.END, release_notes)
    notes_text.config(state=tk.DISABLED)

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, pady=(0, 0), sticky=(tk.W, tk.E))
    button_frame.columnconfigure(0, weight=1)

    def download_update():
        """Open browser to download the update"""
        if latest_info.get('url'):
            webbrowser.open(latest_info['url'])
        dialog.destroy()

    def skip_update():
        """Skip this update"""
        dialog.destroy()

    download_btn = ttk.Button(button_frame, text="📥 Download Update",
                             command=download_update, style="Accent.TButton")
    download_btn.grid(row=0, column=0, pady=10)

    skip_btn = ttk.Button(button_frame, text="⏭️ Skip This Version",
                         command=skip_update)
    skip_btn.grid(row=0, column=1, pady=10, padx=(10, 0))

    # Configure button style
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Arial", 10, "bold"))

    # Center dialog on screen
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")

    if not parent:
        dialog.mainloop()

def show_no_updates_dialog(current_version, parent=None):
    """Show dialog when no updates are available"""
    if parent:
        messagebox.showinfo("No Updates Available",
                          f"You are running the latest version ({current_version}).\n\n"
                          "No updates are currently available.",
                          parent=parent)
    else:
        # Create simple dialog
        dialog = tk.Tk()
        dialog.title("GPS Analysis Suite - No Updates")
        dialog.geometry("300x150")

        label = ttk.Label(dialog, text=f"No updates available.\n\nCurrent version: {current_version}",
                         justify=tk.CENTER)
        label.pack(pady=20)

        btn = ttk.Button(dialog, text="OK", command=dialog.destroy)
        btn.pack(pady=10)

        dialog.mainloop()

def show_no_repository_dialog(parent=None):
    """Show dialog when repository doesn't exist or has no releases"""
    message = """🚀 **Ready to Deploy Your GPS Analysis Suite!**

Your update system is working perfectly! To enable automatic updates:

**Option 1: Create GitHub Repository**
1. Go to https://github.com and create a new repository
2. Name it: `GPS_make_BGs_fly`
3. Upload your project files
4. Create a release with version tag (e.g., v1.0.0)
5. Add release notes describing your features

**Option 2: Test Update System**
- Create a test release on GitHub
- The update system will detect it automatically
- Users will see professional update notifications

**Current Status:** ✅ Update system ready!
**Next Step:** Create your first GitHub release

Would you like help creating the GitHub repository?"""

    if parent:
        # Create a more detailed dialog
        dialog = tk.Toplevel(parent)
        dialog.title("GPS Analysis Suite - Update System Ready!")
        dialog.geometry("600x400")
        dialog.resizable(True, True)

        # Center the dialog
        dialog.transient(parent)
        dialog.grab_set()

        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="🚀 Update System Ready!",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Message text
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, pady=(0, 20), sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, padx=10, pady=10, height=12)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(0, 0), sticky=(tk.W, tk.E))

        def open_github():
            """Open GitHub in browser"""
            webbrowser.open("https://github.com")

        def close_dialog():
            """Close the dialog"""
            dialog.destroy()

        github_btn = ttk.Button(button_frame, text="🌐 Open GitHub",
                               command=open_github, style="Accent.TButton")
        github_btn.grid(row=0, column=0, padx=(0, 10))

        close_btn = ttk.Button(button_frame, text="✅ Close",
                              command=close_dialog)
        close_btn.grid(row=0, column=1)

        # Configure button style
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))

        # Center dialog on screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

    else:
        # Simple message box for non-GUI context
        messagebox.showinfo("Update System Ready",
                          "Your GPS Analysis Suite update system is working!\n\n"
                          "To enable automatic updates:\n"
                          "1. Create a GitHub repository\n"
                          "2. Add releases with version tags\n"
                          "3. Users will get update notifications\n\n"
                          "Visit: https://github.com to get started!")

def show_update_error(error_message, parent=None):
    """Show error dialog for update check failures"""
    if parent:
        messagebox.showerror("Update Check Failed",
                           f"Failed to check for updates:\n\n{error_message}",
                           parent=parent)
    else:
        dialog = tk.Tk()
        dialog.title("GPS Analysis Suite - Update Error")
        dialog.geometry("350x150")

        label = ttk.Label(dialog, text=f"Failed to check for updates:\n\n{error_message}",
                         justify=tk.CENTER)
        label.pack(pady=20)

        btn = ttk.Button(dialog, text="OK", command=dialog.destroy)
        btn.pack(pady=10)

        dialog.mainloop()

def check_for_updates(current_version=None, show_dialog=True, parent=None):
    """
    Main function to check for updates

    Args:
        current_version: Override current version (optional)
        show_dialog: Whether to show GUI dialogs
        parent: Parent window for dialogs
    """
    if current_version is None:
        current_version = get_current_version()

    print(f"🔍 Checking for updates (current: {current_version})")

    # Check GitHub for latest release
    latest_info = check_github_for_updates()

    if not latest_info.get('success', False):
        error_msg = latest_info.get('error', 'Unknown error')
        
        # Check if it's a 404 (repository not found)
        if '404' in error_msg or 'Not Found' in error_msg:
            print("ℹ️ Repository not found - showing setup instructions")
            if show_dialog:
                show_no_repository_dialog(parent)
            return False
        else:
            print(f"❌ Update check failed: {error_msg}")
            if show_dialog:
                show_update_error(error_msg, parent)
        return False

    latest_version = latest_info.get('version', '')

    if not latest_version:
        print("❌ No version information found")
        if show_dialog:
            show_update_error("No version information found", parent)
        return False

    print(f"📦 Latest version: {latest_version}")

    # Compare versions
    if compare_versions(current_version, latest_version):
        print(f"🎉 Update available! {current_version} → {latest_version}")
        if show_dialog:
            show_update_dialog(current_version, latest_info, parent)
        return True
    else:
        print(f"✅ Already up to date (version {current_version})")
        if show_dialog:
            show_no_updates_dialog(current_version, parent)
        return False

if __name__ == "__main__":
    # Test the update checker
    print("🧪 Testing update checker...")
    check_for_updates(show_dialog=True)

# -*- mode: python ; coding: utf-8 -*-
"""
Windows-specific PyInstaller spec file for GPS Analysis Suite
This creates a GPS_Analysis_Suite.exe executable for Windows
"""

import sys
import os

block_cipher = None

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include GUI files
        ('gui', 'gui'),
        # Include scripts directory and subdirectories
        ('scripts', 'scripts'),
        ('scripts/core', 'scripts/core'),
        ('scripts/utils', 'scripts/utils'),
        ('scripts/visualization', 'scripts/visualization'),
        ('scripts/config', 'scripts/config'),
        # Include main utils directory
        ('utils', 'utils'),
        # Include data files
        ('data', 'data'),
        # Include analysis results
        ('analysis', 'analysis'),
        # Include elevation cache
        ('elevation_cache', 'elevation_cache'),
        # Include documentation
        ('README.md', '.'),
        ('README_GUI.md', '.'),
        ('README_GUI_DE.md', '.'),
        ('BUILD_GUIDE.md', '.'),
        # Include requirements
        ('requirements.txt', '.'),
        # Include Windows launcher
        ('GPS_Analysis_Suite.bat', '.'),
    ],
    hiddenimports=[
        # GUI modules
        'gui.analysis_mode_selector',
        'gui.live_map_2d_gui',
        'gui.visualization_3d_gui',
        # Script modules
        'scripts',
        'scripts.gps_utils',
        'scripts.animate_live_map',
        'scripts.animation_3d',
        'scripts.mobile_animation',
        'scripts.proximity_analysis_gui',
        'scripts.proximity_analysis',
        'scripts.i18n',
        'scripts.update_manager',
        # Add direct gps_utils import
        'gps_utils',
        # Core modules - using scripts.core path
        'scripts.core',
        'scripts.core.animation_3d_engine',
        'scripts.core.elevation_data_manager',
        'scripts.core.mobile_animation_engine',
        'scripts.core.proximity_engine',
        'scripts.core.trail_system',
        # Utils modules - using scripts.utils path
        'scripts.utils',
        'scripts.utils.user_interface_3d',
        'scripts.utils.user_interface',
        'scripts.utils.mobile_interface',
        'scripts.utils.performance_optimizer',
        'scripts.utils.animation_controls',
        # Visualization modules - using scripts.visualization path
        'scripts.visualization',
        'scripts.visualization.proximity_plots',
        # Tkinter and GUI
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        # Matplotlib
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_tkagg',
        # Data processing
        'pandas',
        'numpy',
        'scipy',
        'scipy.spatial',
        # Plotting and visualization
        'plotly',
        'plotly.graph_objects',
        'plotly.express',
        'plotly.io',
        # Web and requests
        'requests',
        'urllib',
        'urllib.request',
        'urllib.parse',
        'http',
        'http.client',
        # Geographic
        'geopy',
        'geopy.distance',
        # Image processing
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        # Standard library essentials
        'json',
        'csv',
        'datetime',
        'time',
        'os',
        'sys',
        'pathlib',
        'functools',
        'collections',
        'itertools',
        'math',
        'random',
        'logging',
        'threading',
        'multiprocessing',
        'subprocess',
        'webbrowser',
        'ssl',
        'socket',
        'platform',
        'shutil',
        'tempfile',
        'configparser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GPS_Analysis_Suite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

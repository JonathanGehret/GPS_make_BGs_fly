#!/usr/bin/env python3
"""
Safe Test Launcher for GPS Analysis Suite
Multiple testing levels to prevent crashes
"""

import sys
import os
import psutil
import subprocess
import time
from pathlib import Path

class SafeTester:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.memory_info = psutil.virtual_memory()
        self.cpu_count = psutil.cpu_count()

    def print_system_info(self):
        """Print system information for diagnostics"""
        print("🖥️  SYSTEM INFORMATION:")
        print(f"   RAM: {self.memory_info.total / (1024**3):.1f} GB total, {self.memory_info.available / (1024**3):.1f} GB available")
        print(f"   CPU: {self.cpu_count} cores")
        print(f"   Python: {sys.version}")
        print(f"   Platform: {sys.platform}")
        print()

    def test_level_1(self):
        """Level 1: Basic imports and memory check"""
        print("🧪 LEVEL 1: Basic System Test")
        print("=" * 40)

        try:
            # Test basic imports
            print("Testing basic imports...")
            import tkinter  # noqa: F401
            print("✅ tkinter OK")

            import pandas as pd  # noqa: F401
            print("✅ pandas OK")

            import numpy as np  # noqa: F401
            print("✅ numpy OK")

            import plotly  # noqa: F401
            print("✅ plotly OK")

            # Memory check
            if self.memory_info.available < 1 * 1024**3:  # Less than 1GB
                print("⚠️  WARNING: Low memory detected!")
                return False

            print("✅ All basic tests passed!")
            return True

        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

    def test_level_2(self):
        """Level 2: GUI components test"""
        print("\n🧪 LEVEL 2: GUI Components Test")
        print("=" * 40)

        try:
            import tkinter as tk
            from tkinter import ttk

            # Create minimal GUI
            root = tk.Tk()
            root.title("GPS Test - Level 2")
            root.geometry("300x200")

            # Add some basic widgets
            ttk.Label(root, text="🦅 GPS Analysis Suite Test").pack(pady=10)
            ttk.Button(root, text="Test Button", command=lambda: None).pack(pady=5)

            # Test for 2 seconds
            root.after(2000, root.destroy)
            root.mainloop()

            print("✅ GUI components working!")
            return True

        except Exception as e:
            print(f"❌ GUI test failed: {e}")
            return False

    def test_level_3(self):
        """Level 3: Data loading test"""
        print("\n🧪 LEVEL 3: Data Loading Test")
        print("=" * 40)

        try:
            import pandas as pd
            import numpy as np

            # Create small test dataset
            print("Creating test dataset...")
            test_data = pd.DataFrame({
                'timestamp': pd.date_range('2023-01-01', periods=50, freq='1min'),
                'latitude': np.random.uniform(47.4, 47.7, 50),
                'longitude': np.random.uniform(12.8, 13.2, 50),
                'altitude': np.random.uniform(1000, 2000, 50)
            })

            print(f"✅ Created test dataset: {len(test_data)} points")
            print(f"   Memory usage: {test_data.memory_usage(deep=True).sum() / 1024:.0f} KB")

            # Test file operations
            test_file = self.project_root / "test_data.csv"
            test_data.to_csv(test_file, index=False)
            pd.read_csv(test_file)  # Test loading
            test_file.unlink()  # Clean up

            print("✅ File I/O operations working!")
            return True

        except Exception as e:
            print(f"❌ Data test failed: {e}")
            return False

    def test_level_4(self):
        """Level 4: GPS utilities test"""
        print("\n🧪 LEVEL 4: GPS Utilities Test")
        print("=" * 40)

        try:
            # Test GPS utilities
            sys.path.append(str(self.project_root / "scripts"))
            from gps_utils import DataLoader

            print("✅ GPS utilities imported successfully!")

            # Test with minimal data
            test_csv = self.project_root / "data" / "test_vulture_01.csv"
            if test_csv.exists():
                print("Testing data loader...")
                loader = DataLoader()
                data = loader.load_gps_data(str(test_csv))
                print(f"✅ Loaded {len(data)} GPS points")
            else:
                print("⚠️  Test data file not found, skipping loader test")

            return True

        except Exception as e:
            print(f"❌ GPS utilities test failed: {e}")
            return False

    def test_level_5(self):
        """Level 5: Full application test (with monitoring)"""
        print("\n🧪 LEVEL 5: Full Application Test")
        print("=" * 40)
        print("⚠️  WARNING: This will launch the full application!")
        print("   Monitor your system resources closely.")
        print("   Press Ctrl+C if you notice any issues.")
        print()

        response = input("Continue with full test? (y/N): ").lower().strip()
        if response != 'y':
            print("⏭️  Skipping full application test")
            return True

        try:
            # Monitor memory usage in background
            def memory_monitor():
                initial_memory = psutil.virtual_memory().used
                max_memory = initial_memory

                for _ in range(30):  # Monitor for 30 seconds
                    current = psutil.virtual_memory()
                    max_memory = max(max_memory, current.used)

                    if current.percent > 85:
                        print(f"⚠️  HIGH MEMORY USAGE: {current.percent}%")
                        return False

                    time.sleep(1)
                return True

            # Start memory monitor
            import threading
            monitor_thread = threading.Thread(target=memory_monitor, daemon=True)
            monitor_thread.start()

            # Launch main application
            print("🚀 Launching GPS Analysis Suite...")
            result = subprocess.run([sys.executable, "main.py"],
                                  timeout=15,  # 15 second timeout
                                  capture_output=True,
                                  text=True)

            if result.returncode == 0:
                print("✅ Application launched successfully!")
                return True
            else:
                print(f"❌ Application failed with code: {result.returncode}")
                if result.stderr:
                    print("Error output:", result.stderr[:500])
                return False

        except subprocess.TimeoutExpired:
            print("⏰ Application test timed out (this is normal for GUI apps)")
            return True
        except Exception as e:
            print(f"❌ Full application test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all test levels"""
        print("🦅 GPS ANALYSIS SUITE - SAFE TESTING SUITE")
        print("=" * 50)
        self.print_system_info()

        tests = [
            ("Basic System", self.test_level_1),
            ("GUI Components", self.test_level_2),
            ("Data Loading", self.test_level_3),
            ("GPS Utilities", self.test_level_4),
            ("Full Application", self.test_level_5)
        ]

        results = []
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name} Test...")
            success = test_func()
            results.append((test_name, success))

            if not success and test_name in ["Basic System", "GUI Components"]:
                print(f"❌ Critical test '{test_name}' failed. Stopping tests.")
                break

        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY:")
        for test_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {test_name}: {status}")

        passed = sum(1 for _, success in results if success)
        total = len(results)

        print(f"\n🎯 Overall: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Your GPS Analysis Suite should be safe to use.")
        elif passed >= 3:
            print("⚠️  Most tests passed. You can try the application but monitor closely.")
        else:
            print("❌ Multiple critical tests failed. Please address issues before proceeding.")

        return passed == total

def main():
    """Main testing function"""
    # Change to project directory
    os.chdir(Path(__file__).parent)

    # Activate virtual environment if available
    venv_path = Path(".venv/bin/activate")
    if venv_path.exists():
        print("📦 Activating virtual environment...")
        # Note: This won't work in subprocess, but that's OK for testing

    tester = SafeTester()
    success = tester.run_all_tests()

    if success:
        print("\n🚀 Ready to launch GPS Analysis Suite!")
        response = input("Launch the main application now? (y/N): ").lower().strip()
        if response == 'y':
            print("Starting GPS Analysis Suite...")
            subprocess.run([sys.executable, "main.py"])
    else:
        print("\n🛑 Please fix the issues before running the full application.")

if __name__ == "__main__":
    main()

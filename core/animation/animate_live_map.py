#!/usr/bin/env python3
"""
Thin entrypoint for the Live Map Animation. Delegates to app.live_map_animator.
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from live_map_animator import run_live_map_cli


def main():
    sys.exit(run_live_map_cli())


if __name__ == "__main__":
    main()

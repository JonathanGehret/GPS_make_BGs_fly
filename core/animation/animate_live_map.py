#!/usr/bin/env python3
"""
Thin entrypoint for the Live Map Animation. Delegates to app.live_map_animator.
"""

import sys

from live_map_animator import run_live_map_cli


def main():
    sys.exit(run_live_map_cli())


if __name__ == "__main__":
    main()

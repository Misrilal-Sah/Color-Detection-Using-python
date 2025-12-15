"""
Color Detection Application
A modern, offline-capable color detection application using Python, OpenCV, and CustomTkinter.
"""

import os
import sys

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.app import ColorDetectionApp


def main():
    """Main entry point for the application."""
    app = ColorDetectionApp()
    app.run()


if __name__ == "__main__":
    main()

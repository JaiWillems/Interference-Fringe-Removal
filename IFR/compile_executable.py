"""Executable compilation script.

This script executes the appropriate commands to convert the
Interference-Fringe-Removal program into a single executable file.
"""

import PyInstaller.__main__


PyInstaller.__main__.run([
    "IFR/main.py",  # Top level file.
    "--name",
    "IFR_v0.1-beta_3",  # Executable name.
    "--onefile",  # Compile into one file.
    "--windowed",  # Remove a console when the application is running.
    "--icon",
    "IFR/figures/IFR_logo.ico"  # Add an icon to the application file.
])

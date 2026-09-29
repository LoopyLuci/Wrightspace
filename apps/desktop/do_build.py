#!/usr/bin/env python3
"""Build script that actually runs PyInstaller to create WebBuilder.exe."""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def main():
    print("=" * 60)
    print("WebBuilder Desktop - Build Script")
    print("=" * 60)
    
    # Check PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    # Clean previous builds
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ Cleaned {folder}/")
    
    # PyInstaller command - using cleaned up spec
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=WebBuilder",
        "--windowed",
        "--onefile",
        "--icon=NONE",
        "--add-data=webbuilder;webbuilder",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=numpy",
        "webbuilder_desktop.py"
    ]
    
    print("\nBuilding executable...")
    print("This may take several minutes...\n")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        print(f"\nExecutable: dist/WebBuilder.exe")
        print(f"Size: {os.path.getsize('dist/WebBuilder.exe') / (1024*1024):.1f} MB")
    else:
        print("\nBUILD FAILED")
        return False
    
    return True

if __name__ == "__main__":
    main()

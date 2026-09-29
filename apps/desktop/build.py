#!/usr/bin/env python3
"""WebBuilder Desktop - Build script for distribution."""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def build_executable():
    """Build standalone executable with PyInstaller."""
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
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=WebBuilder",
        "--windowed",  # No console window
        "--onefile",   # Single executable
        "--icon=NONE",  # Add icon path here if available
        "--add-data=webbuilder;webbuilder",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=webbuilder.ml_engine",
        "--hidden-import=webbuilder.ml_engine.core",
        "--hidden-import=webbuilder.ml_engine.models",
        "--hidden-import=webbuilder.ml_engine.data",
        "--hidden-import=webbuilder.ml_engine.training",
        "--hidden-import=webbuilder.gui.chat_panel",
        "--hidden-import=webbuilder.gui.chat_enhanced",
        "--hidden-import=webbuilder.gui.form_builder_dialog",
        "--hidden-import=webbuilder.gui.feedback_dialog",
        "--hidden-import=numpy",
        "--hidden-import=aiohttp",
        "--hidden-import=jwt",
        "--hidden-import=flask",
        "--hidden-import=flask_sqlalchemy",
        "--hidden-import=flask_login",
        "--hidden-import=flask_limiter",
        "--hidden-import=flask_cors",
        "--hidden-import=werkzeug",
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


def create_installer():
    """Create Windows installer using NSIS (if available)."""
    print("\n" + "=" * 60)
    print("Creating Installer")
    print("=" * 60)
    
    nsis_script = """
; WebBuilder Installer Script
!include "MUI2.nsh"

; App info
!define APP_NAME "WebBuilder Desktop"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "WebBuilder"
!define APP_DIR "$PROGRAMFILES\\WebBuilder"
!define APP_EXE "WebBuilder.exe"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "dist/WebBuilder-Setup.exe"
InstallDir "${APP_DIR}"
RequestExecutionLevel admin

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Sections
Section "Install"
    SetOutPath "$INSTDIR"
    File "dist\\WebBuilder.exe"
    
    ; Include ML Engine data directory
    SetOutPath "$INSTDIR\\ml_engine"
    File /r "ml_engine\\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\WebBuilder"
    CreateShortcut "$SMPROGRAMS\\WebBuilder\\WebBuilder.lnk" "$INSTDIR\\WebBuilder.exe"
    CreateShortcut "$DESKTOP\\WebBuilder.lnk" "$INSTDIR\\WebBuilder.exe"
    
    ; Uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    CreateShortcut "$SMPROGRAMS\\WebBuilder\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    
    ; Registry
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\WebBuilder" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\WebBuilder" "UninstallString" "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\WebBuilder.exe"
    Delete "$INSTDIR\\uninstall.exe"
    RMDir /r "$INSTDIR\\ml_engine"
    RMDir "$INSTDIR"
    Delete "$SMPROGRAMS\\WebBuilder\\*.lnk"
    RMDir "$SMPROGRAMS\\WebBuilder"
    Delete "$DESKTOP\\WebBuilder.lnk"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\WebBuilder"
SectionEnd
"""
    
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    print("✓ NSIS script created: installer.nsi")
    print("  Install NSIS from https://nsis.sourceforge.io to compile")


def create_portable_version():
    """Create portable ZIP distribution."""
    print("\n" + "=" * 60)
    print("Creating Portable Version")
    print("=" * 60)
    
    import zipfile
    
    portable_dir = "dist/WebBuilder-Portable"
    os.makedirs(portable_dir, exist_ok=True)
    
    # Copy executable
    shutil.copy("dist/WebBuilder.exe", portable_dir)
    
    # Copy ML Engine data directory
    ml_engine_dest = os.path.join(portable_dir, "ml_engine")
    if os.path.exists("ml_engine"):
        shutil.copytree("ml_engine", ml_engine_dest, dirs_exist_ok=True)
        print(f"✓ Copied ml_engine/ to portable package")
    
    # Create README for portable
    readme = """# WebBuilder Desktop - Portable Version

## Quick Start
1. Run WebBuilder.exe
2. No installation required
3. All data stored in ~/.webbuilder/

## System Requirements
- Windows 10/11 (64-bit)
- 4 GB RAM minimum
- 500 MB disk space

## Support
- GitHub: https://github.com/yourusername/webbuilder
- Email: support@webbuilder.app
"""
    
    with open(f"{portable_dir}/README.txt", "w") as f:
        f.write(readme)
    
    # Create ZIP
    with zipfile.ZipFile("dist/WebBuilder-Portable-v1.0.0.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, portable_dir)
                zf.write(file_path, arcname)
    
    print(f"✓ Portable version: dist/WebBuilder-Portable-v1.0.0.zip")
    print(f"  Size: {os.path.getsize('dist/WebBuilder-Portable-v1.0.0.zip') / (1024*1024):.1f} MB")


if __name__ == "__main__":
    if build_executable():
        create_installer()
        create_portable_version()
        print("\n" + "=" * 60)
        print("ALL DISTRIBUTION FILES CREATED")
        print("=" * 60)
        print("\ndist/")
        print("  WebBuilder.exe - Standalone executable")
        print("  WebBuilder-Setup.exe - Windows installer (requires NSIS)")
        print("  WebBuilder-Portable-v1.0.0.zip - Portable ZIP")

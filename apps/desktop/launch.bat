@echo off
set QT_QPA_PLATFORM=windows
set QT_OPENGL_TYPE=software
cd /d "C:\Users\Server\Desktop\WebBuilder"
start "" "C:\Users\Server\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe" webbuilder_desktop.py
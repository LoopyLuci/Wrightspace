"""Minimal QT import order test"""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Test 1: Set flag before ANY PyQt import
from PyQt5.QtCore import Qt
Qt.AA_ShareOpenGLContexts = True

print("1. Qt imported and flag set")

# Now try webengine import
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    print("2. QWebEngineView imported successfully")
except ImportError as e:
    print(f"2. QWebEngineView failed: {e}")

# Now try creating QApplication
from PyQt5.QtWidgets import QApplication
app = QApplication([''])
print("3. QApplication created successfully")
print(f"   App: {app}, address: {id(app)}")
print("✅ Test passed")
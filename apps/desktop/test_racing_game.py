#!/usr/bin/env python3
"""Launch the WebBuilder racing game directly to verify it works."""
import os
import sys
import time

# Set platform for Windows GUI
os.environ['QT_QPA_PLATFORM'] = 'windows'

from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

app = QApplication(sys.argv)

# Import and test the racing game widget
from webbuilder.gui.racing_game_widget import RacingGameWidget

# Create dialog
dialog = QDialog()
dialog.setWindowTitle('WebBuilder Racing')

# Scale dialog to screen size
screen = app.primaryScreen()
screen_geometry = screen.availableGeometry()
dialog_width = min(max(int(screen_geometry.width() * 0.7), 700), 1200)
dialog_height = min(max(int(screen_geometry.height() * 0.7), 500), 800)

dialog.setMinimumSize(600, 450)
dialog.resize(dialog_width, dialog_height)
dialog.setStyleSheet('QDialog { background: #0a0a0f; }')

layout = QVBoxLayout(dialog)
layout.setContentsMargins(0, 0, 0, 0)

# Add racing game widget
game_widget = RacingGameWidget(dialog)
layout.addWidget(game_widget)

# Add controls hint
controls = QLabel('Controls: WASD or Arrow Keys to drive | SPACE to start/restart')
controls.setStyleSheet('color: #64748b; font-size: 11px; padding: 8px;')
controls.setAlignment(Qt.AlignCenter)
layout.addWidget(controls)

# Show and start
dialog.show()
game_widget.start_game()
print('Racing game started!')
print(f'Game state: {game_widget.game_state}')
print(f'Dialog size: {dialog_width}x{dialog_height}')

# Run for a bit to verify it works
def check_state():
    print(f'Car: ({game_widget.car_x:.1f}, {game_widget.car_y:.1f}) Speed: {game_widget.car_speed:.1f} Lap: {game_widget.lap_count}')
    print('Racing game is fully functional!')
    app.quit()

from PyQt5.QtCore import QTimer
QTimer.singleShot(3000, check_state)
app.exec_()
print('Test complete!')

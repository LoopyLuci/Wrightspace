#!/usr/bin/env python3
"""Launch the racing game in the default web browser."""

import os
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

def launch_racing_game():
    """Launch the racing game in the default browser."""
    game_dir = os.path.dirname(os.path.abspath(__file__))
    game_path = os.path.join(game_dir, 'racing-game.html')
    
    if not os.path.exists(game_path):
        print("ERROR: racing-game.html not found!")
        return False
    
    # Open in default browser
    print("=" * 50)
    print("WebBuilder Racing Game")
    print("=" * 50)
    print("\nLaunching racing game in your browser...")
    print("Controls: WASD or Arrow keys to drive")
    print("Complete 3 laps as fast as you can!\n")
    
    webbrowser.open('file://' + os.path.abspath(game_path))
    return True

if __name__ == '__main__':
    launch_racing_game()

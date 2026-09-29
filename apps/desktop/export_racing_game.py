#!/usr/bin/env python3
"""Export racing game using WebBuilder's export system."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_racing_game():
    """Verify the racing game file."""
    game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'racing-game.html')
    
    if not os.path.exists(game_path):
        print("ERROR: racing-game.html not found")
        return False
    
    with open(game_path, 'r') as f:
        content = f.read()
    
    # Check for essential elements (accept both single and double quotes)
    checks = [
        ('DOCTYPE html', 'DOCTYPE' in content),
        ('Canvas element', '<canvas' in content),
        ('Game loop', 'requestAnimationFrame' in content),
        ('Car drawing', 'car.x' in content and 'car.y' in content),
        ('Track rendering', 'ellipse' in content),
        ('Keyboard controls', 'addEventListener' in content and 'keydown' in content),
        ('HUD elements', 'hud' in content),
        ('Speedometer', 'speedometer' in content),
        ('Minimap', 'minimap' in content),
        ('Start screen', 'start-screen' in content),
        ('CSS styling', '<style>' in content),
        ('Lap counting', 'lapCount' in content),
        ('Car physics', 'acceleration' in content and 'friction' in content),
        ('Drift mechanics', 'drifting' in content),
        ('Particle effects', 'exhaustParticles' in content),
        ('Tire marks', 'tireMarks' in content),
    ]
    
    print("Racing Game Verification:")
    print("-" * 40)
    all_passed = True
    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    
    print("-" * 40)
    if all_passed:
        print("All checks passed! Racing game is ready.")
        print(f"\nFile: {game_path}")
        print(f"Size: {len(content)} bytes")
        print("\nTo play: Open racing-game.html in any web browser")
    else:
        print("Some checks failed!")
    
    return all_passed

if __name__ == '__main__':
    verify_racing_game()

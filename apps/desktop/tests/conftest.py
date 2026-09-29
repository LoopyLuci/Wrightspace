#!/usr/bin/env python3
"""WebBuilder - Complete Test Suite
Run with: python -m pytest tests/ -v
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test configuration
TEST_CONFIG = {
    "temp_dir": tempfile.mkdtemp(prefix="webbuilder_test_"),
    "test_project_name": "Test Project",
    "test_email": "test@example.com",
    "test_password": "securepass123",
}

def get_temp_path(filename: str) -> Path:
    """Get a temp file path."""
    return Path(TEST_CONFIG["temp_dir"]) / filename

def cleanup():
    """Cleanup temp files."""
    import shutil
    if os.path.exists(TEST_CONFIG["temp_dir"]):
        shutil.rmtree(TEST_CONFIG["temp_dir"], ignore_errors=True)

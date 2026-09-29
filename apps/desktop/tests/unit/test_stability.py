#!/usr/bin/env python3
"""Tests for stability and robustness features."""

import sys
import os
import tempfile
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import MagicMock, patch


class TestErrorHandler:
    """Test centralized error handling."""
    
    def test_error_logger_creation(self):
        from webbuilder.gui.error_handler import ErrorLogger
        logger = ErrorLogger()
        assert logger is not None
    
    def test_error_logging(self):
        from webbuilder.gui.error_handler import ErrorLogger
        logger = ErrorLogger()
        try:
            raise ValueError("Test error")
        except ValueError as e:
            record = logger.log_error("TestComponent", e)
        
        assert record.component == "TestComponent"
        assert record.error_type == "ValueError"
        assert "Test error" in record.message
    
    def test_error_history_limit(self):
        from webbuilder.gui.error_handler import ErrorLogger
        logger = ErrorLogger(max_history=5)
        
        for i in range(10):
            try:
                raise ValueError(f"Error {i}")
            except ValueError as e:
                logger.log_error("Test", e)
        
        assert len(logger._errors) == 5
    
    def test_safe_executor_success(self):
        from webbuilder.gui.error_handler import ErrorLogger, SafeExecutor
        error_logger = ErrorLogger()
        executor = SafeExecutor(error_logger)
        
        result = executor.execute(lambda: 42, component="Test")
        assert result == 42
    
    def test_safe_executor_failure(self):
        from webbuilder.gui.error_handler import ErrorLogger, SafeExecutor
        error_logger = ErrorLogger()
        executor = SafeExecutor(error_logger)
        
        result = executor.execute(lambda: 1/0, component="Test", default=0)
        assert result == 0
    
    def test_global_exception_hook(self):
        from webbuilder.gui.error_handler import GlobalExceptionHook, get_error_logger
        logger = get_error_logger()
        hook = GlobalExceptionHook(logger)
        assert hook is not None


class TestStateManager:
    """Test panel state persistence."""
    
    def test_state_manager_creation(self):
        from webbuilder.gui.state_manager import StateManager
        sm = StateManager()
        assert sm is not None
    
    def test_panel_state_to_dict(self):
        from webbuilder.gui.state_manager import PanelState
        state = PanelState(name="test", visible=True)
        d = state.to_dict()
        assert d["name"] == "test"
        assert d["visible"] is True
    
    def test_window_state_serialization(self):
        from webbuilder.gui.state_manager import WindowState
        state = WindowState(
            geometry={"x": 100, "y": 100, "width": 1280, "height": 720},
            active_tab=0,
            project_path="test.webbuilder"
        )
        d = state.to_dict()
        assert d["geometry"]["x"] == 100
        assert d["project_path"] == "test.webbuilder"
        
        restored = WindowState.from_dict(d)
        assert restored.geometry["x"] == 100
        assert restored.project_path == "test.webbuilder"
    
    def test_save_and_restore(self):
        from webbuilder.gui.state_manager import StateManager
        sm = StateManager()
        
        # Create a mock window
        mock_window = MagicMock()
        mock_window.x.return_value = 100
        mock_window.y.return_value = 200
        mock_window.width.return_value = 1280
        mock_window.height.return_value = 720
        mock_window.saveState.return_value = b'test_state'
        mock_window.centralWidget.return_value = None
        
        result = sm.save_state(mock_window, "test_project")
        assert result is True
    
    def test_recovery_points(self):
        from webbuilder.gui.state_manager import StateManager
        sm = StateManager()
        points = sm.get_recovery_points()
        assert isinstance(points, list)


class TestInputValidation:
    """Test input validation framework."""
    
    def test_project_name_validation(self):
        from webbuilder.gui.validation import validate_project_name
        
        valid, msg = validate_project_name("My Project")
        assert valid is True
        
        valid, msg = validate_project_name("")
        assert valid is False
        
        valid, msg = validate_project_name("a" * 101)
        assert valid is False
    
    def test_email_validation(self):
        from webbuilder.gui.validation import validate_email
        
        valid, msg = validate_email("test@example.com")
        assert valid is True
        
        valid, msg = validate_email("")
        assert valid is True  # Empty allowed
        
        valid, msg = validate_email("invalid")
        assert valid is False
    
    def test_url_validation(self):
        from webbuilder.gui.validation import validate_url
        
        valid, msg = validate_url("https://example.com")
        assert valid is True
        
        valid, msg = validate_url("")
        assert valid is True
        
        valid, msg = validate_url("not-a-url")
        assert valid is False
    
    def test_number_validation(self):
        from webbuilder.gui.validation import validate_number
        
        valid, msg = validate_number("42", 0, 100)
        assert valid is True
        
        valid, msg = validate_number("150", 0, 100)
        assert valid is False
        
        valid, msg = validate_number("abc")
        assert valid is False
    
    def test_hex_color_validation(self):
        from webbuilder.gui.validation import Validators
        
        assert Validators.hex_color("#ff0000") is True
        assert Validators.hex_color("#FFF") is True
        assert Validators.hex_color("red") is False
        assert Validators.hex_color("") is True
    
    def test_form_validator(self):
        from webbuilder.gui.validation import FormValidator, ValidationRule, Validators
        
        fv = FormValidator()
        fv.add_field("name", [
            ValidationRule("required", Validators.required, "Name is required"),
            ValidationRule("min_length", Validators.min_length(3), "Min 3 chars"),
        ])
        
        valid, errors = fv.validate_form({"name": "John"})
        assert valid is True
        
        valid, errors = fv.validate_form({"name": ""})
        assert valid is False
        assert "name" in errors
        
        valid, errors = fv.validate_form({"name": "ab"})
        assert valid is False
    
    def test_validators_class(self):
        from webbuilder.gui.validation import Validators
        
        assert Validators.required("test") is True
        assert Validators.required("") is False
        
        assert Validators.email("test@example.com") is True
        assert Validators.email("invalid") is False
        
        assert Validators.url("https://example.com") is True
        assert Validators.url("invalid") is False
        
        min_5 = Validators.min_length(5)
        assert min_5("hello") is True
        assert min_5("hi") is False
        
        in_range = Validators.range(0, 100)
        assert in_range("50") is True
        assert in_range("150") is False


class TestIntegration:
    """Integration tests for stability features."""
    
    def test_error_logging_and_state_save(self):
        from webbuilder.gui.error_handler import ErrorLogger
        from webbuilder.gui.state_manager import StateManager
        
        error_logger = ErrorLogger()
        state_manager = StateManager()
        
        # Log an error
        try:
            raise RuntimeError("Test error")
        except RuntimeError as e:
            error_logger.log_error("Test", e)
        
        assert len(error_logger._errors) == 1
    
    def test_validation_before_save(self):
        from webbuilder.gui.validation import validate_project_name
        
        # Simulate save with invalid name
        valid, msg = validate_project_name("")
        assert valid is False
        assert "required" in msg.lower()
        
        valid, msg = validate_project_name("valid-name")
        assert valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
"""WebBuilder Test Suite v2.

Integration tests, GUI automation, performance benchmarks.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

# Ensure we can import webbuilder
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestProjectLifecycle(unittest.TestCase):
    """Test complete project lifecycle."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_project(self):
        from webbuilder.core import Project, ProjectManager
        pm = ProjectManager()
        p = Project(id="test-1", name="Test Project")
        self.assertEqual(p.name, "Test Project")
        self.assertEqual(len(p.pages), 0)
    
    def test_add_sections(self):
        from webbuilder.core import Project, Section
        p = Project(id="test", name="Test")
        page = p.add_page("Home")
        section = Section(id="s1", type="hero", props={"title": "Welcome"})
        page.sections.append(section)
        self.assertEqual(len(page.sections), 1)
        self.assertEqual(page.sections[0].type, "hero")
    
    def test_multi_page_project(self):
        from webbuilder.core import Project
        p = Project(id="test", name="Multi")
        p.add_page("Home")
        p.add_page("About")
        p.add_page("Contact")
        self.assertEqual(len(p.pages), 3)
        self.assertEqual(p.pages[1].name, "About")


class TestValidation(unittest.TestCase):
    """Test input validation."""
    
    def test_xss_prevention(self):
        from webbuilder.validation import sanitize
        malicious = '<script>alert("xss")</script>'
        result = sanitize(malicious)
        self.assertNotIn("<script>", result)
    
    def test_path_traversal(self):
        from webbuilder.validation import InputValidator
        valid, error = InputValidator.validate_file_path("../../etc/passwd")
        self.assertFalse(valid)
    
    def test_api_key_format(self):
        from webbuilder.validation import InputValidator
        valid, _ = InputValidator.validate_api_key("openai", "sk-" + "a" * 32)
        self.assertTrue(valid)
        valid, _ = InputValidator.validate_api_key("openai", "invalid")
        self.assertFalse(valid)
    
    def test_project_name(self):
        from webbuilder.validation import InputValidator
        valid, _ = InputValidator.validate_project_name("My Project 123")
        self.assertTrue(valid)
        valid, _ = InputValidator.validate_project_name("")
        self.assertFalse(valid)
        valid, _ = InputValidator.validate_project_name("a" * 200)
        self.assertFalse(valid)
    
    def test_color_validation(self):
        from webbuilder.validation import is_valid_color
        self.assertTrue(is_valid_color("#ff0000"))
        self.assertTrue(is_valid_color("rgb(255, 0, 0)"))
        self.assertTrue(is_valid_color("hsl(0, 100%, 50%)"))
        self.assertTrue(is_valid_color("red"))
        self.assertFalse(is_valid_color("not-a-color"))
        self.assertFalse(is_valid_color("rgb(999, 0, 0)"))


class TestCache(unittest.TestCase):
    """Test response cache."""
    
    def setUp(self):
        from webbuilder.ai.cache import ResponseCache
        self.cache = ResponseCache(max_memory_entries=10)
    
    def test_cache_hit(self):
        messages = [{"role": "user", "content": "hello"}]
        self.cache.put(messages, "gpt-3.5", "response", cost_usd=0.001)
        result = self.cache.get(messages, "gpt-3.5")
        self.assertEqual(result, "response")
    
    def test_cache_miss(self):
        messages = [{"role": "user", "content": "new"}]
        result = self.cache.get(messages, "gpt-3.5")
        self.assertIsNone(result)
    
    def test_cache_expiry(self):
        messages = [{"role": "user", "content": "temp"}]
        self.cache.put(messages, "gpt-3.5", "temp", ttl=0)
        import time
        time.sleep(0.1)
        result = self.cache.get(messages, "gpt-3.5")
        self.assertIsNone(result)
    
    def test_cache_stats(self):
        messages = [{"role": "user", "content": "test"}]
        self.cache.put(messages, "gpt-3.5", "resp", cost_usd=0.001)
        stats = self.cache.get_stats()
        self.assertGreater(stats["memory_entries"], 0)


class TestSQLiteBackend(unittest.TestCase):
    """Test SQLite project backend."""
    
    def setUp(self):
        from webbuilder.core.sqlite_backend import SQLiteProjectBackend
        self.db_path = Path(tempfile.mkdtemp()) / "test.db"
        self.backend = SQLiteProjectBackend(db_path=self.db_path)
    
    def tearDown(self):
        self.backend.close()
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_save_load(self):
        data = {"name": "Test", "pages": [{"id": "p1", "name": "Home", "sections": []}]}
        self.backend.save_project("test-1", "Test", data)
        loaded = self.backend.load_project("test-1")
        self.assertEqual(loaded["name"], "Test")
    
    def test_list_projects(self):
        self.backend.save_project("p1", "Project 1", {"name": "P1", "pages": []})
        self.backend.save_project("p2", "Project 2", {"name": "P2", "pages": []})
        projects = self.backend.list_projects()
        self.assertEqual(len(projects), 2)
    
    def test_delete_project(self):
        self.backend.save_project("del", "Delete", {"name": "Del", "pages": []})
        self.backend.delete_project("del")
        loaded = self.backend.load_project("del")
        self.assertIsNone(loaded)
    
    def test_search(self):
        self.backend.save_project("s1", "Search Test", {"name": "Search Test", "pages": []})
        self.backend.update_search_index("s1", {"name": "Search Test"})
        results = self.backend.search("Search")
        self.assertEqual(len(results), 1)


class TestScaling(unittest.TestCase):
    """Test adaptive scaling engine."""
    
    def test_metrics_hd(self):
        from webbuilder.gui.scaling import ScalingEngine
        engine = ScalingEngine()
        m = engine.calculate_metrics(1280, 720)
        self.assertGreater(m.sidebar_width, 0)
        self.assertGreater(m.right_panel_width, 0)
    
    def test_metrics_4k(self):
        from webbuilder.gui.scaling import ScalingEngine
        engine = ScalingEngine()
        m = engine.calculate_metrics(3840, 2160)
        self.assertGreater(m.sidebar_width, 200)
        self.assertGreater(m.right_panel_width, 250)
    
    def test_scale_value(self):
        from webbuilder.gui.scaling import ScalingEngine
        engine = ScalingEngine()
        engine._scale_factor = 1.5
        self.assertEqual(engine.scale_value(100), 150)
    
    def test_stylesheet_generated(self):
        from webbuilder.gui.scaling import ScalingEngine
        engine = ScalingEngine()
        ss = engine.get_stylesheet()
        self.assertIn("QMainWindow", ss)
        self.assertIn("QPushButton", ss)


class TestHardwareDetection(unittest.TestCase):
    """Test hardware detection."""
    
    def test_hardware_info(self):
        from webbuilder.hardware.detector import HardwareDetector
        detector = HardwareDetector()
        info = detector.detect(force=True)
        self.assertGreater(info.cpu.cores_logical, 0)
        self.assertGreater(info.memory.total_gb, 0)
    
    def test_gpu_detection(self):
        from webbuilder.hardware.detector import HardwareDetector
        detector = HardwareDetector()
        info = detector.detect(force=True)
        # May be 0 on systems without discrete GPUs
        self.assertIsInstance(info.gpus, list)


class TestPluginSystem(unittest.TestCase):
    """Test plugin system."""
    
    def test_plugin_manager(self):
        from webbuilder.plugins.v2 import PluginManager
        manager = PluginManager()
        plugins = manager.get_all_plugins()
        self.assertIsInstance(plugins, list)
    
    def test_plugin_manifest(self):
        from webbuilder.plugins.v2 import PluginManifest
        manifest = PluginManifest.from_dict({
            "id": "test",
            "name": "Test Plugin",
            "version": "1.0.0",
        })
        self.assertEqual(manifest.id, "test")
        self.assertEqual(manifest.version, "1.0.0")
    
    def test_plugin_api(self):
        from webbuilder.plugins.v2 import PluginAPI, PluginManager
        manager = PluginManager()
        api = PluginAPI(manager, "test")
        self.assertIsNotNone(api)


class TestPerformance(unittest.TestCase):
    """Performance benchmarks."""
    
    def test_cache_performance(self):
        from webbuilder.ai.cache import ResponseCache
        cache = ResponseCache(max_memory_entries=1000)
        
        start = time.time()
        for i in range(1000):
            messages = [{"role": "user", "content": f"message {i}"}]
            cache.put(messages, "gpt-3.5", f"response {i}")
        elapsed = time.time() - start
        
        # 1000 puts in < 10 seconds (disk writes take time)
        self.assertLess(elapsed, 10.0)
    
    def test_sqlite_performance(self):
        from webbuilder.core.sqlite_backend import SQLiteProjectBackend
        db_path = Path(tempfile.mkdtemp()) / "perf.db"
        backend = SQLiteProjectBackend(db_path=db_path)
        
        start = time.time()
        for i in range(100):
            backend.save_project(f"proj-{i}", f"Project {i}", {"name": f"P{i}", "pages": []})
        elapsed = time.time() - start
        
        # 100 saves in < 2 seconds
        self.assertLess(elapsed, 2.0)
        
        backend.close()
        db_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

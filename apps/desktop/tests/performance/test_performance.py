#!/usr/bin/env python3
"""Performance and Stress Tests for WebBuilder."""

import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from webbuilder.core import Project, Page, Section, ProjectManager
from webbuilder.export import HTMLExporter, ExportManager
from webbuilder.search import ProjectSearch
from webbuilder.performance import PerformanceTimer, MemoryMonitor


class TestPerformance:
    """Performance benchmarks."""

    def test_export_speed_small_project(self):
        """Export a small project quickly."""
        project = Project(id="perf-1", name="Small", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id=f"s{i}", type="Hero", props={"title": f"Section {i}"})
                for i in range(5)
            ])
        ])
        
        exporter = HTMLExporter()
        with PerformanceTimer("small_export", threshold_ms=100) as timer:
            html = exporter.generate(project)
        
        assert len(html) > 0
        assert timer.elapsed_ms < 100

    def test_export_speed_large_project(self):
        """Export a large project (50 sections)."""
        project = Project(id="perf-2", name="Large", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id=f"s{i}", type="Hero", props={"title": f"Section {i}", "description": "x" * 100})
                for i in range(50)
            ])
        ])
        
        exporter = HTMLExporter()
        with PerformanceTimer("large_export", threshold_ms=500) as timer:
            html = exporter.generate(project)
        
        assert len(html) > 0
        assert timer.elapsed_ms < 500

    def test_export_speed_multi_page(self):
        """Export a multi-page project (10 pages, 10 sections each)."""
        project = Project(id="perf-3", name="Multi", pages=[
            Page(id=f"p{i}", name=f"Page {i}", sections=[
                Section(id=f"s{i}_{j}", type="Hero", props={"title": f"Section {j}"})
                for j in range(10)
            ])
            for i in range(10)
        ])
        
        exporter = HTMLExporter()
        with PerformanceTimer("multi_page_export", threshold_ms=1000) as timer:
            html = exporter.generate(project)
        
        assert len(html) > 0
        assert timer.elapsed_ms < 1000

    def test_project_save_speed(self):
        """Save a project quickly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Perf Test")
            
            with PerformanceTimer("save", threshold_ms=50) as timer:
                pm.save(project)
            
            assert timer.elapsed_ms < 50

    def test_project_load_speed(self):
        """Load a project quickly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Perf Test")
            pm.save(project)
            
            with PerformanceTimer("load", threshold_ms=50) as timer:
                loaded = pm.load(project.id)
            
            assert loaded is not None
            assert timer.elapsed_ms < 50

    def test_search_speed(self):
        """Search across many projects."""
        pm = ProjectManager()
        search = ProjectSearch(pm)
        
        # Index 100 projects
        for i in range(100):
            project = Project(id=f"proj-{i}", name=f"Project {i}", pages=[
                Page(id=f"p{i}", name="Home", sections=[
                    Section(id=f"s{i}", type="Hero", props={"title": f"Welcome to project {i}"})
                ])
            ])
            search.add_project(project)
        
        with PerformanceTimer("search_100", threshold_ms=100) as timer:
            results = search.search("project", limit=100)
        
        assert len(results) == 100
        assert timer.elapsed_ms < 100

    def test_memory_usage_stable(self):
        """Memory usage should remain stable."""
        monitor = MemoryMonitor()
        
        # Take multiple measurements
        for _ in range(10):
            monitor.get_memory_usage()
        
        trend = monitor._calculate_trend()
        # Should be stable (not increasing rapidly)
        assert trend in ["stable", "decreasing"]


class TestStress:
    """Stress tests."""

    def test_very_large_project(self):
        """Handle a project with 200 sections."""
        project = Project(id="stress-1", name="Stress", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id=f"s{i}", type="Hero", props={"title": f"Section {i}", "content": "x" * 500})
                for i in range(200)
            ])
        ])
        
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert len(html) > 0

    def test_many_pages(self):
        """Handle a project with 50 pages."""
        project = Project(id="stress-2", name="Many Pages", pages=[
            Page(id=f"p{i}", name=f"Page {i}", sections=[
                Section(id=f"s{i}", type="Hero", props={"title": f"Page {i}"})
            ])
            for i in range(50)
        ])
        
        exporter = HTMLExporter()
        html = exporter.generate(project)
        assert len(html) > 0

    def test_many_projects(self):
        """Handle 100 projects in storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            
            for i in range(100):
                project = pm.create_new(f"Project {i}")
                pm.save(project)
            
            projects = pm.list_projects()
            assert len(projects) >= 100  # May include other test projects

    def test_rapid_saves(self):
        """Handle rapid consecutive saves."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager(Path(tmpdir))
            project = pm.create_new("Rapid")
            
            for i in range(50):
                project.pages[0].sections.append(
                    Section(id=f"s{i}", type="Hero", props={"title": f"Section {i}"})
                )
                pm.save(project)
            
            loaded = pm.load(project.id)
            assert len(loaded.pages[0].sections) == 50

    def test_concurrent_exports(self):
        """Handle multiple exports in sequence."""
        project = Project(id="concurrent-1", name="Concurrent", pages=[
            Page(id="p1", name="Home", sections=[
                Section(id=f"s{i}", type="Hero", props={"title": f"Section {i}"})
                for i in range(20)
            ])
        ])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExportManager()
            
            for i in range(5):
                html_path = manager.export(project, "html", Path(tmpdir) / f"output_{i}.html")
                assert html_path.exists()

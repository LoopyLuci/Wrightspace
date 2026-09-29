#!/usr/bin/env python3
"""Test that all modules can be imported correctly (PyInstaller verification)."""

import sys
import importlib

modules_to_test = [
    'webbuilder',
    'webbuilder.core',
    'webbuilder.core.multi',
    'webbuilder.config',
    'webbuilder.export',
    'webbuilder.ai',
    'webbuilder.templates',
    'webbuilder.forms',
    'webbuilder.seo',
    'webbuilder.custom_code',
    'webbuilder.code_editor',
    'webbuilder.css_designer',
    'webbuilder.plugins',
    'webbuilder.exceptions',
    'webbuilder.logging_config',
    'webbuilder.validation',
    'webbuilder.performance',
    'webbuilder.generative_ui',
    'webbuilder.generative_ui.themes',
    'webbuilder.generative_ui.widget_factory',
    'webbuilder.generative_ui.code_generator',
    'webbuilder.generative_ui.virtual_list',
    'webbuilder.hardware',
    'webbuilder.ml_engine',
    'webbuilder.ml_engine.models',
    'webbuilder.ml_engine.data',
    'webbuilder.ml_engine.training',
    'webbuilder.ml_engine.persistence',
    'webbuilder.ml_engine.code_corpus',
    'webbuilder.ml_engine.train_all',
    'webbuilder.gui',
    'webbuilder.gui.chat_panel',
    'webbuilder.gui.chat_enhanced',
    'webbuilder.gui.form_builder_dialog',
    'webbuilder.gui.feedback_dialog',
    'webbuilder.contrib.cms',
    'webbuilder.contrib.ecommerce',
    'webbuilder.contrib.publishing',
    'webbuilder.contrib.plugin_system',
    'webbuilder.contrib.collaboration',
    'webbuilder.contrib.agentic',
    'webbuilder.contrib.analytics',
    'webbuilder.contrib.search',
    'webbuilder.contrib.import_export',
    'webbuilder.contrib.performance',
    'webbuilder.contrib.api_docs',
    'webbuilder.contrib.resources',
    'webbuilder.contrib.migrations',
    'webbuilder.contrib.feedback',
]

passed = 0
failed = 0

for mod in modules_to_test:
    try:
        importlib.import_module(mod)
        passed += 1
    except Exception as e:
        print(f"FAIL: {mod} - {e}")
        failed += 1

print(f"\nResults: {passed} passed, {failed} failed")
if failed == 0:
    print("All modules import successfully - ready for PyInstaller build!")
else:
    print("Some modules failed to import - fix before building")
    sys.exit(1)

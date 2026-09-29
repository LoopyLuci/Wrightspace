"""webbuilder.gui — GUI package for WebBuilder Desktop application."""

from __future__ import annotations


def __getattr__(name: str):
    if name == "WebBuilderWindow":
        from webbuilder.gui.main_window import WebBuilderWindow
        return WebBuilderWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def main():
    """Launch the WebBuilder desktop application."""
    import sys
    import os

    os.environ['QT_OPENGL_TYPE'] = 'software'
    os.environ['QT_OPENGL'] = 'software'
    os.environ['QT_QPA_PLATFORM'] = 'windows'

    from PyQt5.QtWidgets import QApplication
    from webbuilder.gui.main_window import WebBuilderWindow

    app = QApplication(sys.argv)
    window = WebBuilderWindow()
    window.show()
    sys.exit(app.exec_())


__all__ = ['main', 'WebBuilderWindow']

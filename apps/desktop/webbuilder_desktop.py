"""WebBuilder Desktop — Entry point with Qt OpenGL fix."""

import sys
import os

# Qt OpenGL context sharing must be set before any Qt imports
os.environ['QT_OPENGL_TYPE'] = 'software'
os.environ['QT_OPENGL'] = 'software'
os.environ['QT_QPA_PLATFORM'] = 'windows'

from PyQt5.QtCore import QCoreApplication, Qt
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

from webbuilder.gui import main

if __name__ == "__main__":
    main()

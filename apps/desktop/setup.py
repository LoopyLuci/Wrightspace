#!/usr/bin/env python3
"""WebBuilder: A professional web building platform."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="webbuilder-desktop",
    version="8.0.0",
    author="WebBuilder Community",
    author_email="community@webbuilder.dev",
    description="A professional web building platform with AI assistance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/webbuilder/webbuilder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
        ],
        "server": [
            "flask>=2.0",
            "flask-cors>=4.0",
        ],
        "all": [
            "PyQt5>=5.15.0",
            "flask>=2.0",
            "flask-cors>=4.0",
            "requests>=2.28.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "webbuilder=webbuilder.gui:main",
            "webbuilder-cli=webbuilder.agentic.cli:main",
        ],
        "gui_scripts": [
            "webbuilder-gui=webbuilder.gui:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

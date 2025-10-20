"""
Figmaker: Scientific figure assembly tool with publication-ready exports.

This package provides both a GUI application and a command-line interface
for assembling scientific figures from multiple image panels.
"""

__version__ = "0.2.0"
__author__ = "mhendzel2"

from .recipes import Recipe, FigureSpec, Panel, DataSource
from .styles import apply_style, JOURNALS, PALETTES

__all__ = [
    "Recipe",
    "FigureSpec", 
    "Panel",
    "DataSource",
    "apply_style",
    "JOURNALS",
    "PALETTES",
]
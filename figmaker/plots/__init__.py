"""
Plot rendering modules for Figmaker.

This package contains individual plot renderers that can be used
by both the GUI and CLI interfaces.
"""

from .image_panel import draw as draw_image_panel

__all__ = [
    "draw_image_panel",
]
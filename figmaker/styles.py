"""
Publication-ready style management for Figmaker.

This module provides journal-specific style presets and colorblind-safe palettes
for scientific publication figures.
"""

from __future__ import annotations
import matplotlib as mpl
from cycler import cycler
from typing import Dict, Any, List


# Colorblind-safe palettes
PALETTES = {
    "cb_safe": ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377", "#BBBBBB"],
    "viridis": ["#440154", "#482777", "#3F4A8A", "#31678E", "#26838F", "#1F9D8A", "#6CCE5A", "#B6DE2B", "#FEE825"],
    "paul_tol": ["#332288", "#117733", "#44AA99", "#88CCEE", "#DDCC77", "#CC6677", "#AA4499", "#882255"],
    "nature": ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4", "#91D1C2", "#DC0000"],
}


# Base matplotlib rcParams for scientific figures
RC_BASE: Dict[str, Any] = {
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.transparent": False,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    
    # Typography
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica", "sans-serif"],
    "font.size": 8,
    
    # Axes
    "axes.titlesize": 8,
    "axes.labelsize": 7,
    "axes.linewidth": 0.8,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.axisbelow": True,
    "axes.grid": False,
    
    # Ticks
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.minor.size": 1.5,
    "ytick.minor.size": 1.5,
    "xtick.direction": "out",
    "ytick.direction": "out",
    
    # Legend
    "legend.fontsize": 6,
    "legend.frameon": False,
    "legend.numpoints": 1,
    "legend.scatterpoints": 1,
    "legend.handlelength": 1.0,
    "legend.handletextpad": 0.5,
    "legend.columnspacing": 1.0,
    
    # Lines and markers
    "lines.linewidth": 1.0,
    "lines.markersize": 4,
    "patch.linewidth": 0.5,
    
    # Grid
    "grid.linewidth": 0.5,
    "grid.alpha": 0.3,
}


# Journal-specific style overrides
JOURNALS: Dict[str, Dict[str, Any]] = {
    "default": {},
    
    "nature": {
        "font.size": 7,
        "axes.labelsize": 7,
        "axes.titlesize": 8,
        "xtick.labelsize": 6,
        "ytick.labelsize": 6,
        "legend.fontsize": 6,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "lines.linewidth": 0.8,
        # Nature prefers clean, minimal styling
        "axes.spines.top": False,
        "axes.spines.right": False,
    },
    
    "science": {
        "font.size": 7,
        "axes.labelsize": 7,
        "axes.titlesize": 8,
        "xtick.labelsize": 6,
        "ytick.labelsize": 6,
        "legend.fontsize": 6,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "lines.linewidth": 0.8,
        # Science allows slightly bolder elements
        "axes.spines.top": False,
        "axes.spines.right": False,
    },
    
    "cell": {
        "font.size": 7,
        "axes.labelsize": 7,
        "axes.titlesize": 8,
        "xtick.labelsize": 6,
        "ytick.labelsize": 6,
        "legend.fontsize": 6,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "lines.linewidth": 0.8,
        # Cell style preferences
        "axes.spines.top": False,
        "axes.spines.right": False,
    },
}


def apply_style(name: str) -> None:
    """
    Apply a journal-specific style to matplotlib.
    
    Args:
        name: Journal name ('nature', 'science', 'cell', 'default')
    """
    if name not in JOURNALS:
        raise ValueError(f"Unknown style '{name}'. Available: {list(JOURNALS.keys())}")
    
    # Start with base configuration
    rc = RC_BASE.copy()
    
    # Apply journal-specific overrides
    journal_rc = JOURNALS.get(name, {})
    rc.update(journal_rc)
    
    # Update matplotlib
    mpl.rcParams.update(rc)


def get_palette(name: str) -> List[str]:
    """
    Get a color palette by name.
    
    Args:
        name: Palette name
        
    Returns:
        List of hex color codes
    """
    if name not in PALETTES:
        raise ValueError(f"Unknown palette '{name}'. Available: {list(PALETTES.keys())}")
    
    return PALETTES[name].copy()


def setup_colorblind_safe() -> None:
    """Set up matplotlib with colorblind-safe default colors."""
    mpl.rcParams["axes.prop_cycle"] = cycler(color=PALETTES["cb_safe"])


# Figmaker-specific styling for backward compatibility
FIGMAKER_STYLE_MAP = {
    "Arial": "Arial",
    "Helvetica": "Helvetica", 
    "Times New Roman": "Times New Roman",
    "Calibri": "Calibri",
    "Default": "Arial",
}


def get_figmaker_font(font_name: str) -> str:
    """Map Figmaker font names to system fonts."""
    return FIGMAKER_STYLE_MAP.get(font_name, "Arial")
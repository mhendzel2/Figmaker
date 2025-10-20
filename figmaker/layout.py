"""
Layout engine for Figmaker using matplotlib GridSpec.

This module provides a modern layout engine that replaces the manual
positioning logic from the original Figmaker GUI with a flexible
GridSpec-based approach.
"""

from __future__ import annotations
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import importlib


def cm_to_in(cm: float) -> float:
    """Convert centimeters to inches."""
    return cm / 2.54


def pt_to_in(pt: float) -> float:
    """Convert points to inches."""
    return pt / 72.0


def build_canvas(
    n_panels: int,
    width_cm: float,
    height_cm: float,
    max_cols: int = 3,
    label_style: str = "A, B, C...",
    spacing: float = 0.3,
    margins: float = 0.2
) -> Tuple[Figure, List[Axes]]:
    """
    Build a figure canvas with automatic panel layout.
    
    Args:
        n_panels: Number of panels to create
        width_cm: Figure width in centimeters
        height_cm: Figure height in centimeters  
        max_cols: Maximum number of columns
        label_style: Panel labeling style
        spacing: Spacing between subplots (as fraction of figure size)
        margins: Margins around figure (as fraction of figure size)
        
    Returns:
        Tuple of (Figure, List of Axes)
    """
    # Create figure with specified dimensions
    fig = plt.figure(figsize=(cm_to_in(width_cm), cm_to_in(height_cm)))
    
    # Calculate grid dimensions
    cols = min(max_cols, max(1, n_panels))
    rows = (n_panels + cols - 1) // cols
    
    # Create GridSpec with spacing
    gs = GridSpec(
        rows, cols, figure=fig,
        wspace=spacing / cols,  # Normalize by number of columns
        hspace=spacing / rows,  # Normalize by number of rows
        left=margins,
        right=1 - margins,
        bottom=margins,
        top=1 - margins
    )
    
    # Create axes for each panel
    axes = []
    for i in range(n_panels):
        row, col = divmod(i, cols)
        ax = fig.add_subplot(gs[row, col])
        axes.append(ax)
        
        # Add panel labels
        if label_style != "None":
            label_text = _get_label_text(label_style, i)
            ax.text(
                -0.15, 1.05, label_text,
                transform=ax.transAxes,
                fontsize=9,
                fontweight="bold",
                va="bottom",
                ha="center"
            )
    
    return fig, axes


def _get_label_text(label_style: str, panel_index: int) -> str:
    """Generate label text based on style and index."""
    if label_style == "A, B, C...":
        return chr(65 + panel_index)
    elif label_style == "a, b, c...":
        return chr(97 + panel_index)
    elif label_style == "1, 2, 3...":
        return str(panel_index + 1)
    elif label_style == "i, ii, iii...":
        roman_numerals = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
        return roman_numerals[panel_index] if panel_index < len(roman_numerals) else str(panel_index + 1)
    else:
        return chr(65 + panel_index)


class FigureLayout:
    """
    Advanced layout manager for complex figure arrangements.
    
    This class provides more sophisticated layout capabilities than
    the simple grid approach, including custom panel arrangements
    and shared axes.
    """
    
    def __init__(self, width_cm: float, height_cm: float):
        self.width_cm = width_cm
        self.height_cm = height_cm
        self.fig = plt.figure(figsize=(cm_to_in(width_cm), cm_to_in(height_cm)))
        self.panels: List[Dict[str, Any]] = []
        
    def add_panel(
        self,
        plot_type: str,
        position: Tuple[int, int, int, int],  # (row, col, rowspan, colspan)
        title: Optional[str] = None,
        **kwargs
    ) -> Axes:
        """
        Add a panel to the layout.
        
        Args:
            plot_type: Type of plot ('image_panel', 'scatter', etc.)
            position: (row, col, rowspan, colspan) for GridSpec
            title: Optional panel title
            **kwargs: Additional arguments for the plot
            
        Returns:
            The matplotlib Axes object for this panel
        """
        row, col, rowspan, colspan = position
        
        # Create axes using subplot2grid for flexible positioning
        ax = plt.subplot2grid(
            (10, 10), (row, col),  # Use 10x10 grid for flexibility
            rowspan=rowspan, colspan=colspan,
            fig=self.fig
        )
        
        panel_info = {
            'axes': ax,
            'plot_type': plot_type,
            'title': title,
            'kwargs': kwargs
        }
        self.panels.append(panel_info)
        
        if title:
            ax.set_title(title)
            
        return ax
    
    def render_panels(self, data_sources: Dict[str, Any]) -> None:
        """
        Render all panels with their specified plot types.
        
        Args:
            data_sources: Dictionary mapping data source names to data
        """
        for i, panel in enumerate(self.panels):
            ax = panel['axes']
            plot_type = panel['plot_type']
            kwargs = panel['kwargs']
            
            try:
                # Dynamically import and call the appropriate plot function
                module = importlib.import_module(f"figmaker.plots.{plot_type}")
                module.draw(ax, **kwargs)
                
            except ImportError:
                # Handle unknown plot types
                ax.text(0.5, 0.5, f"Unknown plot type:\n{plot_type}",
                       ha='center', va='center', transform=ax.transAxes,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
            except Exception as e:
                # Handle rendering errors
                ax.text(0.5, 0.5, f"Error rendering {plot_type}:\n{str(e)}",
                       ha='center', va='center', transform=ax.transAxes,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
    
    def add_shared_legend(self, labels: List[str], location: str = "upper right") -> None:
        """Add a shared legend for the entire figure."""
        # Get handles and labels from all axes
        handles, legend_labels = [], []
        for panel in self.panels:
            h, l = panel['axes'].get_legend_handles_labels()
            handles.extend(h)
            legend_labels.extend(l)
        
        if handles:
            self.fig.legend(handles, legend_labels, loc=location, bbox_to_anchor=(0.95, 0.95))
    
    def tight_layout(self, padding: float = 1.0) -> None:
        """Apply tight layout with specified padding."""
        self.fig.tight_layout(pad=padding)
    
    def save(self, filepath: str, dpi: int = 300, **kwargs) -> None:
        """Save the figure to file."""
        self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight', **kwargs)


class AutoLayout:
    """
    Automatic layout generator that optimizes panel arrangement.
    
    This class analyzes panel content and automatically determines
    the best layout arrangement.
    """
    
    @staticmethod
    def calculate_optimal_grid(n_panels: int, aspect_ratio: float = 1.0) -> Tuple[int, int]:
        """
        Calculate optimal grid dimensions for given number of panels.
        
        Args:
            n_panels: Number of panels
            aspect_ratio: Target aspect ratio (width/height)
            
        Returns:
            Tuple of (rows, cols)
        """
        if n_panels == 1:
            return 1, 1
        elif n_panels == 2:
            return (1, 2) if aspect_ratio > 1.0 else (2, 1)
        elif n_panels <= 4:
            return 2, 2
        elif n_panels <= 6:
            return (2, 3) if aspect_ratio > 1.0 else (3, 2)
        elif n_panels <= 9:
            return 3, 3
        else:
            # For larger numbers, try to maintain reasonable aspect ratio
            cols = int(np.ceil(np.sqrt(n_panels * aspect_ratio)))
            rows = int(np.ceil(n_panels / cols))
            return rows, cols
    
    @staticmethod
    def balance_panel_sizes(
        panels: List[Dict[str, Any]], 
        target_width: float, 
        target_height: float
    ) -> List[Dict[str, Any]]:
        """
        Balance panel sizes to fit target dimensions while maintaining aspect ratios.
        
        Args:
            panels: List of panel dictionaries with size information
            target_width: Target total width
            target_height: Target total height
            
        Returns:
            List of panels with optimized sizes
        """
        # This is a placeholder for more sophisticated layout optimization
        # In practice, this would analyze panel content and optimize placement
        return panels


# Legacy compatibility functions for existing Figmaker GUI
def create_legacy_layout(
    panels: List[Dict[str, Any]],
    target_width_in: float,
    dpi: int,
    num_cols: int,
    padding_pt: int,
    margin_pt: int
) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Create layout information compatible with legacy Figmaker logic.
    
    This function maintains compatibility with the existing GUI while
    providing the same calculations in a more organized way.
    
    Returns:
        Tuple of (total_width_px, total_height_px, layout_info_list)
    """
    if not panels:
        return 0, 0, []
    
    # Convert units to pixels
    total_width_px = int(target_width_in * dpi)
    padding_px = int((padding_pt / 72) * dpi)
    margin_px = int((margin_pt / 72) * dpi)
    
    # Calculate layout
    available_width = total_width_px - (2 * margin_px)
    col_width_px = (available_width - (padding_px * (num_cols - 1))) // num_cols
    
    # Calculate panel layouts and row heights
    layouts = []
    row_heights = []
    current_row_max_h = 0
    
    for i, panel_data in enumerate(panels):
        img = panel_data['pil_image']
        
        # Scale to fit column width while maintaining aspect ratio
        scale = col_width_px / img.width
        scaled_w = col_width_px
        scaled_h = int(img.height * scale)
        
        # Calculate position
        row = i // num_cols
        col = i % num_cols
        x = margin_px + col * (col_width_px + padding_px)
        
        layouts.append({
            'width': scaled_w,
            'height': scaled_h,
            'image': img,
            'x': x,
            'row': row,
            'col': col
        })
        
        current_row_max_h = max(current_row_max_h, scaled_h)
        
        # Store row height at end of row or last panel
        if (i + 1) % num_cols == 0 or (i + 1) == len(panels):
            row_heights.append(current_row_max_h)
            current_row_max_h = 0
    
    # Calculate total height
    content_height = sum(row_heights) + padding_px * (len(row_heights) - 1)
    total_height_px = content_height + (2 * margin_px)
    
    # Add y positions to layouts
    current_y = margin_px
    for i, layout in enumerate(layouts):
        row = layout['row']
        if row > 0 and i % num_cols == 0:
            current_y += row_heights[row - 1] + padding_px
        layout['y'] = current_y
    
    return total_width_px, total_height_px, layouts
"""
Recipe and configuration models for Figmaker.

This module defines the Pydantic models that represent figure recipes,
allowing for declarative figure specification and validation.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Dict, List, Optional, Any


class DataSource(BaseModel):
    """Represents a data source for figure generation."""
    name: str
    path: str
    sheet: Optional[str] = None  # For Excel files
    
    class Config:
        extra = "forbid"


class Transform(BaseModel):
    """Represents a data transformation step."""
    op: Literal["filter", "select", "mutate", "p_adjust_bh", "log2fc"]
    args: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "forbid"


class Panel(BaseModel):
    """Represents a single panel in a figure."""
    title: Optional[str] = None
    plot: Literal["image_panel", "scatter", "line_err", "box_swarm", "heatmap"]
    data: str  # DataSource.name
    x: Optional[str] = None  # Column name for x-axis (optional for image panels)
    y: Optional[str] = None  # Column name for y-axis (optional for image panels)
    hue: Optional[str] = None  # Column name for color coding
    image_path: Optional[str] = None  # Path to image file for image_panel type
    transforms: List[Transform] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "forbid"


class FigureSpec(BaseModel):
    """Represents the complete figure specification."""
    style: Literal["nature", "science", "cell", "default"] = "default"
    width_cm: float = 18.0
    height_cm: float = 12.0
    dpi: int = 600
    background: Literal["white", "transparent", "light_gray"] = "white"
    font_family: str = "Arial"
    label_style: Literal["A, B, C...", "a, b, c...", "1, 2, 3...", "i, ii, iii...", "None"] = "A, B, C..."
    panels: List[Panel]
    export: Dict[str, str] = Field(default_factory=lambda: {"png": "out.png"})
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "forbid"


class Recipe(BaseModel):
    """Top-level recipe model containing all figure information."""
    version: str = "1"
    data: List[DataSource] = Field(default_factory=list)
    figure: FigureSpec
    
    class Config:
        extra = "forbid"


# Legacy support for current Figmaker GUI
class LegacyPanelData(BaseModel):
    """Represents the current Figmaker panel data structure."""
    id: int
    pil_image: Any  # PIL Image object (not serializable)
    name: str
    original_path: str
    
    class Config:
        arbitrary_types_allowed = True


class LegacyAnnotation(BaseModel):
    """Represents the current Figmaker annotation structure."""
    text: str
    x: int
    y: int
    
    class Config:
        extra = "forbid"
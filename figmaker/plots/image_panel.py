"""
Image panel rendering for Figmaker.

This module handles the core image panel assembly logic extracted from
the original Figmaker GUI application.
"""

from __future__ import annotations
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
from typing import Optional, Dict, Any, List, Tuple, Union
import os


def draw(ax: Axes, image_path: str, title: Optional[str] = None, **kwargs) -> None:
    """
    Draw an image panel on a matplotlib axes.
    
    This is a matplotlib-based version for integration with other plot types.
    For pure image assembly, use the PIL-based functions below.
    
    Args:
        ax: Matplotlib axes to draw on
        image_path: Path to the image file
        title: Optional title for the panel
        **kwargs: Additional arguments (unused for compatibility)
    """
    try:
        image = Image.open(image_path)
        ax.imshow(np.array(image))
        ax.set_xticks([])
        ax.set_yticks([])
        
        if title:
            ax.set_title(title)
            
        # Remove spines for clean image display
        for spine in ax.spines.values():
            spine.set_visible(False)
            
    except Exception as e:
        # Handle missing or corrupted images
        ax.text(0.5, 0.5, f"Error loading image:\n{image_path}\n\n{str(e)}", 
                ha='center', va='center', transform=ax.transAxes, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        ax.set_xticks([])
        ax.set_yticks([])


class ImagePanelAssembler:
    """
    Handles assembly of multiple image panels into a single figure.
    
    This class extracts and modernizes the core logic from the original 
    Figmaker.py GUI application.
    """
    
    def __init__(self):
        self.panels: List[Dict[str, Any]] = []
        self.annotations: List[Dict[str, Any]] = []
        
    def add_panel(self, image_path: str, name: Optional[str] = None) -> None:
        """Add an image panel to the assembly."""
        try:
            image = Image.open(image_path)
            image.load()  # Ensure image data is loaded
            
            panel_data = {
                'id': id(image),
                'pil_image': image,
                'name': name or os.path.basename(image_path),
                'original_path': image_path
            }
            self.panels.append(panel_data)
            
        except Exception as e:
            raise ValueError(f"Could not load image {image_path}: {e}")
    
    def assemble_figure(
        self,
        target_width_in: float = 7.0,
        dpi: int = 300,
        num_cols: int = 2,
        padding_pt: int = 8,
        margin_pt: int = 12,
        background: str = "white",
        label_style: str = "A, B, C...",
        font_family: str = "Arial",
        label_font_size: int = 14
    ) -> Image.Image:
        """
        Assemble panels into a single figure.
        
        This is the modernized version of the core assembly logic from
        the original Figmaker.py application.
        
        Args:
            target_width_in: Target width in inches
            dpi: Resolution in dots per inch
            num_cols: Number of columns in the grid
            padding_pt: Padding between panels in points
            margin_pt: Margin around the figure in points
            background: Background color ("white", "transparent", "light_gray")
            label_style: Panel labeling style
            font_family: Font family for labels
            label_font_size: Font size for labels in points
            
        Returns:
            PIL Image containing the assembled figure
        """
        if not self.panels:
            raise ValueError("No panels to assemble")
        
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
        
        for i, panel_data in enumerate(self.panels):
            img = panel_data['pil_image']
            
            # Scale to fit column width while maintaining aspect ratio
            scale = col_width_px / img.width
            scaled_w = col_width_px
            scaled_h = int(img.height * scale)
            
            layouts.append({'width': scaled_w, 'height': scaled_h, 'image': img})
            current_row_max_h = max(current_row_max_h, scaled_h)
            
            # Store row height at end of row or last panel
            if (i + 1) % num_cols == 0 or (i + 1) == len(self.panels):
                row_heights.append(current_row_max_h)
                current_row_max_h = 0
        
        # Calculate total dimensions
        content_height = sum(row_heights) + padding_px * (len(row_heights) - 1)
        total_height_px = content_height + (2 * margin_px)
        
        # Create background
        bg_color = self._get_background_color(background)
        if bg_color is None:
            mode = 'RGBA'
            bg_fill = (255, 255, 255, 0)
        else:
            mode = 'RGB'
            bg_fill = bg_color
        
        # Create and assemble figure
        assembled_image = Image.new(mode, (total_width_px, total_height_px), bg_fill)
        draw = ImageDraw.Draw(assembled_image)
        
        # Position and paste panels
        current_x, current_y = margin_px, margin_px
        row_start_y = margin_px
        
        for i, layout in enumerate(layouts):
            col_idx = i % num_cols
            
            # Move to next row if needed
            if col_idx == 0 and i > 0:
                row_idx = i // num_cols
                row_start_y += row_heights[row_idx - 1] + padding_px
            
            current_x = margin_px + col_idx * (col_width_px + padding_px)
            
            # Resize and paste panel
            resized_img = layout['image'].resize(
                (layout['width'], layout['height']), 
                Image.Resampling.LANCZOS
            )
            
            # Handle transparency
            if assembled_image.mode == 'RGBA' and resized_img.mode != 'RGBA':
                resized_img = resized_img.convert('RGBA')
            
            if assembled_image.mode == 'RGBA':
                assembled_image.paste(resized_img, (current_x, row_start_y), resized_img)
            else:
                assembled_image.paste(resized_img, (current_x, row_start_y))
            
            # Add panel labels
            self._add_panel_label(
                draw, i, current_x, row_start_y, dpi, padding_px,
                label_style, font_family, label_font_size
            )
        
        return assembled_image
    
    def _get_background_color(self, background: str) -> Optional[Tuple[int, int, int]]:
        """Convert background string to RGB tuple or None for transparent."""
        bg_map = {
            "white": (255, 255, 255),
            "light_gray": (245, 245, 245),
            "transparent": None
        }
        return bg_map.get(background, (255, 255, 255))
    
    def _add_panel_label(
        self,
        draw: ImageDraw.Draw,
        panel_index: int,
        x: int,
        y: int,
        dpi: int,
        padding_px: int,
        label_style: str,
        font_family: str,
        label_font_size: int
    ) -> None:
        """Add label to a panel."""
        if label_style == "None":
            return
        
        # Generate label text
        label_text = self._get_label_text(label_style, panel_index)
        
        # Get font
        font = self._get_label_font(font_family, label_font_size, dpi)
        
        # Position label
        text_pos_x = x + int(padding_px * 0.3)
        text_pos_y = y + int(padding_px * 0.3)
        
        # Draw label with background
        bbox = draw.textbbox((text_pos_x, text_pos_y), label_text, font=font)
        bg_padding = int(padding_px * 0.1)
        bg_bbox = (
            bbox[0] - bg_padding, bbox[1] - bg_padding,
            bbox[2] + bg_padding, bbox[3] + bg_padding
        )
        
        draw.rectangle(bg_bbox, fill="white", outline="black", width=1)
        draw.text((text_pos_x, text_pos_y), label_text, fill="black", font=font)
    
    def _get_label_text(self, label_style: str, panel_index: int) -> str:
        """Generate label text based on style."""
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
    
    def _get_label_font(self, font_family: str, font_size_pt: int, dpi: int) -> Union[FreeTypeFont, ImageFont.ImageFont]:
        """Get font for panel labels."""
        try:
            font_size_px = int((font_size_pt / 72) * dpi)
            
            if font_family == "Default":
                return ImageFont.load_default()
            
            # Try different font file patterns
            font_patterns = [
                f"{font_family.lower().replace(' ', '')}.ttf",
                f"{font_family.lower().replace(' ', '')}bd.ttf",  # Bold variant
                f"C:/Windows/Fonts/{font_family.replace(' ', '')}.ttf",
                f"C:/Windows/Fonts/{font_family.lower().replace(' ', '')}.ttf",
                f"/System/Library/Fonts/{font_family}.ttf",  # macOS
                f"/usr/share/fonts/truetype/{font_family.lower()}/{font_family.lower()}.ttf",  # Linux
            ]
            
            for pattern in font_patterns:
                try:
                    return ImageFont.truetype(pattern, size=font_size_px)
                except (OSError, IOError):
                    continue
            
            return ImageFont.load_default()
            
        except Exception:
            return ImageFont.load_default()
    
    def add_annotation(self, text: str, x: int, y: int) -> None:
        """Add a text annotation at the specified position."""
        self.annotations.append({'text': text, 'x': x, 'y': y})
    
    def clear_annotations(self) -> None:
        """Clear all annotations."""
        self.annotations = []
    
    def apply_annotations(
        self, 
        image: Image.Image, 
        font_family: str = "Arial",
        font_size_pt: int = 12,
        dpi: int = 300
    ) -> Image.Image:
        """Apply annotations to an assembled image."""
        if not self.annotations:
            return image
        
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        
        # Get annotation font
        font = self._get_annotation_font(font_family, font_size_pt, dpi)
        
        # Draw annotations
        for anno in self.annotations:
            draw.text((anno['x'], anno['y']), anno['text'], fill="black", font=font)
        
        return annotated
    
    def _get_annotation_font(self, font_family: str, font_size_pt: int, dpi: int) -> Union[FreeTypeFont, ImageFont.ImageFont]:
        """Get font for annotations."""
        return self._get_label_font(font_family, font_size_pt, dpi)
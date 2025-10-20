"""
Command-line interface for Figmaker.

This module provides a Typer-based CLI for rendering figures from recipes,
validating configurations, and managing templates.
"""

from __future__ import annotations
import platform
import sys
import yaml
import typer
import importlib
from pathlib import Path
from typing import Optional, List, Dict, Any

from .recipes import Recipe
from .styles import apply_style
from .loader import load_table, fingerprint, save_metadata
from .transforms import apply_pipeline
from .layout import build_canvas
from .plots.image_panel import ImagePanelAssembler

app = typer.Typer(
    name="figmaker",
    help="Scientific figure assembly tool with publication-ready exports",
    no_args_is_help=True
)


@app.command()
def render(
    recipe: str = typer.Argument(..., help="Path to the recipe YAML file"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Output directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate recipe without rendering"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """
    Render a figure from a recipe file.
    
    The recipe file should be a YAML file containing figure specifications,
    data sources, and panel configurations.
    """
    try:
        # Load and validate recipe
        recipe_path = Path(recipe)
        if not recipe_path.exists():
            typer.echo(f"Recipe file not found: {recipe}", err=True)
            raise typer.Exit(1)
        
        with open(recipe_path, "r") as f:
            recipe_data = yaml.safe_load(f)
        
        r = Recipe.model_validate(recipe_data)
        
        if verbose:
            typer.echo(f"Loaded recipe: {recipe_path}")
            typer.echo(f"Figure style: {r.figure.style}")
            typer.echo(f"Panels: {len(r.figure.panels)}")
        
        if dry_run:
            typer.echo("Recipe validation passed ✓")
            return
        
        # Apply style
        apply_style(r.figure.style)
        
        # Determine output directory
        if output_dir is None:
            output_dir = str(recipe_path.parent)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Check if this is an image-only recipe (legacy Figmaker style)
        if all(panel.plot == "image_panel" for panel in r.figure.panels):
            _render_image_figure(r, output_path, verbose)
        else:
            _render_mixed_figure(r, output_path, verbose)
            
        typer.echo("✓ Figure rendered successfully")
        
    except Exception as e:
        typer.echo(f"Error rendering figure: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


def _render_image_figure(recipe: Recipe, output_path: Path, verbose: bool) -> None:
    """Render a figure containing only image panels (legacy Figmaker style)."""
    assembler = ImagePanelAssembler()
    
    # Add panels
    for panel in recipe.figure.panels:
        if panel.image_path:
            assembler.add_panel(panel.image_path, panel.title)
        elif panel.data in {ds.name for ds in recipe.data}:
            # Handle data-driven image panels
            data_source = next(ds for ds in recipe.data if ds.name == panel.data)
            assembler.add_panel(data_source.path, panel.title)
    
    # Assemble figure
    assembled = assembler.assemble_figure(
        target_width_in=recipe.figure.width_cm / 2.54,
        dpi=recipe.figure.dpi,
        background=recipe.figure.background,
        label_style=recipe.figure.label_style,
        font_family=recipe.figure.font_family
    )
    
    # Export
    _export_figure_pil(assembled, recipe, output_path, verbose)


def _render_mixed_figure(recipe: Recipe, output_path: Path, verbose: bool) -> None:
    """Render a figure with mixed panel types using matplotlib."""
    import matplotlib.pyplot as plt
    
    # Load data sources
    data_map = {}
    fps = {}
    
    for ds in recipe.data:
        if verbose:
            typer.echo(f"Loading data: {ds.name} from {ds.path}")
        data_map[ds.name] = load_table(ds.path, ds.sheet)
        fps[ds.name] = fingerprint(ds.path).__dict__
    
    # Create canvas
    fig, axes = build_canvas(
        len(recipe.figure.panels),
        recipe.figure.width_cm,
        recipe.figure.height_cm,
        label_style=recipe.figure.label_style
    )
    
    # Render panels
    for ax, panel in zip(axes, recipe.figure.panels):
        if verbose:
            typer.echo(f"Rendering panel: {panel.plot}")
        
        try:
            # Get data and apply transforms
            if panel.data in data_map:
                df = data_map[panel.data].copy()
                if panel.transforms:
                    df = apply_pipeline(df, [t.model_dump() for t in panel.transforms])
            else:
                df = None
            
            # Import and call plot function
            module = importlib.import_module(f"figmaker.plots.{panel.plot}")
            
            # Handle different plot types
            if panel.plot == "image_panel" and panel.image_path:
                module.draw(ax, panel.image_path, panel.title, **panel.kwargs)
            elif df is not None and panel.x and panel.y:
                module.draw(ax, df, panel.x, panel.y, panel.hue, **panel.kwargs)
            else:
                ax.text(0.5, 0.5, f"Missing data for {panel.plot}",
                       ha='center', va='center', transform=ax.transAxes)
            
            if panel.title:
                ax.set_title(panel.title)
                
        except ImportError:
            ax.text(0.5, 0.5, f"Unknown plot type: {panel.plot}",
                   ha='center', va='center', transform=ax.transAxes,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
        except Exception as e:
            ax.text(0.5, 0.5, f"Error: {str(e)}",
                   ha='center', va='center', transform=ax.transAxes,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
    
    # Create metadata
    meta = {
        "recipe": str(output_path / "recipe.yaml"),
        "data_fingerprints": fps,
        "python": sys.version,
        "platform": platform.platform(),
    }
    
    # Export
    _export_figure_matplotlib(fig, recipe, output_path, meta, verbose)


def _export_figure_pil(
    image, recipe: Recipe, output_path: Path, verbose: bool
) -> None:
    """Export PIL image figure."""
    for fmt, filename in recipe.figure.export.items():
        filepath = output_path / filename
        
        if verbose:
            typer.echo(f"Exporting {fmt.upper()}: {filepath}")
        
        if fmt.lower() in ['png', 'tiff']:
            image.save(filepath, dpi=(recipe.figure.dpi, recipe.figure.dpi))
        elif fmt.lower() == 'pdf':
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(filepath, format='PDF', resolution=recipe.figure.dpi)
        else:
            image.save(filepath)


def _export_figure_matplotlib(
    fig, recipe: Recipe, output_path: Path, meta: Dict[str, Any], verbose: bool
) -> None:
    """Export matplotlib figure."""
    for fmt, filename in recipe.figure.export.items():
        filepath = output_path / filename
        
        if verbose:
            typer.echo(f"Exporting {fmt.upper()}: {filepath}")
        
        if fmt.lower() in ['svg', 'pdf', 'png']:
            fig.savefig(
                filepath,
                dpi=recipe.figure.dpi if fmt.lower() == 'png' else None,
                bbox_inches='tight',
                transparent=(recipe.figure.background == "transparent")
            )
    
    # Save metadata
    meta_path = output_path / f"{Path(list(recipe.figure.export.values())[0]).stem}.meta.json"
    save_metadata(str(meta_path), meta)


@app.command()
def validate(
    recipe: str = typer.Argument(..., help="Path to the recipe YAML file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """
    Validate a recipe file without rendering.
    
    Checks recipe syntax, data source availability, and configuration validity.
    """
    try:
        recipe_path = Path(recipe)
        if not recipe_path.exists():
            typer.echo(f"Recipe file not found: {recipe}", err=True)
            raise typer.Exit(1)
        
        with open(recipe_path, "r") as f:
            recipe_data = yaml.safe_load(f)
        
        r = Recipe.model_validate(recipe_data)
        
        if verbose:
            typer.echo(f"Recipe: {recipe_path}")
            typer.echo(f"Version: {r.version}")
            typer.echo(f"Data sources: {len(r.data)}")
            typer.echo(f"Panels: {len(r.figure.panels)}")
        
        # Check data sources
        missing_files = []
        for ds in r.data:
            if not Path(ds.path).exists():
                missing_files.append(ds.path)
        
        if missing_files:
            typer.echo("⚠ Warning: Missing data files:", err=True)
            for file in missing_files:
                typer.echo(f"  - {file}", err=True)
        
        # Check image paths in panels
        missing_images = []
        for panel in r.figure.panels:
            if panel.image_path and not Path(panel.image_path).exists():
                missing_images.append(panel.image_path)
        
        if missing_images:
            typer.echo("⚠ Warning: Missing image files:", err=True)
            for img in missing_images:
                typer.echo(f"  - {img}", err=True)
        
        if not missing_files and not missing_images:
            typer.echo("✓ Recipe validation passed")
        else:
            typer.echo("⚠ Recipe validation passed with warnings")
            
    except Exception as e:
        typer.echo(f"✗ Recipe validation failed: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def list_templates() -> None:
    """List available plot types and style templates."""
    typer.echo("Available plot types:")
    plot_types = ["image_panel", "scatter", "line_err", "box_swarm", "heatmap"]
    for plot_type in plot_types:
        typer.echo(f"  - {plot_type}")
    
    typer.echo("\nAvailable styles:")
    styles = ["default", "nature", "science", "cell"]
    for style in styles:
        typer.echo(f"  - {style}")


@app.command()
def init(
    name: str = typer.Argument(..., help="Name for the new recipe"),
    style: str = typer.Option("default", help="Figure style"),
    width: float = typer.Option(18.0, help="Figure width in cm"),
    height: float = typer.Option(12.0, help="Figure height in cm"),
) -> None:
    """Create a new recipe template."""
    recipe_data = {
        "version": "1",
        "data": [],
        "figure": {
            "style": style,
            "width_cm": width,
            "height_cm": height,
            "dpi": 600,
            "background": "white",
            "font_family": "Arial",
            "label_style": "A, B, C...",
            "panels": [],
            "export": {"png": f"{name}.png", "pdf": f"{name}.pdf"}
        }
    }
    
    filename = f"{name}.yaml"
    with open(filename, "w") as f:
        yaml.dump(recipe_data, f, indent=2, default_flow_style=False)
    
    typer.echo(f"Created recipe template: {filename}")


@app.command()
def gui() -> None:
    """Launch the Figmaker GUI application."""
    try:
        # Import and run the GUI
        from Figmaker import FigureAssemblerApp
        app = FigureAssemblerApp()
        app.mainloop()
    except ImportError:
        typer.echo("GUI dependencies not available", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
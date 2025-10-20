# Figmaker Examples

This directory contains example recipe files demonstrating different features of the modernized Figmaker system.

## Image Panel Assembly (Legacy Compatible)

**File: `image_panels.yaml`**

This example shows how to use the new recipe system for traditional image panel assembly, maintaining full backward compatibility with the original Figmaker GUI workflow.

Key features:
- Multi-panel image assembly
- Scientific panel labeling (A, B, C...)
- Publication-ready DPI settings
- Multiple export formats
- Nature journal style

Usage:
```bash
figmaker render image_panels.yaml
```

## Scientific Data Visualization

**File: `scientific_figure.yaml`**

This example demonstrates the new capabilities for data-driven figure generation, going beyond simple image assembly.

Key features:
- Data loading from CSV files
- Statistical transformations (p-value correction, filtering)
- Multiple plot types (heatmap, volcano plot, box plot)
- Automatic layout with GridSpec
- Publication-ready styling

Usage:
```bash
figmaker render scientific_figure.yaml
```

## Recipe Validation

You can validate any recipe without rendering:

```bash
figmaker validate image_panels.yaml
figmaker validate scientific_figure.yaml
```

## Creating New Recipes

Generate a new recipe template:

```bash
figmaker init my_figure --style nature --width 15 --height 10
```

## Available Commands

- `figmaker render <recipe.yaml>` - Render figure from recipe
- `figmaker validate <recipe.yaml>` - Validate recipe syntax and data availability  
- `figmaker list-templates` - List available plot types and styles
- `figmaker init <name>` - Create new recipe template
- `figmaker gui` - Launch traditional GUI interface

## Migration from Original Figmaker

The new system is designed to be fully backward-compatible. Your existing workflow using the GUI remains unchanged, but you now have additional options:

1. **Continue using GUI**: The original interface still works exactly as before
2. **Export recipes**: Save your GUI projects as recipes for reproducibility
3. **Use CLI**: Render figures from command line for automation
4. **Extend with data**: Add data visualization capabilities to image assembly

## Directory Structure

```
examples/
├── README.md              # This file
├── image_panels.yaml      # Image assembly example
├── scientific_figure.yaml # Data visualization example
└── sample_data/           # Sample data files (to be created)
    ├── gene_expression.csv
    └── deseq_results.csv
```
# Figmaker: Scientific Figure Assembly Tool

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Figmaker** is a production-grade scientific figure assembly tool that combines the simplicity of GUI-based image arrangement with the power of declarative, reproducible figure generation.

## 🔬 What's New in v0.2.0

Figmaker has been completely rearchitected from a single-file GUI application into a robust, modular system while maintaining **100% backward compatibility** with existing workflows.

### Key Improvements

- **📋 Declarative Recipes**: YAML-based figure specifications for reproducible science
- **🎨 Journal Styles**: Built-in presets for Nature, Science, Cell with publication-ready formatting
- **⚡ CLI Interface**: Automated figure generation for workflows and CI/CD
- **🔍 Data Integration**: Native support for CSV, Excel, and statistical transformations
- **📊 Provenance Tracking**: Automatic metadata and data fingerprinting
- **🎯 Modular Architecture**: Clean separation of concerns for maintainability
- **✅ Type Safety**: Pydantic models with full validation
- **🧪 Golden Image Tests**: Regression testing with pytest-mpl

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/mhendzel2/Figmaker.git
cd Figmaker

# Install with pip (recommended)
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

### GUI Mode (Original Interface)

```bash
# Launch the familiar GUI interface
python Figmaker.py
# OR
figmaker gui
```

### CLI Mode (New!)

```bash
# Create a new recipe template
figmaker init my_figure --style nature

# Render a figure from recipe
figmaker render examples/image_panels.yaml

# Validate a recipe
figmaker validate my_figure.yaml

# List available templates and styles
figmaker list-templates
```

## 📖 Usage Examples

### Image Panel Assembly (Traditional Workflow)

```yaml
# image_panels.yaml
version: "1"
figure:
  style: nature
  width_cm: 18.0
  height_cm: 12.0
  dpi: 600
  panels:
    - plot: image_panel
      image_path: "western_blot.tiff"
      title: "Western Blot"
    - plot: image_panel
      image_path: "microscopy.tiff"
      title: "Fluorescence"
export:
  png: "figure1.png"
  pdf: "figure1.pdf"
```

### Data-Driven Figures (New Capability)

```yaml
# scientific_figure.yaml
version: "1"
data:
  - name: expression
    path: "gene_expression.csv"
figure:
  style: nature
  panels:
    - plot: volcano
      data: expression
      x: log2FoldChange
      y: neglog10_pvalue
      transforms:
        - op: p_adjust_bh
          args: {pcol: "pvalue"}
```

## 🏗️ Architecture

### Before: Monolithic Design
```
Figmaker.py (730 lines)
├── GUI logic
├── Image processing  
├── Layout calculations
├── Export handling
└── Project persistence
```

### After: Modular Architecture
```
figmaker/
├── recipes.py      # Pydantic models & validation
├── styles.py       # Journal presets & palettes  
├── loader.py       # Data loading & fingerprinting
├── transforms.py   # Statistical operations
├── layout.py       # GridSpec-based layouts
├── plots/          # Modular plot renderers
│   └── image_panel.py
├── cli.py          # Typer-based CLI
└── export.py       # Multi-format exports
```

## 🔄 Migration Guide

### Existing Users (GUI)
**No changes required!** Your existing workflow continues to work exactly as before. The GUI interface (`Figmaker.py`) remains unchanged and fully functional.

### Power Users (New Features)
1. **Save projects as recipes** for reproducibility
2. **Use CLI** for batch processing and automation
3. **Add data visualization** to your image assembly workflow
4. **Apply journal styles** for publication-ready formatting

### Developers (API)
The core functionality is now available as importable modules:

```python
from figmaker import Recipe, apply_style
from figmaker.plots.image_panel import ImagePanelAssembler

# Load and validate recipe
recipe = Recipe.model_validate_file("my_figure.yaml")

# Apply publication style
apply_style("nature")

# Assemble images programmatically
assembler = ImagePanelAssembler()
assembler.add_panel("panel_a.tiff")
result = assembler.assemble_figure(dpi=600)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=figmaker

# Run specific test modules
pytest tests/test_modular_architecture.py -v
pytest tests/test_figmaker_core.py -v

# Golden image tests (requires pytest-mpl)
pytest --mpl-generate-path=baseline tests/
pytest --mpl tests/
```

## 📊 Technical Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Architecture** | Single 730-line file | Modular package with separation of concerns |
| **Testing** | Basic unit tests | Comprehensive test suite + golden image tests |
| **Reproducibility** | GUI-only, manual | Declarative recipes with data fingerprinting |
| **Styles** | Hardcoded settings | Journal presets (Nature, Science, Cell) |
| **Data Handling** | Image files only | CSV, Excel + statistical transforms |
| **CLI** | None | Full Typer-based interface |
| **Type Safety** | None | Pydantic models with validation |
| **Extensibility** | Monolithic | Plugin-friendly modular design |

## 🤝 Contributing

We welcome contributions! The new modular architecture makes it much easier to:

- Add new plot types (`figmaker/plots/`)
- Extend statistical transforms (`figmaker/transforms.py`)
- Add journal styles (`figmaker/styles.py`) 
- Improve layout algorithms (`figmaker/layout.py`)

See `CONTRIBUTING.md` for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original Figmaker GUI design and core algorithms
- Scientific community feedback on publication requirements
- [Your production-grade scaffold](https://github.com/user/assessment) for the architectural improvements

---

**Figmaker v0.2.0**: Same great tool, now with production-grade reliability and reproducible science capabilities.

# Figmaker AI Coding Guidelines

## Project Overview
Figmaker is a desktop GUI application for assembling scientific publication figures from multiple image panels. Built with `customtkinter` and PIL/Pillow, it provides publication-ready figure generation with precise DPI control, scientific labeling conventions, and multi-format export.

## Architecture & Core Components

### Single-File Design Pattern
- **Everything in `Figmaker.py`**: The entire application lives in one 730-line file with the main `FigureAssemblerApp` class
- **State Management**: Core data structures are `self.panels` (list of panel dicts) and `self.annotations` (list of annotation dicts)
- **UI Framework**: Uses `customtkinter` for modern UI with left control panel + right canvas layout

### Key Data Structures
```python
# Panel structure - maintain this exact format
{'id': id(image), 'pil_image': Image, 'name': str, 'original_path': str}

# Annotation structure
{'text': str, 'x': int, 'y': int}  # coordinates in original image pixels
```

### Publication-Focused Design Principles
- **DPI-First Workflow**: All measurements convert to pixels via DPI (72 points = 1 inch)
- **Scientific Labeling**: Built-in support for A,B,C / a,b,c / 1,2,3 / i,ii,iii panel labels
- **Format Support**: PNG/TIFF (with DPI), PDF, JPEG export with proper metadata

## Development Patterns

### GUI Testing Strategy
Use the `DummyApp` pattern from `tests/test_figmaker_core.py`:
```python
class DummyApp(FigureAssemblerApp):
    def __init__(self):
        object.__init__(self)  # Skip CTk.__init__ for headless testing
        # Mock UI elements as needed
        self.dpi_var = type('X', (), {'get': lambda self: '300'})()
```

### Image Processing Workflow
1. **Load & Store**: `select_files()` loads images into `self.panels` list
2. **Calculate Layout**: `assemble_figure()` computes pixel dimensions from DPI/inches
3. **Resize & Position**: Maintain aspect ratios, align to grid with padding/margins
4. **Label & Annotate**: Add scientific labels and custom text annotations
5. **Export**: Save with proper DPI metadata for publication

### Font Handling Pattern
The app uses a multi-fallback font loading system:
```python
# Always try multiple font file patterns for cross-platform compatibility
font_patterns = [
    f"{font_name.lower().replace(' ', '')}.ttf",
    f"C:/Windows/Fonts/{font_name.replace(' ', '')}.ttf"
]
```

## Testing & Quality

### Running Tests
```bash
pytest                    # Run all tests with pytest.ini config
pytest tests/test_*.py   # Explicit test pattern
```

### Test Coverage Focus
- Core assembly logic (`assemble_figure()`)
- Background color handling (including transparency)
- DPI/dimension calculations
- Panel data structure integrity

## Key Implementation Notes

### Coordinate System Management
- **Canvas Display**: Scaled coordinates for UI display
- **Original Image**: Full-resolution coordinates for export
- **Conversion**: Always convert between display ↔ original when handling clicks/annotations

### Memory Management
- PIL Images are loaded with `.load()` to ensure data stays in memory
- Canvas images require reference keeping: `self.canvas.image = self.canvas_image`

### Project Persistence
- Save/load projects as JSON with panel file paths and all settings
- Handle missing files gracefully when loading projects

## Common Modification Patterns

### Adding New Export Formats
1. Add to `export_format_dropdown` values
2. Extend format handling in `export_figure()`
3. Consider DPI metadata requirements

### Adding Layout Options
1. Add UI controls in `create_controls_frame()`
2. Extend calculation logic in `assemble_figure()`
3. Test with various panel counts/aspect ratios

### Font System Extensions
1. Extend `_get_system_fonts()` for new platforms
2. Add fallback patterns in font loading methods
3. Consider font embedding for PDF export

## Dependencies & Environment
- **Core**: `customtkinter`, `Pillow`, `tkinter` (built-in)
- **Testing**: `pytest`
- **Platform**: Windows-focused (font paths), but cross-platform capable
- **Python**: Modern Python 3.x with type hints where beneficial
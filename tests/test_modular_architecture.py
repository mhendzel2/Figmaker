"""
Tests for the new modular Figmaker architecture.

These tests cover the new recipe system, transforms, layout engine,
and image panel assembler while maintaining compatibility with existing tests.
"""

import tempfile
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image

from figmaker.recipes import Recipe, FigureSpec, Panel, DataSource, Transform
from figmaker.styles import apply_style, get_palette
from figmaker.loader import fingerprint, load_table, create_project_fingerprint
from figmaker.transforms import apply_pipeline, p_adjust_bh, log2fc
from figmaker.layout import build_canvas, create_legacy_layout
from figmaker.plots.image_panel import ImagePanelAssembler


def create_test_image(size=(100, 80), color=(200, 100, 50)):
    """Create a test image for testing."""
    return Image.new('RGB', size, color=color)


def create_test_csv(path: Path, n_rows: int = 100):
    """Create a test CSV file with sample data."""
    np.random.seed(42)
    data = {
        'gene': [f'Gene_{i:03d}' for i in range(n_rows)],
        'log2FoldChange': np.random.normal(0, 2, n_rows),
        'pvalue': np.random.uniform(0, 1, n_rows),
        'expression_control': np.random.lognormal(0, 1, n_rows),
        'expression_treated': np.random.lognormal(0.5, 1, n_rows),
    }
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    return df


class TestRecipes:
    """Test recipe validation and parsing."""
    
    def test_recipe_validation(self):
        """Test that recipe models validate correctly."""
        recipe_data = {
            "version": "1",
            "data": [{"name": "test", "path": "test.csv"}],
            "figure": {
                "style": "nature",
                "width_cm": 18.0,
                "height_cm": 12.0,
                "dpi": 600,
                "panels": [
                    {
                        "plot": "image_panel",
                        "data": "test",
                        "image_path": "test.png"
                    }
                ]
            }
        }
        
        recipe = Recipe.model_validate(recipe_data)
        assert recipe.version == "1"
        assert len(recipe.data) == 1
        assert recipe.figure.style == "nature"
        assert len(recipe.figure.panels) == 1
    
    def test_recipe_defaults(self):
        """Test that recipe defaults are applied correctly."""
        minimal_recipe = {
            "figure": {
                "panels": []
            }
        }
        
        recipe = Recipe.model_validate(minimal_recipe)
        assert recipe.version == "1"
        assert recipe.figure.style == "default"
        assert recipe.figure.dpi == 600
        assert recipe.figure.background == "white"


class TestStyles:
    """Test style system."""
    
    def test_apply_style(self):
        """Test that styles can be applied without error."""
        for style in ["default", "nature", "science", "cell"]:
            apply_style(style)  # Should not raise
    
    def test_unknown_style(self):
        """Test that unknown styles raise appropriate error."""
        with pytest.raises(ValueError):
            apply_style("unknown_style")
    
    def test_get_palette(self):
        """Test palette retrieval."""
        cb_safe = get_palette("cb_safe")
        assert len(cb_safe) == 7
        assert all(color.startswith("#") for color in cb_safe)
    
    def test_unknown_palette(self):
        """Test that unknown palettes raise appropriate error."""
        with pytest.raises(ValueError):
            get_palette("unknown_palette")


class TestLoader:
    """Test data loading and fingerprinting."""
    
    def test_fingerprint_creation(self, tmp_path):
        """Test file fingerprinting."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, world!")
        
        fp = fingerprint(str(test_file))
        assert fp.path == str(test_file)
        assert fp.size > 0
        assert len(fp.sha256) == 64  # SHA256 hex length
    
    def test_load_csv(self, tmp_path):
        """Test CSV loading."""
        csv_file = tmp_path / "test.csv"
        test_df = create_test_csv(csv_file)
        
        loaded_df = load_table(str(csv_file))
        pd.testing.assert_frame_equal(test_df, loaded_df)
    
    def test_project_fingerprint(self, tmp_path):
        """Test project fingerprint creation."""
        # Create test images
        img1_path = tmp_path / "img1.png"
        img2_path = tmp_path / "img2.png"
        
        create_test_image().save(img1_path)
        create_test_image(color=(100, 200, 50)).save(img2_path)
        
        panels = [
            {'name': 'img1', 'original_path': str(img1_path)},
            {'name': 'img2', 'original_path': str(img2_path)},
        ]
        
        settings = {'dpi': 300, 'style': 'nature'}
        
        fp = create_project_fingerprint(panels, settings)
        assert 'timestamp' in fp
        assert 'file_fingerprints' in fp
        assert len(fp['file_fingerprints']) == 2


class TestTransforms:
    """Test data transformation pipeline."""
    
    def test_p_adjust_bh(self):
        """Test Benjamini-Hochberg correction."""
        df = pd.DataFrame({
            'pvalue': [0.001, 0.01, 0.05, 0.1, 0.5]
        })
        
        result = p_adjust_bh(df, 'pvalue')
        assert 'p_adj' in result.columns
        # Adjusted p-values should be >= original p-values
        assert all(result['p_adj'] >= result['pvalue'])
    
    def test_log2fc(self):
        """Test log2 fold change calculation."""
        df = pd.DataFrame({
            'treated': [10, 20, 5],
            'control': [5, 10, 10]
        })
        
        result = log2fc(df, 'treated', 'control')
        assert 'log2fc' in result.columns
        # Check specific values
        expected = np.log2(df['treated'] / df['control'])
        np.testing.assert_array_almost_equal(result['log2fc'], expected, decimal=6)
    
    def test_transform_pipeline(self):
        """Test applying multiple transforms in sequence."""
        df = pd.DataFrame({
            'gene': ['A', 'B', 'C', 'D'],
            'pvalue': [0.001, 0.01, 0.05, 0.1],
            'expr_control': [5, 10, 15, 20],
            'expr_treated': [10, 20, 7.5, 10]
        })
        
        transforms = [
            {'op': 'log2fc', 'args': {'num': 'expr_treated', 'den': 'expr_control'}},
            {'op': 'p_adjust_bh', 'args': {'pcol': 'pvalue'}},
            {'op': 'filter', 'args': {'expr': 'p_adj < 0.1'}}
        ]
        
        result = apply_pipeline(df, transforms)
        assert 'log2fc' in result.columns
        assert 'p_adj' in result.columns
        assert len(result) <= len(df)  # Some rows filtered


class TestLayout:
    """Test layout engine."""
    
    def test_build_canvas(self):
        """Test canvas creation with GridSpec."""
        fig, axes = build_canvas(
            n_panels=4,
            width_cm=18.0,
            height_cm=12.0,
            label_style="A, B, C..."
        )
        
        assert len(axes) == 4
        assert fig.get_figwidth() == pytest.approx(18.0 / 2.54, rel=1e-2)
        assert fig.get_figheight() == pytest.approx(12.0 / 2.54, rel=1e-2)
    
    def test_legacy_layout_compatibility(self):
        """Test that legacy layout calculations work correctly."""
        # Create mock panels
        panels = []
        for i in range(3):
            img = create_test_image(size=(200, 150))
            panels.append({
                'pil_image': img,
                'name': f'panel_{i}',
                'original_path': f'test_{i}.png'
            })
        
        width_px, height_px, layouts = create_legacy_layout(
            panels=panels,
            target_width_in=7.0,
            dpi=300,
            num_cols=2,
            padding_pt=8,
            margin_pt=12
        )
        
        assert width_px == 7.0 * 300  # 2100 pixels
        assert height_px > 0
        assert len(layouts) == 3
        assert all('x' in layout and 'y' in layout for layout in layouts)


class TestImagePanelAssembler:
    """Test image panel assembly."""
    
    def test_assembler_creation(self):
        """Test that assembler can be created and panels added."""
        assembler = ImagePanelAssembler()
        assert len(assembler.panels) == 0
        assert len(assembler.annotations) == 0
    
    def test_add_panel(self, tmp_path):
        """Test adding panels to assembler."""
        assembler = ImagePanelAssembler()
        
        # Create test image
        img_path = tmp_path / "test.png"
        create_test_image().save(img_path)
        
        assembler.add_panel(str(img_path), "Test Panel")
        assert len(assembler.panels) == 1
        assert assembler.panels[0]['name'] == "Test Panel"
    
    def test_figure_assembly(self, tmp_path):
        """Test complete figure assembly."""
        assembler = ImagePanelAssembler()
        
        # Create test images
        for i in range(2):
            img_path = tmp_path / f"panel_{i}.png"
            create_test_image(color=(100*i, 150, 200)).save(img_path)
            assembler.add_panel(str(img_path), f"Panel {i+1}")
        
        # Assemble figure
        result = assembler.assemble_figure(
            target_width_in=4.0,
            dpi=150,
            num_cols=2,
            background="white"
        )
        
        assert result is not None
        assert result.width == 4.0 * 150  # 600 pixels
        assert result.height > 0
        assert result.mode == 'RGB'
    
    def test_transparent_background(self, tmp_path):
        """Test assembly with transparent background."""
        assembler = ImagePanelAssembler()
        
        img_path = tmp_path / "test.png"
        create_test_image().save(img_path)
        assembler.add_panel(str(img_path))
        
        result = assembler.assemble_figure(
            target_width_in=2.0,
            dpi=100,
            background="transparent"
        )
        
        assert result.mode == 'RGBA'
    
    def test_annotations(self, tmp_path):
        """Test annotation functionality."""
        assembler = ImagePanelAssembler()
        
        img_path = tmp_path / "test.png"
        create_test_image().save(img_path)
        assembler.add_panel(str(img_path))
        
        # Add annotation
        assembler.add_annotation("Test annotation", 50, 50)
        assert len(assembler.annotations) == 1
        
        # Test applying annotations
        base_image = assembler.assemble_figure(
            target_width_in=2.0,
            dpi=100
        )
        
        annotated = assembler.apply_annotations(base_image)
        assert annotated is not None
        # Annotated image should be different from base
        assert not np.array_equal(np.array(base_image), np.array(annotated))


class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_full_recipe_processing(self, tmp_path):
        """Test complete recipe-to-figure workflow."""
        # Create test data
        csv_file = tmp_path / "test_data.csv"
        create_test_csv(csv_file, n_rows=20)
        
        # Create test images
        img_paths = []
        for i in range(2):
            img_path = tmp_path / f"panel_{i}.png"
            create_test_image(color=(100*i, 150, 200)).save(img_path)
            img_paths.append(str(img_path))
        
        # Create recipe
        recipe_data = {
            "version": "1",
            "data": [{"name": "test_data", "path": str(csv_file)}],
            "figure": {
                "style": "nature",
                "width_cm": 12.0,
                "height_cm": 8.0,
                "dpi": 150,
                "panels": [
                    {
                        "plot": "image_panel",
                        "data": "test_data",
                        "image_path": img_paths[0],
                        "title": "Panel A"
                    },
                    {
                        "plot": "image_panel", 
                        "data": "test_data",
                        "image_path": img_paths[1],
                        "title": "Panel B"
                    }
                ],
                "export": {"png": "test_output.png"}
            }
        }
        
        recipe = Recipe.model_validate(recipe_data)
        assert len(recipe.figure.panels) == 2
        assert recipe.figure.style == "nature"
    
    def test_backward_compatibility(self):
        """Test that new system maintains compatibility with original Figmaker structures."""
        # Test that legacy panel data structure still works
        legacy_panel = {
            'id': 12345,
            'pil_image': create_test_image(),
            'name': 'test_panel.png',
            'original_path': '/path/to/test_panel.png'
        }
        
        # This should work with new layout functions
        width_px, height_px, layouts = create_legacy_layout(
            panels=[legacy_panel],
            target_width_in=5.0,
            dpi=300,
            num_cols=1,
            padding_pt=8,
            margin_pt=12
        )
        
        assert width_px > 0
        assert height_px > 0
        assert len(layouts) == 1


# Run tests with: pytest tests/test_modular_architecture.py -v
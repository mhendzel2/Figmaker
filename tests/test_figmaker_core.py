import io
import os
import sys
from PIL import Image
import pytest

# Ensure repository root is on sys.path so tests can import Figmaker
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Provide a minimal stub for customtkinter to allow importing Figmaker in CI/headless
import types
if 'customtkinter' not in sys.modules:
    fake_ctk = types.SimpleNamespace(
        CTk=object,
        CTkFrame=object,
        CTkLabel=object,
        CTkButton=object,
        CTkEntry=object,
        CTkOptionMenu=object,
        CTkScrollableFrame=object,
        CTkCanvas=object,
        set_appearance_mode=lambda m: None,
        set_default_color_theme=lambda t: None,
        CTkFont=lambda **k: None
    )
    sys.modules['customtkinter'] = fake_ctk

from Figmaker import FigureAssemblerApp


class DummyApp(FigureAssemblerApp):
    """Subclass the app to avoid initializing the full CTk GUI loop for tests.
    We override methods that create windows to keep tests headless.
    """
    def __init__(self):
        # Avoid calling CTk.__init__ to prevent GUI initialization
        # Instead, set up only the attributes used by the tested methods
        # by calling object.__init__ and then manually setting fields.
        object.__init__(self)
        # Minimal attributes used by methods under test
        import io
        import os
        from PIL import Image
        import pytest

        from Figmaker import FigureAssemblerApp


        class DummyApp(FigureAssemblerApp):
            """Subclass the app to avoid initializing the full CTk GUI loop for tests.
            We override methods that create windows to keep tests headless.
            """
            def __init__(self):
                # Avoid calling CTk.__init__ to prevent GUI initialization
                # Instead, set up only the attributes used by the tested methods
                # by calling object.__init__ and then manually setting fields.
                object.__init__(self)
                # Minimal attributes used by methods under test
                self.pub_settings = {
                    'label_font_size': 14
                }
                self.font_var = type('X', (), {'get': lambda self: 'Default'})()
                self.dpi_var = type('X', (), {'get': lambda self: '300'})()
                self.bg_var = type('X', (), {'get': lambda self: 'White'})()
                self.font_size_entry = type('E', (), {'get': lambda self: '12'})()
                self.target_width_entry = type('E', (), {'get': lambda self: '7.0', 'delete': lambda *a, **k: None, 'insert': lambda *a, **k: None})()
                self.num_cols_entry = type('E', (), {'get': lambda self: '2'})()
                self.padding_entry = type('E', (), {'get': lambda self: '8'})()
                self.margin_entry = type('E', (), {'get': lambda self: '12'})()
                self.label_style_var = type('X', (), {'get': lambda self: 'A, B, C...'})()
                self.panels = []
                self.annotations = []
                self.canvas = None
                self.canvas_frame = None
                self.canvas_placeholder = None
                self.canvas_image = None
                self.export_button = type('E', (), {'configure': lambda *a, **k: None})()

            def update_panel_list(self):
                pass

    def display_image(self, img):
        # For tests, don't require a real canvas — just store the image
    self._last_displayed = pil_image


        def make_test_image(color=(200, 100, 50), size=(100, 80)):
            img = Image.new('RGB', size, color=color)
            return img


        def test_get_background_color_white():
            app = DummyApp()
            app.bg_var = type('X', (), {'get': lambda self: 'White'})()
            assert app._get_background_color() == 'white'


        def test_get_background_color_transparent():
            app = DummyApp()
            app.bg_var = type('X', (), {'get': lambda self: 'Transparent'})()
            assert app._get_background_color() is None


        def test_assemble_figure_basic_layout():
            app = DummyApp()
            # Create two panels and set UI-like fields
            img1 = make_test_image(size=(200, 100))
            img2 = make_test_image(size=(50, 150))
            app.panels = [
                {'id': 1, 'pil_image': img1, 'name': 'img1', 'original_path': ''},
                {'id': 2, 'pil_image': img2, 'name': 'img2', 'original_path': ''}
            ]

            # Settings
            app.target_width_entry = type('E', (), {'get': lambda self: '4.0'})()
            app.dpi_var = type('X', (), {'get': lambda self: '150'})()
            app.num_cols_entry = type('E', (), {'get': lambda self: '2'})()
            app.padding_entry = type('E', (), {'get': lambda self: '10'})()
            app.margin_entry = type('E', (), {'get': lambda self: '12'})()
            app.bg_var = type('X', (), {'get': lambda self: 'White'})()

            # Call assemble
            app.assemble_figure()

            # Check assembled image exists and has expected width
            assert hasattr(app, 'assembled_image') and app.assembled_image is not None
            dpi = int(app.dpi_var.get())
            expected_width = int(float(app.target_width_entry.get()) * dpi)
            assert app.assembled_image.width == expected_width


        def test_assemble_with_transparent_bg():
            app = DummyApp()
            img1 = make_test_image(size=(120, 80))
            app.panels = [{'id': 1, 'pil_image': img1, 'name': 'img1', 'original_path': ''}]

            app.target_width_entry = type('E', (), {'get': lambda self: '2.0'})()
            app.dpi_var = type('X', (), {'get': lambda self: '100'})()
            app.num_cols_entry = type('E', (), {'get': lambda self: '1'})()
            app.padding_entry = type('E', (), {'get': lambda self: '5'})()
            app.margin_entry = type('E', (), {'get': lambda self: '4'})()
            app.bg_var = type('X', (), {'get': lambda self: 'Transparent'})()

            app.assemble_figure()

    assert app.assembled_image is not None
    assert app.assembled_image.mode == 'RGBA'

*** End Patch
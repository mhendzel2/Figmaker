import tkinter
from tkinter import filedialog, simpledialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageEnhance
import os
import json
from pathlib import Path

# Set theme and color scheme for the application
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

class FigureAssemblerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("Scientific Figure Assembler")
        self.geometry("1400x800")

        # --- App State ---
        self.panels = [] # List to store panel data: {'id', 'pil_image', 'name', 'original_path'}
        self.annotations = [] # List to store annotation data
        self.assembled_image = None # To hold the final PIL Image
        self.canvas_image = None # To hold the displayable PhotoImage for the canvas
        
        # --- Publication Settings ---
        self.pub_settings = {
            'default_dpi': 300,
            'high_dpi': 600,
            'font_family': 'Arial',
            'label_font_size': 14,
            'annotation_font_size': 12,
            'background_color': 'white',
            'label_style': 'bold',
            'export_formats': ['PNG', 'TIFF', 'PDF', 'SVG']
        }
        
        # --- Font Management ---
        self.available_fonts = self._get_system_fonts()

        # --- Layout Configuration ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Create UI Frames ---
        self.create_controls_frame()
        self.create_canvas_frame()
        
    def _get_system_fonts(self):
        """Get available system fonts for publication use."""
        common_fonts = [
            'Arial', 'Arial Bold', 'Helvetica', 'Times New Roman', 
            'Calibri', 'Liberation Sans', 'DejaVu Sans'
        ]
        available = []
        for font_name in common_fonts:
            try:
                ImageFont.truetype(f"{font_name.lower().replace(' ', '')}.ttf", 12)
                available.append(font_name)
            except (OSError, IOError):
                try:
                    # Try common font paths
                    font_paths = [
                        f"C:/Windows/Fonts/{font_name.replace(' ', '')}.ttf",
                        f"C:/Windows/Fonts/{font_name.lower().replace(' ', '')}.ttf"
                    ]
                    for path in font_paths:
                        if os.path.exists(path):
                            available.append(font_name)
                            break
                except:
                    continue
        return available if available else ['Default']
        
    def create_controls_frame(self):
        """Creates the left-side panel for all user controls."""
        controls_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        controls_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        controls_frame.grid_propagate(False) # Prevent resizing
        
        # --- File Upload Section ---
        upload_label = ctk.CTkLabel(controls_frame, text="1. Upload Panels", font=ctk.CTkFont(size=16, weight="bold"))
        upload_label.pack(pady=10, padx=20, anchor="w")

        upload_button = ctk.CTkButton(controls_frame, text="Select Image Files", command=self.select_files)
        upload_button.pack(pady=5, padx=20, fill="x")

        # --- Panel List Section ---
        self.panel_list_frame = ctk.CTkScrollableFrame(controls_frame, label_text="Panel Order")
        self.panel_list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.panel_list_placeholder = ctk.CTkLabel(self.panel_list_frame, text="No panels uploaded.")
        self.panel_list_placeholder.pack(pady=20)


        # --- Layout Settings Section ---
        layout_label = ctk.CTkLabel(controls_frame, text="2. Layout Settings", font=ctk.CTkFont(size=16, weight="bold"))
        layout_label.pack(pady=10, padx=20, anchor="w")

        self.target_width_entry = self.create_setting_entry(controls_frame, "Width (in)", "7.0")
        
        # DPI Selection with presets
        dpi_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        dpi_frame.pack(pady=2, padx=20, fill="x")
        dpi_label = ctk.CTkLabel(dpi_frame, text="Resolution (DPI)", width=120, anchor="w")
        dpi_label.pack(side="left")
        self.dpi_var = ctk.StringVar(value="300")
        self.dpi_dropdown = ctk.CTkOptionMenu(dpi_frame, values=["150", "300", "600", "1200"], variable=self.dpi_var)
        self.dpi_dropdown.pack(side="left", fill="x", expand=True)
        
        self.num_cols_entry = self.create_setting_entry(controls_frame, "Columns", "2")
        self.padding_entry = self.create_setting_entry(controls_frame, "Spacing (pt)", "8")
        
        # Add margin controls
        self.margin_entry = self.create_setting_entry(controls_frame, "Margins (pt)", "12")
        
        # Background color option
        bg_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        bg_frame.pack(pady=2, padx=20, fill="x")
        bg_label = ctk.CTkLabel(bg_frame, text="Background", width=120, anchor="w")
        bg_label.pack(side="left")
        self.bg_var = ctk.StringVar(value="White")
        self.bg_dropdown = ctk.CTkOptionMenu(bg_frame, values=["White", "Transparent", "Light Gray"], variable=self.bg_var)
        self.bg_dropdown.pack(side="left", fill="x", expand=True)

        # --- Annotation Settings Section ---
        anno_label = ctk.CTkLabel(controls_frame, text="3. Annotation Settings", font=ctk.CTkFont(size=16, weight="bold"))
        anno_label.pack(pady=10, padx=20, anchor="w")

        # Font selection
        font_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        font_frame.pack(pady=2, padx=20, fill="x")
        font_label = ctk.CTkLabel(font_frame, text="Font Family", width=120, anchor="w")
        font_label.pack(side="left")
        self.font_var = ctk.StringVar(value=self.available_fonts[0] if self.available_fonts else "Default")
        self.font_dropdown = ctk.CTkOptionMenu(font_frame, values=self.available_fonts, variable=self.font_var)
        self.font_dropdown.pack(side="left", fill="x", expand=True)

        self.font_size_entry = self.create_setting_entry(controls_frame, "Font Size (pt)", "12")
        
        # Label style options
        label_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        label_frame.pack(pady=2, padx=20, fill="x")
        label_label = ctk.CTkLabel(label_frame, text="Panel Labels", width=120, anchor="w")
        label_label.pack(side="left")
        self.label_style_var = ctk.StringVar(value="A, B, C...")
        self.label_style_dropdown = ctk.CTkOptionMenu(label_frame, values=["A, B, C...", "a, b, c...", "1, 2, 3...", "i, ii, iii...", "None"], variable=self.label_style_var)
        self.label_style_dropdown.pack(side="left", fill="x", expand=True)

        self.add_text_button = ctk.CTkButton(controls_frame, text="Add Text Annotation", command=self.enable_add_text_mode)
        self.add_text_button.pack(pady=5, padx=20, fill="x")
        
        # Annotation management
        self.clear_annotations_button = ctk.CTkButton(controls_frame, text="Clear All Annotations", command=self.clear_annotations)
        self.clear_annotations_button.pack(pady=2, padx=20, fill="x")

        # --- Actions Section ---
        actions_label = ctk.CTkLabel(controls_frame, text="4. Finalize Figure", font=ctk.CTkFont(size=16, weight="bold"))
        actions_label.pack(pady=10, padx=20, anchor="w")
        
        assemble_button = ctk.CTkButton(controls_frame, text="Assemble / Update Figure", command=self.assemble_figure)
        assemble_button.pack(pady=5, padx=20, fill="x")

        # Export format selection
        export_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        export_frame.pack(pady=2, padx=20, fill="x")
        export_label = ctk.CTkLabel(export_frame, text="Export Format", width=120, anchor="w")
        export_label.pack(side="left")
        self.export_format_var = ctk.StringVar(value="PNG")
        self.export_format_dropdown = ctk.CTkOptionMenu(export_frame, values=["PNG", "TIFF", "PDF", "JPEG"], variable=self.export_format_var)
        self.export_format_dropdown.pack(side="left", fill="x", expand=True)

        self.export_button = ctk.CTkButton(controls_frame, text="Export Figure", command=self.export_figure, state="disabled")
        self.export_button.pack(pady=5, padx=20, fill="x")
        
        # Save/Load project
        project_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        project_frame.pack(pady=5, padx=20, fill="x")
        self.save_project_button = ctk.CTkButton(project_frame, text="Save Project", command=self.save_project)
        self.save_project_button.pack(side="left", fill="x", expand=True, padx=(0,2))
        self.load_project_button = ctk.CTkButton(project_frame, text="Load Project", command=self.load_project)
        self.load_project_button.pack(side="left", fill="x", expand=True, padx=(2,0))

    def create_setting_entry(self, parent, label_text, default_value):
        """Helper to create a label and entry widget pair."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=2, padx=20, fill="x")
        label = ctk.CTkLabel(frame, text=label_text, width=120, anchor="w")
        label.pack(side="left")
        entry = ctk.CTkEntry(frame, placeholder_text=default_value)
        entry.insert(0, default_value)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def create_canvas_frame(self):
        """Creates the right-side panel for displaying the figure."""
        self.canvas_frame = ctk.CTkFrame(self, fg_color="gray20")
        self.canvas_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.canvas_frame.grid_propagate(False)

        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="gray20", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas_placeholder = ctk.CTkLabel(self.canvas, text="Your assembled figure will appear here.", font=ctk.CTkFont(size=18))
        self.canvas_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas.bind("<Button-1>", self.canvas_click_handler)

    def select_files(self):
        """Opens a file dialog to select images and adds them to the panel list."""
        f_types = [('Image Files', '*.tiff *.tif *.png *.jpg *.jpeg')]
        filenames = filedialog.askopenfilenames(title='Select image panels', filetypes=f_types)
        
        for file in filenames:
            try:
                image = Image.open(file)
                # Keep a copy of the original for re-assembly
                image.load() # Ensure file is loaded into memory
                
                panel_data = {
                    'id': id(image), # Unique ID based on object in memory
                    'pil_image': image,
                    'name': file.split('/')[-1] if '/' in file else file.split('\\')[-1],
                    'original_path': file
                }
                self.panels.append(panel_data)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {file}\n\n{e}")
        
        self.update_panel_list()

    def update_panel_list(self):
        """Refreshes the scrollable list of panels based on the self.panels list."""
        for widget in self.panel_list_frame.winfo_children():
            widget.destroy()

        if not self.panels:
            self.panel_list_placeholder = ctk.CTkLabel(self.panel_list_frame, text="No panels uploaded.")
            self.panel_list_placeholder.pack(pady=20)
            return

        for i, panel in enumerate(self.panels):
            item_frame = ctk.CTkFrame(self.panel_list_frame)
            item_frame.pack(fill="x", pady=2, padx=2)
            
            label = ctk.CTkLabel(item_frame, text=f"{i+1}. {panel['name']}", wraplength=180, justify="left")
            label.pack(side="left", padx=5, pady=5, fill="x", expand=True)
            
            # --- Reordering and Deletion Buttons ---
            up_button = ctk.CTkButton(item_frame, text="▲", width=30, command=lambda idx=i: self.move_panel(idx, -1))
            up_button.pack(side="right", padx=(2,0))
            if i == 0: up_button.configure(state="disabled")

            down_button = ctk.CTkButton(item_frame, text="▼", width=30, command=lambda idx=i: self.move_panel(idx, 1))
            down_button.pack(side="right", padx=(2,0))
            if i == len(self.panels) - 1: down_button.configure(state="disabled")

            del_button = ctk.CTkButton(item_frame, text="✕", fg_color="red", hover_color="darkred", width=30, command=lambda pid=panel['id']: self.delete_panel(pid))
            del_button.pack(side="right")
    
    def move_panel(self, index, direction):
        """Moves a panel up or down in the list."""
        if (index == 0 and direction == -1) or (index == len(self.panels) - 1 and direction == 1):
            return
        
        panel = self.panels.pop(index)
        self.panels.insert(index + direction, panel)
        self.update_panel_list()

    def delete_panel(self, panel_id):
        """Deletes a panel from the list."""
        self.panels = [p for p in self.panels if p['id'] != panel_id]
        self.update_panel_list()

    def assemble_figure(self):
        """The core logic to assemble the final figure image from panels and settings."""
        if not self.panels:
            messagebox.showwarning("Warning", "Please upload at least one panel image.")
            return

        try:
            target_width_in = float(self.target_width_entry.get())
            dpi = int(self.dpi_var.get())
            num_cols = int(self.num_cols_entry.get())
            padding_pt = int(self.padding_entry.get())
            margin_pt = int(self.margin_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for layout settings.")
            return

        # 1. Convert units to pixels
        total_width_px = int(target_width_in * dpi)
        padding_px = int((padding_pt / 72) * dpi)
        margin_px = int((margin_pt / 72) * dpi)
        
        # Account for margins in available width
        available_width = total_width_px - (2 * margin_px)
        col_width_px = (available_width - (padding_px * (num_cols - 1))) // num_cols

        # 2. Calculate column and row layout
        layouts = []
        row_heights = []
        current_row_max_h = 0
        
        for i, panel_data in enumerate(self.panels):
            img = panel_data['pil_image']
            
            # Calculate scaled dimensions while maintaining aspect ratio
            scale = col_width_px / img.width
            scaled_w = col_width_px
            scaled_h = int(img.height * scale)
            
            layouts.append({'width': scaled_w, 'height': scaled_h, 'image': img})
            current_row_max_h = max(current_row_max_h, scaled_h)

            # If end of row or last item, store row height
            if (i + 1) % num_cols == 0 or (i + 1) == len(self.panels):
                row_heights.append(current_row_max_h)
                current_row_max_h = 0
        
        content_height = sum(row_heights) + padding_px * (len(row_heights) - 1)
        total_height_px = content_height + (2 * margin_px)
        
        # 3. Determine background color
        bg_color = self._get_background_color()
        
        # 4. Create new image and paste panels
        # If background is None (Transparent), create an RGBA image with transparent background
        if bg_color is None:
            mode = 'RGBA'
            bg_fill = (255, 255, 255, 0)
        else:
            mode = 'RGB'
            bg_fill = bg_color

        self.assembled_image = Image.new(mode, (total_width_px, total_height_px), bg_fill)
        draw = ImageDraw.Draw(self.assembled_image)
        
        current_x, current_y = margin_px, margin_px
        row_start_y = margin_px
        
        for i, layout in enumerate(layouts):
            col_idx = i % num_cols
            
            if col_idx == 0 and i > 0:
                # Move to next row
                row_idx = i // num_cols
                row_start_y += row_heights[row_idx - 1] + padding_px

            current_x = margin_px + col_idx * (col_width_px + padding_px)
            
            resized_img = layout['image'].resize((layout['width'], layout['height']), Image.Resampling.LANCZOS)
            # If we're working in RGBA mode, ensure pasted image has alpha channel
            if self.assembled_image.mode == 'RGBA' and resized_img.mode != 'RGBA':
                resized_img = resized_img.convert('RGBA')

            # Use mask for RGBA pasting to preserve transparency
            if self.assembled_image.mode == 'RGBA':
                self.assembled_image.paste(resized_img, (current_x, row_start_y), resized_img)
            else:
                self.assembled_image.paste(resized_img, (current_x, row_start_y))

            # 5. Draw labels based on selected style
            self._add_panel_label(draw, i, current_x, row_start_y, dpi, padding_px)

        # 6. Clear old annotations and display
        self.annotations = []
        self.display_image(self.assembled_image)
        self.export_button.configure(state="normal")
        messagebox.showinfo("Success", "Figure assembled successfully.")
        
    def _get_background_color(self):
        """Get background color based on selection."""
        bg_choice = self.bg_var.get()
        if bg_choice == "White":
            return "white"
        elif bg_choice == "Transparent":
            return None  # Will need special handling for transparency
        elif bg_choice == "Light Gray":
            return "#F5F5F5"
        return "white"
    
    def _add_panel_label(self, draw, panel_index, x, y, dpi, padding_px):
        """Add panel labels (A, B, C, etc.) based on selected style."""
        label_style = self.label_style_var.get()
        
        if label_style == "None":
            return
            
        # Generate label text
        if label_style == "A, B, C...":
            label_text = chr(65 + panel_index)
        elif label_style == "a, b, c...":
            label_text = chr(97 + panel_index)
        elif label_style == "1, 2, 3...":
            label_text = str(panel_index + 1)
        elif label_style == "i, ii, iii...":
            roman_numerals = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
            label_text = roman_numerals[panel_index] if panel_index < len(roman_numerals) else str(panel_index + 1)
        else:
            label_text = chr(65 + panel_index)
        
        # Get font
        font = self._get_label_font(dpi)
        
        # Position label
        text_pos_x = x + int(padding_px * 0.3)
        text_pos_y = y + int(padding_px * 0.3)
        
        # Draw background and text with better styling
        bbox = draw.textbbox((text_pos_x, text_pos_y), label_text, font=font)
        # Add padding to background
        bg_padding = int(padding_px * 0.1)
        bg_bbox = (bbox[0] - bg_padding, bbox[1] - bg_padding, 
                   bbox[2] + bg_padding, bbox[3] + bg_padding)
        
        draw.rectangle(bg_bbox, fill="white", outline="black", width=1)
        draw.text((text_pos_x, text_pos_y), label_text, fill="black", font=font)
    
    def _get_label_font(self, dpi):
        """Get appropriate font for labels."""
        try:
            font_size_px = int((self.pub_settings['label_font_size'] / 72) * dpi)
            font_name = self.font_var.get()
            
            if font_name == "Default":
                return ImageFont.load_default()
            
            # Try different font file patterns
            font_patterns = [
                f"{font_name.lower().replace(' ', '')}.ttf",
                f"{font_name.lower().replace(' ', '')}bd.ttf",  # Bold variant
                f"C:/Windows/Fonts/{font_name.replace(' ', '')}.ttf",
                f"C:/Windows/Fonts/{font_name.lower().replace(' ', '')}.ttf"
            ]
            
            for pattern in font_patterns:
                try:
                    return ImageFont.truetype(pattern, size=font_size_px)
                except (OSError, IOError):
                    continue
                    
            return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()

    def display_image(self, pil_image):
        """Displays a PIL image on the canvas, resizing if necessary."""
        if not pil_image:
            return
            
        if self.canvas_placeholder:
            self.canvas_placeholder.destroy()
            self.canvas_placeholder = None

        # Calculate display size to fit canvas while maintaining aspect ratio
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        # Ensure canvas has been rendered
        if canvas_w <= 1 or canvas_h <= 1:
            self.after(100, lambda: self.display_image(pil_image))
            return
        
        img_w, img_h = pil_image.size
        
        scale = min(canvas_w / img_w, canvas_h / img_h)
        display_w = int(img_w * scale)
        display_h = int(img_h * scale)
        
        display_img = pil_image.resize((display_w, display_h), Image.Resampling.LANCZOS)
        
        self.canvas_image = ImageTk.PhotoImage(display_img)
        self.canvas.delete("all")  # Clear previous content
        self.canvas.create_image(canvas_w / 2, canvas_h / 2, anchor="center", image=self.canvas_image)
        self.canvas.image = self.canvas_image # Keep reference
        
    def enable_add_text_mode(self):
        if not self.assembled_image:
            messagebox.showwarning("Warning", "Please assemble a figure first.")
            return
        self.canvas.config(cursor="crosshair")
        self.add_text_button.configure(text="Click on Figure to Add Text...", state="disabled")

    def canvas_click_handler(self, event):
        """Handles clicks on the canvas, primarily for adding text."""
        if self.canvas.cget("cursor") != "crosshair" or not self.assembled_image:
            return
        
        text = simpledialog.askstring("Input", "Enter annotation text:", parent=self)
        if not text:
            self.canvas.config(cursor="")
            self.add_text_button.configure(text="Add Text Annotation", state="normal")
            return
            
        # Convert canvas display coordinates to original image coordinates
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        img_w, img_h = self.assembled_image.size
        
        scale = min(canvas_w / img_w, canvas_h / img_h)
        display_w = int(img_w * scale)
        display_h = int(img_h * scale)
        
        # Calculate offsets if image is centered
        offset_x = (canvas_w - display_w) / 2
        offset_y = (canvas_h - display_h) / 2

        # Convert click coordinates to display image coordinates
        click_x_on_display = event.x - offset_x
        click_y_on_display = event.y - offset_y
        
        # Convert display image coordinates to original image coordinates
        orig_x = int(click_x_on_display / scale)
        orig_y = int(click_y_on_display / scale)
        
        self.annotations.append({'text': text, 'x': orig_x, 'y': orig_y})
        self.redraw_with_annotations()

        self.canvas.config(cursor="")
        self.add_text_button.configure(text="Add Text Annotation", state="normal")
        
    def redraw_with_annotations(self):
        """Redraws the figure with the current annotations."""
        if not self.assembled_image: 
            return
        
        # Start with the clean assembled image (without previous text)
        temp_img = self.assembled_image.copy()
        draw = ImageDraw.Draw(temp_img)
        
        try:
            dpi = int(self.dpi_var.get())
            font_size_pt = int(self.font_size_entry.get())
            font_size_px = int((font_size_pt / 72) * dpi)
            font = self._get_annotation_font(font_size_px)
        except (ValueError, IOError):
            font = ImageFont.load_default()
            
        for anno in self.annotations:
            draw.text((anno['x'], anno['y']), anno['text'], fill="black", font=font)
        
        self.display_image(temp_img)
        
    def export_figure(self):
        """Exports the final figure with annotations to a file."""
        if not self.assembled_image:
            messagebox.showerror("Error", "No figure has been assembled yet.")
            return

        # Get export format
        export_format = self.export_format_var.get().lower()
        format_extensions = {
            'png': '.png',
            'tiff': '.tiff', 
            'pdf': '.pdf',
            'jpeg': '.jpg'
        }
        
        f_types = [(f'{export_format.upper()} file', f'*{format_extensions[export_format]}')]
        filepath = filedialog.asksaveasfilename(
            filetypes=f_types, 
            defaultextension=format_extensions[export_format]
        )
        
        if not filepath:
            return

        # Create final image with annotations
        final_image_to_save = self.assembled_image.copy()
        draw = ImageDraw.Draw(final_image_to_save)
        
        try:
            dpi = int(self.dpi_var.get())
            font_size_pt = int(self.font_size_entry.get())
            font_size_px = int((font_size_pt / 72) * dpi)
            font = self._get_annotation_font(font_size_px)
        except (ValueError, IOError):
            dpi = 300
            font = ImageFont.load_default()
            
        for anno in self.annotations:
            draw.text((anno['x'], anno['y']), anno['text'], fill="black", font=font)
        
        # Save with appropriate settings
        try:
            if export_format in ['png', 'tiff']:
                final_image_to_save.save(filepath, dpi=(dpi, dpi))
            elif export_format == 'pdf':
                # Convert to RGB if needed for PDF
                if final_image_to_save.mode != 'RGB':
                    final_image_to_save = final_image_to_save.convert('RGB')
                final_image_to_save.save(filepath, format='PDF', resolution=dpi)
            else:
                final_image_to_save.save(filepath)
            messagebox.showinfo("Success", f"Figure saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file.\n\n{e}")
    
    def _get_annotation_font(self, font_size_px):
        """Get font for annotations."""
        try:
            font_name = self.font_var.get()
            if font_name == "Default":
                return ImageFont.load_default()
            
            font_patterns = [
                f"{font_name.lower().replace(' ', '')}.ttf",
                f"C:/Windows/Fonts/{font_name.replace(' ', '')}.ttf",
                f"C:/Windows/Fonts/{font_name.lower().replace(' ', '')}.ttf"
            ]
            
            for pattern in font_patterns:
                try:
                    return ImageFont.truetype(pattern, size=font_size_px)
                except (OSError, IOError):
                    continue
                    
            return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()
    
    def clear_annotations(self):
        """Clear all annotations from the figure."""
        self.annotations = []
        if self.assembled_image:
            self.display_image(self.assembled_image)
    
    def save_project(self):
        """Save current project configuration to JSON file."""
        if not self.panels:
            messagebox.showwarning("Warning", "No panels to save.")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if not filepath:
            return
        
        project_data = {
            'panels': [{'name': p['name'], 'path': p['original_path']} for p in self.panels],
            'settings': {
                'width': self.target_width_entry.get(),
                'dpi': self.dpi_var.get(),
                'columns': self.num_cols_entry.get(),
                'spacing': self.padding_entry.get(),
                'margins': self.margin_entry.get(),
                'background': self.bg_var.get(),
                'font_family': self.font_var.get(),
                'font_size': self.font_size_entry.get(),
                'label_style': self.label_style_var.get(),
                'export_format': self.export_format_var.get()
            },
            'annotations': self.annotations
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(project_data, f, indent=2)
            messagebox.showinfo("Success", f"Project saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save project.\n\n{e}")
    
    def load_project(self):
        """Load project configuration from JSON file."""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r') as f:
                project_data = json.load(f)
            
            # Clear current panels
            self.panels = []
            
            # Load panels
            for panel_info in project_data.get('panels', []):
                try:
                    if os.path.exists(panel_info['path']):
                        image = Image.open(panel_info['path'])
                        image.load()
                        panel_data = {
                            'id': id(image),
                            'pil_image': image,
                            'name': panel_info['name'],
                            'original_path': panel_info['path']
                        }
                        self.panels.append(panel_data)
                    else:
                        messagebox.showwarning("Warning", f"Could not find: {panel_info['path']}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not load: {panel_info['path']}\n{e}")
            
            # Load settings
            settings = project_data.get('settings', {})
            self.target_width_entry.delete(0, 'end')
            self.target_width_entry.insert(0, settings.get('width', '7.0'))
            self.dpi_var.set(settings.get('dpi', '300'))
            self.num_cols_entry.delete(0, 'end')
            self.num_cols_entry.insert(0, settings.get('columns', '2'))
            self.padding_entry.delete(0, 'end')
            self.padding_entry.insert(0, settings.get('spacing', '8'))
            self.margin_entry.delete(0, 'end')
            self.margin_entry.insert(0, settings.get('margins', '12'))
            self.bg_var.set(settings.get('background', 'White'))
            self.font_var.set(settings.get('font_family', self.available_fonts[0] if self.available_fonts else 'Default'))
            self.font_size_entry.delete(0, 'end')
            self.font_size_entry.insert(0, settings.get('font_size', '12'))
            self.label_style_var.set(settings.get('label_style', 'A, B, C...'))
            self.export_format_var.set(settings.get('export_format', 'PNG'))
            
            # Load annotations
            self.annotations = project_data.get('annotations', [])
            
            # Update UI
            self.update_panel_list()
            messagebox.showinfo("Success", "Project loaded successfully.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load project.\n\n{e}")

if __name__ == "__main__":
    app = FigureAssemblerApp()
    app.mainloop()

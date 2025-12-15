# -*- coding: utf-8 -*-
"""Main CustomTkinter application for Color Detection Pro.

Features:
- Image upload, live camera capture, snapshot
- Click‑to‑detect colors, palette extraction (K‑Means)
- Color name matching (KDTree), conversions (HEX, RGB, HSV, HSL, CMYK)
- Color harmony (complementary, triadic, analogous, split‑complementary)
- WCAG contrast checker, favorite colors, history
- Color mixer, gradient generator (new cool features)
- **CSS export button removed** as requested
- Smooth theme transition using a short fade animation
"""

import os
import sys
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading

# Ensure core modules are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.color_detector import ColorDetector, CameraCapture
from core.color_matcher import get_color_matcher
from core.color_converter import (
    rgb_to_hex,
    rgb_to_hsv,
    rgb_to_hsl,
    rgb_to_cmyk,
    get_complementary_color,
    get_triadic_colors,
    get_analogous_colors,
    get_split_complementary,
    calculate_contrast_ratio,
    get_wcag_rating,
)

class ColorDetectionApp:
    """Main application class for the Color Detection Pro desktop app."""

    def __init__(self):
        # Appearance mode and theme (default dark, can be toggled)
        ctk.set_appearance_mode("light")  # Default to light mode
        ctk.set_default_color_theme("blue")

        # Root window
        self.root = ctk.CTk()
        self.root.title("🎨 Color Detection Pro")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)

        # Core objects
        self.detector = ColorDetector()
        self.matcher = get_color_matcher()
        self.camera = None
        self.camera_running = False
        self.current_image = None
        self.photo_image = None

        # History / favorites
        self.color_history = []
        self.favorite_colors = []
        self.max_history = 20
        self._load_saved_data()

        # Build UI
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self._create_ui()
        self._bind_events()

    # ---------------------------------------------------------------------
    # Persistence
    # ---------------------------------------------------------------------
    def _load_saved_data(self):
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        history_file = os.path.join(data_dir, "data", "user_data.json")
        try:
            if os.path.exists(history_file):
                with open(history_file, "r") as f:
                    data = json.load(f)
                    self.color_history = data.get("history", [])
                    self.favorite_colors = data.get("favorites", [])
        except Exception:
            pass

    def _save_user_data(self):
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        history_file = os.path.join(data_dir, "data", "user_data.json")
        try:
            data = {
                "history": self.color_history[-self.max_history:],
                "favorites": self.favorite_colors,
            }
            with open(history_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    # ---------------------------------------------------------------------
    # UI construction
    # ---------------------------------------------------------------------
    def _create_ui(self):
        self._create_sidebar()
        self._create_main_content()
        self._create_color_info_panel()

    def _create_sidebar(self):
        """Sidebar with navigation/buttons using a clean neutral theme."""
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(12, weight=1)

        # Title
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkLabel(title_frame, text="🎨 Color Detection", font=ctk.CTkFont(size=18, weight="bold")).pack()
        # ctk.CTkLabel(title_frame, text="Pro Edition", font=ctk.CTkFont(size=12), text_color="gray").pack()

        # Separator
        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30").grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        # Buttons – neutral blue theme
        btn_cfg = dict(width=200, height=40, font=ctk.CTkFont(size=14))
        self.btn_upload = ctk.CTkButton(self.sidebar, text="📁 Upload Image", command=self._upload_image, **btn_cfg)
        self.btn_upload.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.btn_camera = ctk.CTkButton(self.sidebar, text="📷 Camera Capture", command=self._toggle_camera, **btn_cfg)
        self.btn_camera.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.btn_capture = ctk.CTkButton(self.sidebar, text="📸 Take Snapshot", command=self._capture_snapshot, state="disabled", **btn_cfg)
        self.btn_capture.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        # Separator
        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30").grid(row=5, column=0, sticky="ew", padx=20, pady=10)

        # Tools
        self.btn_palette = ctk.CTkButton(self.sidebar, text="🎨 Extract Palette", command=self._extract_palette, fg_color="#6B5B95", hover_color="#5A4A84", **btn_cfg)
        self.btn_palette.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        self.btn_mixer = ctk.CTkButton(self.sidebar, text="🔀 Color Mixer", command=self._show_color_mixer, fg_color="#E17055", hover_color="#D35400", **btn_cfg)
        self.btn_mixer.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        self.btn_gradient = ctk.CTkButton(self.sidebar, text="🌈 Gradient Maker", command=self._show_gradient_generator, fg_color="#00B894", hover_color="#00A383", **btn_cfg)
        self.btn_gradient.grid(row=8, column=0, padx=20, pady=5, sticky="ew")

        # Separator
        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30").grid(row=9, column=0, sticky="ew", padx=20, pady=10)

        # Saved
        self.btn_history = ctk.CTkButton(self.sidebar, text="🕐 Color History", command=self._show_history, fg_color="#45B7D1", hover_color="#3AA6C0", **btn_cfg)
        self.btn_history.grid(row=10, column=0, padx=20, pady=5, sticky="ew")
        self.btn_favorites = ctk.CTkButton(self.sidebar, text="⭐ Favorites", command=self._show_favorites, fg_color="#F7DC6F", hover_color="#F4D03F", text_color="black", **btn_cfg)
        self.btn_favorites.grid(row=11, column=0, padx=20, pady=5, sticky="ew")

        # Theme toggle
        self.theme_var = ctk.StringVar(value="light")
        self.theme_switch = ctk.CTkSwitch(self.sidebar, text="☀️ Light Mode", variable=self.theme_var, onvalue="dark", offvalue="light", command=self._toggle_theme_smooth)
        self.theme_switch.grid(row=12, column=0, padx=20, pady=20, sticky="s")
        # Don't select - starts in light mode (deselected)

    def _create_main_content(self):
        """Main area where images are displayed and palette shown."""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.instructions = ctk.CTkLabel(
            self.main_frame,
            text="📌 Upload an image or start camera to detect colors",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self.instructions.grid(row=0, column=0, pady=5)

        self.canvas_frame = ctk.CTkFrame(self.main_frame, fg_color="gray20")
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        # Placeholder text will be centered when canvas is configured
        self.placeholder_id = None
        self.canvas.bind("<Configure>", self._center_placeholder)
        self._create_placeholder()

        self.palette_frame = ctk.CTkFrame(self.main_frame, height=80)
        self.palette_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.palette_frame.grid_columnconfigure(0, weight=1)
        self.palette_label = ctk.CTkLabel(self.palette_frame, text="🎨 Extracted Palette", font=ctk.CTkFont(size=12, weight="bold"))
        self.palette_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.palette_container = ctk.CTkFrame(self.palette_frame, fg_color="transparent")
        self.palette_container.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

    def _create_color_info_panel(self):
        """Right‑hand panel showing selected color details."""
        self.info_panel = ctk.CTkFrame(self.root, width=300)
        self.info_panel.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self.info_panel.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(self.info_panel, text="🔍 Color Info", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10, 5))

        self.color_swatch = ctk.CTkFrame(self.info_panel, width=260, height=100, fg_color="#3b3b3b", corner_radius=10)
        self.color_swatch.grid(row=1, column=0, columnspan=2, padx=20, pady=10)
        self.color_swatch.grid_propagate(False)
        self.color_name_label = ctk.CTkLabel(self.color_swatch, text="No color selected", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        self.color_name_label.place(relx=0.5, rely=0.5, anchor="center")

        self.confidence_label = ctk.CTkLabel(self.info_panel, text="Confidence: --", font=ctk.CTkFont(size=12), text_color="gray")
        self.confidence_label.grid(row=2, column=0, columnspan=2, pady=2)

        # Color codes
        self.codes_frame = ctk.CTkFrame(self.info_panel, fg_color="transparent")
        self.codes_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.code_labels = {}
        code_types = ["HEX", "RGB", "HSV", "HSL", "CMYK"]
        for i, ct in enumerate(code_types):
            row_frame = ctk.CTkFrame(self.codes_frame, fg_color="transparent")
            row_frame.grid(row=i, column=0, sticky="ew", pady=2)
            ctk.CTkLabel(row_frame, text=f"{ct}:", font=ctk.CTkFont(size=12, weight="bold"), width=50).grid(row=0, column=0, sticky="w")
            val = ctk.CTkLabel(row_frame, text="--", font=ctk.CTkFont(size=12, family="Consolas"), width=140)
            val.grid(row=0, column=1, sticky="w", padx=5)
            ctk.CTkButton(row_frame, text="📋", width=30, height=25, command=lambda t=ct: self._copy_code(t)).grid(row=0, column=2, padx=2)
            self.code_labels[ct] = val

        # Add to favorites
        ctk.CTkButton(self.info_panel, text="⭐ Add to Favorites", command=self._add_to_favorites, height=35, fg_color="#F7DC6F", hover_color="#F4D03F", text_color="black").grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        # Separator
        ctk.CTkFrame(self.info_panel, height=2, fg_color="gray30").grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        # Harmony
        ctk.CTkLabel(self.info_panel, text="🎭 Color Harmony", font=ctk.CTkFont(size=14, weight="bold")).grid(row=6, column=0, columnspan=2, pady=5)
        self.harmony_frame = ctk.CTkFrame(self.info_panel, fg_color="transparent")
        self.harmony_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10)

        # Separator
        ctk.CTkFrame(self.info_panel, height=2, fg_color="gray30").grid(row=8, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

    # ---------------------------------------------------------------------
    # Helper methods for placeholder
    # ---------------------------------------------------------------------
    def _create_placeholder(self):
        """Create the placeholder text on the canvas."""
        if self.placeholder_id:
            self.canvas.delete(self.placeholder_id)
        width = self.canvas.winfo_width() or 600
        height = self.canvas.winfo_height() or 400
        self.placeholder_id = self.canvas.create_text(
            width // 2, height // 2,
            text="🎨\n\nDrop an image here\nor use the sidebar buttons",
            font=("Segoe UI", 16),
            fill="gray",
            justify="center",
        )
    
    def _center_placeholder(self, event=None):
        """Re-center placeholder when canvas resizes."""
        if self.placeholder_id and self.current_image is None:
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            self.canvas.coords(self.placeholder_id, width // 2, height // 2)

    # ---------------------------------------------------------------------
    # Event binding
    # ---------------------------------------------------------------------
    def _bind_events(self):
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.root.bind("<Configure>", self._on_resize)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------------------------------------------------------------
    # Core functionality (upload, camera, palette, color display, etc.)
    # ---------------------------------------------------------------------
    def _upload_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(title="Select an image", filetypes=filetypes)
        if filepath:
            if self.camera_running:
                self._stop_camera()
            if self.detector.load_image(filepath):
                self.current_image = self.detector.get_rgb_image()
                self._display_image()
                self.instructions.configure(text="📌 Click on the image to detect colors")
            else:
                messagebox.showerror("Error", "Failed to load image")

    def _display_image(self):
        if self.current_image is None:
            return
        self.canvas.delete(self.placeholder_id)
        self.canvas.update()
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return
        resized = self.detector.resize_for_display(cw - 20, ch - 20)
        if resized is None:
            return
        pil = Image.fromarray(resized)
        self.photo_image = ImageTk.PhotoImage(pil)
        x, y = cw // 2, ch // 2
        self.canvas.delete("all")
        self.canvas.create_image(x, y, image=self.photo_image, anchor="center")
        self.image_offset_x = x - resized.shape[1] // 2
        self.image_offset_y = y - resized.shape[0] // 2
        self.displayed_size = (resized.shape[1], resized.shape[0])

    def _on_canvas_click(self, event):
        if self.current_image is None:
            return
        x, y = self._canvas_to_image_coords(event.x, event.y)
        if x is None:
            return
        color = self.detector.get_color_at_point(x, y)
        if color:
            self._update_color_display(color)
            self._add_to_history(color)

    def _on_canvas_motion(self, event):
        """Handle mouse motion over canvas for live preview."""
        pass  # Can be extended for hover preview

    def _on_resize(self, event):
        """Handle window resize."""
        if self.current_image is not None and not self.camera_running:
            self._display_image()

    def _toggle_camera(self):
        """Toggle camera on/off."""
        if self.camera_running:
            self._stop_camera()
        else:
            self._start_camera()

    def _start_camera(self):
        """Start the camera feed."""
        try:
            self.camera = CameraCapture()
            if not self.camera.start():
                messagebox.showerror("Error", "Could not access camera")
                return
            self.camera_running = True
            self.btn_camera.configure(text="⏹️ Stop Camera")
            self.btn_capture.configure(state="normal")
            self.instructions.configure(text="📌 Camera active - Click to detect colors or take a snapshot")
            self._update_camera_frame()
        except Exception as e:
            messagebox.showerror("Error", f"Camera error: {e}")

    def _stop_camera(self):
        """Stop the camera feed."""
        self.camera_running = False
        if self.camera:
            self.camera.stop()
            self.camera = None
        self.btn_camera.configure(text="📷 Camera Capture")
        self.btn_capture.configure(state="disabled")
        self.instructions.configure(text="📌 Upload an image or start camera to detect colors")

    def _update_camera_frame(self):
        """Update the canvas with the current camera frame."""
        if not self.camera_running or self.camera is None:
            return
        frame = self.camera.read_frame()
        if frame is not None:
            self.current_image = frame
            self.detector.current_image = frame
            self._display_image()
        if self.camera_running:
            self.root.after(30, self._update_camera_frame)

    def _capture_snapshot(self):
        """Capture current camera frame as snapshot."""
        if self.camera_running and self.camera:
            frame = self.camera.read_frame()
            if frame is not None:
                self._stop_camera()
                self.current_image = frame
                self.detector.current_image = frame
                self._display_image()
                self.instructions.configure(text="📌 Snapshot captured - Click to detect colors")

    def _canvas_to_image_coords(self, cx, cy):
        if self.current_image is None or not hasattr(self, "displayed_size"):
            return None, None
        rel_x = cx - self.image_offset_x
        rel_y = cy - self.image_offset_y
        if not (0 <= rel_x < self.displayed_size[0] and 0 <= rel_y < self.displayed_size[1]):
            return None, None
        ih, iw = self.current_image.shape[:2]
        scale_x = iw / self.displayed_size[0]
        scale_y = ih / self.displayed_size[1]
        return int(rel_x * scale_x), int(rel_y * scale_y)

    def _update_color_display(self, rgb, add_to_history=True):
        r, g, b = rgb
        match = self.matcher.find_closest_color(r, g, b)
        hex_c = rgb_to_hex(r, g, b)
        self.color_swatch.configure(fg_color=hex_c)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        txt = "black" if brightness > 128 else "white"
        self.color_name_label.configure(text=match["name"], text_color=txt)
        self.confidence_label.configure(text=f"Confidence: {match['confidence']}%")
        hsv = rgb_to_hsv(r, g, b)
        hsl = rgb_to_hsl(r, g, b)
        cmyk = rgb_to_cmyk(r, g, b)
        self.code_labels["HEX"].configure(text=hex_c)
        self.code_labels["RGB"].configure(text=f"rgb({r}, {g}, {b})")
        self.code_labels["HSV"].configure(text=f"hsv({hsv[0]}°, {hsv[1]}%, {hsv[2]}%)")
        self.code_labels["HSL"].configure(text=f"hsl({hsl[0]}°, {hsl[1]}%, {hsl[2]}%)")
        self.code_labels["CMYK"].configure(text=f"cmyk({cmyk[0]}%, {cmyk[1]}%, {cmyk[2]}%, {cmyk[3]}%)")
        self.current_color = {
            "rgb": (r, g, b),
            "hex": hex_c,
            "hsv": hsv,
            "hsl": hsl,
            "cmyk": cmyk,
            "name": match["name"],
        }
        self._update_harmony_display(r, g, b)
        if add_to_history:
            self._add_to_history((r, g, b))

    def _update_harmony_display(self, r, g, b):
        for widget in self.harmony_frame.winfo_children():
            widget.destroy()
        harmonies = {
            "Complementary": [get_complementary_color(r, g, b)],
            "Triadic": get_triadic_colors(r, g, b),
            "Analogous": get_analogous_colors(r, g, b),
            "Split": get_split_complementary(r, g, b),
        }
        for row, (name, colors) in enumerate(harmonies.items()):
            ctk.CTkLabel(self.harmony_frame, text=f"{name}:", font=ctk.CTkFont(size=10)).grid(row=row, column=0, sticky="w", pady=2)
            for i, col in enumerate(colors):
                sw = ctk.CTkFrame(self.harmony_frame, width=30, height=20, fg_color=rgb_to_hex(*col), corner_radius=3)
                sw.grid(row=row, column=i+1, padx=2, pady=2)
                sw.grid_propagate(False)
                sw.bind("<Button-1>", lambda e, c=col: self._update_color_display(c))



    def _copy_code(self, code_type):
        if not hasattr(self, "current_color"):
            return
        mapping = {
            "HEX": self.current_color["hex"],
            "RGB": f"rgb{self.current_color['rgb']}",
            "HSV": f"hsv{self.current_color['hsv']}",
            "HSL": f"hsl{self.current_color['hsl']}",
            "CMYK": f"cmyk{self.current_color['cmyk']}",
        }
        value = mapping.get(code_type)
        if value:
            self.root.clipboard_clear()
            self.root.clipboard_append(value)
            self._show_toast(f"✅ {code_type} copied: {value}")

    def _add_to_history(self, rgb):
        hex_c = rgb_to_hex(*rgb)
        # Look up color name
        match = self.matcher.find_closest_color(*rgb)
        name = match["name"] if match else hex_c
        entry = {"rgb": rgb, "hex": hex_c, "name": name}
        self.color_history = [c for c in self.color_history if c["hex"] != hex_c]
        self.color_history.insert(0, entry)
        self.color_history = self.color_history[:self.max_history]

    def _add_to_favorites(self):
        if not hasattr(self, "current_color"):
            return
        entry = {"rgb": self.current_color["rgb"], "hex": self.current_color["hex"], "name": self.current_color["name"]}
        if any(f["hex"] == entry["hex"] for f in self.favorite_colors):
            self._show_toast("⚠️ Already in favorites!")
            return
        self.favorite_colors.append(entry)
        self._save_user_data()
        self._show_toast(f"⭐ '{entry['name']}' added to favorites!")

    def _show_toast(self, message, duration=2500):
        """Show a notification using a simple messagebox for reliability."""
        # Use window title flash as feedback
        original_title = self.root.title()
        self.root.title(message)
        self.root.after(duration, lambda: self.root.title(original_title))
        
        # Also copy confirmation via brief status update
        if hasattr(self, 'instructions'):
            old_text = self.instructions.cget("text")
            self.instructions.configure(text=message, text_color="#00B894")
            self.root.after(duration, lambda: self.instructions.configure(text=old_text, text_color="gray"))

    def _show_history(self):
        self._show_color_list("Color History", self.color_history)

    def _show_favorites(self):
        self._show_color_list("Favorite Colors", self.favorite_colors, allow_delete=True)

    def _show_color_list(self, title, colors, allow_delete=False):
        popup = ctk.CTkToplevel(self.root)
        popup.title(title)
        popup.geometry("400x500")
        popup.transient(self.root)
        popup.grab_set()
        ctk.CTkLabel(popup, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        if not colors:
            ctk.CTkLabel(popup, text="No colors yet!", font=ctk.CTkFont(size=14), text_color="gray").pack(pady=50)
            return
        scroll = ctk.CTkScrollableFrame(popup, width=360, height=400)
        scroll.pack(pady=10, padx=10, fill="both", expand=True)
        for color in colors:
            frame = ctk.CTkFrame(scroll)
            frame.pack(fill="x", pady=5, padx=5)
            sw = ctk.CTkFrame(frame, width=50, height=40, fg_color=color["hex"], corner_radius=5)
            sw.pack(side="left", padx=10, pady=5)
            sw.pack_propagate(False)
            info = ctk.CTkFrame(frame, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            name = color.get("name", "Unknown")
            ctk.CTkLabel(info, text=name, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=color["hex"], font=ctk.CTkFont(size=11, family="Consolas"), text_color="gray").pack(anchor="w")
            ctk.CTkButton(frame, text="Use", width=50, height=30, command=lambda c=color: [self._update_color_display(c["rgb"]), popup.destroy()]).pack(side="right", padx=5, pady=10)
            if allow_delete:
                ctk.CTkButton(frame, text="Delete", width=50, height=30, fg_color="#E74C3C", hover_color="#C0392B", command=lambda c=color, f=frame: self._delete_favorite_inline(c, f)).pack(side="right", padx=2, pady=10)

    def _delete_favorite_inline(self, color, frame):
        """Delete a favorite color and remove its row without reopening popup."""
        self.favorite_colors = [f for f in self.favorite_colors if f["hex"] != color["hex"]]
        self._save_user_data()
        frame.destroy()  # Just remove this row, don't reopen popup

    def _delete_favorite(self, color, popup, scroll):
        self.favorite_colors = [f for f in self.favorite_colors if f["hex"] != color["hex"]]
        self._save_user_data()
        popup.destroy()
        self._show_favorites()

    def _extract_palette(self):
        if self.current_image is None:
            messagebox.showinfo("Info", "Please load an image first!")
            return
        colors = self.detector.extract_dominant_colors(n_colors=8)
        if not colors:
            return
        for widget in self.palette_container.winfo_children():
            widget.destroy()
        for color_info in colors:
            rgb = color_info["rgb"]
            hex_c = rgb_to_hex(*rgb)
            pct = color_info["percentage"]
            frame = ctk.CTkFrame(self.palette_container)
            frame.pack(side="left", padx=5, pady=5)
            sw = ctk.CTkFrame(frame, width=60, height=40, fg_color=hex_c, corner_radius=5)
            sw.pack()
            sw.pack_propagate(False)
            sw.bind("<Button-1>", lambda e, c=rgb: self._update_color_display(c))
            ctk.CTkLabel(frame, text=f"{pct:.0f}%", font=ctk.CTkFont(size=10), text_color="gray").pack()

    # ---------------------------------------------------------------------
    # Additional cool features (color mixer & gradient generator)
    # ---------------------------------------------------------------------
    def _show_color_mixer(self):
        """Show color mixer dialog with clickable color selectors."""
        mixer = ctk.CTkToplevel(self.root)
        mixer.title("🔀 Color Mixer")
        mixer.geometry("400x520")
        mixer.transient(self.root)
        mixer.grab_set()
        
        # Title
        ctk.CTkLabel(mixer, text="Mix Two Colors", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        # Color 1
        self.mixer_color1 = (255, 0, 0)  # Default red
        self.mixer_color2 = (0, 0, 255)  # Default blue
        
        colors_frame = ctk.CTkFrame(mixer, fg_color="transparent")
        colors_frame.pack(pady=10)
        
        # Color 1 picker
        c1_frame = ctk.CTkFrame(colors_frame, fg_color="transparent")
        c1_frame.pack(side="left", padx=20)
        ctk.CTkLabel(c1_frame, text="Color 1", font=ctk.CTkFont(size=12)).pack()
        self.mixer_swatch1 = ctk.CTkFrame(c1_frame, width=80, height=80, fg_color="#FF0000", corner_radius=10)
        self.mixer_swatch1.pack(pady=5)
        self.mixer_swatch1.pack_propagate(False)
        
        def pick_color1():
            color = self._ask_color()
            if color:
                self.mixer_color1 = color
                self.mixer_swatch1.configure(fg_color=rgb_to_hex(*color))
                update_preview()
        
        ctk.CTkButton(c1_frame, text="Pick Color", command=pick_color1, width=80).pack(pady=5)
        
        # Color 2 picker
        c2_frame = ctk.CTkFrame(colors_frame, fg_color="transparent")
        c2_frame.pack(side="left", padx=20)
        ctk.CTkLabel(c2_frame, text="Color 2", font=ctk.CTkFont(size=12)).pack()
        self.mixer_swatch2 = ctk.CTkFrame(c2_frame, width=80, height=80, fg_color="#0000FF", corner_radius=10)
        self.mixer_swatch2.pack(pady=5)
        self.mixer_swatch2.pack_propagate(False)
        
        def pick_color2():
            color = self._ask_color()
            if color:
                self.mixer_color2 = color
                self.mixer_swatch2.configure(fg_color=rgb_to_hex(*color))
                update_preview()
        
        ctk.CTkButton(c2_frame, text="Pick Color", command=pick_color2, width=80).pack(pady=5)
        
        # Mix ratio slider
        ctk.CTkLabel(mixer, text="Mix Ratio", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        ratio_slider = ctk.CTkSlider(mixer, from_=0, to=1, number_of_steps=100, width=300, command=lambda v: update_preview())
        ratio_slider.set(0.5)
        ratio_slider.pack(pady=5)
        
        # Result preview
        ctk.CTkLabel(mixer, text="Result", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        result_swatch = ctk.CTkFrame(mixer, width=150, height=60, fg_color="#800080", corner_radius=10)
        result_swatch.pack(pady=5)
        result_swatch.pack_propagate(False)
        result_label = ctk.CTkLabel(result_swatch, text="#800080", font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
        result_label.place(relx=0.5, rely=0.5, anchor="center")
        
        def update_preview():
            t = ratio_slider.get()
            r = int(self.mixer_color1[0] * (1 - t) + self.mixer_color2[0] * t)
            g = int(self.mixer_color1[1] * (1 - t) + self.mixer_color2[1] * t)
            b = int(self.mixer_color1[2] * (1 - t) + self.mixer_color2[2] * t)
            hex_c = rgb_to_hex(r, g, b)
            result_swatch.configure(fg_color=hex_c)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            result_label.configure(text=hex_c, text_color="black" if brightness > 128 else "white")
            self.mixed_result = (r, g, b)
            self.mixed_hex = hex_c
        
        update_preview()
        
        # Buttons frame for Copy and Apply
        btn_frame = ctk.CTkFrame(mixer, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        def copy_mixed():
            if hasattr(self, 'mixed_hex'):
                self.root.clipboard_clear()
                self.root.clipboard_append(self.mixed_hex)
                copy_btn.configure(text="✅ Copied!")
                mixer.after(1500, lambda: copy_btn.configure(text="📋 Copy HEX"))
        
        def apply_mix():
            if hasattr(self, 'mixed_result'):
                self._update_color_display(self.mixed_result)
            mixer.destroy()
        
        copy_btn = ctk.CTkButton(btn_frame, text="📋 Copy HEX", command=copy_mixed, width=100, fg_color="#6c5ce7", hover_color="#5b4cdb")
        copy_btn.pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✓ Apply", command=apply_mix, fg_color="#00B894", hover_color="#00A383", width=80).pack(side="left", padx=5)

    def _show_gradient_generator(self):
        """Show gradient gallery with beautiful preset gradients like uiGradients."""
        grad = ctk.CTkToplevel(self.root)
        grad.title("🌈 Gradient Gallery")
        grad.geometry("700x600")
        grad.transient(self.root)
        grad.grab_set()
        
        # Beautiful gradient presets (name, color1, color2, optional color3)
        self.gradient_presets = [
            ("Sunset", "#FF512F", "#DD2476", None),
            ("Cool Blues", "#2193b0", "#6dd5ed", None),
            ("Piggy Pink", "#ee9ca7", "#ffdde1", None),
            ("Grade Grey", "#bdc3c7", "#2c3e50", None),
            ("Harvey", "#1f4037", "#99f2c8", None),
            ("Sublime Light", "#FC5C7D", "#6A82FB", None),
            ("Moonlit Asteroid", "#0F2027", "#203A43", "#2C5364"),
            ("JShine", "#12c2e9", "#c471ed", "#f64f59"),
            ("Flare", "#f12711", "#f5af19", None),
            ("Mirage", "#16222A", "#3A6073", None),
            ("Passion", "#e53935", "#e35d5b", None),
            ("Aqua Marine", "#1A2980", "#26D0CE", None),
            ("Aubergine", "#AA076B", "#61045F", None),
            ("Bloody Mary", "#FF512F", "#DD2476", None),
            ("Mango Pulp", "#F09819", "#EDDE5D", None),
            ("Frozen", "#403B4A", "#E7E9BB", None),
            ("Lush", "#56ab2f", "#a8e063", None),
            ("Stellar", "#7474BF", "#348AC7", None),
            ("Vice City", "#3494E6", "#EC6EAD", None),
            ("Pacific Dream", "#34e89e", "#0f3443", None),
            ("Shifter", "#bc4e9c", "#f80759", None),
            ("Relay", "#3A1C71", "#D76D77", "#FFAF7B"),
            ("Argon", "#03001e", "#7303c0", "#ec38bc"),
            ("Crystalline", "#00cdac", "#8ddad5", None),
            ("Nepal", "#de6161", "#2657eb", None),
        ]
        
        self.selected_gradient = self.gradient_presets[1]  # Default: Cool Blues
        
        # Header with selected gradient info
        header = ctk.CTkFrame(grad, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        self.grad_name_label = ctk.CTkLabel(header, text="Cool Blues", font=ctk.CTkFont(size=20, weight="bold"))
        self.grad_name_label.pack(side="left")
        
        self.grad_colors_label = ctk.CTkLabel(header, text="#2193b0 → #6dd5ed", font=ctk.CTkFont(size=12, family="Consolas"), text_color="gray")
        self.grad_colors_label.pack(side="right")
        
        # Selected gradient preview - use a canvas for true smooth gradient
        self.grad_canvas = ctk.CTkCanvas(grad, height=80, bg="#2b2b2b", highlightthickness=0)
        self.grad_canvas.pack(fill="x", padx=20, pady=10)
        
        self._draw_gradient_canvas()
        
        self._update_selected_preview()
        
        # CSS display
        css_frame = ctk.CTkFrame(grad, fg_color=("gray85", "gray20"), corner_radius=8)
        css_frame.pack(fill="x", padx=20, pady=5)
        self.grad_css_label = ctk.CTkLabel(css_frame, text="", font=ctk.CTkFont(size=11, family="Consolas"), wraplength=600)
        self.grad_css_label.pack(pady=8, padx=10)
        self._update_css_label()
        
        # Buttons
        btn_frame = ctk.CTkFrame(grad, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        def copy_css():
            css = self._generate_gradient_css()
            self.root.clipboard_clear()
            self.root.clipboard_append(css)
            self._show_toast(f"✅ {self.selected_gradient[0]} gradient copied!")
        
        ctk.CTkButton(btn_frame, text="📋 Copy CSS", command=copy_css, fg_color="#00B894", hover_color="#00A383", width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🎨 Custom", command=lambda: self._show_custom_gradient(grad), fg_color="#6c5ce7", hover_color="#5b4cdb", width=100).pack(side="left", padx=5)
        
        # Scrollable gradient gallery
        ctk.CTkLabel(grad, text="Choose a Gradient", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        gallery_scroll = ctk.CTkScrollableFrame(grad, height=280)
        gallery_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create gradient cards in a grid
        for idx, preset in enumerate(self.gradient_presets):
            row = idx // 4
            col = idx % 4
            
            card = ctk.CTkFrame(gallery_scroll, width=150, height=90, corner_radius=10)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.grid_propagate(False)
            
            # Create gradient effect on card
            inner = ctk.CTkFrame(card, corner_radius=8)
            inner.pack(fill="both", expand=True, padx=2, pady=2)
            
            # Simplified gradient display (just show first color as bg)
            c1 = preset[1]
            inner.configure(fg_color=c1)
            
            # Name label
            name_lbl = ctk.CTkLabel(inner, text=preset[0], font=ctk.CTkFont(size=11, weight="bold"), text_color="white")
            name_lbl.place(relx=0.5, rely=0.5, anchor="center")
            
            # Click handler
            def select_gradient(p=preset):
                self.selected_gradient = p
                self.grad_name_label.configure(text=p[0])
                colors_text = f"{p[1]} → {p[2]}" + (f" → {p[3]}" if p[3] else "")
                self.grad_colors_label.configure(text=colors_text)
                self._update_selected_preview()
                self._update_css_label()
            
            inner.bind("<Button-1>", lambda e, p=preset: select_gradient(p))
            name_lbl.bind("<Button-1>", lambda e, p=preset: select_gradient(p))
        
        # Configure grid columns
        for i in range(4):
            gallery_scroll.grid_columnconfigure(i, weight=1)
    
    def _update_selected_preview(self):
        """Update the selected gradient preview."""
        preset = self.selected_gradient
        c1 = self._hex_to_rgb(preset[1])
        c2 = self._hex_to_rgb(preset[2])
        c3 = self._hex_to_rgb(preset[3]) if preset[3] else None
        
        # Draw smooth gradient on canvas
        self._draw_gradient_canvas()
    
    def _draw_gradient_canvas(self):
        """Draw a smooth gradient on the canvas."""
        if not hasattr(self, 'grad_canvas'):
            return
        
        self.grad_canvas.delete("all")
        self.grad_canvas.update()
        width = self.grad_canvas.winfo_width() or 660
        height = self.grad_canvas.winfo_height() or 80
        
        preset = self.selected_gradient
        c1 = self._hex_to_rgb(preset[1])
        c2 = self._hex_to_rgb(preset[2])
        c3 = self._hex_to_rgb(preset[3]) if preset[3] else None
        
        # Draw gradient line by line for smooth effect
        for x in range(width):
            t = x / max(width - 1, 1)
            if c3:  # 3-color gradient
                if t < 0.5:
                    t2 = t * 2
                    r = int(c1[0] * (1 - t2) + c3[0] * t2)
                    g = int(c1[1] * (1 - t2) + c3[1] * t2)
                    b = int(c1[2] * (1 - t2) + c3[2] * t2)
                else:
                    t2 = (t - 0.5) * 2
                    r = int(c3[0] * (1 - t2) + c2[0] * t2)
                    g = int(c3[1] * (1 - t2) + c2[1] * t2)
                    b = int(c3[2] * (1 - t2) + c2[2] * t2)
            else:  # 2-color gradient
                r = int(c1[0] * (1 - t) + c2[0] * t)
                g = int(c1[1] * (1 - t) + c2[1] * t)
                b = int(c1[2] * (1 - t) + c2[2] * t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.grad_canvas.create_line(x, 0, x, height, fill=color)
    
    def _update_css_label(self):
        """Update the CSS display label."""
        self.grad_css_label.configure(text=self._generate_gradient_css())
    
    def _generate_gradient_css(self):
        """Generate CSS for the selected gradient."""
        preset = self.selected_gradient
        if preset[3]:
            return f"background: linear-gradient(90deg, {preset[1]}, {preset[3]}, {preset[2]});"
        else:
            return f"background: linear-gradient(90deg, {preset[1]}, {preset[2]});"
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _show_custom_gradient(self, parent):
        """Show custom gradient picker."""
        custom = ctk.CTkToplevel(parent)
        custom.title("🎨 Custom Gradient")
        custom.geometry("350x300")
        custom.transient(parent)
        custom.grab_set()
        
        ctk.CTkLabel(custom, text="Create Custom Gradient", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        self.custom_c1 = (255, 0, 0)
        self.custom_c2 = (0, 0, 255)
        
        colors_frame = ctk.CTkFrame(custom, fg_color="transparent")
        colors_frame.pack(pady=10)
        
        # Color 1
        c1_frame = ctk.CTkFrame(colors_frame, fg_color="transparent")
        c1_frame.pack(side="left", padx=20)
        ctk.CTkLabel(c1_frame, text="Start").pack()
        self.custom_swatch1 = ctk.CTkFrame(c1_frame, width=60, height=60, fg_color="#FF0000", corner_radius=8)
        self.custom_swatch1.pack(pady=5)
        ctk.CTkButton(c1_frame, text="Pick", command=lambda: self._pick_custom(1), width=60).pack()
        
        # Color 2
        c2_frame = ctk.CTkFrame(colors_frame, fg_color="transparent")
        c2_frame.pack(side="left", padx=20)
        ctk.CTkLabel(c2_frame, text="End").pack()
        self.custom_swatch2 = ctk.CTkFrame(c2_frame, width=60, height=60, fg_color="#0000FF", corner_radius=8)
        self.custom_swatch2.pack(pady=5)
        ctk.CTkButton(c2_frame, text="Pick", command=lambda: self._pick_custom(2), width=60).pack()
        
        def apply_custom():
            hex1 = rgb_to_hex(*self.custom_c1)
            hex2 = rgb_to_hex(*self.custom_c2)
            self.selected_gradient = ("Custom", hex1, hex2, None)
            self.grad_name_label.configure(text="Custom")
            self.grad_colors_label.configure(text=f"{hex1} → {hex2}")
            self._update_selected_preview()
            self._update_css_label()
            custom.destroy()
        
        ctk.CTkButton(custom, text="✓ Apply", command=apply_custom, fg_color="#00B894").pack(pady=20)
    
    def _pick_custom(self, which):
        """Pick custom gradient color."""
        color = self._ask_color()
        if color:
            if which == 1:
                self.custom_c1 = color
                self.custom_swatch1.configure(fg_color=rgb_to_hex(*color))
            else:
                self.custom_c2 = color
                self.custom_swatch2.configure(fg_color=rgb_to_hex(*color))

    def _ask_color(self):
        """Open a simple color picker dialog."""
        from tkinter import colorchooser
        result = colorchooser.askcolor(title="Choose a Color")
        if result and result[0]:
            return tuple(int(c) for c in result[0])
        return None

    # ---------------------------------------------------------------------
    # Theme handling – smooth fade animation
    # ---------------------------------------------------------------------
    def _toggle_theme_smooth(self):
        """Toggle theme instantly without delay."""
        current = ctk.get_appearance_mode()
        target = "light" if current == "Dark" else "dark"
        
        # Instant switch - no overlay, no delay
        ctk.set_appearance_mode(target)
        self.theme_switch.configure(text="☀️ Light Mode" if target == "light" else "🌙 Dark Mode")

    # ---------------------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------------------
    def _on_close(self):
        self._save_user_data()
        if self.camera:
            self.camera.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ColorDetectionApp()
    app.run()

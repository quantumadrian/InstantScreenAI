import tkinter as tk
from PIL import ImageGrab, ImageTk
import numpy as np

class AreaSelector:
    def __init__(self, callback):
        self.callback = callback
        self.root = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.screenshot = None
        
    def select_area(self):
        """Start area selection process"""
        # Take screenshot first
        self.screenshot = ImageGrab.grab()
        
        # Create fullscreen overlay
        self.root = tk.Toplevel()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(bg='black')
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Escape>', self.cancel_selection)
        
        # Add instructions
        self.canvas.create_text(
            self.root.winfo_screenwidth() // 2,
            50,
            text="Click and drag to select an area. Press ESC to cancel.",
            fill='white',
            font=('Arial', 16)
        )
        
    def on_mouse_down(self, event):
        """Handle mouse button press"""
        self.start_x = event.x
        self.start_y = event.y
        
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )
        
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
            
    def on_mouse_up(self, event):
        """Handle mouse button release"""
        if self.start_x and self.start_y:
            x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
            x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
            
            # Ensure minimum size
            if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                # Crop the screenshot
                cropped = self.screenshot.crop((x1, y1, x2, y2))
                self.callback(cropped)
            
        self.root.destroy()
        
    def cancel_selection(self, event=None):
        """Cancel the selection"""
        self.root.destroy() 
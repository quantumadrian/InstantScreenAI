import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import base64
import io
from PIL import Image, ImageTk, ImageGrab
import threading
import os
from datetime import datetime
import configparser
from area_selector import AreaSelector

# Try to import optional dependencies
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

class ModernButton(tk.Button):
    """Custom modern button with hover effects"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            bg='#6366f1',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
    
    def on_enter(self, event):
        self.configure(bg='#4f46e5')
    
    def on_leave(self, event):
        self.configure(bg='#6366f1')

class ModernEntry(tk.Entry):
    """Custom modern entry with better styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            bg='#374151',
            fg='white',
            font=('Segoe UI', 10),
            relief='flat',
            bd=0,
            insertbackground='white',
            selectbackground='#6366f1',
            selectforeground='white'
        )

class ModernText(tk.Text):
    """Custom modern text widget with better styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            bg='#374151',
            fg='white',
            font=('Segoe UI', 10),
            relief='flat',
            bd=0,
            insertbackground='white',
            selectbackground='#6366f1',
            selectforeground='white',
            padx=10,
            pady=10
        )

class MultiAPIAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("InstantScreenAI - Multi-API Assistant")
        self.root.geometry("500x750")  # Made wider and taller
        self.root.resizable(True, True)
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Modern color scheme
        self.colors = {
            'bg_dark': '#111827',
            'bg_card': '#1f2937',
            'bg_input': '#374151',
            'primary': '#6366f1',
            'primary_hover': '#4f46e5',
            'text_primary': '#f9fafb',
            'text_secondary': '#d1d5db',
            'border': '#4b5563',
            'success': '#10b981',
            'warning': '#f59e0b'
        }
        
        # Configure window style
        self.root.configure(bg=self.colors['bg_dark'])
        
        # API Configuration
        self.api_keys = {
            'openai': '',
            'gemini': '',
            'claude': ''
        }
        self.selected_api = 'openai'
        self.load_config()
        
        # Screenshot data
        self.current_screenshot = None
        self.screenshot_path = None
        
        # Area selector
        self.area_selector = AreaSelector(self.on_area_selected)
        
        self.setup_ui()
        self.center_window()
        
    def load_config(self):
        """Load API configuration from config file"""
        config = configparser.ConfigParser()
        config_file = 'config.ini'
        
        if os.path.exists(config_file):
            config.read(config_file)
            self.api_keys['openai'] = config.get('API', 'openai_key', fallback='')
            self.api_keys['gemini'] = config.get('API', 'gemini_key', fallback='')
            self.api_keys['claude'] = config.get('API', 'claude_key', fallback='')
            self.selected_api = config.get('API', 'selected', fallback='openai')
        else:
            # Create default config
            config['API'] = {
                'openai_key': '',
                'gemini_key': '',
                'claude_key': '',
                'selected': 'openai'
            }
            with open(config_file, 'w') as f:
                config.write(f)
    
    def save_config(self):
        """Save API configuration to config file"""
        config = configparser.ConfigParser()
        config['API'] = {
            'openai_key': self.api_keys['openai'],
            'gemini_key': self.api_keys['gemini'],
            'claude_key': self.api_keys['claude'],
            'selected': self.selected_api
        }
        with open('config.ini', 'w') as f:
            config.write(f)
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_card_frame(self, parent, title, row, columnspan=2):
        """Create a modern card-style frame"""
        # Card container
        card_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=0)
        card_frame.grid(row=row, column=0, columnspan=columnspan, sticky=(tk.W, tk.E), pady=(0, 15), padx=5)
        card_frame.columnconfigure(0, weight=1)
        
        # Title label
        title_label = tk.Label(card_frame, text=title, 
                              font=('Segoe UI', 12, 'bold'), 
                              fg=self.colors['text_primary'], 
                              bg=self.colors['bg_card'],
                              anchor='w')
        title_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(15, 10), padx=15)
        
        # Content frame
        content_frame = tk.Frame(card_frame, bg=self.colors['bg_card'])
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=15, pady=(0, 15))
        content_frame.columnconfigure(1, weight=1)
        
        return content_frame
    
    def setup_ui(self):
        """Setup the modern user interface with proper scrolling"""
        # Create main canvas with scrollbar
        canvas = tk.Canvas(self.root, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main frame inside scrollable frame
        main_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_dark'], padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Header with logo and title
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="InstantScreenAI", 
                              font=('Segoe UI', 24, 'bold'), 
                              fg=self.colors['text_primary'], 
                              bg=self.colors['bg_dark'])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Multi-AI Screenshot Assistant", 
                                 font=('Segoe UI', 12), 
                                 fg=self.colors['text_secondary'], 
                                 bg=self.colors['bg_dark'])
        subtitle_label.pack()
        
        # AI Service Selection Card
        api_select_frame = self.create_card_frame(main_frame, "🤖 Select AI Service", 1)
        
        # API selection radio buttons with modern styling
        self.api_var = tk.StringVar(value=self.selected_api)
        
        # Create modern radio buttons
        services = [
            ("OpenAI (GPT-4)", "openai", "🔵"),
            ("Google Gemini", "gemini", "🔮"),
            ("Anthropic Claude", "claude", "🧠")
        ]
        
        for i, (name, value, icon) in enumerate(services):
            radio_frame = tk.Frame(api_select_frame, bg=self.colors['bg_card'])
            radio_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5)
            
            radio_btn = tk.Radiobutton(radio_frame, 
                                     text=f"{icon} {name}", 
                                     variable=self.api_var, 
                                     value=value,
                                     command=self.on_api_change,
                                     font=('Segoe UI', 11),
                                     fg=self.colors['text_primary'],
                                     bg=self.colors['bg_card'],
                                     selectcolor=self.colors['bg_card'],
                                     activebackground=self.colors['bg_card'],
                                     activeforeground=self.colors['primary'])
            radio_btn.pack(anchor='w')
        
        # API Configuration Card
        api_config_frame = self.create_card_frame(main_frame, "🔑 API Configuration", 2)
        
        # API Key entries with modern styling
        api_entries = [
            ("OpenAI API Key:", "openai_key_entry"),
            ("Gemini API Key:", "gemini_key_entry"),
            ("Claude API Key:", "claude_key_entry")
        ]
        
        for i, (label_text, entry_name) in enumerate(api_entries):
            # Label
            label = tk.Label(api_config_frame, text=label_text,
                           font=('Segoe UI', 10, 'bold'),
                           fg=self.colors['text_primary'],
                           bg=self.colors['bg_card'])
            label.grid(row=i, column=0, sticky=tk.W, pady=(10, 5))
            
            # Entry
            entry = ModernEntry(api_config_frame, show="*", width=45)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=(15, 0), pady=(10, 5))
            setattr(self, entry_name, entry)
        
        # Save button
        save_btn = ModernButton(api_config_frame, text="💾 Save All Keys", command=self.save_api_keys)
        save_btn.grid(row=len(api_entries), column=0, columnspan=2, pady=15)
        
        # Screenshot Card
        screenshot_frame = self.create_card_frame(main_frame, "📸 Screenshot Tools", 3)
        
        # Screenshot buttons in a modern layout
        btn_frame = tk.Frame(screenshot_frame, bg=self.colors['bg_card'])
        btn_frame.grid(row=0, column=0, pady=10)
        
        buttons = [
            ("📸 Full Screen", self.capture_full_screen),
            ("✂️ Select Area", self.capture_area),
            ("📁 Load Image", self.load_image)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ModernButton(btn_frame, text=text, command=command)
            btn.grid(row=0, column=i, padx=(0, 10) if i < len(buttons)-1 else (0, 0))
        
        # Screenshot preview with modern styling
        preview_frame = tk.Frame(screenshot_frame, bg=self.colors['bg_input'], relief='flat', bd=0)
        preview_frame.grid(row=1, column=0, pady=15, sticky=(tk.W, tk.E))
        
        self.preview_label = tk.Label(preview_frame, 
                                     text="No screenshot captured\nClick a button above to capture", 
                                     bg=self.colors['bg_input'], 
                                     fg=self.colors['text_secondary'],
                                     font=('Segoe UI', 10),
                                     width=50, height=8,
                                     justify='center')
        self.preview_label.pack(pady=20)
        
        # Question Card
        question_frame = self.create_card_frame(main_frame, "❓ Ask AI", 4)
        
        # Question text with modern styling
        self.question_text = ModernText(question_frame, height=4, width=50)
        self.question_text.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))
        self.question_text.insert("1.0", "What do you see in this screenshot?")
        
        # Ask button
        ask_btn = ModernButton(question_frame, text="🚀 Ask AI", command=self.ask_ai)
        ask_btn.grid(row=1, column=0, pady=10)
        
        # Response Card
        response_frame = self.create_card_frame(main_frame, "💬 AI Response", 5)
        
        # Response text with modern styling and scrollbar
        response_container = tk.Frame(response_frame, bg=self.colors['bg_card'])
        response_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        response_container.columnconfigure(0, weight=1)
        response_container.rowconfigure(0, weight=1)
        
        self.response_text = ModernText(response_container, height=10, width=50)
        response_scrollbar = ttk.Scrollbar(response_container, orient="vertical", command=self.response_text.yview)
        self.response_text.configure(yscrollcommand=response_scrollbar.set)
        
        self.response_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        response_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Status bar with modern styling
        status_frame = tk.Frame(main_frame, bg=self.colors['bg_card'], relief='flat', bd=0)
        status_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(10, 0), padx=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("✨ Ready to capture and analyze screenshots")
        status_bar = tk.Label(status_frame, textvariable=self.status_var,
                             font=('Segoe UI', 9),
                             fg=self.colors['text_secondary'],
                             bg=self.colors['bg_card'],
                             anchor='w')
        status_bar.pack(fill='x', padx=15, pady=10)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Load saved API keys
        self.openai_key_entry.insert(0, self.api_keys['openai'])
        self.gemini_key_entry.insert(0, self.api_keys['gemini'])
        self.claude_key_entry.insert(0, self.api_keys['claude'])
        
    def on_api_change(self):
        """Handle API selection change"""
        self.selected_api = self.api_var.get()
        self.save_config()
        
    def save_api_keys(self):
        """Save all API keys"""
        self.api_keys['openai'] = self.openai_key_entry.get().strip()
        self.api_keys['gemini'] = self.gemini_key_entry.get().strip()
        self.api_keys['claude'] = self.claude_key_entry.get().strip()
        self.save_config()
        
        # Modern success message
        self.status_var.set("✅ All API keys saved successfully!")
        self.root.after(3000, lambda: self.status_var.set("✨ Ready to capture and analyze screenshots"))
    
    def capture_full_screen(self):
        """Capture the entire screen"""
        try:
            self.status_var.set("📸 Capturing full screen...")
            self.root.update()
            
            # Capture screenshot
            screenshot = ImageGrab.grab()
            self.current_screenshot = screenshot
            
            # Save screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.screenshot_path = f"screenshot_{timestamp}.png"
            screenshot.save(self.screenshot_path)
            
            # Update preview
            self.update_preview(screenshot)
            self.status_var.set(f"✅ Screenshot saved: {self.screenshot_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture screenshot: {str(e)}")
            self.status_var.set("❌ Screenshot capture failed")
    
    def capture_area(self):
        """Capture a selected area of the screen"""
        self.root.iconify()  # Minimize main window
        self.root.after(500, self._start_area_capture)
    
    def _start_area_capture(self):
        """Start the area capture process"""
        try:
            self.area_selector.select_area()
        except Exception as e:
            messagebox.showerror("Error", f"Area capture failed: {str(e)}")
        finally:
            self.root.deiconify()  # Restore main window
    
    def on_area_selected(self, cropped_image):
        """Callback when area selection is complete"""
        try:
            self.current_screenshot = cropped_image
            
            # Save screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.screenshot_path = f"screenshot_area_{timestamp}.png"
            cropped_image.save(self.screenshot_path)
            
            # Update preview
            self.update_preview(cropped_image)
            self.status_var.set(f"✅ Area screenshot saved: {self.screenshot_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process area selection: {str(e)}")
            self.status_var.set("❌ Area selection failed")
    
    def load_image(self):
        """Load an image from file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if file_path:
            try:
                image = Image.open(file_path)
                self.current_screenshot = image
                self.screenshot_path = file_path
                self.update_preview(image)
                self.status_var.set(f"✅ Image loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def update_preview(self, image):
        """Update the preview with the captured image - preserving aspect ratio"""
        # Create a copy to avoid modifying the original
        preview_image = image.copy()
        
        # Calculate aspect ratio preserving resize
        preview_width = 200
        preview_height = 150
        
        # Get original dimensions
        orig_width, orig_height = preview_image.size
        
        # Calculate scaling factor to fit within preview area
        scale_x = preview_width / orig_width
        scale_y = preview_height / orig_height
        scale = min(scale_x, scale_y)  # Use the smaller scale to fit both dimensions
        
        # Calculate new dimensions
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)
        
        # Resize image preserving aspect ratio
        preview_image = preview_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create a background canvas with the preview size
        background = Image.new('RGB', (preview_width, preview_height), self.colors['bg_input'])
        
        # Calculate position to center the image
        x_offset = (preview_width - new_width) // 2
        y_offset = (preview_height - new_height) // 2
        
        # Paste the resized image onto the background
        background.paste(preview_image, (x_offset, y_offset))
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(background)
        
        # Update preview label
        self.preview_label.configure(image=photo, text="")
        self.preview_label.image = photo  # Keep a reference
    
    def ask_ai(self):
        """Send screenshot and question to selected AI service"""
        if not self.api_keys[self.selected_api]:
            messagebox.showerror("Error", f"Please enter your {self.selected_api.title()} API key first!")
            return
        
        if not self.current_screenshot:
            messagebox.showerror("Error", "Please capture or load an image first!")
            return
        
        question = self.question_text.get("1.0", tk.END).strip()
        if not question:
            messagebox.showerror("Error", "Please enter a question!")
            return
        
        # Run API call in separate thread to avoid blocking UI
        threading.Thread(target=self._send_to_ai, args=(question,), daemon=True).start()
    
    def _send_to_ai(self, question):
        """Send request to selected AI service"""
        try:
            self.status_var.set(f"🤖 Sending to {self.selected_api.title()}...")
            self.root.update()
            
            if self.selected_api == 'openai':
                response_text = self._send_to_openai(question)
            elif self.selected_api == 'gemini':
                response_text = self._send_to_gemini(question)
            elif self.selected_api == 'claude':
                response_text = self._send_to_claude(question)
            else:
                raise ValueError(f"Unknown API: {self.selected_api}")
            
            # Update UI in main thread
            self.root.after(0, lambda: self._update_response(response_text))
            self.root.after(0, lambda: self.status_var.set("✅ Response received"))
                
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.root.after(0, lambda: self.status_var.set("❌ Request failed"))
    
    def _send_to_openai(self, question):
        """Send request to OpenAI API"""
        # Convert image to base64 with proper error handling
        try:
            img_buffer = io.BytesIO()
            self.current_screenshot.save(img_buffer, format='PNG')
            img_buffer.seek(0)  # Reset buffer position
            img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to encode image: {str(e)}")
        
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_keys['openai']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_str}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        # Send request
        response = requests.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI API Error: {response.status_code} - {response.text}")
    
    def _send_to_gemini(self, question):
        """Send request to Gemini API - Fixed blob issue"""
        if not GEMINI_AVAILABLE:
            raise Exception("Gemini library not installed. Run: pip install google-generativeai")
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_keys['gemini'])
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Convert image to bytes with proper error handling
            img_buffer = io.BytesIO()
            self.current_screenshot.save(img_buffer, format='PNG')
            img_buffer.seek(0)  # Reset buffer position
            img_data = img_buffer.getvalue()
            
            # Create PIL Image object for Gemini (this fixes the blob issue)
            from PIL import Image
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Send request with PIL Image instead of raw bytes
            response = model.generate_content([question, pil_image])
            
            if response.text:
                return response.text
            else:
                raise Exception("Empty response from Gemini")
                
        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")
    
    def _send_to_claude(self, question):
        """Send request to Claude API"""
        if not CLAUDE_AVAILABLE:
            raise Exception("Claude library not installed. Run: pip install anthropic")
        
        try:
            # Convert image to base64 with proper error handling
            img_buffer = io.BytesIO()
            self.current_screenshot.save(img_buffer, format='PNG')
            img_buffer.seek(0)  # Reset buffer position
            img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to encode image: {str(e)}")
        
        # Prepare API request
        headers = {
            "x-api-key": self.api_keys['claude'],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_str
                            }
                        }
                    ]
                }
            ]
        }
        
        # Send request
        response = requests.post("https://api.anthropic.com/v1/messages", 
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            raise Exception(f"Claude API Error: {response.status_code} - {response.text}")
    
    def _update_response(self, response_text):
        """Update the response text widget with modern formatting"""
        self.response_text.delete("1.0", tk.END)
        
        # Format the response with better typography
        formatted_response = f"🤖 AI Response:\n\n{response_text}\n\n---\nGenerated by {self.selected_api.title()}"
        
        self.response_text.insert("1.0", formatted_response)
        
        # Apply some styling (make the first line bold)
        self.response_text.tag_add("bold", "1.0", "2.0")
        self.response_text.tag_config("bold", font=('Segoe UI', 11, 'bold'))
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MultiAPIAssistant()
    app.run()

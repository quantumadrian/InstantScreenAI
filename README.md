# InstantScreenAI - Floating ChatGPT Assistant

A powerful Windows desktop application that provides instant AI assistance by capturing screenshots and sending them to ChatGPT for analysis. The app stays as a small, always-on-top window, making it perfect for quick AI-powered screen analysis.

## ✨ Features

- **📸 Screenshot Capture**: Take full-screen screenshots or select specific areas
- **🤖 ChatGPT Integration**: Send screenshots directly to ChatGPT for analysis
- **🪟 Always-on-Top**: Window stays visible even when other applications are active
- **📁 Image Loading**: Load existing images from your computer
- **💾 Automatic Saving**: Screenshots are automatically saved with timestamps
- **🔐 Secure API**: Your OpenAI API key is stored locally and securely
- **🎨 Modern UI**: Clean, dark-themed interface for better visibility

## 🚀 Quick Start

### Prerequisites

- Windows 10/11
- Python 3.8 or higher
- OpenAI API key (get one from [OpenAI Platform](https://platform.openai.com/api-keys))

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd InstantScreenAI
   ```

2. **Install Python dependencies**
   ```bash
   pip install requests>=2.31.0
   pip install Pillow>=10.0.0
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Configure your API key**
   - Enter your OpenAI API key in the "API Configuration" section
   - Click "Save" to store it securely

## 📖 How to Use

### Taking Screenshots

1. **Full Screen Capture**: Click "📸 Full Screen" to capture your entire screen
2. **Area Selection**: Click "✂️ Select Area" to select a specific region
   - The main window will minimize
   - Click and drag to select an area
   - Press ESC to cancel
3. **Load Image**: Click "📁 Load Image" to use an existing image file

### Asking ChatGPT

1. **Enter your question** in the "Ask ChatGPT" text box
2. **Click "🤖 Ask ChatGPT"** to send the screenshot for analysis
3. **View the response** in the "Response" section

### Tips for Better Results

- **Be specific** in your questions for more detailed responses
- **Use area selection** for focused analysis of specific UI elements
- **Try different questions** like:
  - "What do you see in this screenshot?"
  - "Explain this error message"
  - "What is this application doing?"
  - "How can I fix this issue?"

## 🔧 Configuration

The application automatically creates a `config.ini` file to store your API key securely. The file is stored in the same directory as the application.

### API Key Management

- **First Time**: Enter your OpenAI API key and click "Save"
- **Subsequent Runs**: Your API key is automatically loaded
- **Security**: The API key is stored locally and never transmitted except to OpenAI

## 📁 File Structure

```
InstantScreenAI/
├── main.py              # Main application
├── area_selector.py     # Area selection functionality
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── config.ini          # API configuration (created automatically)
└── screenshot_*.png    # Captured screenshots (created automatically)
```

## 🛠️ Technical Details

### Dependencies

- **tkinter**: GUI framework (included with Python)
- **Pillow**: Image processing and screenshot capture
- **requests**: HTTP requests to OpenAI API
- **configparser**: Configuration file management

### API Usage

The application uses OpenAI's GPT-4 Vision API (`gpt-4-vision-preview`) for image analysis. Each request includes:
- Your question as text
- The screenshot as a base64-encoded image
- Maximum 1000 tokens for the response

### Screenshot Storage

- Screenshots are automatically saved with timestamps
- Full screen: `screenshot_YYYYMMDD_HHMMSS.png`
- Area selection: `screenshot_area_YYYYMMDD_HHMMSS.png`

## 🐛 Troubleshooting

### Common Issues

1. **"API key not found"**
   - Make sure you've entered and saved your OpenAI API key
   - Check that the `config.ini` file exists in the application directory

2. **"Failed to capture screenshot"**
   - Ensure you have permission to capture screenshots
   - Try running the application as administrator if needed

3. **"API request failed"**
   - Check your internet connection
   - Verify your OpenAI API key is valid
   - Ensure you have sufficient API credits

4. **Area selection not working**
   - Make sure no other applications are in full-screen mode
   - Try the full-screen capture option instead

### Performance Tips

- **Close unnecessary applications** before taking screenshots
- **Use area selection** for faster processing of smaller images
- **Keep the window small** if you don't need the full interface

## 🔒 Privacy & Security

- **Local Storage**: All screenshots and API keys are stored locally on your computer
- **No Cloud Upload**: Screenshots are only sent to OpenAI when you explicitly request analysis
- **Secure API**: API keys are stored in a local configuration file
- **No Tracking**: The application doesn't collect or transmit any usage data

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Python and tkinter
- Powered by OpenAI's GPT-4 Vision API
- Inspired by the need for quick AI-powered screen analysis

---

**Happy AI-powered screen analysis! 🚀**

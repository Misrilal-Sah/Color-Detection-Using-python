# 🎨 Color Detection Pro

A modern, offline-capable desktop application for intelligent color detection using Python, Machine Learning, and OpenCV.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-purple.svg)

## 📥 Download

**Windows Users**: Download the standalone executable - no Python installation required!

[![Download](https://img.shields.io/badge/Download-ColorDetectionPro.exe-brightgreen?style=for-the-badge&logo=windows)](https://github.com/Misrilal-Sah/Color-Detection-Using-python/releases/latest)

> **Note**: The .exe file is ~370 MB as it includes all dependencies (OpenCV, scikit-learn, etc.)

## ✨ Features

### Core Features
- **📁 Image Upload**: Load images (JPG, PNG, BMP, GIF, WebP) for color analysis
- **📷 Live Camera Detection**: Real-time color detection from webcam
- **📸 Camera Capture**: Take snapshots for detailed analysis
- **🖱️ Click-to-Detect**: Click anywhere on an image to identify colors
- **🎨 Palette Extraction**: Extract dominant colors using K-Means clustering

### Color Information
- **Color Name Matching**: AI-powered color name identification (265+ colors)
- **Multiple Formats**: HEX, RGB, HSV, HSL, CMYK codes
- **One-Click Copy**: Copy any color code to clipboard instantly

### Advanced Features
- **🎭 Color Harmony**: Complementary, triadic, and analogous colors
- **👁️ Color Blindness Simulation**: Protanopia, Deuteranopia, Tritanopia preview
- **♿ Accessibility Checker**: WCAG contrast ratio analysis
- **🕐 Color History**: Track recently detected colors
- **⭐ Favorites**: Save your favorite colors
- **🌙 Dark/Light Theme**: Toggle between themes

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Webcam (optional, for camera features)

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd Color_detection
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate     # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
Color_detection/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md
├── core/
│   ├── color_converter.py  # Color format conversions
│   ├── color_detector.py   # Image/camera processing
│   └── color_matcher.py    # Color name matching (KNN)
├── ui/
│   ├── app.py              # Main application window
│   └── components/         # UI components
├── data/
│   ├── colors.json         # Color database (265+ colors)
│   └── user_data.json      # History & favorites
├── utils/
└── tests/
```

## 🎮 Usage Guide

### Detecting Colors from Images
1. Click **"📁 Upload Image"** in the sidebar
2. Select an image file
3. Click anywhere on the image to detect the color at that point
4. View detailed color information in the right panel

### Using Live Camera
1. Click **"📷 Camera Capture"** to start the webcam
2. Point at any colored object
3. The center crosshair shows real-time color detection
4. Click **"📸 Take Snapshot"** to capture and analyze

### Extracting Color Palette
1. Load an image
2. Click **"🎨 Extract Palette"**
3. View the dominant colors below the image
4. Click any palette color to see its details

### Saving Colors
- Click **"⭐ Add to Favorites"** to save the current color
- View saved colors via **"⭐ Favorites"** button
- History automatically tracks recent colors

## 🔧 Technology Stack

| Component | Technology |
|-----------|------------|
| GUI Framework | CustomTkinter |
| Image Processing | OpenCV |
| ML Algorithm | K-Means Clustering, KDTree |
| Color Matching | scikit-learn |
| Image Library | Pillow |

## 🎯 Color Database

The application includes 265+ named colors from:
- CSS/Web standard colors
- Material Design palette
- Popular design system colors
- Nature-inspired colors
- Pantone-inspired shades

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

---

**Made with ❤️ using Python, OpenCV, and CustomTkinter**

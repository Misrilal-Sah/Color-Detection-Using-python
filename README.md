<div align="center">

<img src="https://capsule-render.vercel.app/api?type=cylinder&height=190&color=gradient&customColorList=12,28,30,20,14&text=Color%20Detection%20Pro&fontAlign=50&fontAlignY=42&fontSize=48&desc=Offline%20Desktop%20Color%20Intelligence%20with%20OpenCV%20%2B%20ML&descAlign=50&descAlignY=64&animation=twinkling" alt="Color Detection Pro" />

<p>
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/CustomTkinter-5.2%2B-1F2937?style=for-the-badge&logo=windows-terminal&logoColor=white" alt="CustomTkinter" />
  <img src="https://img.shields.io/badge/Offline-First-0EA5E9?style=for-the-badge&logo=icloud&logoColor=white" alt="Offline First" />
</p>

<p>
  A premium desktop toolkit for fast, accurate, and fully offline color analysis.<br/>
  Detect, convert, match, mix, extract, and build color systems from images or live camera feed.
</p>

</div>

---

## Why This Project Stands Out

- Pixel-accurate click detection from uploaded images and live camera frames.
- Fast color intelligence powered by KDTree matching and K-Means palette extraction.
- Designer-ready outputs in HEX, RGB, HSV, HSL, and CMYK with one-click copy.
- Built-in harmony generation, favorites, and history for practical workflow speed.
- Smooth desktop UX with modern CustomTkinter components and theme transitions.

## Download (Windows)

Run instantly without installing Python:

[![Download EXE](https://img.shields.io/badge/Download-ColorDetectionPro.exe-16A34A?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Misrilal-Sah/Color-Detection-Using-python/releases/latest)

> Packaged executable is large (around 370 MB) because it bundles computer-vision and ML dependencies.

## Feature Showcase

### Detection and Analysis
- Image upload: JPG, JPEG, PNG, BMP, GIF, WebP
- Live webcam color detection and instant snapshot capture
- Click-to-detect sampling from any point in the image
- Dominant palette extraction using K-Means clustering

### Color Intelligence
- Nearest named color matching using KDTree search
- 265+ color database entries
- Full format conversion: HEX, RGB, HSV, HSL, CMYK
- Copy any code format directly to clipboard

### Creative Toolkit
- Harmony sets: complementary, triadic, analogous, split-complementary
- Interactive color mixer with blend ratio slider
- Gradient gallery with presets and custom gradient creation
- CSS gradient string generation and copy support

### Productivity and UX
- Recent color history
- Favorites management (persisted to local JSON)
- Light and dark appearance toggle with smooth transition
- Offline-first workflow with local data storage

## Quick Start

### Requirements
- Python 3.8+
- Webcam (optional, for camera mode)

### Installation

```bash
cd Color_detection
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## How It Works

```mermaid
flowchart LR
    A[Image Upload or Camera Frame] --> B[OpenCV RGB Processing]
    B --> C[Point Sampling / Palette Extraction]
    C --> D[KDTree Color Name Matching]
    C --> E[Format Conversion Engine]
    C --> F[Harmony + Creative Tools]
    D --> G[UI Info Panel]
    E --> G
    F --> G
    G --> H[History and Favorites Persistence]
```

## Tech Stack

| Layer | Technology |
|---|---|
| UI | CustomTkinter |
| Image Processing | OpenCV |
| Numeric Processing | NumPy |
| ML / Search | scikit-learn (KMeans, KDTree) |
| Image Handling | Pillow |
| Packaging | PyInstaller |

## Project Structure

```text
Color_detection/
|- main.py
|- requirements.txt
|- ColorDetectionPro.spec
|- core/
|  |- color_detector.py
|  |- color_matcher.py
|  \- color_converter.py
|- ui/
|  |- app.py
|  \- components/
|- data/
|  |- colors.json
|  \- user_data.json
|- utils/
\- tests/
```

## Usage Flow

1. Launch the app and choose Upload Image or Camera Capture.
2. Click any pixel to detect and identify color details.
3. Review color name confidence and all format conversions.
4. Extract dominant palette or explore harmonies.
5. Save key colors to Favorites for later reuse.

## Roadmap Ideas

- Batch image processing mode
- Exportable palette formats (ASE, GPL, JSON)
- Enhanced accessibility panel (contrast pair testing)
- Plugin-style color datasets

## Contributing

Contributions, ideas, and improvements are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=venom&height=170&color=0:0F172A,30:1E293B,65:0EA5E9,100:22D3EE&text=Color%20Detection%20Pro&fontColor=FFFFFF&fontSize=36&stroke=FFFFFF&strokeWidth=0" alt="Color Detection Pro Footer" />
  <p><strong>Crafted for Designers and Developers</strong></p>
  <p>Fast • Offline • Aesthetic • Practical</p>
  <p>
    <a href="https://github.com/Misrilal-Sah/Color-Detection-Using-python/releases/latest">Download</a>
    •
    <a href="https://github.com/Misrilal-Sah/Color-Detection-Using-python/issues">Issues</a>
    •
    <a href="https://github.com/Misrilal-Sah/Color-Detection-Using-python">Star the Project</a>
  </p>
</div>

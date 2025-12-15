"""
Color Converter Module
Handles all color format conversions: RGB, HEX, HSV, HSL, CMYK
"""

import colorsys
from typing import Tuple, Dict


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to HEX color code."""
    return f"#{r:02x}{g:02x}{b:02x}".upper()


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert HEX to RGB color values."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c * 2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """Convert RGB to HSV color values."""
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return (int(h * 360), int(s * 100), int(v * 100))


def hsv_to_rgb(h: int, s: int, v: int) -> Tuple[int, int, int]:
    """Convert HSV to RGB color values."""
    r, g, b = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
    return (int(r * 255), int(g * 255), int(b * 255))


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """Convert RGB to HSL color values."""
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return (int(h * 360), int(s * 100), int(l * 100))


def hsl_to_rgb(h: int, s: int, l: int) -> Tuple[int, int, int]:
    """Convert HSL to RGB color values."""
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return (int(r * 255), int(g * 255), int(b * 255))


def rgb_to_cmyk(r: int, g: int, b: int) -> Tuple[int, int, int, int]:
    """Convert RGB to CMYK color values (percentages)."""
    if r == 0 and g == 0 and b == 0:
        return (0, 0, 0, 100)
    
    c = 1 - (r / 255)
    m = 1 - (g / 255)
    y = 1 - (b / 255)
    k = min(c, m, y)
    
    if k == 1:
        return (0, 0, 0, 100)
    
    c = (c - k) / (1 - k)
    m = (m - k) / (1 - k)
    y = (y - k) / (1 - k)
    
    return (int(c * 100), int(m * 100), int(y * 100), int(k * 100))


def cmyk_to_rgb(c: int, m: int, y: int, k: int) -> Tuple[int, int, int]:
    """Convert CMYK to RGB color values."""
    c, m, y, k = c / 100, m / 100, y / 100, k / 100
    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)
    return (int(r), int(g), int(b))


def get_all_formats(r: int, g: int, b: int) -> Dict[str, any]:
    """Get all color formats for a given RGB color."""
    return {
        'rgb': (r, g, b),
        'hex': rgb_to_hex(r, g, b),
        'hsv': rgb_to_hsv(r, g, b),
        'hsl': rgb_to_hsl(r, g, b),
        'cmyk': rgb_to_cmyk(r, g, b)
    }


def get_complementary_color(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """Get the complementary (opposite) color."""
    return (255 - r, 255 - g, 255 - b)


def get_triadic_colors(r: int, g: int, b: int) -> list:
    """Get triadic colors (120° apart on color wheel)."""
    h, s, v = rgb_to_hsv(r, g, b)
    colors = []
    for offset in [120, 240]:
        new_h = (h + offset) % 360
        colors.append(hsv_to_rgb(new_h, s, v))
    return colors


def get_analogous_colors(r: int, g: int, b: int) -> list:
    """Get analogous colors (30° apart on color wheel)."""
    h, s, v = rgb_to_hsv(r, g, b)
    colors = []
    for offset in [-30, 30]:
        new_h = (h + offset) % 360
        colors.append(hsv_to_rgb(new_h, s, v))
    return colors


def get_split_complementary(r: int, g: int, b: int) -> list:
    """Get split-complementary colors (150° and 210° from base)."""
    h, s, v = rgb_to_hsv(r, g, b)
    colors = []
    for offset in [150, 210]:
        new_h = (h + offset) % 360
        colors.append(hsv_to_rgb(new_h, s, v))
    return colors


def calculate_contrast_ratio(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    def get_luminance(rgb):
        r, g, b = [x / 255 for x in rgb]
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    l1 = get_luminance(rgb1)
    l2 = get_luminance(rgb2)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    return (lighter + 0.05) / (darker + 0.05)


def get_wcag_rating(contrast_ratio: float) -> str:
    """Get WCAG accessibility rating based on contrast ratio."""
    if contrast_ratio >= 7:
        return "AAA (Excellent)"
    elif contrast_ratio >= 4.5:
        return "AA (Good)"
    elif contrast_ratio >= 3:
        return "AA Large (Acceptable)"
    else:
        return "Fail (Poor)"


# Color blindness simulation matrices
COLOR_BLINDNESS_MATRICES = {
    'protanopia': [  # Red-blind
        [0.567, 0.433, 0.000],
        [0.558, 0.442, 0.000],
        [0.000, 0.242, 0.758]
    ],
    'deuteranopia': [  # Green-blind
        [0.625, 0.375, 0.000],
        [0.700, 0.300, 0.000],
        [0.000, 0.300, 0.700]
    ],
    'tritanopia': [  # Blue-blind
        [0.950, 0.050, 0.000],
        [0.000, 0.433, 0.567],
        [0.000, 0.475, 0.525]
    ],
    'achromatopsia': [  # Complete color blindness
        [0.299, 0.587, 0.114],
        [0.299, 0.587, 0.114],
        [0.299, 0.587, 0.114]
    ]
}


def simulate_color_blindness(r: int, g: int, b: int, blindness_type: str) -> Tuple[int, int, int]:
    """Simulate how a color appears to someone with color blindness."""
    if blindness_type not in COLOR_BLINDNESS_MATRICES:
        return (r, g, b)
    
    matrix = COLOR_BLINDNESS_MATRICES[blindness_type]
    new_r = int(min(255, max(0, matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b)))
    new_g = int(min(255, max(0, matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b)))
    new_b = int(min(255, max(0, matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b)))
    
    return (new_r, new_g, new_b)

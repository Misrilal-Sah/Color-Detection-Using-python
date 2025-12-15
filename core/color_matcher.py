"""
Color Matcher Module
Uses KNN algorithm to find the closest named color from the database
"""

import json
import os
import numpy as np
from typing import Tuple, Dict, List, Optional
from sklearn.neighbors import KDTree


class ColorMatcher:
    """
    Matches RGB colors to their closest named color using KDTree for fast lookup.
    """
    
    def __init__(self, colors_file: str = None):
        """Initialize the color matcher with the color database."""
        if colors_file is None:
            # Get the path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            colors_file = os.path.join(base_dir, 'data', 'colors.json')
        
        self.colors = []
        self.color_names = []
        self.color_hex = []
        self._load_colors(colors_file)
        self._build_tree()
    
    def _load_colors(self, colors_file: str):
        """Load colors from the JSON database."""
        try:
            with open(colors_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for color in data['colors']:
                    self.colors.append(color['rgb'])
                    self.color_names.append(color['name'])
                    self.color_hex.append(color['hex'])
        except FileNotFoundError:
            # Use a minimal fallback color set
            self._use_fallback_colors()
    
    def _use_fallback_colors(self):
        """Use fallback colors if database is not found."""
        fallback = [
            {"name": "Black", "rgb": [0, 0, 0], "hex": "#000000"},
            {"name": "White", "rgb": [255, 255, 255], "hex": "#FFFFFF"},
            {"name": "Red", "rgb": [255, 0, 0], "hex": "#FF0000"},
            {"name": "Green", "rgb": [0, 255, 0], "hex": "#00FF00"},
            {"name": "Blue", "rgb": [0, 0, 255], "hex": "#0000FF"},
            {"name": "Yellow", "rgb": [255, 255, 0], "hex": "#FFFF00"},
            {"name": "Cyan", "rgb": [0, 255, 255], "hex": "#00FFFF"},
            {"name": "Magenta", "rgb": [255, 0, 255], "hex": "#FF00FF"},
            {"name": "Gray", "rgb": [128, 128, 128], "hex": "#808080"},
            {"name": "Orange", "rgb": [255, 165, 0], "hex": "#FFA500"},
            {"name": "Purple", "rgb": [128, 0, 128], "hex": "#800080"},
            {"name": "Pink", "rgb": [255, 192, 203], "hex": "#FFC0CB"},
            {"name": "Brown", "rgb": [165, 42, 42], "hex": "#A52A2A"},
        ]
        for color in fallback:
            self.colors.append(color['rgb'])
            self.color_names.append(color['name'])
            self.color_hex.append(color['hex'])
    
    def _build_tree(self):
        """Build KDTree for fast nearest neighbor lookup."""
        self.color_array = np.array(self.colors)
        self.tree = KDTree(self.color_array)
    
    def find_closest_color(self, r: int, g: int, b: int, k: int = 1) -> Dict:
        """
        Find the closest named color to the given RGB values.
        
        Args:
            r, g, b: RGB values (0-255)
            k: Number of closest colors to consider
        
        Returns:
            Dictionary with color info including name, hex, rgb, and confidence
        """
        query = np.array([[r, g, b]])
        distances, indices = self.tree.query(query, k=k)
        
        idx = indices[0][0]
        distance = distances[0][0]
        
        # Calculate confidence based on distance (closer = higher confidence)
        # Max possible distance in RGB space is sqrt(3 * 255^2) ≈ 441.67
        max_distance = 441.67
        confidence = max(0, (1 - (distance / max_distance))) * 100
        
        return {
            'name': self.color_names[idx],
            'hex': self.color_hex[idx],
            'rgb': tuple(self.colors[idx]),
            'input_rgb': (r, g, b),
            'distance': float(distance),
            'confidence': round(confidence, 1)
        }
    
    def find_multiple_matches(self, r: int, g: int, b: int, count: int = 5) -> List[Dict]:
        """
        Find multiple closest named colors.
        
        Args:
            r, g, b: RGB values (0-255)
            count: Number of matches to return
        
        Returns:
            List of color info dictionaries
        """
        query = np.array([[r, g, b]])
        distances, indices = self.tree.query(query, k=min(count, len(self.colors)))
        
        max_distance = 441.67
        results = []
        
        for i in range(len(indices[0])):
            idx = indices[0][i]
            distance = distances[0][i]
            confidence = max(0, (1 - (distance / max_distance))) * 100
            
            results.append({
                'name': self.color_names[idx],
                'hex': self.color_hex[idx],
                'rgb': tuple(self.colors[idx]),
                'distance': float(distance),
                'confidence': round(confidence, 1)
            })
        
        return results
    
    def search_by_name(self, name: str) -> Optional[Dict]:
        """
        Search for a color by name (case-insensitive).
        
        Args:
            name: Color name to search for
        
        Returns:
            Color info dictionary or None if not found
        """
        name_lower = name.lower()
        for i, color_name in enumerate(self.color_names):
            if color_name.lower() == name_lower:
                return {
                    'name': color_name,
                    'hex': self.color_hex[i],
                    'rgb': tuple(self.colors[i])
                }
        return None
    
    def get_all_colors(self) -> List[Dict]:
        """Get all colors in the database."""
        return [
            {
                'name': self.color_names[i],
                'hex': self.color_hex[i],
                'rgb': tuple(self.colors[i])
            }
            for i in range(len(self.colors))
        ]


# Global instance for convenience
_matcher_instance = None

def get_color_matcher() -> ColorMatcher:
    """Get or create the global ColorMatcher instance."""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = ColorMatcher()
    return _matcher_instance


def match_color(r: int, g: int, b: int) -> Dict:
    """Convenience function to match a color using the global matcher."""
    return get_color_matcher().find_closest_color(r, g, b)

"""
Color Detector Module
Handles image processing and color extraction using OpenCV
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict, Optional
from sklearn.cluster import KMeans


class ColorDetector:
    """
    Detects and extracts colors from images using OpenCV and K-Means clustering.
    """
    
    def __init__(self):
        """Initialize the color detector."""
        self.current_image = None
        self.original_image = None
    
    def load_image(self, image_path: str) -> bool:
        """
        Load an image from file.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.original_image = cv2.imread(image_path)
            if self.original_image is None:
                return False
            self.current_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            return True
        except Exception:
            return False
    
    def load_from_array(self, image_array: np.ndarray, is_bgr: bool = True) -> bool:
        """
        Load an image from a numpy array.
        
        Args:
            image_array: Image as numpy array
            is_bgr: Whether the image is in BGR format (OpenCV default)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.original_image = image_array.copy()
            if is_bgr:
                self.current_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            else:
                self.current_image = image_array.copy()
            return True
        except Exception:
            return False
    
    def get_color_at_point(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """
        Get the RGB color at a specific point in the image.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Tuple of (R, G, B) values or None if out of bounds
        """
        if self.current_image is None:
            return None
        
        height, width = self.current_image.shape[:2]
        
        if 0 <= x < width and 0 <= y < height:
            pixel = self.current_image[y, x]
            return tuple(int(c) for c in pixel)
        return None
    
    def get_average_color_in_region(self, x: int, y: int, radius: int = 5) -> Optional[Tuple[int, int, int]]:
        """
        Get the average color in a circular region around a point.
        
        Args:
            x: Center X coordinate
            y: Center Y coordinate
            radius: Radius of the region
        
        Returns:
            Tuple of (R, G, B) values or None
        """
        if self.current_image is None:
            return None
        
        height, width = self.current_image.shape[:2]
        
        # Create a mask for the circular region
        y_min = max(0, y - radius)
        y_max = min(height, y + radius + 1)
        x_min = max(0, x - radius)
        x_max = min(width, x + radius + 1)
        
        region = self.current_image[y_min:y_max, x_min:x_max]
        
        if region.size == 0:
            return None
        
        # Calculate average color
        avg_color = np.mean(region, axis=(0, 1))
        return tuple(int(c) for c in avg_color)
    
    def extract_dominant_colors(self, n_colors: int = 5, sample_size: int = 10000) -> List[Dict]:
        """
        Extract the dominant colors from the image using K-Means clustering.
        
        Args:
            n_colors: Number of dominant colors to extract
            sample_size: Number of pixels to sample for performance
        
        Returns:
            List of dictionaries with color info and percentage
        """
        if self.current_image is None:
            return []
        
        # Reshape image to be a list of pixels
        pixels = self.current_image.reshape(-1, 3)
        
        # Sample pixels if there are too many
        if len(pixels) > sample_size:
            indices = np.random.choice(len(pixels), sample_size, replace=False)
            pixels = pixels[indices]
        
        # Convert to float for K-Means
        pixels = pixels.astype(float)
        
        # Apply K-Means clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get cluster centers and labels
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_
        
        # Calculate percentage of each color
        unique, counts = np.unique(labels, return_counts=True)
        percentages = counts / len(labels) * 100
        
        # Create result list sorted by percentage
        results = []
        for i, (color, percentage) in enumerate(zip(colors, percentages)):
            results.append({
                'rgb': tuple(int(c) for c in color),
                'percentage': round(percentage, 1),
                'count': int(counts[i])
            })
        
        # Sort by percentage (most dominant first)
        results.sort(key=lambda x: x['percentage'], reverse=True)
        
        return results
    
    def get_color_histogram(self, bins: int = 16) -> Dict:
        """
        Get the color histogram of the image.
        
        Args:
            bins: Number of bins per channel
        
        Returns:
            Dictionary with histogram data for each channel
        """
        if self.current_image is None:
            return {}
        
        histograms = {}
        colors = ['red', 'green', 'blue']
        
        for i, color in enumerate(colors):
            hist = cv2.calcHist([self.current_image], [i], None, [bins], [0, 256])
            histograms[color] = hist.flatten().tolist()
        
        return histograms
    
    def normalize_lighting(self) -> bool:
        """
        Normalize the image lighting using CLAHE.
        
        Returns:
            True if successful, False otherwise
        """
        if self.current_image is None:
            return False
        
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2LAB)
            
            # Apply CLAHE to the L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            
            # Convert back to RGB
            self.current_image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            return True
        except Exception:
            return False
    
    def get_image_size(self) -> Optional[Tuple[int, int]]:
        """Get the current image dimensions (width, height)."""
        if self.current_image is None:
            return None
        height, width = self.current_image.shape[:2]
        return (width, height)
    
    def get_rgb_image(self) -> Optional[np.ndarray]:
        """Get the current image in RGB format."""
        return self.current_image
    
    def get_bgr_image(self) -> Optional[np.ndarray]:
        """Get the current image in BGR format (for OpenCV operations)."""
        if self.current_image is None:
            return None
        return cv2.cvtColor(self.current_image, cv2.COLOR_RGB2BGR)
    
    def resize_for_display(self, max_width: int = 800, max_height: int = 600) -> Optional[np.ndarray]:
        """
        Resize the image to fit within the specified dimensions while maintaining aspect ratio.
        
        Args:
            max_width: Maximum width
            max_height: Maximum height
        
        Returns:
            Resized image or None
        """
        if self.current_image is None:
            return None
        
        height, width = self.current_image.shape[:2]
        
        # Calculate scaling factor
        scale_w = max_width / width
        scale_h = max_height / height
        scale = min(scale_w, scale_h, 1.0)  # Don't upscale
        
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            return cv2.resize(self.current_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return self.current_image.copy()


class CameraCapture:
    """
    Handles camera capture for live color detection.
    """
    
    def __init__(self, camera_id: int = 0):
        """
        Initialize camera capture.
        
        Args:
            camera_id: Camera device ID (default 0 for primary camera)
        """
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
    
    def start(self) -> bool:
        """
        Start the camera capture.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                return False
            
            # Set camera properties for better quality
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            self.is_running = True
            return True
        except Exception:
            return False
    
    def stop(self):
        """Stop the camera capture."""
        self.is_running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        Read a frame from the camera.
        
        Returns:
            Frame as numpy array in RGB format, or None
        """
        if self.cap is None or not self.is_running:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None
    
    def get_color_at_center(self, radius: int = 20) -> Optional[Tuple[int, int, int]]:
        """
        Get the average color at the center of the current frame.
        
        Args:
            radius: Radius of the center region to sample
        
        Returns:
            Tuple of (R, G, B) values or None
        """
        frame = self.read_frame()
        if frame is None:
            return None
        
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Extract center region
        y_min = max(0, center_y - radius)
        y_max = min(height, center_y + radius)
        x_min = max(0, center_x - radius)
        x_max = min(width, center_x + radius)
        
        region = frame[y_min:y_max, x_min:x_max]
        avg_color = np.mean(region, axis=(0, 1))
        
        return tuple(int(c) for c in avg_color)
    
    def capture_snapshot(self) -> Optional[np.ndarray]:
        """
        Capture a snapshot from the camera.
        
        Returns:
            Frame as numpy array in RGB format, or None
        """
        return self.read_frame()
    
    def is_available(self) -> bool:
        """Check if the camera is available."""
        return self.cap is not None and self.cap.isOpened()
    
    def __del__(self):
        """Clean up camera resources."""
        self.stop()

import cv2
import numpy as np
from typing import List, Dict, Any

def extract_color_matrix(image_bytes: bytes, num_colors: int = 3) -> List[Dict[str, Any]]:
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        return []

    # Resize drastically for performance (colors remain relatively intact)
    img = cv2.resize(img, (100, 100), interpolation=cv2.INTER_AREA)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Flatten image into a list of pixels
    pixels = img.reshape((-1, 3))
    pixels = np.float32(pixels)

    # K-Means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    centers = np.uint8(centers)
    counts = np.bincount(labels.flatten())
    total_pixels = len(pixels)
    
    dominant_colors = []
    for i in range(num_colors):
        color = centers[i]
        hex_code = f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"
        percentage = round((counts[i] / total_pixels) * 100, 2)
        dominant_colors.append({
            "hex_code": hex_code,
            "percentage": percentage
        })
        
    # Sort from most dominant to least
    dominant_colors.sort(key=lambda x: x["percentage"], reverse=True)
    return dominant_colors
import cv2
import numpy as np

def extract_dominant_color(image_bytes: bytes) -> dict:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Invalid image payload structure")

    # Parity Calculation: Extract standard deviation for VDB complexity profiling
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, stddev = cv2.meanStdDev(gray)
    sigma = stddev[0][0]

    if sigma <= 15.0:
        analysis_label = "Solid"
    elif sigma <= 45.0:
        analysis_label = "Gradient"
    else:
        analysis_label = "Cluttered"

    # Color Extraction: K-Means Clustering
    pixels = np.float32(img.reshape(-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    
    _, labels, palette = cv2.kmeans(pixels, 1, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    _, counts = np.unique(labels, return_counts=True)
    
    dominant = palette[np.argmax(counts)]
    hex_str = f"#{int(dominant[2]):02x}{int(dominant[1]):02x}{int(dominant[0]):02x}"

    return {
        "hex_color": hex_str,
        "analysis": analysis_label
    }
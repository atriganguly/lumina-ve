import io
from PIL import Image
from typing import Dict, Any

def analyze_metadata(image_bytes: bytes) -> Dict[str, Any]:
    file_size = len(image_bytes)
    
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            width, height = img.size
            fmt = img.format or "UNKNOWN"
            mode = img.mode
            
            channels = 4 if mode == 'RGBA' else (1 if mode == 'L' else 3)
            raw_size = width * height * channels
            
            compression_ratio = round(raw_size / file_size, 2) if file_size > 0 else 0
            
            return {
                "file_size_bytes": file_size,
                "format": fmt,
                "dimensions": {"width": width, "height": height},
                "color_space": mode,
                "compression_ratio": f"{compression_ratio}:1"
            }
    except Exception:
        return {
            "file_size_bytes": file_size,
            "format": "ERROR",
            "dimensions": {"width": 0, "height": 0},
            "color_space": "ERROR",
            "compression_ratio": "0:1"
        }
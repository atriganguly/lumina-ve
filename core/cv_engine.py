import cv2
import numpy as np
import psutil
from typing import Dict, Any, Tuple, Optional
from infra.config import settings

def get_available_memory_mb() -> float:
    """Reads memory limits, accurately supporting containerized cgroups environments."""
    try:
        # Check cgroups v2 (Modern Docker/Render)
        with open("/sys/fs/cgroup/memory.max", "r") as f:
            mem_max_str = f.read().strip()
        if mem_max_str != "max":
            mem_max = int(mem_max_str)
            with open("/sys/fs/cgroup/memory.current", "r") as f:
                mem_current = int(f.read().strip())
            return (mem_max - mem_current) / (1024 * 1024)
    except Exception:
        pass
    
    try:
        # Check cgroups v1 (Older Docker)
        with open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "r") as f:
            mem_max = int(f.read().strip())
        if mem_max < 9223372036854771712: # Avoid 'no limit' default max value
            with open("/sys/fs/cgroup/memory/memory.usage_in_bytes", "r") as f:
                mem_current = int(f.read().strip())
            return (mem_max - mem_current) / (1024 * 1024)
    except Exception:
        pass

    # Fallback to standard Host OS Memory
    vm = psutil.virtual_memory()
    return vm.available / (1024 * 1024)

def analyze_compliance(image_bytes: bytes) -> Tuple[Dict[str, Any], Optional[str]]:
    # 1. Decode image for OpenCV
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not decode image for CV processing")

    total_pixels = img.shape[0] * img.shape[1]

    # 2. Blur Detection (Laplacian Variance - Lightweight, runs regardless of config)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    is_blurry = variance < 100.0
    
    compliance_data = {
        "is_blurry": bool(is_blurry),
        "blur_variance_score": round(variance, 2),
        "is_amazon_compliant": None,
        "pure_white_background_percentage": None,
        "foreground_to_background_ratio": None,
        "bounding_box_padding_pct": None
    }

    # 3. Environment Toggle Check
    if not settings.ENABLE_HEAVY_ML:
        return compliance_data, "BACKGROUND_COMPLIANCE_SKIPPED: Feature disabled via ENABLE_HEAVY_ML environment configuration."

    # 4. Memory Check before Heavy ML Operations
    available_mb = get_available_memory_mb()
    if available_mb < settings.MIN_RAM_REQUIRED_MB:
        warning_msg = f"BACKGROUND_COMPLIANCE_SKIPPED: Insufficient container memory (Available: {available_mb:.0f}MB, Required: {settings.MIN_RAM_REQUIRED_MB}MB)."
        return compliance_data, warning_msg

    # 5. Background Removal using rembg (Lazy Loaded)
    try:
        from rembg import remove
        output_bgra = remove(image_bytes)
        output_np = np.frombuffer(output_bgra, np.uint8)
        rgba_img = cv2.imdecode(output_np, cv2.IMREAD_UNCHANGED)
        
        if rgba_img is not None and rgba_img.shape[2] == 4:
            alpha_channel = rgba_img[:, :, 3]
        else:
            alpha_channel = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255

        # Computations
        foreground_pixels = cv2.countNonZero(alpha_channel)
        fg_bg_ratio = foreground_pixels / total_pixels if total_pixels > 0 else 0

        bg_mask = cv2.bitwise_not(alpha_channel)
        bg_pixels = cv2.bitwise_and(img, img, mask=bg_mask)
        
        lower_white = np.array([250, 250, 250], dtype=np.uint8)
        upper_white = np.array([255, 255, 255], dtype=np.uint8)
        white_mask = cv2.inRange(bg_pixels, lower_white, upper_white)
        
        total_bg_pixels = total_pixels - foreground_pixels
        pure_white_pixels = cv2.countNonZero(white_mask)
        white_bg_pct = (pure_white_pixels / total_bg_pixels * 100) if total_bg_pixels > 0 else 100.0

        x, y, w, h = cv2.boundingRect(alpha_channel)
        canvas_w, canvas_h = img.shape[1], img.shape[0]
        
        padding_x = ((canvas_w - w) / canvas_w) * 100 if canvas_w > 0 else 0
        padding_y = ((canvas_h - h) / canvas_h) * 100 if canvas_h > 0 else 0
        avg_padding = (padding_x + padding_y) / 2

        is_amazon_compliant = (white_bg_pct > 95.0) and (not is_blurry) and (10.0 <= avg_padding <= 25.0)

        compliance_data.update({
            "is_amazon_compliant": bool(is_amazon_compliant),
            "pure_white_background_percentage": round(white_bg_pct, 2),
            "foreground_to_background_ratio": round(fg_bg_ratio, 2),
            "bounding_box_padding_pct": round(avg_padding, 2)
        })

        return compliance_data, None

    except Exception as e:
        warning_msg = f"BACKGROUND_COMPLIANCE_FAILED: Background separation failed due to unexpected error: {str(e)}"
        return compliance_data, warning_msg
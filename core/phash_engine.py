import cv2
import numpy as np

def compute_phash(image_bytes: bytes) -> str:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise ValueError("Invalid image payload structure")

    resized = cv2.resize(img, (32, 32), interpolation=cv2.INTER_AREA)
    dct = cv2.dct(np.float32(resized))
    dctlowfreq = dct[:8, :8]
    
    med = np.median(dctlowfreq)
    diff = dctlowfreq > med
    
    hash_str = "".join("1" if bit else "0" for bit in diff.flatten())
    
    return hex(int(hash_str, 2))[2:].zfill(16)
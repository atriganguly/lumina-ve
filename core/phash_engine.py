import io
from PIL import Image
import imagehash

def generate_phash(image_bytes: bytes) -> str:
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Generate a 64-bit perceptual hash
            phash = imagehash.phash(img)
            return str(phash)
    except Exception:
        return "ERROR_GENERATING_HASH"
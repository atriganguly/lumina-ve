from fastapi import HTTPException
from urllib.parse import urlparse

def validate_image_url(url: str) -> str:
    """
    Validates that the provided URL is well-formed and uses a secure/standard scheme.
    Raises an HTTPException if the URL is invalid.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")
        
    parsed = urlparse(url)
    
    if parsed.scheme not in ["http", "https"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid URL scheme '{parsed.scheme}'. Only 'http' and 'https' are supported."
        )
        
    if not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL format. Hostname is missing.")
        
    return url
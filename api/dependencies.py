from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from urllib.parse import urlparse
import ipaddress
import asyncio
import socket
from infra.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key != settings.LUMINA_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key."
        )
    return api_key

async def validate_image_url(url: str) -> dict:
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
    
    # Async DNS Resolution to unblock event loop
    loop = asyncio.get_running_loop()
    try:
        # getaddrinfo returns: (family, type, proto, canonname, sockaddr)
        addr_info = await loop.getaddrinfo(parsed.hostname, None)
        ip = addr_info[0][4][0]
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Could not resolve hostname.")
    
    # SSRF Protection using the strictly resolved IP
    if settings.ENVIRONMENT != "dev":
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid URL. Resolution to internal/private IPs is forbidden in production."
                )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid IP address resolved.")
    
    # Return dict containing original url, hostname, and validated IP to prevent DNS rebinding
    return {
        "original_url": url,
        "hostname": parsed.hostname,
        "resolved_ip": ip,
        "scheme": parsed.scheme,
        "path": parsed.path or "/",
        "query": parsed.query
    }
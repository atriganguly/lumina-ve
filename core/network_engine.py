import httpx
import time
from typing import Tuple, Dict, Any
from fastapi import HTTPException
from infra.config import settings

async def fetch_and_analyze_network(safe_url_data: dict) -> Tuple[bytes, Dict[str, Any]]:
    hostname = safe_url_data["hostname"]
    ip_address = safe_url_data["resolved_ip"]
    geo_location = "Unknown"
    
    # 1. Geo-IP Fetch (strict 2.0s timeout to prevent hanging)
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            geo_resp = await client.get(f"https://freeipapi.com/api/json/{ip_address}")
            if geo_resp.status_code == 200:
                geo_data = geo_resp.json()
                geo_location = f"{geo_data.get('cityName', 'Unknown')}, {geo_data.get('countryCode', 'Unknown')}"
    except Exception:
        pass # Silently fail GeoIP to prioritize the core application payload
    
    # 2. Image Download with DNS Rebinding prevention (use IP directly, pass Host header)
    start_time = time.perf_counter()
    image_bytes = bytearray()
    
    # Reconstruct URL using IP for transport, preserving scheme and path
    query_str = f"?{safe_url_data['query']}" if safe_url_data['query'] else ""
    transport_url = f"{safe_url_data['scheme']}://{ip_address}{safe_url_data['path']}{query_str}"
    headers = {"Host": hostname}
    
    async with httpx.AsyncClient(timeout=settings.FETCH_TIMEOUT_SECONDS, verify=False) as client:
        try:
            async with client.stream("GET", transport_url, headers=headers) as response:
                response.raise_for_status()
                ttfb = (time.perf_counter() - start_time) * 1000
                
                # Stream the download to enforce max file size and prevent OOM DoS
                async for chunk in response.aiter_bytes():
                    image_bytes.extend(chunk)
                    if len(image_bytes) > settings.MAX_FILE_SIZE_BYTES:
                        raise HTTPException(
                            status_code=413, 
                            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
                        )
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Network request failed: {str(e)}")
    
    total_time = (time.perf_counter() - start_time) * 1000
    
    network_data = {
        "status_code": response.status_code,
        "is_alive": response.status_code == 200,
        "dns_resolution_ip": ip_address,
        "ttfb_ms": round(ttfb, 2),
        "download_duration_ms": round(total_time, 2),
        "geo_location": geo_location
    }
    
    return bytes(image_bytes), network_data
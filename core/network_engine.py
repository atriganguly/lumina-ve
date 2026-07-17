import httpx
import time
import socket
from urllib.parse import urlparse
from typing import Tuple, Dict, Any

async def fetch_and_analyze_network(url: str) -> Tuple[bytes, Dict[str, Any]]:
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    
    ip_address = None
    geo_location = "Unknown"
    
    try:
        ip_address = socket.gethostbyname(hostname)
        async with httpx.AsyncClient() as client:
            geo_resp = await client.get(f"http://ip-api.com/json/{ip_address}")
            if geo_resp.status_code == 200:
                geo_data = geo_resp.json()
                geo_location = f"{geo_data.get('city', 'Unknown')}, {geo_data.get('countryCode', 'Unknown')}"
    except Exception:
        pass

    start_time = time.perf_counter()
    
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            ttfb = (time.perf_counter() - start_time) * 1000
            
            image_bytes = await response.aread()
            total_time = (time.perf_counter() - start_time) * 1000
            
            network_data = {
                "status_code": response.status_code,
                "is_alive": response.status_code == 200,
                "dns_resolution_ip": ip_address,
                "ttfb_ms": round(ttfb, 2),
                "download_duration_ms": round(total_time, 2),
                "geo_location": geo_location
            }
            
            return image_bytes, network_data
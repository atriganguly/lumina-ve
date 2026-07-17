from pydantic import BaseModel
from typing import Dict, Optional, List

class ValidationRequest(BaseModel):
    url: str

class NetworkIntelligence(BaseModel):
    status_code: int
    is_alive: bool
    dns_resolution_ip: Optional[str]
    ttfb_ms: float
    download_duration_ms: float
    geo_location: Optional[str]

class AssetProperties(BaseModel):
    file_size_bytes: int
    format: str
    dimensions: Dict[str, int]
    color_space: str
    compression_ratio: str

class MarketplaceCompliance(BaseModel):
    is_blurry: bool
    blur_variance_score: float
    is_amazon_compliant: Optional[bool] = None
    pure_white_background_percentage: Optional[float] = None
    foreground_to_background_ratio: Optional[float] = None
    bounding_box_padding_pct: Optional[float] = None

class DominantColor(BaseModel):
    hex_code: str
    percentage: float

class ContentIntelligence(BaseModel):
    perceptual_hash: str
    dominant_colors: List[DominantColor]

class ValidationResponse(BaseModel):
    url: str
    status: str
    system_warnings: Optional[List[str]] = None
    network_intelligence: NetworkIntelligence
    asset_properties: AssetProperties
    marketplace_compliance: MarketplaceCompliance
    content_intelligence: ContentIntelligence
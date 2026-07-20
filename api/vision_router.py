import asyncio
from fastapi import APIRouter, HTTPException, Depends
from api.schemas import ValidationRequest, ValidationResponse
from api.dependencies import validate_image_url, verify_api_key
from core.network_engine import fetch_and_analyze_network
from core.metadata_engine import analyze_metadata
from core.cv_engine import analyze_compliance
from core.phash_engine import generate_phash
from core.color_matrix import extract_color_matrix

# Initialize the router and inject the API Key dependency globally for these routes
router = APIRouter(
    prefix="/v1/vision", 
    tags=["Vision Analysis"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("/validate/url", response_model=ValidationResponse)
async def validate_image_url_endpoint(request: ValidationRequest):
    try:
        # 0. Pre-Flight Security Check: Validate URL schema and asynchronously resolve IP for SSRF defense
        safe_url_data = await validate_image_url(request.url)
        
        # 1. Fetch & Network Intelligence
        image_bytes, network_data = await fetch_and_analyze_network(safe_url_data)
        
        if not network_data["is_alive"]:
            raise HTTPException(status_code=400, detail="Image URL is unreachable or returned non-200 status.")
            
        # 2. Metadata Extraction (Lightweight)
        asset_data = analyze_metadata(image_bytes)
        
        # 3. Offload Heavy/Blocking Operations to Thread Pool to unblock the Event Loop
        loop = asyncio.get_running_loop()
        
        compliance_data, cv_warning = await loop.run_in_executor(None, analyze_compliance, image_bytes)
        phash_value = await loop.run_in_executor(None, generate_phash, image_bytes)
        dominant_colors, color_warning = await loop.run_in_executor(None, extract_color_matrix, image_bytes)
        
        # 4. Formulate System Warnings
        system_warnings = []
        if cv_warning:
            system_warnings.append(cv_warning)
        if color_warning:
            system_warnings.append(color_warning)
            
        # 5. Formulate Response Status
        status = "PARTIAL_SUCCESS" if system_warnings else "VALIDATION_PASSED"
        
        return ValidationResponse(
            url=safe_url_data["original_url"],
            status=status,
            system_warnings=system_warnings if system_warnings else None,
            network_intelligence=network_data,
            asset_properties=asset_data,
            marketplace_compliance=compliance_data,
            content_intelligence={
                "perceptual_hash": phash_value,
                "dominant_colors": dominant_colors
            }
        )
        
    except HTTPException as he:
        # Re-raise standard HTTPExceptions to preserve their specific status codes (e.g., 400 Bad Request)
        raise he
    except Exception as e:
        # Catch any unhandled engine exceptions as 500 Internal Server Errors
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
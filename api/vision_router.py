from fastapi import APIRouter, HTTPException
from api.schemas import ValidationRequest, ValidationResponse
from api.dependencies import validate_image_url
from core.network_engine import fetch_and_analyze_network
from core.metadata_engine import analyze_metadata
from core.cv_engine import analyze_compliance
from core.phash_engine import generate_phash
from core.color_matrix import extract_color_matrix

# Initialize the router
router = APIRouter(prefix="/v1/vision", tags=["Vision Analysis"])

@router.post("/validate/url", response_model=ValidationResponse)
async def validate_image_url_endpoint(request: ValidationRequest):
    try:
        # 0. Pre-Flight Security Check: Validate URL schema
        safe_url = validate_image_url(request.url)

        # 1. Fetch & Network Intelligence
        image_bytes, network_data = await fetch_and_analyze_network(safe_url)
        
        if not network_data["is_alive"]:
            raise HTTPException(status_code=400, detail="Image URL is unreachable or returned non-200 status.")

        # 2. Metadata Extraction
        asset_data = analyze_metadata(image_bytes)

        # 3. CV & Compliance Engine (with memory fallback)
        compliance_data, warning_msg = analyze_compliance(image_bytes)

        # 4. Content Intelligence (Legacy Engines Re-integrated)
        phash_value = generate_phash(image_bytes)
        dominant_colors = extract_color_matrix(image_bytes)

        # 5. Formulate Response Status
        status = "PARTIAL_SUCCESS" if warning_msg else "VALIDATION_PASSED"
        system_warnings = [warning_msg] if warning_msg else None

        return ValidationResponse(
            url=safe_url,
            status=status,
            system_warnings=system_warnings,
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
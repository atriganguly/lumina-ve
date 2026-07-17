from fastapi import APIRouter, HTTPException
from api.schemas import ValidationRequest, ValidationResponse
from api.dependencies import validate_image_url
from core.network_engine import fetch_and_analyze_network
from core.metadata_engine import analyze_metadata
from core.cv_engine import analyze_compliance
from core.phash_engine import generate_phash
from core.color_matrix import extract_color_matrix

# Initialize the router
router = APIRouter(prefix="/v1/vision", tags=["Vision Analysis"])[cite: 2]

@router.post("/validate/url", response_model=ValidationResponse)[cite: 2]
async def validate_image_url_endpoint(request: ValidationRequest):[cite: 2]
    try:
        # 0. Pre-Flight Security Check: Validate URL schema
        safe_url = validate_image_url(request.url)

        # 1. Fetch & Network Intelligence[cite: 2]
        image_bytes, network_data = await fetch_and_analyze_network(safe_url)[cite: 2]
        
        if not network_data["is_alive"]:[cite: 2]
            raise HTTPException(status_code=400, detail="Image URL is unreachable or returned non-200 status.")[cite: 2]

        # 2. Metadata Extraction[cite: 2]
        asset_data = analyze_metadata(image_bytes)[cite: 2]

        # 3. CV & Compliance Engine (with memory fallback)[cite: 2]
        compliance_data, warning_msg = analyze_compliance(image_bytes)[cite: 2]

        # 4. Content Intelligence (Legacy Engines Re-integrated)[cite: 2]
        phash_value = generate_phash(image_bytes)[cite: 2]
        dominant_colors = extract_color_matrix(image_bytes)[cite: 2]

        # 5. Formulate Response Status
        status = "PARTIAL_SUCCESS" if warning_msg else "VALIDATION_PASSED"[cite: 2]
        system_warnings = [warning_msg] if warning_msg else None[cite: 2]

        return ValidationResponse([cite: 2]
            url=safe_url,[cite: 2]
            status=status,[cite: 2]
            system_warnings=system_warnings,[cite: 2]
            network_intelligence=network_data,[cite: 2]
            asset_properties=asset_data,[cite: 2]
            marketplace_compliance=compliance_data,[cite: 2]
            content_intelligence={[cite: 2]
                "perceptual_hash": phash_value,[cite: 2]
                "dominant_colors": dominant_colors[cite: 2]
            }
        )

    except HTTPException as he:[cite: 2]
        # Re-raise standard HTTPExceptions to preserve their specific status codes (e.g., 400 Bad Request)
        raise he[cite: 2]
    except Exception as e:[cite: 2]
        # Catch any unhandled engine exceptions as 500 Internal Server Errors
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")[cite: 2]
import asyncio
from concurrent.futures import ProcessPoolExecutor
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from api.dependencies import verify_access_token
from api.schemas import ColorResponse, PHashResponse
from core.color_matrix import extract_dominant_color
from core.phash_engine import compute_phash

router = APIRouter(dependencies=[Depends(verify_access_token)])
pool = ProcessPoolExecutor(max_workers=4)

@router.post("/analyze-background", response_model=ColorResponse)
async def analyze_background(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    try:
        loop = asyncio.get_running_loop()
        # Dispatches the dictionary response directly from the process worker thread
        result = await loop.run_in_executor(pool, extract_dominant_color, image_bytes)
        return ColorResponse(hex_color=result["hex_color"], analysis=result["analysis"])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

@router.post("/compute-phash", response_model=PHashResponse)
async def process_phash(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    try:
        loop = asyncio.get_running_loop()
        phash_val = await loop.run_in_executor(pool, compute_phash, image_bytes)
        return PHashResponse(phash=phash_val)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
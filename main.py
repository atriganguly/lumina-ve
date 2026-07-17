import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.vision_router import router as vision_router
from api.schemas import HealthResponse
from infra.config import config

app = FastAPI(title="Lumina VE", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vision_router, prefix="/api/v1")

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ONLINE", engine="Lumina-V8")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.port, log_level="info", workers=1)
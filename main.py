from fastapi import FastAPI
from api.vision_router import router as vision_router

app = FastAPI(
    title="Lumina-VE God-Tier Validator",
    description="Marketplace Image Validation & Performance Intelligence Tool",
    version="2.0.0"
)

app.include_router(vision_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
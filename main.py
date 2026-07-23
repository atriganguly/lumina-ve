from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from api.vision_router import router as vision_router
from infra.config import settings

app = FastAPI(
    title="Lumina VE",
    description="Marketplace Image Validation & Performance Intelligence Tool",
    version="1.0.0"
)

# Attach Core Vision Router
app.include_router(vision_router)

# Resolve Base Directory & Static Asset Paths
BASE_DIR = Path(__file__).resolve().parent
DOCS_INDEX_PATH = BASE_DIR / "docs" / "index.html"
README_PATH = BASE_DIR / "README.md"
ICON_PATH = BASE_DIR / "docs" / "icon.png"

@app.get("/health")
async def health_check():
    """
    Real-time health check probe for uptime monitoring and container probes.
    """
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/demo", response_class=HTMLResponse)
async def render_demo_page():
    """
    Serves the executive demo UI from docs/index.html with auto-injected authentication credentials.
    """
    if not DOCS_INDEX_PATH.exists():
        raise HTTPException(
            status_code=404, 
            detail="Demo page template not found at docs/index.html"
        )
    
    with open(DOCS_INDEX_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Inject active API key into frontend client script for friction-free executive testing
    return html_content.replace("{{ DEFAULT_API_KEY }}", settings.LUMINA_API_KEY)

@app.get("/README.md")
async def get_readme():
    """
    Serves the root README.md file directly for dynamic frontend rendering.
    """
    if not README_PATH.exists():
        raise HTTPException(
            status_code=404, 
            detail="README.md documentation file not found on server."
        )
    return FileResponse(README_PATH, media_type="text/markdown")

@app.get("/docs/icon.png")
@app.get("/favicon.ico")
async def get_app_icon():
    """
    Serves the Swagger UI icon for the browser favicon and topbar header logo.
    """
    if not ICON_PATH.exists():
        raise HTTPException(
            status_code=404, 
            detail="Icon file not found at docs/icon.png"
        )
    return FileResponse(ICON_PATH, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
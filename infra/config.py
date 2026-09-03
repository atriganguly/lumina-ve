import os
from pathlib import Path

# Load .env file into os.environ if it exists locally
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

class Config:
    PROJECT_NAME = "Lumina-VE"
    VERSION = "1.0.0"
    
    # Environment toggle: 'dev' or 'production'
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    
    # Feature Toggles
    ENABLE_HEAVY_ML = os.getenv("ENABLE_HEAVY_ML", "True").lower() in ("true", "1", "yes")
    
    # API Authentication
    LUMINA_API_KEY = os.getenv("LUMINA_API_KEY")

    if not LUMINA_API_KEY:
        raise ValueError("LUMINA_API_KEY environment variable is missing! It must be provided in all environments.")
    
    # ML & CV Settings
    MIN_RAM_REQUIRED_MB = int(os.getenv("MIN_RAM_REQUIRED_MB", 400))
    
    # Network Settings
    FETCH_TIMEOUT_SECONDS = int(os.getenv("FETCH_TIMEOUT_SECONDS", 15))
    MAX_FILE_SIZE_BYTES = int(os.getenv("MAX_FILE_SIZE_BYTES", 25 * 1024 * 1024)) # 25 MB

settings = Config()
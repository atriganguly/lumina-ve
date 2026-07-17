import os

class Config:
    PROJECT_NAME = "Lumina-VE God-Tier Validator"
    VERSION = "2.0.0"
    
    # ML & CV Settings
    MIN_RAM_REQUIRED_MB = int(os.getenv("MIN_RAM_REQUIRED_MB", 400))
    
    # Network Settings
    FETCH_TIMEOUT_SECONDS = int(os.getenv("FETCH_TIMEOUT_SECONDS", 15))

settings = Config()
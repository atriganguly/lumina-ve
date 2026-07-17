from fastapi import Header, HTTPException, status
from infra.config import config

def verify_access_token(authorization: str = Header(...)) -> bool:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed authorization header"
        )
        
    token = authorization.split(" ")[1]
    
    if token != config.lumina_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid cryptographic token"
        )
        
    return True
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    engine: str

class ColorResponse(BaseModel):
    hex_color: str

class PHashResponse(BaseModel):
    phash: str
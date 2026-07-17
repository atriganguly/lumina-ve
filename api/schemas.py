from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    engine: str

class ColorResponse(BaseModel):
    hex_color: str
    analysis: str

class PHashResponse(BaseModel):
    phash: str
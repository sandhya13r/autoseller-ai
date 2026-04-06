# schemas/item_schema.py
from pydantic import BaseModel
from typing import Optional, List

class ItemUploadRequest(BaseModel):
    seller_id:   str
    description: Optional[str] = None

class ItemAnalysisResponse(BaseModel):
    item_id:       str
    title:         str
    brand:         str
    model:         str
    category:      str
    condition:     str
    estimated_price: float
    min_price:     float
    max_price:     float
    key_features:  List[str]
    selling_points: List[str]
    defects:       List[str]
    confidence:    float
    state:         str

class ListingResponse(BaseModel):
    item_id:         str
    title:           str
    description:     str
    tags:            List[str]
    asking_price:    float
    platform:        str
    platform_url:    str
    agent_chat_url:  str
    state:           str
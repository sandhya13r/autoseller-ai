# schemas/negotiation_schema.py
from pydantic import BaseModel
from typing import Optional

class OfferRequest(BaseModel):
    item_id:      str
    offer_amount: float
    buyer_name:   Optional[str] = None
    buyer_phone:  Optional[str] = None

class CounterOfferResponse(BaseModel):
    action:        str
    counter_price: Optional[float] = None
    message:       str
    explanation:   Optional[str]   = None
    risk_level:    Optional[str]   = None

class DealConfirmRequest(BaseModel):
    item_id:     str
    final_price: float
    buyer_name:  str
    buyer_phone: str
    buyer_email: Optional[str] = None

class DealConfirmResponse(BaseModel):
    success:     bool
    item_id:     str
    final_price: float
    message:     str
    state:       str
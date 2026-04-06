# schemas/payment_schema.py
from pydantic import BaseModel
from typing import Optional

class PaymentCreateRequest(BaseModel):
    item_id: str

class PaymentCreateResponse(BaseModel):
    success:   bool
    order_id:  Optional[str]   = None
    amount:    Optional[float] = None
    currency:  Optional[str]   = None
    key_id:    Optional[str]   = None
    item_id:   Optional[str]   = None
    error:     Optional[str]   = None

class PaymentConfirmRequest(BaseModel):
    item_id:    str
    payment_id: str
    order_id:   str
    signature:  Optional[str] = None

class PaymentConfirmResponse(BaseModel):
    success:    bool
    payment_id: Optional[str] = None
    message:    str
# schemas/chat_schema.py
from pydantic import BaseModel
from typing import Optional

class BuyerMessageRequest(BaseModel):
    item_id:  str
    message:  str
    buyer_id: Optional[str] = None

class AgentReplyResponse(BaseModel):
    message:       str
    type:          str
    counter_price: Optional[float] = None
    final_price:   Optional[float] = None
    explanation:   Optional[str]   = None

class BuyerContactRequest(BaseModel):
    item_id: str
    name:    str
    phone:   str
    email:   Optional[str] = None

class ChatHistoryResponse(BaseModel):
    item_id:  str
    messages: list
    state:    str
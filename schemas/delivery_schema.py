# schemas/delivery_schema.py
from pydantic import BaseModel
from typing import Optional, List

class PickupScheduleRequest(BaseModel):
    item_id:          str
    selected_slot:    str
    seller_address:   str
    seller_city:      str
    seller_pincode:   str
    seller_state:     str

class ShipmentResponse(BaseModel):
    success:            bool
    awb:                Optional[str] = None
    courier:            Optional[str] = None
    tracking_url:       Optional[str] = None
    estimated_delivery: Optional[str] = None
    message:            str

class TrackingResponse(BaseModel):
    status:            str
    label:             str
    description:       str
    icon:              str
    current_stage:     int
    total_stages:      int
    timeline:          list
    awb:               Optional[str] = None
    courier:           Optional[str] = None
    estimated_delivery: Optional[str] = None
    is_delivered:      bool
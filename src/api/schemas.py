from pydantic import BaseModel, Field
from typing import Optional

class CancellationInput(BaseModel):
    hotel: str
    lead_time: int = Field(45, ge=0, le=800)
    arrival_date_week_number: int = Field(28, ge=1, le=53)
    stays_in_weekend_nights: int = Field(1, ge=0, le=50)
    stays_in_week_nights: int = Field(3, ge=0, le=50)
    adults: int = Field(2, ge=1, le=20)
    children: int = Field(0, ge=0, le=20)
    market_segment: str
    distribution_channel: str
    deposit_type: str
    customer_type: str
    reserved_room_type: Optional[str] = "A"
    previous_cancellations: Optional[int] = 0
    booking_changes: Optional[int] = 0
    days_in_waiting_list: Optional[int] = 0
    adr: Optional[float] = 100.0

class CancellationResponse(BaseModel):
    is_canceled_prediction: int
    cancellation_probability: float
    risk_level: str
    recommendation: str

class PriceInput(BaseModel):
    hotel: str
    lead_time: int = Field(45, ge=0, le=800)
    arrival_date_week_number: int = Field(28, ge=1, le=53)
    stays_in_weekend_nights: int = Field(1, ge=0, le=50)
    stays_in_week_nights: int = Field(3, ge=0, le=50)
    adults: int = Field(2, ge=1, le=20)
    children: int = Field(0, ge=0, le=20)
    market_segment: str
    distribution_channel: str
    deposit_type: Optional[str] = "No Deposit"
    customer_type: str
    reserved_room_type: str
    previous_cancellations: Optional[int] = 0
    booking_changes: Optional[int] = 0
    days_in_waiting_list: Optional[int] = 0
    adr: Optional[float] = 100.0

class PriceResponse(BaseModel):
    predicted_adr: float
    total_nights: int
    estimated_total_stay_price: float
    currency: str = "EUR"
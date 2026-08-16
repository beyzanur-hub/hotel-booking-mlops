from pydantic import BaseModel, Field
from typing import Literal

# Sınıflandırma (İptal Tahmini) için Girdi Şeması
class CancellationInput(BaseModel):
    lead_time: int = Field(..., ge=0, le=800, description="Rezervasyon ile varış arasındaki gün sayısı", example=45)
    arrival_date_week_number: int = Field(..., ge=1, le=53, description="Yılın kaçıncı haftası giriş yapılacak", example=28)
    stays_in_weekend_nights: int = Field(..., ge=0, le=20, example=1)
    stays_in_week_nights: int = Field(..., ge=0, le=50, example=3)
    adults: int = Field(..., ge=1, le=10, example=2)
    children: int = Field(0, ge=0, le=10, example=0)
    previous_cancellations: int = Field(0, ge=0, le=50, example=0)
    booking_changes: int = Field(0, ge=0, le=20, example=0)
    days_in_waiting_list: int = Field(0, ge=0, le=500, example=0)
    adr: float = Field(100.0, ge=0.0, description="Referans ortalama gecelik fiyat", example=95.5)
    hotel: Literal["City Hotel", "Resort Hotel"] = "City Hotel"
    market_segment: Literal["Online TA", "Offline TA/TO", "Direct", "Corporate", "Groups", "Complementary"] = "Online TA"
    distribution_channel: Literal["TA/TO", "Direct", "Corporate", "GDS"] = "TA/TO"
    deposit_type: Literal["No Deposit", "Non Refund", "Refundable"] = "No Deposit"
    customer_type: Literal["Transient", "Transient-Party", "Contract", "Group"] = "Transient"

# Regresyon (Fiyat Tahmini) için Girdi Şeması
class PriceInput(BaseModel):
    lead_time: int = Field(..., ge=0, le=800, example=45)
    arrival_date_week_number: int = Field(..., ge=1, le=53, example=28)
    stays_in_weekend_nights: int = Field(..., ge=0, le=20, example=1)
    stays_in_week_nights: int = Field(..., ge=0, le=50, example=3)
    adults: int = Field(..., ge=1, le=10, example=2)
    children: int = Field(0, ge=0, le=10, example=0)
    booking_changes: int = Field(0, ge=0, le=20, example=0)
    hotel: Literal["City Hotel", "Resort Hotel"] = "City Hotel"
    market_segment: Literal["Online TA", "Offline TA/TO", "Direct", "Corporate", "Groups", "Complementary"] = "Online TA"
    distribution_channel: Literal["TA/TO", "Direct", "Corporate", "GDS"] = "TA/TO"
    reserved_room_type: Literal["A", "B", "C", "D", "E", "F", "G", "H", "L"] = "A"
    customer_type: Literal["Transient", "Transient-Party", "Contract", "Group"] = "Transient"

# API Yanıt (Response) Şemaları
class CancellationResponse(BaseModel):
    is_canceled_prediction: int
    cancellation_probability: float
    risk_level: str
    recommendation: str

class PriceResponse(BaseModel):
    predicted_adr: float
    total_nights: int
    estimated_total_stay_price: float
    currency: str = "EUR"
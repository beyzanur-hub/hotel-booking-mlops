import os
import sys
import pytest
from fastapi.testclient import TestClient

# Proje ana dizinini Python path'ine ekleyerek modül bulma hatasını kalıcı çözer
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.api.main import app, load_ml_models

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_models():
    """Testler başlamadan önce modelleri belleğe yükler"""
    load_ml_models()

def test_health_endpoint():
    """Health check endpoint'inin 200 OK ve doğru format döndüğünü doğrular"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"] is True

def test_cancellation_prediction_valid():
    """Geçerli bir iptal tahmini isteğinde 200 ve mantıklı metrikler dönmeli"""
    payload = {
        "lead_time": 100,
        "arrival_date_week_number": 25,
        "stays_in_weekend_nights": 1,
        "stays_in_week_nights": 2,
        "adults": 2,
        "children": 0,
        "previous_cancellations": 0,
        "booking_changes": 0,
        "days_in_waiting_list": 0,
        "adr": 100.0,
        "hotel": "City Hotel",
        "market_segment": "Online TA",
        "distribution_channel": "TA/TO",
        "deposit_type": "No Deposit",
        "customer_type": "Transient"
    }
    response = client.post("/predict/cancellation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "is_canceled_prediction" in data
    assert 0.0 <= data["cancellation_probability"] <= 1.0
    assert data["risk_level"] in ["High", "Low"]

def test_cancellation_prediction_invalid_input():
    """Hatalı veri tipi (örneğin kural dışı adults=0) gönderildiğinde 422 Unprocessable Entity dönmeli"""
    payload = {
        "lead_time": 10,
        "arrival_date_week_number": 20,
        "stays_in_weekend_nights": 1,
        "stays_in_week_nights": 1,
        "adults": 0,  # Pydantic şemasında ge=1 olarak kısıtlanmıştır
        "hotel": "City Hotel",
        "market_segment": "Online TA",
        "distribution_channel": "TA/TO",
        "deposit_type": "No Deposit",
        "customer_type": "Transient"
    }
    response = client.post("/predict/cancellation", json=payload)
    assert response.status_code == 422

def test_price_prediction_valid():
    """Geçerli bir fiyat tahmini isteğinde pozitif ADR ve doğru toplam hesap dönmeli"""
    payload = {
        "lead_time": 30,
        "arrival_date_week_number": 28,
        "stays_in_weekend_nights": 2,
        "stays_in_week_nights": 3,
        "adults": 2,
        "children": 1,
        "booking_changes": 0,
        "hotel": "Resort Hotel",
        "market_segment": "Direct",
        "distribution_channel": "Direct",
        "reserved_room_type": "A",
        "customer_type": "Transient"
    }
    response = client.post("/predict/price", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_adr"] > 0
    assert data["total_nights"] == 5
    assert data["estimated_total_stay_price"] == round(data["predicted_adr"] * 5, 2)
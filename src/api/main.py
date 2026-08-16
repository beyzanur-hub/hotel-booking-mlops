from fastapi import FastAPI, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import joblib
import io
import os
import time
import json
import logging
from datetime import datetime

from src.api.schemas import (
    CancellationInput, 
    CancellationResponse, 
    PriceInput, 
    PriceResponse
)

# Logging Yapılandırması
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "inferences.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def log_inference(endpoint: str, input_data: dict, output_data: dict, duration_ms: float):
    """Arka planda çalışan loglama fonksiyonu"""
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": endpoint,
        "duration_ms": duration_ms,
        "input": input_data,
        "output": output_data
    }
    logging.info(json.dumps(record, ensure_ascii=False))

app = FastAPI(
    title="🏨 Boutique-Stay MLOps Engine",
    description="Otel Rezervasyon İptal Riski ve Dinamik Fiyatlandırma REST API Servisi",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model Dosya Yolları
CANCEL_MODEL_PATH = os.path.join(BASE_DIR, "models", "cancellation_model.joblib")
PRICE_MODEL_PATH = os.path.join(BASE_DIR, "models", "price_model.joblib")

cancel_pipeline = None
price_pipeline = None

@app.on_event("startup")
def load_ml_models():
    global cancel_pipeline, price_pipeline
    try:
        cancel_pipeline = joblib.load(CANCEL_MODEL_PATH)
        price_pipeline = joblib.load(PRICE_MODEL_PATH)
        print("✅ [ML Engine] Tüm modeller başarıyla belleğe yüklendi.")
    except Exception as e:
        print(f"❌ [ML Engine Hata] Modeller yüklenirken hata oluştu: {str(e)}")

# Frontend Dosyalarını Sunma
STATIC_DIR = os.path.join(BASE_DIR, "app")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", tags=["Frontend"])
def serve_home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/app.js", include_in_schema=False)
def serve_js():
    return FileResponse(os.path.join(STATIC_DIR, "app.js"))

# Sağlık Kontrolü
@app.get("/health", tags=["Monitoring"])
def health_check():
    return {
        "status": "healthy",
        "models_loaded": cancel_pipeline is not None and price_pipeline is not None,
        "timestamp": time.time()
    }

# 1. İptal Riski Tahmini
@app.post("/predict/cancellation", response_model=CancellationResponse, status_code=status.HTTP_200_OK, tags=["Predictions"])
def predict_cancellation(payload: CancellationInput, background_tasks: BackgroundTasks):
    if cancel_pipeline is None:
        raise HTTPException(status_code=500, detail="Sınıflandırma modeli yüklü değil.")
    
    start_time = time.perf_counter()
    input_dict = payload.dict()
    input_df = pd.DataFrame([input_dict])
    
    try:
        prob = float(cancel_pipeline.predict_proba(input_df)[0][1])
        prediction = int(prob >= 0.50)
        risk_level = "High" if prob >= 0.50 else "Low"
        recommendation = (
            "Ön ödeme / depozito talep edin veya teyit araması yapın." 
            if risk_level == "High" 
            else "Standart rezervasyon prosedürünü uygulayın."
        )
        
        response = CancellationResponse(
            is_canceled_prediction=prediction,
            cancellation_probability=round(prob, 4),
            risk_level=risk_level,
            recommendation=recommendation
        )
        
        duration = round((time.perf_counter() - start_time) * 1000, 2)
        background_tasks.add_task(log_inference, "/predict/cancellation", input_dict, response.dict(), duration)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")

# 2. Dinamik Fiyat Tahmini
@app.post("/predict/price", response_model=PriceResponse, status_code=status.HTTP_200_OK, tags=["Predictions"])
def predict_price(payload: PriceInput, background_tasks: BackgroundTasks):
    if price_pipeline is None:
        raise HTTPException(status_code=500, detail="Fiyat tahmin modeli yüklü değil.")
    
    start_time = time.perf_counter()
    input_dict = payload.dict()
    input_df = pd.DataFrame([input_dict])
    
    try:
        predicted_adr = float(price_pipeline.predict(input_df)[0])
        total_nights = payload.stays_in_weekend_nights + payload.stays_in_week_nights
        effective_nights = total_nights if total_nights > 0 else 1
        total_price = predicted_adr * effective_nights
        
        response = PriceResponse(
            predicted_adr=round(predicted_adr, 2),
            total_nights=total_nights,
            estimated_total_stay_price=round(total_price, 2),
            currency="EUR"
        )
        
        duration = round((time.perf_counter() - start_time) * 1000, 2)
        background_tasks.add_task(log_inference, "/predict/price", input_dict, response.dict(), duration)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")


# 3. Toplu CSV Tahmin Endpoint'i (Batch Prediction)
@app.post("/predict/batch", tags=["Predictions"])
async def predict_batch_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Lütfen geçerli bir .csv dosyası yükleyin.")
    
    if cancel_pipeline is None or price_pipeline is None:
        raise HTTPException(status_code=500, detail="Modeller henüz yüklenmedi.")
        
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Eksik sütun kontrolü
        required_cols = [
            'hotel', 'lead_time', 'arrival_date_week_number', 
            'stays_in_weekend_nights', 'stays_in_week_nights', 
            'adults', 'children', 'market_segment', 
            'distribution_channel', 'deposit_type', 'customer_type'
        ]
        
        for col in required_cols:
            if col not in df.columns:
                raise HTTPException(status_code=422, detail=f"Eksik sütun: '{col}' CSV içinde bulunamadı.")
        
        # 1. Toplu İptal Olasılığı
        cancel_probs = cancel_pipeline.predict_proba(df)[:, 1]
        df['cancellation_probability'] = (cancel_probs * 100).round(1)
        df['risk_level'] = ["High" if p >= 50.0 else "Low" for p in df['cancellation_probability']]
        
        # 2. Toplu Dinamik Fiyat
        predicted_adrs = price_pipeline.predict(df)
        df['predicted_adr_eur'] = predicted_adrs.round(2)
        
        # Sonuç DataFrame'ini CSV stream'e dönüştürme
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=scored_hotel_bookings.csv"
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Toplu işlem hatası: {str(e)}")
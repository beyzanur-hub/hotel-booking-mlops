# Hafif ve güvenli resmi Python imajı
FROM python:3.11-slim

# Konteyner içi çalışma dizini
WORKDIR /app

# Sistem bağımlılıklarını güncelle
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları yükle (Docker cache optimizasyonu)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Gerekli proje dosyalarını kopyala
COPY src/ ./src/
COPY app/ ./app/
COPY models/ ./models/
COPY logs/ ./logs/

# API & Web Arayüzü Portu
EXPOSE 8000

# Uygulamayı ayağa kaldır
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
# 🏨 Boutique-Stay: Enterprise Revenue & Risk Inference Engine

![CI Pipeline](https://github.com/beyzanur-hub/hotel-booking-mlops/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4+-F7931E?logo=scikit-learn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

Boutique-Stay, konaklama sektörü için geliştirilmiş **Uçtan Uca (End-to-End) MLOps ve Karar Destek Platformudur**. Sistem, rezervasyon iptal risklerini olasılıksal olarak tahmin ederken aynı zamanda piyasa dinamiklerine göre optimum gecelik oda fiyatı (ADR) önerisinde bulunur.

---

## 🏗️ Sistem Mimarisi

Sistem, gevşek bağlı (decoupled) mikroservis mimarisi standartlarına uygun olarak tasarlanmıştır:

```text
┌─────────────────────────────────────────────────────────────┐
│                 1. MODERN SAAS FRONTEND                     │
│    (HTML5 + Tailwind CSS + Vanilla Async JS Fetch Engine)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP POST (JSON / Multipart)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  2. FASTAPI BACKEND ENGINE                  │
│   • Pydantic V2 ile Tip Güvenliği & Girdi Doğrulama        │
│   • BackgroundTasks ile Asenkron Inference Loglama         │
│   • Otomatik Swagger UI / OpenAPI Dokümantasyonu            │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│   3. CLASSIFICATION ENGINE   │    │     4. REGRESSION ENGINE     │
│  Distance-Weighted KNN (k=7) │    │  Distance-Weighted KNN       │
│  StandardScaler + OHE        │    │  StandardScaler + OHE        │
│  Target: is_canceled (Prob%) │    │  Target: adr (EUR / Night)   │
└──────────────────────────────┘    └──────────────────────────────┘
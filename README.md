# 🏨 Boutique-Stay: Enterprise Revenue & Risk Inference Engine

[![MLOps CI Pipeline](https://github.com/beyzanur-hub/hotel-booking-mlops/actions/workflows/ci.yml/badge.svg)](https://github.com/beyzanur-hub/hotel-booking-mlops/actions)
![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4.1-F7931E?logo=scikit-learn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-Passing-brightgreen?logo=pytest&logoColor=white)

**Boutique-Stay**, konaklama ve turizm sektörü için geliştirilmiş **Uçtan Uca (End-to-End) MLOps Karar Destek Platformudur**. 

Sistem, gelen rezervasyonların iptal risklerini olasılıksal olarak tahmin ederken (`Classification`), eş zamanlı olarak pazar dinamiklerine ve oda özelliklerine göre optimum gecelik oda fiyatı (`Regression - ADR`) önerisinde bulunur.

---

## 🏛️ Sistem Mimarisi & İş Akışı

Sistem, gevşek bağlı (*loosely-coupled*) modern mikroservis standartlarına uygun olarak inşa edilmiştir:

```text
                                  ┌───────────────────────────┐
                                  │   Modern SaaS Dashboard   │
                                  │ (Tailwind + Async Fetch)  │
                                  └─────────────┬─────────────┘
                                                │
                                    HTTP POST (JSON / Multipart)
                                                ▼
                                  ┌───────────────────────────┐
                                  │    FastAPI REST Engine    │
                                  │  • Pydantic V2 Validation │
                                  │  • Async Logging Worker   │
                                  │  • Swagger / OpenAPI Docs │
                                  └─────────────┬─────────────┘
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       ▼                                                 ▼
        ┌─────────────────────────────┐                   ┌─────────────────────────────┐
        │  Cancellation Risk Engine   │                   │    Dynamic Pricing Engine   │
        │  -------------------------- │                   │  -------------------------- │
        │  • Preprocessing: OHE+Scale │                   │  • Preprocessing: OHE+Scale │
        │  • Model: KNN Classifier    │                   │  • Model: KNN Regressor     │
        │  • Target: Prob % & Level   │                   │  • Target: ADR (EUR / Night)│
        └─────────────────────────────┘                   └─────────────────────────────┘
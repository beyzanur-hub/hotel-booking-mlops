import streamlit as st
import requests

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Boutique-Stay AI Dashboard",
    page_icon="🏨",
    layout="wide"
)

# FastAPI URL Tanımı
API_URL = "http://127.0.0.1:8000"

st.title("🏨 Boutique-Stay: Akıllı Rezervasyon & Dinamik Fiyatlandırma")
st.caption("Mikroservis Mimarisi: FastAPI REST API & Scikit-Learn MLOps Engine")
st.divider()

# Yan Panel - Kullanıcı Girişleri
st.sidebar.header("📋 Rezervasyon Detayları")

hotel = st.sidebar.selectbox("Otel Türü", ["City Hotel", "Resort Hotel"])
lead_time = st.sidebar.slider("Kaç Gün Önceden Yapıldı? (Lead Time)", 0, 700, 45)
arrival_week = st.sidebar.slider("Giriş Haftası (Yılın Kaçıncı Haftası?)", 1, 53, 28)

col_stay1, col_stay2 = st.sidebar.columns(2)
with col_stay1:
    weekend_nights = st.number_input("Hafta Sonu Gece", min_value=0, max_value=20, value=1)
with col_stay2:
    week_nights = st.number_input("Hafta İçi Gece", min_value=0, max_value=50, value=3)

col_g1, col_g2 = st.sidebar.columns(2)
with col_g1:
    adults = st.number_input("Yetişkin", min_value=1, max_value=10, value=2)
with col_g2:
    children = st.number_input("Çocuk", min_value=0, max_value=10, value=0)

market_segment = st.sidebar.selectbox(
    "Pazar Segmenti", 
    ["Online TA", "Offline TA/TO", "Direct", "Corporate", "Groups", "Complementary"]
)
distribution_channel = st.sidebar.selectbox(
    "Dağıtım Kanalı", 
    ["TA/TO", "Direct", "Corporate", "GDS"]
)
deposit_type = st.sidebar.selectbox(
    "Depozito Türü", 
    ["No Deposit", "Non Refund", "Refundable"]
)
customer_type = st.sidebar.selectbox(
    "Müşteri Tipi", 
    ["Transient", "Transient-Party", "Contract", "Group"]
)
reserved_room_type = st.sidebar.selectbox(
    "Oda Tipi", 
    ["A", "B", "C", "D", "E", "F", "G", "H", "L"]
)

prev_cancellations = st.sidebar.number_input("Geçmiş İptal Sayısı", min_value=0, max_value=50, value=0)
booking_changes = st.sidebar.number_input("Rezervasyon Değişikliği", min_value=0, max_value=20, value=0)
waiting_days = st.sidebar.number_input("Bekleme Listesindeki Gün", min_value=0, max_value=500, value=0)

# Tahmin Butonu
if st.button("🚀 Analiz Et ve Fiyat Hesapla", type="primary", use_container_width=True):
    col_left, col_right = st.columns(2)
    
    # 1. İPTAL TAHMİNİ (API İSTEĞİ)
    with col_left:
        st.subheader("🎯 İptal Riski Analizi")
        cancel_payload = {
            "lead_time": lead_time,
            "arrival_date_week_number": arrival_week,
            "stays_in_weekend_nights": weekend_nights,
            "stays_in_week_nights": week_nights,
            "adults": adults,
            "children": children,
            "previous_cancellations": prev_cancellations,
            "booking_changes": booking_changes,
            "days_in_waiting_list": waiting_days,
            "adr": 100.0,
            "hotel": hotel,
            "market_segment": market_segment,
            "distribution_channel": distribution_channel,
            "deposit_type": deposit_type,
            "customer_type": customer_type
        }
        
        try:
            res_cancel = requests.post(f"{API_URL}/predict/cancellation", json=cancel_payload)
            if res_cancel.status_code == 200:
                data = res_cancel.json()
                prob = data["cancellation_probability"] * 100
                st.metric(label="Tahmini İptal Olasılığı", value=f"%{prob:.1f}")
                
                if data["risk_level"] == "High":
                    st.error(f"⚠️ YÜKSEK RİSK")
                else:
                    st.success(f"✅ DÜŞÜK RİSK")
                st.info(f"💡 **Öneri:** {data['recommendation']}")
            else:
                st.error(f"API Hatası: {res_cancel.status_code}")
        except Exception as e:
            st.error(f"Backend API'ye ulaşılamadı. FastAPI'nin çalıştığından emin olun. Hata: {e}")

    # 2. FİYAT TAHMİNİ (API İSTEĞİ)
    with col_right:
        st.subheader("💰 Dinamik Fiyat Önerisi")
        price_payload = {
            "lead_time": lead_time,
            "arrival_date_week_number": arrival_week,
            "stays_in_weekend_nights": weekend_nights,
            "stays_in_week_nights": week_nights,
            "adults": adults,
            "children": children,
            "booking_changes": booking_changes,
            "hotel": hotel,
            "market_segment": market_segment,
            "distribution_channel": distribution_channel,
            "reserved_room_type": reserved_room_type,
            "customer_type": customer_type
        }
        
        try:
            res_price = requests.post(f"{API_URL}/predict/price", json=price_payload)
            if res_price.status_code == 200:
                data = res_price.json()
                st.metric(label="Önerilen Gecelik Fiyat (ADR)", value=f"{data['predicted_adr']} €")
                st.caption(f"Toplam Konaklama ({data['total_nights']} Gece): **{data['estimated_total_stay_price']} €**")
            else:
                st.error(f"API Hatası: {res_price.status_code}")
        except Exception as e:
            st.error(f"Backend API'ye ulaşılamadı. Hata: {e}")
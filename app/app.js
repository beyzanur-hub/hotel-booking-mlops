const API_URL = "http://127.0.0.1:8000";

// Sayfa yüklendiğinde Backend Health Check kontrolü
window.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch(`${API_URL}/health`);
        const data = await res.json();
        if (data.status === "healthy") {
            document.getElementById("apiStatusText").innerText = "API: Online";
            document.getElementById("apiStatusDot").className = "w-2 h-2 rounded-full bg-emerald-400 animate-pulse";
        }
    } catch {
        document.getElementById("apiStatusText").innerText = "API: Offline";
        document.getElementById("apiStatusDot").className = "w-2 h-2 rounded-full bg-rose-500";
    }
});

// Hızlı Senaryo Yükleme (Presets)
function loadPreset(type) {
    const presets = {
        high_risk: {
            hotel: "City Hotel",
            market_segment: "Online TA",
            lead_time: 290,
            arrival_date_week_number: 30,
            reserved_room_type: "A",
            stays_in_weekend_nights: 2,
            stays_in_week_nights: 5,
            adults: 2,
            children: 0,
            deposit_type: "No Deposit",
            customer_type: "Transient",
            distribution_channel: "TA/TO",
            previous_cancellations: 2,
            booking_changes: 0,
            days_in_waiting_list: 0
        },
        direct_vip: {
            hotel: "Resort Hotel",
            market_segment: "Direct",
            lead_time: 14,
            arrival_date_week_number: 24,
            reserved_room_type: "E",
            stays_in_weekend_nights: 2,
            stays_in_week_nights: 2,
            adults: 2,
            children: 1,
            deposit_type: "No Deposit",
            customer_type: "Transient",
            distribution_channel: "Direct",
            previous_cancellations: 0,
            booking_changes: 2,
            days_in_waiting_list: 0
        },
        summer_resort: {
            hotel: "Resort Hotel",
            market_segment: "Online TA",
            lead_time: 120,
            arrival_date_week_number: 32,
            reserved_room_type: "D",
            stays_in_weekend_nights: 2,
            stays_in_week_nights: 5,
            adults: 2,
            children: 2,
            deposit_type: "Refundable",
            customer_type: "Transient-Party",
            distribution_channel: "TA/TO",
            previous_cancellations: 0,
            booking_changes: 1,
            days_in_waiting_list: 0
        }
    };

    const data = presets[type];
    if (!data) return;

    // Form Elemanlarını Doldur
    for (const key in data) {
        const el = document.getElementById(key);
        if (el) el.value = data[key];
    }

    // Otomatik Analizi Başlat
    document.getElementById("btnExecute").click();
}

// Ana Analiz İşlemi
document.getElementById("btnExecute").addEventListener("click", async () => {
    const btn = document.getElementById("btnExecute");
    const riskValue = document.getElementById("riskValue");
    const riskBadge = document.getElementById("riskBadge");
    const riskBar = document.getElementById("riskBar");
    const riskNote = document.getElementById("riskNote");
    const priceValue = document.getElementById("priceValue");
    const stayNights = document.getElementById("stayNights");
    const totalRevenue = document.getElementById("totalRevenue");
    const latencyBadge = document.getElementById("latencyBadge");
    const latencyValue = document.getElementById("latencyValue");

    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin text-xs"></i> Model Çıkarımı Yapılıyor...`;

    const formData = {
        hotel: document.getElementById("hotel").value,
        market_segment: document.getElementById("market_segment").value,
        lead_time: parseInt(document.getElementById("lead_time").value) || 0,
        arrival_date_week_number: parseInt(document.getElementById("arrival_date_week_number").value) || 1,
        reserved_room_type: document.getElementById("reserved_room_type").value,
        stays_in_weekend_nights: parseInt(document.getElementById("stays_in_weekend_nights").value) || 0,
        stays_in_week_nights: parseInt(document.getElementById("stays_in_week_nights").value) || 0,
        adults: parseInt(document.getElementById("adults").value) || 1,
        children: parseInt(document.getElementById("children").value) || 0,
        deposit_type: document.getElementById("deposit_type").value,
        customer_type: document.getElementById("customer_type").value,
        distribution_channel: document.getElementById("distribution_channel").value,
        previous_cancellations: parseInt(document.getElementById("previous_cancellations").value) || 0,
        booking_changes: parseInt(document.getElementById("booking_changes").value) || 0,
        days_in_waiting_list: parseInt(document.getElementById("days_in_waiting_list").value) || 0,
        adr: 100.0
    };

    const startTime = performance.now();

    try {
        const [resCancel, resPrice] = await Promise.all([
            fetch(`${API_URL}/predict/cancellation`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            }),
            fetch(`${API_URL}/predict/price`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            })
        ]);

        const endTime = performance.now();
        const duration = Math.round(endTime - startTime);

        // Latency göstergesi
        latencyBadge.classList.remove("hidden");
        latencyValue.innerText = `${duration} ms`;

        if (!resCancel.ok || !resPrice.ok) {
            throw new Error("Backend API hata kodu döndürdü.");
        }

        const cancelData = await resCancel.json();
        const priceData = await resPrice.json();

        // 1. İptal Riski Kartı
        const prob = (cancelData.cancellation_probability * 100).toFixed(1);
        const isHigh = cancelData.risk_level === "High";

        riskValue.innerText = `%${prob}`;
        riskBar.style.width = `${prob}%`;

        if (isHigh) {
            riskValue.className = "text-3xl font-semibold tracking-tight text-rose-400 mono";
            riskBar.className = "bg-rose-500 h-1.5 rounded-full transition-all duration-500";
            riskBadge.className = "text-[11px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20";
            riskBadge.innerText = "YÜKSEK RİSK";
        } else {
            riskValue.className = "text-3xl font-semibold tracking-tight text-emerald-400 mono";
            riskBar.className = "bg-emerald-500 h-1.5 rounded-full transition-all duration-500";
            riskBadge.className = "text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
            riskBadge.innerText = "DÜŞÜK RİSK";
        }

        riskNote.innerHTML = `<i class="fa-solid fa-shield-halved ${isHigh ? 'text-rose-400' : 'text-emerald-400'} text-xs"></i> <span><strong>Aksiyon:</strong> ${cancelData.recommendation}</span>`;

        // 2. Dinamik Fiyat Kartı
        priceValue.innerText = priceData.predicted_adr.toFixed(2);
        stayNights.innerText = `${priceData.total_nights} Gece`;
        totalRevenue.innerText = `${priceData.estimated_total_stay_price.toFixed(2)} €`;

    } catch (err) {
        riskNote.innerHTML = `<span class="text-rose-400">Bağlantı Hatası: ${err.message}</span>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-microchip text-xs"></i> Tahmin ve Fiyat Analizini Çalıştır`;
    }
});

// Sıfırla
document.getElementById("btnReset").addEventListener("click", () => {
    document.getElementById("calcForm").reset();
    document.getElementById("riskValue").innerText = "--%";
    document.getElementById("riskBar").style.width = "0%";
    document.getElementById("priceValue").innerText = "--.--";
    document.getElementById("stayNights").innerText = "0 Gece";
    document.getElementById("totalRevenue").innerText = "--.-- €";
});

// Toplu CSV İşleme
document.getElementById("btnUploadBatch").addEventListener("click", async () => {
    const fileInput = document.getElementById("batchFileInput");
    const statusDiv = document.getElementById("batchStatus");
    const btn = document.getElementById("btnUploadBatch");

    if (!fileInput.files.length) {
        statusDiv.classList.remove("hidden");
        statusDiv.innerHTML = `<span class="text-amber-400">Lütfen önce bir .csv dosyası seçin.</span>`;
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-indigo-400"></i> Analiz Ediliyor...`;
    statusDiv.classList.remove("hidden");
    statusDiv.innerHTML = `<span>Dosya işleniyor, model tahminleri hesaplanıyor...</span>`;

    try {
        const response = await fetch(`${API_URL}/predict/batch`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Dosya işlenirken hata oluştu.");
        }

        // Dönen CSV dosyasını indirtme
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `scored_${file.name}`;
        document.body.appendChild(a);
        a.click();
        a.remove();

        statusDiv.innerHTML = `<span class="text-emerald-400">✅ Başarılı! Puanlanmış CSV dosyası indirildi.</span>`;
    } catch (err) {
        statusDiv.innerHTML = `<span class="text-rose-400">Hata: ${err.message}</span>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-cloud-arrow-up text-indigo-400"></i> Dosyayı İşle ve Sonucu İndir`;
    }
});

// Örnek Şablon Oluşturup İndirme
document.getElementById("btnDownloadSample").addEventListener("click", () => {
    const sampleCsv = `hotel,lead_time,arrival_date_week_number,stays_in_weekend_nights,stays_in_week_nights,adults,children,market_segment,distribution_channel,deposit_type,customer_type,reserved_room_type,previous_cancellations,booking_changes,days_in_waiting_list,adr
City Hotel,45,28,1,3,2,0,Online TA,TA/TO,No Deposit,Transient,A,0,0,0,100.0
Resort Hotel,120,32,2,5,2,2,Direct,Direct,Refundable,Transient,D,0,1,0,150.0
City Hotel,290,30,2,5,2,0,Online TA,TA/TO,No Deposit,Transient,A,2,0,0,90.0`;

    const blob = new Blob([sampleCsv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "sample_hotel_batch_template.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
});
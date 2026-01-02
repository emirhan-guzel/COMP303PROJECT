import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression 
from db_manager import DOSYA_ADI, stok_ekle, RECETELER, verileri_sifirla

def show():
    # --- SIDEBAR AYARLARI ---
    st.sidebar.markdown("## 🛡️ Yönetici Paneli")
    
    st.sidebar.divider()
    st.sidebar.markdown("### ⚠️ Demo Ayarları")
    if st.sidebar.button("🧹 TÜM VERİLERİ SİL (SIFIRLA)", type="primary"):
        if verileri_sifirla():
            st.sidebar.success("Veritabanı temizlendi! Sayfayı yenile.")
            st.rerun()
        else:
            st.sidebar.error("Silme hatası.")
            
    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.logged_in = False
        st.rerun()
    
    # --- ANA SEKMELER ---
    tab_analiz, tab_ai, tab_stok = st.tabs(["📊 FİNANSAL ANALİZ", "🧠 AI STRATEJİ", "📦 STOK YÖNETİMİ"])
    
    # Veritabanından verileri çekiyoruz - Emirhan Güzel
    conn = sqlite3.connect(DOSYA_ADI)
    df = pd.read_sql("SELECT * FROM siparisler", conn)
    conn.close()

    # ===================================
    #  SEKME 1: FİNANSAL ANALİZ
    # ===================================
    with tab_analiz:
        st.markdown("### 📈 İşletme Performans Göstergeleri")
        
        if df.empty:
            st.info("Analiz için yeterli veri yok. Sipariş girildikçe burası dolacak.")
        else:
            # Veri Ön İşleme
            df["Tarih"] = pd.to_datetime(df["Tarih"])
            df["Gun"] = df["Tarih"].dt.date
            df["Saat"] = df["Tarih"].dt.hour
            df["NetKar"] = df["Fiyat"] - df["Maliyet"]

            # --- 1. KPI KARTLARI (ÖZET) ---
            # En üstte işletmenin anlık durumunu gösteren büyük rakamlar - Emirhan Güzel
            col1, col2, col3, col4 = st.columns(4)
            
            toplam_ciro = df["Fiyat"].sum()
            toplam_kar = df["NetKar"].sum()
            toplam_siparis = len(df)
            ort_sepet = toplam_ciro / toplam_siparis if toplam_siparis > 0 else 0
            
            col1.metric("💰 Toplam Ciro", f"{toplam_ciro:,.2f} TL", delta="Canlı")
            col2.metric("💸 Net Kâr", f"{toplam_kar:,.2f} TL", delta_color="normal")
            col3.metric("🧾 Toplam Adisyon", f"{toplam_siparis} Adet")
            col4.metric("🛒 Ort. Sepet", f"{ort_sepet:.1f} TL") # Ortalama sipariş tutarı - Emirhan Güzel

            st.markdown("---")

            # --- 2. ZAMAN BAZLI ANALİZ (GÜNLÜK SATIŞ GRAFİĞİ) ---
            # Hangi gün ne kadar satış yapılmış? Çizgi grafik. - Emirhan Güzel
            st.subheader("📅 Günlük Ciro Trendi")
            gunluk_ciro = df.groupby("Gun")["Fiyat"].sum().reset_index()
            
            fig_trend = px.area(gunluk_ciro, x="Gun", y="Fiyat", 
                                title="Günlük Satış Hacmi",
                                labels={"Fiyat": "Ciro (TL)", "Gun": "Tarih"},
                                color_discrete_sequence=["#6a11cb"])
            st.plotly_chart(fig_trend, use_container_width=True)

            # --- 3. PERSONEL PERFORMANSI (ÇİFT EKSENLİ GRAFİK) ---
            # Garsonlar ne kadar ciro yapmış ve kaç sipariş almış? - Emirhan Güzel
            st.subheader("👔 Personel Verimlilik Analizi")
            
            personel_perf = df.groupby("Garson").agg({
                "Fiyat": "sum",
                "id": "count"
            }).reset_index().rename(columns={"Fiyat": "ToplamCiro", "id": "IslemAdedi"})
            
            personel_perf = personel_perf.sort_values(by="ToplamCiro", ascending=False)

            # Bar Grafiği (Ciro) ve Çizgi (İşlem Sayısı) bir arada - Emirhan Güzel
            fig_personel = go.Figure()
            
            # Bar: Ciro
            fig_personel.add_trace(go.Bar(
                x=personel_perf["Garson"],
                y=personel_perf["ToplamCiro"],
                name="Toplam Ciro (TL)",
                marker_color='#00d2ff'
            ))

            # Çizgi: İşlem Adedi
            fig_personel.add_trace(go.Scatter(
                x=personel_perf["Garson"],
                y=personel_perf["IslemAdedi"],
                name="Sipariş Adedi",
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#ff4b4b', width=3)
            ))

            fig_personel.update_layout(
                title="Garson Puanı: Ciro ve İşlem Yoğunluğu",
                yaxis=dict(title="Ciro (TL)"),
                yaxis2=dict(title="Adet", overlaying='y', side='right'),
                legend=dict(x=0.1, y=1.1, orientation="h")
            )
            st.plotly_chart(fig_personel, use_container_width=True)

            # --- 4. MENÜ ANALİZİ & EN ÇOK SATANLAR ---
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("🏆 En Çok Satan Ürünler")
                # Ürün bazlı satış adedi - Emirhan Güzel
                urun_adet = df["Yemek Adi"].value_counts().reset_index()
                urun_adet.columns = ["Yemek", "Adet"]
                
                fig_best = px.bar(urun_adet.head(10), x="Adet", y="Yemek", orientation='h', 
                                  title="Top 10 Popüler Ürün", color="Adet", color_continuous_scale="Viridis")
                st.plotly_chart(fig_best, use_container_width=True)
                
            with c2:
                st.subheader("🍕 Ürün Kârlılık Dağılımı")
                # Ürün bazlı toplam kâr analizi (Pasta Grafik) - Emirhan Güzel
                urun_kar = df.groupby("Yemek Adi")["NetKar"].sum().reset_index()
                
                fig_pie = px.pie(urun_kar, values="NetKar", names="Yemek Adi", 
                                 title="Toplam Kâra Katkı Oranı", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)

    # =============================
    #  SEKME 2: AI STRATEJİ
    # =============================
    with tab_ai:
        st.markdown("### 🚀 Akıllı Stok ve Satış Tahmini")
        st.info("AI Modeli, Lineer Regresyon Modeli kullanarak sadece geçmişe değil **son trendlere** bakarak tahmin üretir.")

        if df.empty:
            st.warning("Veri yok. Sipariş girildikçe analiz başlayacak.")
        else:
            # AI hesaplamaları için tarih formatı - Emirhan Güzel
            if "Tarih" not in df.columns or df["Tarih"].dtype == object:
                 df["Tarih"] = pd.to_datetime(df["Tarih"])
                 
            tahmin_raporu = []
            yemekler = df["Yemek Adi"].unique()
            
            for yemek in yemekler:
                df_yemek = df[df["Yemek Adi"] == yemek]
                toplam_satis = len(df_yemek)
                
                # Trend Analizi: Son 10 sipariş içindeki yoğunluğu
                son_10_siparis = df.tail(10)
                son_trend_sayisi = len(son_10_siparis[son_10_siparis["Yemek Adi"] == yemek])
                
                # Basit Ağırlıklı Tahmin: (Toplam Ort.) + (Son Trend * 2)
                tahmin = (toplam_satis / max(1, len(df["Tarih"].dt.date.unique()))) + (son_trend_sayisi * 1.5)
                tahmin = int(round(tahmin))
                if tahmin < 1: tahmin = 1 
                
                # Stok Kontrolü
                uyari = "✅ Yeterli"
                renk = "green"
                
                if yemek in RECETELER:
                    conn_stok = sqlite3.connect(DOSYA_ADI)
                    cur = conn_stok.cursor()
                    for mlz, gr in RECETELER[yemek].items():
                        ihtiyac = gr * tahmin
                        cur.execute("SELECT miktar, birim FROM stok WHERE malzeme=?", (mlz,))
                        res = cur.fetchone()
                        if res:
                            eldeki, birim = res
                            if eldeki < ihtiyac:
                                eksik = ihtiyac - eldeki
                                uyari = f"⚠️ KRİTİK: {eksik} {birim} {mlz} AL!"
                                renk = "red"
                                break
                    conn_stok.close()
                
                tahmin_raporu.append({
                    "Ürün": yemek,
                    "Toplam Satış": toplam_satis,
                    "🔥 Son Trend": f"{son_trend_sayisi} (Son 10'da)",
                    "🔮 Tahmin": tahmin,
                    "Stok Durumu": uyari,
                    "Renk": renk
                })
            
            df_ai = pd.DataFrame(tahmin_raporu).sort_values(by="🔥 Son Trend", ascending=False)
            
            def highlight_row(row):
                return ['background-color: #ffcccc' if row['Renk'] == 'red' else '' for _ in row]

            st.dataframe(
                df_ai.style.apply(highlight_row, axis=1),
                column_config={"Renk": None},
                use_container_width=True
            )

    # ==========================
    # SEKME 3: STOK YÖNETİMİ
    # =========================
    with tab_stok:
        conn = sqlite3.connect(DOSYA_ADI)
        df_stok = pd.read_sql("SELECT * FROM stok", conn)
        conn.close()
        st.dataframe(df_stok, use_container_width=True, height=300)
        
        with st.form("add_stok"):
            c1, c2 = st.columns(2)
            sec = c1.selectbox("Malzeme", df_stok["malzeme"].tolist())
            mik = c2.number_input("Ekle", 100)
            if st.form_submit_button("Güncelle"):
                stok_ekle(sec, mik)
                st.rerun()
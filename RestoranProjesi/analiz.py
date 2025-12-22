import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import random
import numpy as np
from datetime import datetime, timedelta
from matplotlib.figure import Figure
from sklearn.linear_model import LinearRegression

# --- AYARLAR ---
DOSYA_ADI = "siparis_gecmisi.csv"
plt.style.use("dark_background")

YEMEKLER_DB = [
    {"isim": "Mercimek", "fiyat": 40, "maliyet": 12, "sure": 3},
    {"isim": "İskender", "fiyat": 150, "maliyet": 65, "sure": 8},
    {"isim": "Adana", "fiyat": 140, "maliyet": 60, "sure": 7},
    {"isim": "Künefe", "fiyat": 80, "maliyet": 35, "sure": 5},
    {"isim": "Su", "fiyat": 10, "maliyet": 2, "sure": 1},
    {"isim": "Kola", "fiyat": 25, "maliyet": 15, "sure": 1},
    {"isim": "Beyti", "fiyat": 160, "maliyet": 70, "sure": 9},
    {"isim": "Gavurdağı", "fiyat": 60, "maliyet": 20, "sure": 3},
    {"isim": "Ezogelin", "fiyat": 40, "maliyet": 12, "sure": 3},
    {"isim": "Ayran", "fiyat": 15, "maliyet": 4, "sure": 1},
]

GARSONLAR = ["Ali", "Ayşe", "Mehmet", "Zeynep"] 

def demo_veri_olustur():
    """MANİPÜLE EDİLMİŞ DEMO VERİSİ"""
    veriler = []
    bugun = datetime.now()
    
    print("DEMO MODU: Yoğunluk Haritası İçin Veri Üretiliyor...")
    
    for i in range(180): # 6 Aylık Veri
        gun = bugun - timedelta(days=i)
        
        if gun.weekday() >= 5: gunluk_musteri = random.randint(40, 80)
        else: gunluk_musteri = random.randint(15, 35)

        for _ in range(gunluk_musteri):
            secim = random.choice(YEMEKLER_DB)
            garson = random.choice(GARSONLAR)
            
            # SAAT SİMÜLASYONU (Heatmap güzel görünsün diye)
            # Öğle (12-13) ve Akşam (19-20) saatlerini yoğun yapalım
            saatler = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
            agirliklar = [5, 30, 40, 15, 10, 10, 20, 35, 50, 45, 20, 5]
            
            secilen_saat = random.choices(saatler, weights=agirliklar, k=1)[0]
            tarih_saat = gun.replace(hour=secilen_saat, minute=random.randint(0, 59))
            
            veriler.append([
                tarih_saat.strftime("%Y-%m-%d %H:%M:%S"), 
                secim["isim"], secim["fiyat"], secim["maliyet"], secim["sure"],
                garson
            ])
            
    df = pd.DataFrame(veriler, columns=["Tarih", "Yemek Adi", "Fiyat", "Maliyet", "Hazirlanma Suresi", "Garson"])
    df.to_csv(DOSYA_ADI, index=False)
    return df

def veri_yukle():
    if not os.path.exists(DOSYA_ADI) or os.stat(DOSYA_ADI).st_size < 100:
        return demo_veri_olustur()
    df = pd.read_csv(DOSYA_ADI)
    df["Tarih"] = pd.to_datetime(df["Tarih"])
    df["Kar"] = df["Fiyat"] - df["Maliyet"]
    if "Garson" not in df.columns: df["Garson"] = "Sistem"
    return df

def personel_performansi_getir():
    df = veri_yukle()
    if "Garson" not in df.columns: return pd.DataFrame()
    performans = df.groupby("Garson").agg({"Fiyat": "sum", "Yemek Adi": "count", "Kar": "sum"}).reset_index()
    performans.columns = ["Garson", "Toplam_Ciro", "Siparis_Adedi", "Toplam_Kar"]
    return performans.sort_values(by="Toplam_Ciro", ascending=False)

def yapay_zeka_tahmini_yap():
    df = veri_yukle()
    sonuclar = []
    son_tarih = df["Tarih"].max()
    ilk_tarih = son_tarih - timedelta(days=30)
    df_bu_ay = df[df["Tarih"] > ilk_tarih]
    
    if df_bu_ay.empty: return pd.DataFrame()
    ortalama_satis = df_bu_ay["Yemek Adi"].value_counts().mean()

    for yemek in df["Yemek Adi"].unique():
        df_yemek = df[df["Yemek Adi"] == yemek].copy()
        df_yemek_bu_ay = df_bu_ay[df_bu_ay["Yemek Adi"] == yemek]
        bu_ay_satis = len(df_yemek_bu_ay)
        bu_ay_kar = df_yemek_bu_ay["Kar"].sum()
        gunluk = df_yemek.groupby(df_yemek["Tarih"].dt.date).size().reset_index(name="Adet")
        gunluk["Index"] = range(len(gunluk))
        gelecek = bu_ay_satis
        egim = 0
        if len(gunluk) > 5:
            model = LinearRegression()
            model.fit(gunluk[["Index"]], gunluk["Adet"])
            gelecek = int(sum(model.predict(np.array(range(gunluk["Index"].max()+1, gunluk["Index"].max()+31)).reshape(-1,1))))
            if gelecek < 0: gelecek = 0
            egim = model.coef_[0]

        puan = bu_ay_satis
        durum, stok, fiyat = "STANDART", "Sabit Tut", "Sabit"
        if bu_ay_satis > ortalama_satis * 1.5: durum="⭐ BEST SELLER"; stok="%30 ARTIR"; fiyat="%10 Zam"; puan+=1000
        elif bu_ay_satis < ortalama_satis * 0.2: durum="⛔ MENÜDEN ÇIKAR"; stok="SIFIRLA"; fiyat="-"; puan-=1000
        elif egim > 0.1: durum="📈 YÜKSELİŞTE"; stok="%15 Artır"; fiyat="%5 Zam"; puan+=500
        elif egim < -0.1: durum="📉 DÜŞÜŞTE"; stok="%20 Azalt"; fiyat="Kampanya"; puan-=200

        sonuclar.append({"Urun": yemek, "BuAy": bu_ay_satis, "Tahmin": gelecek, "Durum": durum, "StokAction": stok, "FiyatAction": fiyat, "Puan": puan, "Kar": bu_ay_kar})
    return pd.DataFrame(sonuclar).sort_values(by="Puan", ascending=False)

def excel_raporu_indir():
    try:
        df_ai = yapay_zeka_tahmini_yap().drop(columns=["Puan"])
        df_pers = personel_performansi_getir()
        dosya = f"Rapor_{datetime.now().strftime('%Y%m%d')}.xlsx"
        with pd.ExcelWriter(dosya, engine='openpyxl') as writer:
            df_ai.to_excel(writer, sheet_name="AI_Strateji", index=False)
            df_pers.to_excel(writer, sheet_name="Personel", index=False)
        return dosya
    except: return None

def grafik_olustur():
    df_raw = veri_yukle()
    fig = Figure(figsize=(12, 8), dpi=100)
    
    # --- GRAFİK 1: FİNANSAL AKIŞ (ÜST - ALAN GRAFİĞİ) ---
    ax1 = fig.add_subplot(211)
    gunluk = df_raw.groupby(df_raw["Tarih"].dt.date)[["Fiyat", "Kar"]].sum().tail(30)
    x = range(len(gunluk))
    ax1.fill_between(x, gunluk["Fiyat"], color="#00d2ff", alpha=0.2)
    ax1.plot(x, gunluk["Fiyat"], color="#00d2ff", label="Ciro")
    ax1.fill_between(x, gunluk["Kar"], color="#00ff00", alpha=0.3)
    ax1.plot(x, gunluk["Kar"], color="#00ff00", linestyle="--", label="Kâr")
    ax1.legend(); ax1.set_title("Finansal Akış (Son 30 Gün)", color="white"); ax1.tick_params(colors="white")
    
    # --- GRAFİK 2: SAATLİK İŞ YERİ YOĞUNLUĞU (HEATMAP) - YENİ! ---
    
    ax2 = fig.add_subplot(223)
    
    # Gün ve Saat bilgilerini çıkar
    df_raw["Saat"] = df_raw["Tarih"].dt.hour
    df_raw["Gun"] = df_raw["Tarih"].dt.day_name()
    
    # Pivot Tablo: Günlere ve Saatlere göre sipariş yoğunluğu
    # fillna(0) boş saatleri 0 yapar
    yogunluk = df_raw.pivot_table(index="Gun", columns="Saat", values="Fiyat", aggfunc="count").fillna(0)
    
    # Günleri doğru sıraya dizelim
    sirali_gunler = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # Veride olan günleri filtrele ve sırala
    yogunluk = yogunluk.reindex(sirali_gunler)
    
    # Isı Haritasını Çiz
    # cmap="magma" (Siyah -> Mor -> Turuncu -> Sarı) çok şık durur
    sns.heatmap(yogunluk, cmap="magma", ax=ax2, cbar=False, linewidths=0.5, linecolor='black')
    
    ax2.set_title("İş Yeri Yoğunluk Haritası (Gün/Saat)", color="white")
    ax2.set_xlabel("Saatler (11:00 - 23:00)", color="white")
    ax2.set_ylabel("", color="white")
    ax2.tick_params(colors="white", labelsize=8)
    
    # --- GRAFİK 3: CİRO KAYNAKLARI (DONUT) ---
    ax3 = fig.add_subplot(224)
    ciro_dag = df_raw.groupby("Yemek Adi")["Fiyat"].sum().sort_values(ascending=False).head(5)
    ax3.pie(ciro_dag, labels=ciro_dag.index, autopct='%1.1f%%', colors=sns.color_palette("bright"), textprops={'color':"white"})
    ax3.set_title("En Çok Ciro Getiren 5 Ürün", color="white")
    
    fig.tight_layout(pad=3.0)
    return fig
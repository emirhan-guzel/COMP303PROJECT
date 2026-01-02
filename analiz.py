import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import os
import random
import numpy as np
from datetime import datetime, timedelta
from matplotlib.figure import Figure
from sklearn.linear_model import LinearRegression

# Atilla 


# --- AYARLAR ---
DOSYA_ADI = "restoran_verisi.db"
plt.style.use("dark_background") # Grafiklerin temasını koyu mod yapar

# Demo veri üretimi için kullanılacak sabit menü listesi
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
    """
    DEMO VERİSİ OLUŞTURUR - SQLite'a
    Eğer veritabanı boşsa, analiz yapabilmek için geçmişe dönük 6 aylık
    sahte ama mantıklı satış verisi üretir.
    """
    print("🔄 DEMO MODU: Yoğunluk Haritası İçin Veri Üretiliyor...")
    
    conn = sqlite3.connect(DOSYA_ADI)
    cursor = conn.cursor()
    
    # Tabloyu temizle (Sıfırdan temiz veri seti için)
    cursor.execute("DELETE FROM siparisler")
    
    bugun = datetime.now()
    
    # 180 gün (6 ay) geriye giderek her gün için sipariş oluştur
    for i in range(180):  
        gun = bugun - timedelta(days=i)
        
        # Hafta sonları (Cumartesi-Pazar) müşteri sayısı daha fazla olsun (40-80 arası)
        if gun.weekday() >= 5: 
            gunluk_musteri = random.randint(40, 80)
        else: 
            # Hafta içi daha az müşteri (15-35 arası)
            gunluk_musteri = random.randint(15, 35)

        for _ in range(gunluk_musteri):
            secim = random.choice(YEMEKLER_DB)
            garson = random.choice(GARSONLAR)
            
            # Saat Simülasyonu: Öğle (12-13) ve Akşam (19-20) saatlerine ağırlık veriyoruz
            saatler = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
            agirliklar = [5, 30, 40, 15, 10, 10, 20, 35, 50, 45, 20, 5]
            
            secilen_saat = random.choices(saatler, weights=agirliklar, k=1)[0]
            tarih_saat = gun.replace(hour=secilen_saat, minute=random.randint(0, 59))
            
            # Veriyi veritabanına ekle
            cursor.execute("""
                INSERT INTO siparisler 
                (Tarih, "Yemek Adi", Fiyat, Maliyet, "Hazirlanma Suresi", Garson) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tarih_saat.strftime("%Y-%m-%d %H:%M:%S"),
                secim["isim"],
                secim["fiyat"],
                secim["maliyet"],
                secim["sure"],
                garson
            ))
    
    conn.commit()
    conn.close()
    print(f"✅ Demo veri oluşturuldu: {DOSYA_ADI}")
    return veri_yukle()

def veri_yukle():
    """
    SQLite veritabanındaki veriyi okuyup Pandas DataFrame formatına çevirir.
    Veri analizi için gerekli olan 'Kar' sütununu hesaplar.
    """
    if not os.path.exists(DOSYA_ADI):
        return demo_veri_olustur()
    
    try:
        conn = sqlite3.connect(DOSYA_ADI)
        df = pd.read_sql_query("SELECT * FROM siparisler", conn)
        conn.close()
        
        # Eğer veri çok azsa analiz yapılamaz, demo verisi oluştur
        if df.empty or len(df) < 10:
            return demo_veri_olustur()
        
        # Tarih formatını datetime objesine çevir
        df["Tarih"] = pd.to_datetime(df["Tarih"])
        # Kar hesapla: Satış Fiyatı - Maliyet
        df["Kar"] = df["Fiyat"] - df["Maliyet"]
        
        if "Garson" not in df.columns: 
            df["Garson"] = "Sistem"
            
        return df
    except Exception as e:
        print(f"❌ Veri yükleme hatası: {e}")
        return demo_veri_olustur()

def personel_performansi_getir():
    """
    Hangi garsonun ne kadar ciro yaptığını ve kaç sipariş aldığını analiz eder.
    """
    df = veri_yukle()
    if "Garson" not in df.columns or df.empty: 
        return pd.DataFrame()
    
    # Garson bazında gruplama yap
    performans = df.groupby("Garson").agg({
        "Fiyat": "sum",       # Toplam Ciro
        "Yemek Adi": "count", # Toplam Sipariş Sayısı
        "Kar": "sum"          # Toplam Kâr
    }).reset_index()
    
    performans.columns = ["Garson", "Toplam_Ciro", "Siparis_Adedi", "Toplam_Kar"]
    # En çok ciro yapana göre sırala
    return performans.sort_values(by="Toplam_Ciro", ascending=False)

def yapay_zeka_tahmini_yap():
    """
    Basit bir Makine Öğrenmesi (Lineer Regresyon) algoritması kullanır.
    Son 30 günlük verilere bakarak:
    1. Gelecek ay ne kadar satılacağını tahmin eder.
    2. Satış trendinin (Eğim) artışta mı düşüşte mi olduğunu bulur.
    3. Buna göre Stok ve Fiyat önerisi verir (Action).
    """
    df = veri_yukle()
    if df.empty:
        return pd.DataFrame()
    
    sonuclar = []
    # Son 30 günün verisini filtrele
    son_tarih = df["Tarih"].max()
    ilk_tarih = son_tarih - timedelta(days=30)
    df_bu_ay = df[df["Tarih"] > ilk_tarih]
    
    if df_bu_ay.empty: 
        return pd.DataFrame()
    
    # Genel ortalama satış adedi
    ortalama_satis = df_bu_ay["Yemek Adi"].value_counts().mean()

    # Her yemek için döngü
    for yemek in df["Yemek Adi"].unique():
        df_yemek = df[df["Yemek Adi"] == yemek].copy()
        df_yemek_bu_ay = df_bu_ay[df_bu_ay["Yemek Adi"] == yemek]
        bu_ay_satis = len(df_yemek_bu_ay)
        bu_ay_kar = df_yemek_bu_ay["Kar"].sum()
        
        # Günlük satış sayılarını çıkar (Regresyon için veri hazırlığı)
        gunluk = df_yemek.groupby(df_yemek["Tarih"].dt.date).size().reset_index(name="Adet")
        gunluk["Index"] = range(len(gunluk))
        
        gelecek = bu_ay_satis
        egim = 0
        
        # --- MAKİNE ÖĞRENMESİ KISMI ---
        # Eğer yeterli veri varsa Lineer Regresyon modelini eğit
        if len(gunluk) > 5:
            model = LinearRegression()
            model.fit(gunluk[["Index"]], gunluk["Adet"]) # X=Zaman, Y=Satış Adedi
            # Gelecek 30 günü tahmin et
            gelecek = int(sum(model.predict(np.array(range(gunluk["Index"].max()+1, gunluk["Index"].max()+31)).reshape(-1,1))))
            if gelecek < 0: gelecek = 0
            egim = model.coef_[0] # Eğimin yönü (Pozitifse artışta, negatifse düşüşte)

        # --- KARAR MEKANİZMASI ---
        puan = bu_ay_satis
        durum, stok, fiyat = "STANDART", "Sabit Tut", "Sabit"
        
        if bu_ay_satis > ortalama_satis * 1.5: 
            durum="⭐ BEST SELLER"
            stok="%30 ARTIR"
            fiyat="%10 Zam"
            puan+=1000
        elif bu_ay_satis < ortalama_satis * 0.2: 
            durum="⛔ MENÜDEN ÇIKAR"
            stok="SIFIRLA"
            fiyat="-"
            puan-=1000
        elif egim > 0.1: 
            durum="📈 YÜKSELİŞTE"
            stok="%15 Artır"
            fiyat="%5 Zam"
            puan+=500
        elif egim < -0.1: 
            durum="📉 DÜŞÜŞTE"
            stok="%20 Azalt"
            fiyat="Kampanya"
            puan-=200

        sonuclar.append({
            "Urun": yemek, 
            "BuAy": bu_ay_satis, 
            "Tahmin": gelecek, 
            "Durum": durum, 
            "StokAction": stok, 
            "FiyatAction": fiyat, 
            "Puan": puan, 
            "Kar": bu_ay_kar
        })
    
    return pd.DataFrame(sonuclar).sort_values(by="Puan", ascending=False)

def excel_raporu_indir():
    """
    Analiz sonuçlarını Excel dosyası olarak kaydeder.
    """
    try:
        df_ai = yapay_zeka_tahmini_yap()
        if df_ai.empty:
            return None
        df_ai = df_ai.drop(columns=["Puan"]) # Puan sütununu rapora koymaya gerek yok
        df_pers = personel_performansi_getir()
        
        dosya = f"Rapor_{datetime.now().strftime('%Y%m%d')}.xlsx"
        with pd.ExcelWriter(dosya, engine='openpyxl') as writer:
            df_ai.to_excel(writer, sheet_name="AI_Strateji", index=False)
            df_pers.to_excel(writer, sheet_name="Personel", index=False)
        return dosya
    except Exception as e:
        print(f"❌ Excel hatası: {e}")
        return None

def grafik_olustur():
    """
    Streamlit arayüzünde gösterilecek Matplotlib grafiklerini çizer.
    """
    df_raw = veri_yukle()
    fig = Figure(figsize=(12, 8), dpi=100)
    
    if df_raw.empty:
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "❌ Veri yok. Demo veri oluşturun.", 
                ha='center', va='center', color="white", fontsize=14)
        return fig
    
    # --- GRAFİK 1: FİNANSAL AKIŞ (Çizgi Grafiği) ---
    ax1 = fig.add_subplot(211) # 2 satır, 1 sütunluk alanın 1. grafiği
    gunluk = df_raw.groupby(df_raw["Tarih"].dt.date)[["Fiyat", "Kar"]].sum().tail(30)
    x = range(len(gunluk))
    # Ciro Alanı
    ax1.fill_between(x, gunluk["Fiyat"], color="#00d2ff", alpha=0.2)
    ax1.plot(x, gunluk["Fiyat"], color="#00d2ff", label="Ciro")
    # Kâr Alanı
    ax1.fill_between(x, gunluk["Kar"], color="#00ff00", alpha=0.3)
    ax1.plot(x, gunluk["Kar"], color="#00ff00", linestyle="--", label="Kâr")
    ax1.legend()
    ax1.set_title("Finansal Akış (Son 30 Gün)", color="white")
    ax1.tick_params(colors="white")
    
    # --- GRAFİK 2: HEATMAP (Sıcaklık Haritası) ---
    # Hangi günün hangi saatinde restoranın yoğun olduğunu gösterir.
    ax2 = fig.add_subplot(223)
    df_raw["Saat"] = df_raw["Tarih"].dt.hour
    df_raw["Gun"] = df_raw["Tarih"].dt.day_name()
    
    # Pivot tablo oluştur (Satırlar: Günler, Sütunlar: Saatler)
    yogunluk = df_raw.pivot_table(index="Gun", columns="Saat", values="Fiyat", aggfunc="count").fillna(0)
    sirali_gunler = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    yogunluk = yogunluk.reindex(sirali_gunler)
    
    sns.heatmap(yogunluk, cmap="magma", ax=ax2, cbar=False, linewidths=0.5, linecolor='black')
    ax2.set_title("İş Yeri Yoğunluk Haritası (Gün/Saat)", color="white")
    ax2.set_xlabel("Saatler (11:00 - 23:00)", color="white")
    ax2.set_ylabel("", color="white")
    ax2.tick_params(colors="white", labelsize=8)
    
    # --- GRAFİK 3: CİRO KAYNAKLARI (Pasta Grafiği) ---
    ax3 = fig.add_subplot(224)
    ciro_dag = df_raw.groupby("Yemek Adi")["Fiyat"].sum().sort_values(ascending=False).head(5)
    ax3.pie(ciro_dag, labels=ciro_dag.index, autopct='%1.1f%%', colors=sns.color_palette("bright"), textprops={'color':"white"})
    ax3.set_title("En Çok Ciro Getiren 5 Ürün", color="white")
    
    fig.tight_layout(pad=3.0)
    return fig
#Alperen
import sqlite3
import os
from datetime import datetime

DOSYA_ADI = "restoran_verisi.db"

def baslangic_kontrol():
    """Veritabanı ve tablo oluşturur"""
    try:
        conn = sqlite3.connect(DOSYA_ADI)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS siparisler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Tarih TEXT NOT NULL,
                "Yemek Adi" TEXT NOT NULL,
                Fiyat REAL NOT NULL,
                Maliyet REAL NOT NULL,
                "Hazirlanma Suresi" INTEGER NOT NULL,
                Garson TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print(f"✅ Veritabanı hazır: {DOSYA_ADI}")
    except sqlite3.Error as e:
        print(f"❌ Veritabanı hatası: {e}")

def siparis_kaydet(siparis):
    """Sipariş veritabanına kaydedilir"""
    baslangic_kontrol()
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        conn = sqlite3.connect(DOSYA_ADI, timeout=10)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO siparisler 
            (Tarih, "Yemek Adi", Fiyat, Maliyet, "Hazirlanma Suresi", Garson) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tarih, 
            siparis.yemek.isim, 
            float(siparis.yemek.fiyat),
            float(siparis.yemek.maliyet),
            int(siparis.yemek.hazirlanma_suresi),
            siparis.garson_adi
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Kaydedildi: {siparis.yemek.isim} - {siparis.garson_adi}")
    except sqlite3.Error as e:
        print(f"❌ KAYIT HATASI: {e}")
    except Exception as e:
        print(f"❌ GENEL HATA: {e}")
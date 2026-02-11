import sqlite3
import os
from datetime import datetime
# Atilla 

DOSYA_ADI = "restoran_verisi.db" # Oluşturulacak veritabanı dosyasının adı

def baslangic_kontrol():
    """Veritabanı ve tablo oluşturur"""
    try:
        # Veritabanına bağlanır. Eğer dosya yoksa otomatik olarak oluşturur.
        conn = sqlite3.connect(DOSYA_ADI)
        cursor = conn.cursor() # SQL komutlarını çalıştırmak için imleç (cursor) oluşturur
        
        # SQL Sorgusu: Eğer 'siparisler' tablosu daha önce oluşturulmamışsa oluşturur.
        # Tablo sütunları ve veri tipleri burada tanımlanır.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS siparisler (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- Her sipariş için benzersiz, otomatik artan numara
                Tarih TEXT NOT NULL,                  -- Sipariş zamanı
                "Yemek Adi" TEXT NOT NULL,            -- Yemeğin ismi
                Fiyat REAL NOT NULL,                  -- Ondalıklı sayı (Para birimi)
                Maliyet REAL NOT NULL,                -- Yemeğin maliyeti
                "Hazirlanma Suresi" INTEGER NOT NULL, -- Saniye cinsinden tam sayı
                Garson TEXT NOT NULL                  -- Siparişi giren kişi
            )
        """)
        conn.commit() # Yapılan değişiklikleri (tablo oluşturma) kaydeder
        conn.close()  # Bağlantıyı kapatır
        print(f"✅ Veritabanı hazır: {DOSYA_ADI}")
    except sqlite3.Error as e:
        # Veritabanı oluşturulurken bir hata çıkarsa ekrana basar
        print(f"❌ Veritabanı hatası: {e}")

def siparis_kaydet(siparis):
    """Sipariş veritabanına kaydedilir"""
    # Kayıt yapmadan önce tablonun varlığından emin olmak için kontrol fonksiyonunu çağırır
    baslangic_kontrol()
    
    # Şu anki zamanı alır ve string formatına (Yıl-Ay-Gün Saat:Dakika:Saniye) çevirir
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Veritabanına bağlanır (timeout=10: Veritabanı meşgulse 10 saniye bekler)
        conn = sqlite3.connect(DOSYA_ADI, timeout=10)
        cursor = conn.cursor()
        
        # SQL Parametreli Sorgu (Güvenlik için):
        # VALUES (?, ?, ...) kısımlarına aşağıdaki parantez içindeki değişkenler yerleştirilir.
        # Bu yöntem SQL Injection saldırılarını önler.
        cursor.execute("""
            INSERT INTO siparisler 
            (Tarih, "Yemek Adi", Fiyat, Maliyet, "Hazirlanma Suresi", Garson) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tarih, 
            siparis.yemek.isim, 
            float(siparis.yemek.fiyat),            # Veri tipini garantiye almak için float'a çeviriyoruz
            float(siparis.yemek.maliyet),
            int(siparis.yemek.hazirlanma_suresi),  # Veri tipini garantiye almak için int'e çeviriyoruz
            siparis.garson_adi
        ))
        
        conn.commit() # Veriyi kalıcı olarak veritabanına yazar
        conn.close()  # İşlem bitince bağlantıyı kapatır
        print(f"✅ Kaydedildi: {siparis.yemek.isim} - {siparis.garson_adi}")
    except sqlite3.Error as e:
        # SQLite ile ilgili spesifik hataları yakalar
        print(f"❌ KAYIT HATASI: {e}")
    except Exception as e:
        # Beklenmedik diğer tüm hataları yakalar
        print(f"❌ GENEL HATA: {e}")
import csv
import os
from datetime import datetime

DOSYA_ADI = "siparis_gecmisi.csv"

def baslangic_kontrol():
    if not os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, mode='w', newline='', encoding='utf-8') as dosya:
            yazici = csv.writer(dosya)
            # YENİ SÜTUN: Garson
            yazici.writerow(["Tarih", "Yemek Adi", "Fiyat", "Maliyet", "Hazirlanma Suresi", "Garson"])

def siparis_kaydet(siparis):
    baslangic_kontrol()
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(DOSYA_ADI, mode='a', newline='', encoding='utf-8') as dosya:
        yazici = csv.writer(dosya)
        yazici.writerow([
            tarih, 
            siparis.yemek.isim, 
            siparis.yemek.fiyat,
            siparis.yemek.maliyet,
            siparis.yemek.hazirlanma_suresi,
            siparis.garson_adi # Veritabanına yazılıyor
        ])
    print(f"Kayıt Başarılı: {siparis.yemek.isim} - {siparis.garson_adi}")
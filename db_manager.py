import sqlite3
import pandas as pd
from datetime import datetime

DOSYA_ADI = "restoran_verisi.db"

# Demo süreleri (Saniye)
HAZIRLANMA_SURELERI = {
    "Mercimek": 3, "İskender": 6, "Adana": 5, "Künefe": 4, "Su": 1,
    "Kola": 1, "Beyti": 5, "Gavurdağı": 3, "Ezogelin": 3, "Ayran": 1
}

RECETELER = {
    "Mercimek": {"Mercimek": 50, "Salça": 10, "Su": 200},
    "İskender": {"Döner Eti": 150, "Pide": 1, "Tereyağı": 20, "Yoğurt": 50},
    "Adana": {"Kıyma": 180, "Kuyruk Yağı": 20, "Lavaş": 1},
    "Künefe": {"Kadayıf": 100, "Peynir": 50, "Şerbet": 50},
    "Su": {"Su Şişe": 1},
    "Kola": {"Kola Kutu": 1},
    "Beyti": {"Kıyma": 200, "Yufka": 1, "Domates Sosu": 30, "Yoğurt": 50},
    "Gavurdağı": {"Domates": 2, "Ceviz": 20, "Salatalık": 1},
    "Ezogelin": {"Mercimek": 40, "Pirinç": 10, "Salça": 10},
    "Ayran": {"Yoğurt": 100, "Su": 100},
}

def init_db():
    # --- PERFORMANS AYARI: WAL MODU ---
    with sqlite3.connect(DOSYA_ADI) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")  # Kilitlenmeyi önler
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS siparisler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Tarih TEXT, "Yemek Adi" TEXT, Fiyat REAL, 
                Maliyet REAL, Garson TEXT, Masa TEXT, Durum TEXT DEFAULT 'Hazırlanıyor'
            )
        """)
        cursor.execute("CREATE TABLE IF NOT EXISTS stok (malzeme TEXT PRIMARY KEY, miktar REAL, birim TEXT)")
        
        # Başlangıç stoğu
        cursor.execute("SELECT count(*) FROM stok")
        if cursor.fetchone()[0] == 0:
            baslangic = [("Mercimek", 5000, "gr"), ("Salça", 1000, "gr"), ("Su", 20000, "ml"), ("Döner Eti", 5000, "gr"), ("Pide", 50, "adet"), ("Tereyağı", 1000, "gr"), ("Yoğurt", 5000, "gr"), ("Kıyma", 10000, "gr"), ("Kuyruk Yağı", 1000, "gr"), ("Lavaş", 100, "adet"), ("Kadayıf", 2000, "gr"), ("Peynir", 1000, "gr"), ("Şerbet", 2000, "ml"), ("Su Şişe", 100, "adet"), ("Kola Kutu", 100, "adet"), ("Yufka", 100, "adet"), ("Domates Sosu", 2000, "gr"), ("Domates", 50, "adet"), ("Ceviz", 1000, "gr"), ("Salatalık", 50, "adet"), ("Pirinç", 1000, "gr")]
            cursor.executemany("INSERT INTO stok VALUES (?,?,?)", baslangic)
            conn.commit()

def verileri_sifirla():
    try:
        with sqlite3.connect(DOSYA_ADI) as conn:
            conn.execute("DELETE FROM siparisler")
        return True
    except: return False

def stok_kontrol(yemek_adi):
    if yemek_adi not in RECETELER: return True, "Mevcut"
    try:
        with sqlite3.connect(DOSYA_ADI, timeout=5) as conn: # Timeout arttırıldı
            cursor = conn.cursor()
            malzemeler = RECETELER[yemek_adi]
            max_uretim = 9999
            for mlz, gereken in malzemeler.items():
                cursor.execute("SELECT miktar FROM stok WHERE malzeme=?", (mlz,))
                res = cursor.fetchone()
                if not res: return False, "Stok Yok"
                mumkun = int(res[0] // gereken)
                if mumkun < max_uretim: max_uretim = mumkun
            if max_uretim <= 0: return False, "TÜKENDİ"
            elif max_uretim <= 5: return True, f"KRİTİK ({max_uretim})"
            return True, "Mevcut"
    except: return False, "Hata"

def siparis_ver(yemek, garson, masa_no):
    durum, msg = stok_kontrol(yemek["isim"])
    if not durum: return False, msg
    
    try:
        with sqlite3.connect(DOSYA_ADI, timeout=5) as conn:
            cursor = conn.cursor()
            if yemek["isim"] in RECETELER:
                for mlz, gereken in RECETELER[yemek["isim"]].items():
                    cursor.execute("UPDATE stok SET miktar = miktar - ? WHERE malzeme = ?", (gereken, mlz))
            
            tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO siparisler (Tarih, \"Yemek Adi\", Fiyat, Maliyet, Garson, Masa, Durum) VALUES (?,?,?,?,?,?, 'Hazırlanıyor')", 
                           (tarih, yemek["isim"], yemek["fiyat"], yemek["maliyet"], garson, masa_no))
            conn.commit()
        return True, "Alındı"
    except Exception as e: return False, str(e)

def siparis_durum_guncelle(siparis_id, yeni_durum):
    try:
        with sqlite3.connect(DOSYA_ADI, timeout=5) as conn:
            conn.execute("UPDATE siparisler SET Durum = ? WHERE id = ?", (yeni_durum, siparis_id))
            conn.commit()
        return True
    except: return False

def stok_ekle(malzeme, miktar):
    try:
        with sqlite3.connect(DOSYA_ADI, timeout=5) as conn:
            conn.execute("UPDATE stok SET miktar = miktar + ? WHERE malzeme = ?", (miktar, malzeme))
            conn.commit()
        return True, "OK"
    except Exception as e: return False, str(e)

# --- OPTİMİZE EDİLMİŞ SÜRE KONTROLÜ ---
def mutfak_surec_kontrol():
    try:
        with sqlite3.connect(DOSYA_ADI, timeout=1) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, Tarih, \"Yemek Adi\" FROM siparisler WHERE Durum='Hazırlanıyor'")
            bekleyenler = cursor.fetchall()
            
            simdi = datetime.now()
            guncellenecekler = []
            
            for sip in bekleyenler:
                sip_id, tarih_str, yemek = sip
                try:
                    sip_tarih = datetime.strptime(tarih_str, "%Y-%m-%d %H:%M:%S")
                    gecen = (simdi - sip_tarih).total_seconds()
                    hedef = HAZIRLANMA_SURELERI.get(yemek, 5)
                    
                    if gecen >= hedef:
                        guncellenecekler.append((sip_id,))
                except: continue
            
            if guncellenecekler:
                cursor.executemany("UPDATE siparisler SET Durum = 'HAZIR' WHERE id = ?", guncellenecekler)
                conn.commit()
    except: pass
import pandas as pd
import sqlite3
import os

def verileri_tasi():
    csv_dosyasi = "siparis_gecmisi.csv"
    db_dosyasi = "restoran_verisi.db"

    # 1. Kontrol: CSV dosyası var mı?
    if not os.path.exists(csv_dosyasi):
        print("Hata: Aktarılacak 'siparis_gecmisi.csv' dosyası bulunamadı!")
        return

    print("Veriler okunuyor...")
    # 2. CSV verisini oku
    df = pd.read_csv(csv_dosyasi)

    # 3. SQLite'a bağlan (Dosya yoksa otomatik oluşur)
    conn = sqlite3.connect(db_dosyasi)
    
    try:
        # 4. Veriyi 'siparisler' tablosuna aktar
        # index=False: Satır numaralarını aktarma
        # if_exists='append': Eğer tablo varsa üzerine ekle (silme)
        df.to_sql("siparisler", conn, if_exists="append", index=False)
        print(f"Başarılı! {len(df)} adet sipariş SQLite'a taşındı.")
    except Exception as e:
        print(f"Aktarım sırasında hata oluştu: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verileri_tasi()
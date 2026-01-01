import sqlite3

def test_sqlite():
    try:
        # 1. Veritabanına bağlan (Dosya yoksa oluşturur)
        conn = sqlite3.connect('test_baglanti.db')
        cursor = conn.cursor()
        
        # 2. Test amaçlı bir tablo oluştur
        cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER, ad TEXT)")
        
        # 3. Veri ekle
        cursor.execute("INSERT INTO test VALUES (1, 'Deneme Verisi')")
        conn.commit()
        
        # 4. Veriyi oku
        cursor.execute("SELECT ad FROM test")
        sonuc = cursor.fetchone()
        
        print(f"Bağlantı Başarılı! Okunan Veri: {sonuc[0]}")
        
        conn.close()
    except Exception as e:
        print(f"Hata Oluştu: {e}")

test_sqlite()

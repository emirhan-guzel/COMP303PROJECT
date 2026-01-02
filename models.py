import time

# Atilla 
class Yemek:
    # Menüdeki bir yemeği temsil eden sınıf (İsim, fiyat, maliyet vb.)
    def __init__(self, isim, fiyat, maliyet, hazirlanma_suresi):
        self.isim = isim
        self._fiyat = fiyat  # _ (alt çizgi) bu değişkenin doğrudan değiştirilmemesi gerektiğini belirtir (Kapsülleme)
        self.maliyet = maliyet
        self.hazirlanma_suresi = hazirlanma_suresi 

    @property
    def fiyat(self):
        # Yemeğin fiyatını okumak istendiğinde burası çalışır (Getter)
        return self._fiyat

    @fiyat.setter
    def fiyat(self, deger):
        # Yemeğin fiyatı değiştirilmek istendiğinde burası çalışır (Setter)
        # Fiyatın negatif girilmesini engeller
        if deger < 0: raise ValueError("Negatif fiyat olamaz!")
        self._fiyat = deger
    
    @property
    def kar(self):
        # Yemeğin kârını anlık hesaplar (Satış Fiyatı - Maliyet)
        return self._fiyat - self.maliyet

class Siparis:
    # GÜNCELLEME: Artık siparişi alan garsonun ismini de alıyoruz
    def __init__(self, masa_no, yemek, garson_adi="Sistem"):
        self.masa_no = masa_no
        self.yemek = yemek           # Sipariş edilen Yemek nesnesi
        self.garson_adi = garson_adi # YENİ ALAN: Siparişi giren garson
        self.durum = "Bekliyor"      # Siparişin varsayılan durumu
        self.siparis_zamani = time.time() # Siparişin verildiği anı kaydeder

class Masa:
    # Restorandaki bir masayı ve o masanın hesabını yönetir
    def __init__(self, masa_no):
        self.masa_no = masa_no
        self.siparisler = []  # Masaya verilen tüm siparişlerin listesi
        self.hesap = 0.0      # Masanın ödemesi gereken toplam tutar

    def siparis_ekle(self, siparis):
        # Listeye yeni siparişi ekler
        self.siparisler.append(siparis)
        # Yeni gelen yemeğin fiyatını toplam hesaba ekler
        self.hesap += siparis.yemek.fiyat
import time

class Yemek:
    def __init__(self, isim, fiyat, maliyet, hazirlanma_suresi):
        self.isim = isim
        self._fiyat = fiyat
        self.maliyet = maliyet
        self.hazirlanma_suresi = hazirlanma_suresi 

    @property
    def fiyat(self):
        return self._fiyat

    @fiyat.setter
    def fiyat(self, deger):
        if deger < 0: raise ValueError("Negatif fiyat olamaz!")
        self._fiyat = deger
    
    @property
    def kar(self):
        return self._fiyat - self.maliyet

class Siparis:
    # GÜNCELLEME: Artık siparişi alan garsonun ismini de alıyoruz
    def __init__(self, masa_no, yemek, garson_adi="Sistem"):
        self.masa_no = masa_no
        self.yemek = yemek
        self.garson_adi = garson_adi # YENİ ALAN
        self.durum = "Bekliyor" 
        self.siparis_zamani = time.time()

class Masa:
    def __init__(self, masa_no):
        self.masa_no = masa_no
        self.siparisler = [] 
        self.hesap = 0.0

    def siparis_ekle(self, siparis):
        self.siparisler.append(siparis)
        self.hesap += siparis.yemek.fiyat
import threading
import time

# Atilla Thread kısımları Önemli. 
class Mutfak:
    def __init__(self):
        # Mutfakta o an pişen yemekleri takip eden liste
        self.aktif_siparisler = []

    def siparisi_pisir(self, siparis, callback_fonksiyonu):
        # Siparişi listeye ekle (Yoğunluk hesabı için)
        self.aktif_siparisler.append(siparis)
        
        t = threading.Thread(target=self._pisirme_sureci, args=(siparis, callback_fonksiyonu))
        t.start()

    def _pisirme_sureci(self, siparis, callback):
        siparis.durum = "Hazırlanıyor..."
        
        # Simülasyon: Yemeğin süresi kadar bekle
        time.sleep(siparis.yemek.hazirlanma_suresi)
        
        siparis.durum = "HAZIR!"
        # Yemek pişince listeden çıkar (Artık yoğunluk yaratmıyor)
        if siparis in self.aktif_siparisler:
            self.aktif_siparisler.remove(siparis)
            
        if callback:
            callback(siparis)

    def tahmini_bekleme_suresi_hesapla(self, yeni_yemek_suresi):
        """
        Mevcut yoğunluğa göre müşteriye tahmini süre verir.
        Mantık: (Mevcut İşlerin Toplam Süresi / Aşçı Sayısı) + Yeni Yemek
        Biz burada ortalama 2 aşçı çalışıyor gibi bir algoritma kuruyoruz.
        """
        if not self.aktif_siparisler:
            return yeni_yemek_suresi
        
        toplam_bekleyen_saniye = sum([s.yemek.hazirlanma_suresi for s in self.aktif_siparisler])
        
        # Algoritma: Mutfaktaki iş yükünü biraz hafifleterek yansıtıyoruz (Paralel çalışma payı)
        tahmini_sure = (toplam_bekleyen_saniye / 2) + yeni_yemek_suresi
        
        return round(tahmini_sure, 1)  
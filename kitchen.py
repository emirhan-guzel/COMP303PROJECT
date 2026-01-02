import threading
import time

# Atilla 
class Mutfak:
    # Mutfak işleyişini ve çoklu pişirme (threading) süreçlerini yöneten sınıf
    def __init__(self):
        # Mutfakta o an pişen yemekleri takip eden liste
        self.aktif_siparisler = []

    def siparisi_pisir(self, siparis, callback_fonksiyonu):
        # Siparişi listeye ekle (Yoğunluk hesabı için kullanılır)
        self.aktif_siparisler.append(siparis)
        
        # Threading (İş Parçacığı) Kullanımı:
        # target: Arka planda çalışacak fonksiyon (_pisirme_sureci)
        # args: O fonksiyona gönderilecek veriler (siparis ve bildirim fonksiyonu)
        # Bu işlem sayesinde yemek pişerken program donmaz, diğer işlemler devam eder.
        t = threading.Thread(target=self._pisirme_sureci, args=(siparis, callback_fonksiyonu))
        t.start() # İş parçacığını başlatır

    def _pisirme_sureci(self, siparis, callback):
        # Bu metod ana programdan bağımsız, ayrı bir thread içinde çalışır
        siparis.durum = "Hazırlanıyor..."
        
        # Simülasyon: Yemeğin hazırlanma süresi kadar kodu duraklatır (uyutur)
        time.sleep(siparis.yemek.hazirlanma_suresi)
        
        siparis.durum = "HAZIR!"
        # Yemek pişince listeden çıkar (Artık yoğunluk yaratmıyor)
        if siparis in self.aktif_siparisler:
            self.aktif_siparisler.remove(siparis)
            
        # Yemek hazır olduğunda, ilgili fonksiyonu (callback) çağırarak haber verir
        if callback:
            callback(siparis)

    def tahmini_bekleme_suresi_hesapla(self, yeni_yemek_suresi):
        """
        Mevcut yoğunluğa göre müşteriye tahmini süre verir.
        Mantık: (Mevcut İşlerin Toplam Süresi / Aşçı Sayısı) + Yeni Yemek
        Biz burada ortalama 2 aşçı çalışıyor gibi bir algoritma kuruyoruz.
        """
        # Eğer mutfakta hiç sipariş yoksa sadece yeni yemeğin süresini döndür
        if not self.aktif_siparisler:
            return yeni_yemek_suresi
        
        # O an yapılan tüm yemeklerin sürelerini toplar
        toplam_bekleyen_saniye = sum([s.yemek.hazirlanma_suresi for s in self.aktif_siparisler])
        
        # Algoritma: Mutfaktaki iş yükünü biraz hafifleterek yansıtıyoruz (Paralel çalışma payı)
        # Toplam yükü 2'ye bölüyoruz (2 ocak/aşçı varmış varsayımı) + yeni sipariş süresi
        tahmini_sure = (toplam_bekleyen_saniye / 2) + yeni_yemek_suresi
        
        # Sonucu virgülden sonra tek basamak kalacak şekilde yuvarlar
        return round(tahmini_sure, 1)
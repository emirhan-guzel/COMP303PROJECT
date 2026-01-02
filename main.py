import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.scrolledtext import ScrolledText
import os
import threading
import datetime
from matplotlib.figure import Figure
import seaborn as sns

from models import Masa, Yemek, Siparis
from kitchen import Mutfak
from database import siparis_kaydet, DOSYA_ADI, baslangic_kontrol
from analiz import grafik_olustur, yapay_zeka_tahmini_yap, excel_raporu_indir, personel_performansi_getir

# --- KULLANICI VERİTABANI ---
USERS = {
    "admin":  {"sifre": "1234", "rol": "yonetici", "isim": "Yönetici"},
    "ali":    {"sifre": "1111", "rol": "garson",   "isim": "Ali"},
    "ayse":   {"sifre": "2222", "rol": "garson",   "isim": "Ayşe"},
    "mehmet": {"sifre": "3333", "rol": "garson",   "isim": "Mehmet"}
}

class LoginWindow:  
    def __init__(self):
        self.root = ttk.Window(themename="superhero")
        self.root.title("GastroAnalyst - Güvenli Giriş")
        self.root.geometry("450x550")
        
        # SQLite tablosu oluştur
        baslangic_kontrol()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill="both")

        lbl_baslik = ttk.Label(main_frame, text="GASTRO ANALYST\nAI SYSTEM", 
                              font=("Helvetica", 24, "bold"), bootstyle="info", justify="center")
        lbl_baslik.pack(pady=(40, 30))
        
        login_frame = ttk.Labelframe(main_frame, text="Personel Girişi", padding=20, bootstyle="secondary")
        login_frame.pack(fill="x")

        ttk.Label(login_frame, text="Kullanıcı Adı:", font=("Arial", 10)).pack(anchor="w")
        self.ent_user = ttk.Entry(login_frame, font=("Arial", 12))
        self.ent_user.pack(pady=(5, 15), fill="x")
        
        ttk.Label(login_frame, text="Şifre:", font=("Arial", 10)).pack(anchor="w")
        self.ent_pass = ttk.Entry(login_frame, show="●", font=("Arial", 12))
        self.ent_pass.pack(pady=(5, 20), fill="x")
        
        btn_giris = ttk.Button(login_frame, text="SİSTEME GİRİŞ YAP", bootstyle="success", command=self.giris_yap)
        btn_giris.pack(fill="x", ipady=10)
        
        self.root.mainloop()

    def giris_yap(self):
        user = self.ent_user.get().lower()
        password = self.ent_pass.get()
        
        if user in USERS and USERS[user]["sifre"] == password:
            user_data = USERS[user]
            self.root.destroy()
            app_root = ttk.Window(themename="superhero")
            RestoranApp(app_root, user_data)
            app_root.mainloop()
        else:
            messagebox.showerror("Hata", "Hatalı Kullanıcı Adı veya Şifre!")

class RestoranApp:
    def __init__(self, root, user_data):
        self.root = root
        self.user = user_data
        self.root.title(f"GastroAnalyst AI - Aktif: {self.user['isim']} ({self.user['rol'].upper()})")
        self.root.geometry("1600x900")
        
        self.mutfak = Mutfak()
        self.masalar = [Masa(i) for i in range(1, 13)]
        self.aktif_masa = self.masalar[0]
        self.sepetler = {masa.masa_no: [] for masa in self.masalar}

        self.menu = [
            Yemek("Mercimek", 40, 12, 3), Yemek("Ezogelin", 40, 12, 3),
            Yemek("İskender", 150, 65, 8), Yemek("Beyti", 160, 70, 9),
            Yemek("Adana", 140, 60, 7), Yemek("Künefe", 80, 35, 5),
            Yemek("Gavurdağı", 60, 20, 3), Yemek("Su", 10, 2, 1),
            Yemek("Kola", 25, 15, 1), Yemek("Ayran", 15, 5, 1)
        ]

        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', 12, 'bold'), padding=[10, 5])

        # ÜST BAR
        top_bar = ttk.Frame(self.root, padding=5)
        top_bar.pack(fill="x")
        ttk.Label(top_bar, text=f"👤 {self.user['isim']}", font=("Arial", 12, "bold"), bootstyle="info").pack(side="left", padx=10)
        ttk.Button(top_bar, text="🚪 ÇIKIŞ YAP", bootstyle="danger", command=self.cikis_yap).pack(side="right", padx=10)

        self.tabs = ttk.Notebook(self.root, bootstyle="primary")
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # SEKMELER
        self.tab_salon = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_salon, text=" 🍽️ SALON & SİPARİŞ ")
        self.salon_arayuzu_olustur()
        
        self.tab_mutfak = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_mutfak, text=" 👨‍🍳 CANLI MUTFAK ")
        self.mutfak_arayuzu_olustur()

        if self.user["rol"] == "yonetici":
            self.tab_analiz = ttk.Frame(self.tabs)
            self.tabs.add(self.tab_analiz, text=" 📊 FİNANSAL ANALİZ ")
            self.analiz_arayuzu_olustur()

            self.tab_strateji = ttk.Frame(self.tabs)
            self.tabs.add(self.tab_strateji, text=" 🧠 AI STRATEJİ ")
            self.strateji_arayuzu_olustur()
            
            self.tab_personel = ttk.Frame(self.tabs)
            self.tabs.add(self.tab_personel, text=" 👔 PERSONEL PERFORMANS ")
            self.personel_arayuzu_olustur()
        
        self.log_ekle(f"Oturum Açıldı: {self.user['isim']}", "SYSTEM")

    def cikis_yap(self):
        if messagebox.askyesno("Çıkış", "Oturumu kapatmak istediğine emin misin?"):
            self.root.destroy()
            LoginWindow()

    # --- ARAYÜZLER ---
    
    def salon_arayuzu_olustur(self):
        frame_masalar = ttk.Labelframe(self.tab_salon, text="Masa Durumları", bootstyle="primary", padding=10)
        frame_masalar.place(x=10, y=10, width=450, height=780)
        row, col = 0, 0
        for i, masa in enumerate(self.masalar):
            btn = ttk.Button(frame_masalar, text=f"Masa {masa.masa_no}\n(Boş)", bootstyle="secondary-outline", command=lambda m=masa: self.masa_sec(m))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew", ipady=20)
            masa.buton = btn
            col += 1
            if col > 2: col=0; row+=1
        frame_masalar.columnconfigure(0, weight=1)
        frame_masalar.columnconfigure(1, weight=1)
        frame_masalar.columnconfigure(2, weight=1)

        frame_menu = ttk.Labelframe(self.tab_salon, text="Menü", bootstyle="info", padding=10)
        frame_menu.place(x=470, y=10, width=350, height=780)
        for yemek in self.menu:
            ttk.Button(frame_menu, text=f"{yemek.isim}\n{yemek.fiyat} TL", bootstyle="info-outline", command=lambda y=yemek: self.sepete_ekle(y)).pack(fill="x", pady=4, ipady=5)

        frame_sag = ttk.Frame(self.tab_salon)
        frame_sag.place(x=830, y=10, width=700, height=780)
        
        self.frame_sepet = ttk.Labelframe(frame_sag, text="Sipariş Sepeti", bootstyle="warning", padding=10)
        self.frame_sepet.pack(fill="both", expand=True, pady=(0, 10))
        self.liste_sepet = tk.Listbox(self.frame_sepet, font=("Consolas", 14), bg="#2c3e50", fg="#f39c12", borderwidth=0)
        self.liste_sepet.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        btn_frame = ttk.Frame(self.frame_sepet)
        btn_frame.pack(side="bottom", fill="x", pady=5)
        ttk.Button(btn_frame, text="🗑️ SEÇİLENİ SİL", bootstyle="danger", command=self.sepetten_cikar).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(btn_frame, text="✅ SİPARİŞİ ONAYLA", bootstyle="success", command=self.siparisi_onayla).pack(side="right", fill="x", expand=True, padx=5)

        self.frame_adisyon = ttk.Labelframe(frame_sag, text="Aktif Adisyon", bootstyle="secondary", padding=10)
        self.frame_adisyon.pack(fill="both", expand=True)
        self.liste_adisyon = tk.Listbox(self.frame_adisyon, font=("Consolas", 14), bg="#222", fg="#00ff00", borderwidth=0)
        self.liste_adisyon.pack(fill="both", expand=True, padx=5, pady=5)
        self.lbl_toplam = ttk.Label(self.frame_adisyon, text="TOPLAM: 0.00 TL", font=("Arial", 24, "bold"), bootstyle="inverse-secondary", anchor="center")
        self.lbl_toplam.pack(pady=10, fill="x")
        self.renkleri_guncelle()

    def mutfak_arayuzu_olustur(self):
        self.frame_kds = ttk.Labelframe(self.tab_mutfak, text="👨‍🍳 KDS - MUTFAK EKRANI", bootstyle="danger", padding=10)
        self.frame_kds.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.configure("Treeview", font=("Arial", 11), rowheight=30)
        self.tree_mutfak = ttk.Treeview(self.frame_kds, columns=("Masa","Urun","Durum","Garson"), show="headings", bootstyle="danger")
        self.tree_mutfak.heading("Masa", text="Masa")
        self.tree_mutfak.heading("Urun", text="Ürün")
        self.tree_mutfak.heading("Durum", text="Durum")
        self.tree_mutfak.heading("Garson", text="Garson")
        self.tree_mutfak.column("Masa", width=80, anchor="center")
        self.tree_mutfak.column("Durum", width=120, anchor="center")
        self.tree_mutfak.pack(fill="both", expand=True)
        
        self.frame_log = ttk.Labelframe(self.tab_mutfak, text="🖥️ SİSTEM LOGLARI", bootstyle="dark", padding=10)
        self.frame_log.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.text_log = ScrolledText(self.frame_log, state="disabled", bg="black", fg="#00ff00", font=("Consolas", 11))
        self.text_log.pack(fill="both", expand=True)

    def analiz_arayuzu_olustur(self):
        pnl_ust = ttk.Frame(self.tab_analiz, padding=10)
        pnl_ust.pack(fill="x")
        ttk.Button(pnl_ust, text="🔄 VERİLERİ GÜNCELLE", bootstyle="success-outline", command=self.analizi_baslat).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(pnl_ust, text="⚠️ DEMO VERİSİ YARAT", bootstyle="danger-outline", command=self.demo_sifirla).pack(side="right", fill="x", padx=5)
        self.frame_grafik = ttk.Frame(self.tab_analiz)
        self.frame_grafik.pack(fill="both", expand=True, padx=10, pady=5)

    def strateji_arayuzu_olustur(self):
        pnl_ust = ttk.Frame(self.tab_strateji, padding=10)
        pnl_ust.pack(fill="x")
        ttk.Button(pnl_ust, text="🧠 AI MODELİNİ ÇALIŞTIR", bootstyle="warning", command=self.analizi_baslat).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(pnl_ust, text="📥 EXCEL RAPORU İNDİR", bootstyle="primary", command=self.excel_baslat).pack(side="left", fill="x", expand=True, padx=5)
        self.frame_tablo = ttk.Labelframe(self.tab_strateji, text="🚀 YAPAY ZEKA DESTEKLİ BÜYÜME STRATEJİSİ", bootstyle="warning", padding=10)
        self.frame_tablo.pack(fill="both", expand=True, padx=10, pady=5)
        cols = ("Urun", "BuAy", "Tahmin", "Durum", "StokAction", "FiyatAction")
        self.tablo = ttk.Treeview(self.frame_tablo, columns=cols, show="headings", bootstyle="warning")
        for col in cols: 
            self.tablo.heading(col, text=col)
        self.tablo.pack(fill="both", expand=True)

    def personel_arayuzu_olustur(self):
        pnl_ust = ttk.Frame(self.tab_personel, padding=10)
        pnl_ust.pack(fill="x")
        ttk.Button(pnl_ust, text="🔄 PERFORMANS RAPORU ÇEK", bootstyle="info", command=self.personel_guncelle).pack(side="left", fill="x", expand=True, padx=10)
        pnl_govde = ttk.Frame(self.tab_personel)
        pnl_govde.pack(fill="both", expand=True, padx=10, pady=5)
        self.frame_personel_grafik = ttk.Labelframe(pnl_govde, text="Ciro Grafiği", bootstyle="primary", padding=10)
        self.frame_personel_grafik.pack(side="left", fill="both", expand=True, padx=5)
        self.frame_personel_tablo = ttk.Labelframe(pnl_govde, text="Çalışan Karnesi", bootstyle="success", padding=10)
        self.frame_personel_tablo.pack(side="right", fill="both", expand=True, padx=5)
        self.tablo_personel = ttk.Treeview(self.frame_personel_tablo, columns=("Isim", "Ciro", "Adet", "Kar"), show="headings")
        self.tablo_personel.heading("Isim", text="Garson")
        self.tablo_personel.heading("Ciro", text="Ciro")
        self.tablo_personel.heading("Adet", text="Adet")
        self.tablo_personel.heading("Kar", text="Kâr")
        self.tablo_personel.pack(fill="both", expand=True)

    def personel_guncelle(self):
        for i in self.tablo_personel.get_children(): 
            self.tablo_personel.delete(i)
        df_personel = personel_performansi_getir()
        if df_personel.empty: 
            return
        for index, row in df_personel.iterrows():
            self.tablo_personel.insert("", "end", values=(
                row["Garson"], 
                f"{int(row['Toplam_Ciro'])} TL", 
                f"{int(row['Siparis_Adedi'])} Adet", 
                f"{int(row['Toplam_Kar'])} TL"
            ))
        
        for widget in self.frame_personel_grafik.winfo_children(): 
            widget.destroy()
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        sns.barplot(x="Garson", y="Toplam_Ciro", data=df_personel, ax=ax, palette="viridis")
        ax.set_title("Garson Ciro Sıralaması", color="white")
        ax.tick_params(colors="white")
        canvas = FigureCanvasTkAgg(fig, master=self.frame_personel_grafik)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # --- MANTIK ---
    def siparisi_onayla(self):
        sepet = self.sepetler[self.aktif_masa.masa_no]
        if not sepet: 
            return
        
        tahmini_sure = self.mutfak.tahmini_bekleme_suresi_hesapla(
            sum([y.hazirlanma_suresi for y in sepet])
        )
        messagebox.showinfo("Onay", 
            f"✅ Mutfak Onayladı!\n🕒 Tahmini Süre: {int(tahmini_sure)}s")
        
        for yemek in sepet:
            sip = Siparis(self.aktif_masa.masa_no, yemek, garson_adi=self.user["isim"])
            
            # ÖNEMLİ: Sipariş BURADA kaydediliyor
            siparis_kaydet(sip)
            
            self.aktif_masa.siparis_ekle(sip)
            self.mutfak.siparisi_pisir(sip, self.yemek_hazir_oldu)
            self.log_ekle(f"{self.user['isim']} sipariş geçti: {yemek.isim}", "GARSON")
        
        self.sepetler[self.aktif_masa.masa_no] = []
        self.sepet_listesini_guncelle()
        self.renkleri_guncelle()
        self.adisyon_listesini_yenile()
        self.mutfak_listesini_guncelle()

    def log_ekle(self, mesaj, tur="INFO"):
        zaman = datetime.datetime.now().strftime("%H:%M:%S")
        self.text_log.config(state="normal")
        self.text_log.insert(tk.END, f"[{zaman}] [{tur}] > {mesaj}\n")
        self.text_log.see(tk.END)
        self.text_log.config(state="disabled")

    def mutfak_listesini_guncelle(self):
        for i in self.tree_mutfak.get_children(): 
            self.tree_mutfak.delete(i)
        for masa in self.masalar:
            for siparis in masa.siparisler:
                if siparis.durum == "Hazırlanıyor...":
                    self.tree_mutfak.insert("", "end", values=(
                        f"Masa {masa.masa_no}", 
                        siparis.yemek.isim, 
                        "🔥 PİŞİYOR", 
                        siparis.garson_adi
                    ))

    def yemek_hazir_oldu(self, siparis):
        # TEKRAR KAYDETME! Sadece UI güncelleniyor
        self.root.after(0, self.adisyon_listesini_yenile)
        self.root.after(0, self.mutfak_listesini_guncelle)
        self.log_ekle(f"✅ {siparis.yemek.isim} hazır!", "MUTFAK")

    def sepete_ekle(self, yemek):
        self.sepetler[self.aktif_masa.masa_no].append(yemek)
        self.sepet_listesini_guncelle()

    def sepetten_cikar(self):
        try:
            index = self.liste_sepet.curselection()[0]
            del self.sepetler[self.aktif_masa.masa_no][index]
            self.sepet_listesini_guncelle()
        except: 
            pass

    def sepet_listesini_guncelle(self):
        self.liste_sepet.delete(0, tk.END)
        toplam = 0
        for yemek in self.sepetler[self.aktif_masa.masa_no]:
            self.liste_sepet.insert(tk.END, f"🛒 {yemek.isim} - {yemek.fiyat} TL")
            toplam += yemek.fiyat
        self.frame_sepet.config(text=f"Masa {self.aktif_masa.masa_no} - Sepet Toplamı: {toplam} TL")

    def masa_sec(self, masa):
        self.aktif_masa = masa
        self.frame_sepet.config(text=f"Masa {masa.masa_no} - Sepet")
        self.frame_adisyon.config(text=f"Masa {masa.masa_no} - Adisyon")
        self.renkleri_guncelle()
        self.sepet_listesini_guncelle()
        self.adisyon_listesini_yenile()

    def adisyon_listesini_yenile(self):
        self.liste_adisyon.delete(0, tk.END)
        for siparis in self.aktif_masa.siparisler:
            icon = "✅" if siparis.durum == "HAZIR!" else "🔥"
            self.liste_adisyon.insert(tk.END, 
                f"{icon} {siparis.yemek.isim:<12} | {siparis.yemek.fiyat} TL | ({siparis.garson_adi})")
        self.lbl_toplam.config(text=f"TOPLAM: {self.aktif_masa.hesap} TL")

    def renkleri_guncelle(self):
        for masa in self.masalar:
            txt = f"Masa {masa.masa_no}\n"
            if masa == self.aktif_masa: 
                masa.buton.configure(bootstyle="success")
                txt+="(SEÇİLİ)"
            elif len(masa.siparisler)>0: 
                masa.buton.configure(bootstyle="danger")
                txt+=f"({masa.hesap} TL)"
            else: 
                masa.buton.configure(bootstyle="secondary-outline")
                txt+="(Boş)"
            masa.buton.config(text=txt)

    def demo_sifirla(self):
        from analiz import demo_veri_olustur
        if messagebox.askyesno("Demo Veri", "Mevcut veriler silinip demo veri oluşturulsun mu?"):
            demo_veri_olustur()
            self.analizi_baslat()
            messagebox.showinfo("Başarılı", "Demo veri oluşturuldu!")

    def excel_baslat(self):
        dosya = excel_raporu_indir()
        if dosya: 
            messagebox.showinfo("Excel", f"İndirildi: {dosya}")

    def analizi_baslat(self):
        if not hasattr(self, 'tablo'): 
            return
        
        for widget in self.frame_grafik.winfo_children(): 
            widget.destroy()
        
        try:
            fig = grafik_olustur()
            canvas = FigureCanvasTkAgg(fig, master=self.frame_grafik)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            for i in self.tablo.get_children(): 
                self.tablo.delete(i)
            
            df_ai = yapay_zeka_tahmini_yap()
            for index, row in df_ai.iterrows():
                tag = "normal"
                if "BEST" in row["Durum"]: 
                    tag = "best"
                elif "MENÜDEN" in row["Durum"]: 
                    tag = "olu"
                self.tablo.insert("", "end", values=(
                    row["Urun"], 
                    row["BuAy"], 
                    row["Tahmin"], 
                    row["Durum"], 
                    row["StokAction"], 
                    row["FiyatAction"]
                ), tags=(tag,))
            
            self.tablo.tag_configure("best", foreground="#00ff00", font=("Arial", 10, "bold"))
            self.tablo.tag_configure("olu", foreground="#ff5555", font=("Arial", 10, "bold"))
        except Exception as e: 
            messagebox.showerror("Hata", str(e))

if __name__ == "__main__":
    LoginWindow()
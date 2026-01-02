import streamlit as st
import time
from datetime import datetime
import pandas as pd
import sqlite3
from db_manager import stok_kontrol, siparis_ver, siparis_durum_guncelle, mutfak_surec_kontrol, DOSYA_ADI

MENU = [
    {"isim": "Mercimek", "fiyat": 40, "maliyet": 12}, {"isim": "İskender", "fiyat": 150, "maliyet": 65},
    {"isim": "Adana", "fiyat": 140, "maliyet": 60}, {"isim": "Künefe", "fiyat": 80, "maliyet": 35},
    {"isim": "Su", "fiyat": 10, "maliyet": 2}, {"isim": "Kola", "fiyat": 25, "maliyet": 15},
    {"isim": "Beyti", "fiyat": 160, "maliyet": 70}, {"isim": "Gavurdağı", "fiyat": 60, "maliyet": 20},
    {"isim": "Ezogelin", "fiyat": 40, "maliyet": 12}, {"isim": "Ayran", "fiyat": 15, "maliyet": 4},
]

# --- SÜPER HIZLI CANLI MUTFAK (FRAGMENT) ---
# run_every=4 saniye idealdir, donmayı engeller.
@st.fragment(run_every=4)
def canli_mutfak_tablosu():
    mutfak_surec_kontrol() 
    
    # Bağlantıyı sadece okuma için açıp hemen kapatıyoruz
    try:
        with sqlite3.connect(DOSYA_ADI, timeout=3) as conn:
            sorgu = """SELECT id, Masa, Tarih, "Yemek Adi", Durum FROM siparisler 
                       WHERE Durum IN ('Hazırlanıyor', 'HAZIR') ORDER BY id DESC"""
            df_mutfak = pd.read_sql(sorgu, conn)
            
        st.caption(f"⚡ Son Veri: {datetime.now().strftime('%H:%M:%S')}")

        if df_mutfak.empty:
            st.success("Tüm siparişler servis edildi! Mutfak temiz. 👨‍🍳")
        else:
            for index, row in df_mutfak.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    
                    yemek_adi = row['Yemek Adi']
                    durum = row['Durum']
                    
                    if durum == "HAZIR":
                        durum_html = f"<h4 style='color:green; margin:0;'>✅ HAZIR</h4>"
                        btn_text = "🍽️ SERVİS"
                        btn_type = "primary"
                    else:
                        durum_html = f"<h4 style='color:orange; margin:0;'>🔥 PİŞİYOR</h4>"
                        btn_text = "⏳"
                        btn_type = "secondary"
                    
                    c1.markdown(f"**{yemek_adi}**")
                    c1.caption(f"📍 {row['Masa']} | 🕒 {row['Tarih'][-8:]}") 
                    c2.markdown(durum_html, unsafe_allow_html=True)
                    
                    # Butona basınca sadece bu alan güncellenir
                    if c3.button(btn_text, key=f"act_{row['id']}", 
                                 type=btn_type,
                                 disabled=(durum == "Hazırlanıyor")): 
                        siparis_durum_guncelle(row['id'], "TAMAMLANDI")
                        st.toast(f"{yemek_adi} servise çıktı!")
                        st.rerun()
                        
    except Exception as e: st.error(f"Bağlantı bekleniyor... ({e})")

def show(mode="siparis"):
    if 'selected_table' not in st.session_state: st.session_state.selected_table = None
    if 'cart' not in st.session_state: st.session_state.cart = []

    with st.sidebar:
        st.info(f"Kullanıcı: {st.session_state.user}")
        if mode == "siparis" and st.session_state.selected_table:
            st.warning(f"📍 AÇIK: {st.session_state.selected_table}")
            if st.button("🔙 MASALARA DÖN"):
                st.session_state.selected_table = None; st.session_state.cart = []; st.rerun()

    if mode == "siparis":
        st.markdown("## 🍽️ Sipariş Yönetimi")
        if not st.session_state.selected_table:
            st.markdown("### 🪑 Masa Seçimi")
            cols = st.columns(4)
            for i in range(1, 13):
                if cols[(i-1)%4].button(f"🪑 Masa {i}", use_container_width=True):
                    st.session_state.selected_table = f"Masa {i}"; st.rerun()
        else:
            secili_masa = st.session_state.selected_table
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader(f"📜 Menü ({secili_masa})")
                rows = [MENU[i:i+3] for i in range(0, len(MENU), 3)]
                for row in rows:
                    cols = st.columns(3)
                    for idx, y in enumerate(row):
                        ok, msg = stok_kontrol(y["isim"])
                        with cols[idx]:
                            with st.container(border=True):
                                st.write(f"**{y['isim']}**")
                                st.caption(f"{y['fiyat']} TL | {msg}")
                                if st.button("Ekle", key=f"b_{y['isim']}", disabled=not ok, use_container_width=True):
                                    st.session_state.cart.append(y); st.rerun()
            with c2:
                st.subheader("🛒 Sepet")
                if st.session_state.cart:
                    for i,x in enumerate(st.session_state.cart): st.text(f"{x['isim']}")
                    if st.button("✅ GÖNDER", type="primary", use_container_width=True):
                        for x in st.session_state.cart: siparis_ver(x, st.session_state.user, secili_masa)
                        st.session_state.cart = []; time.sleep(0.5); st.rerun()
                    if st.button("🗑️ İPTAL", use_container_width=True): st.session_state.cart = []; st.rerun()
                else: st.info("Boş")
            
            st.divider()
            st.subheader(f"🧾 {secili_masa} Adisyonu")
            try:
                with sqlite3.connect(DOSYA_ADI, timeout=3) as conn:
                    df = pd.read_sql("SELECT \"Yemek Adi\", Fiyat, Durum FROM siparisler WHERE Masa = ? AND Durum != 'TAMAMLANDI'", conn, params=(secili_masa,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    if st.button("💰 HESABI KAPAT", type="primary"):
                        with sqlite3.connect(DOSYA_ADI, timeout=3) as conn:
                            conn.execute("UPDATE siparisler SET Durum='TAMAMLANDI' WHERE Masa=?", (secili_masa,))
                            conn.commit()
                        st.session_state.selected_table=None; st.rerun()
                else: st.info("Sipariş yok.")
            except: st.error("Adisyon yüklenemedi.")

    elif mode == "mutfak":
        st.markdown("## 👨‍🍳 Canlı Mutfak Paneli")
        canli_mutfak_tablosu()
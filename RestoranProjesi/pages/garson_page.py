import streamlit as st
import pandas as pd

from models import Yemek
from services.stock_service import StockService
from services.kitchen_service import KitchenService

MENU = [
    Yemek("Mercimek", 40, 12, 3),
    Yemek("Ezogelin", 40, 12, 3),
    Yemek("İskender", 150, 65, 8),
    Yemek("Beyti", 160, 70, 9),
    Yemek("Adana", 140, 60, 7),
    Yemek("Künefe", 80, 35, 5),
    Yemek("Gavurdağı", 60, 20, 3),
    Yemek("Su", 10, 2, 1),
    Yemek("Kola", 25, 15, 1),
    Yemek("Ayran", 15, 5, 1),
]

class GarsonPage:
    def render(self, user: dict):
        st.title("🧾 Garson Paneli")
        st.markdown('<span class="badge">Sipariş</span><span class="badge">Stok Kontrol</span>', unsafe_allow_html=True)

        # stok.csv migrate (Esik kolonunu yoksa ekler)
        _ = StockService.load_df()

        KitchenService.flush_ready_to_csv(st.session_state.aktif_siparisler)

        masa_no = st.selectbox("Masa Seç", list(range(1, 13)), index=st.session_state.aktif_masa - 1)
        st.session_state.aktif_masa = masa_no

        left, right = st.columns([1.05, 0.95])
        with left:
            st.subheader("Menü")
            st.dataframe(
                pd.DataFrame([{"Ürün": y.isim, "Fiyat": y.fiyat, "Süre(dk)": y.hazirlanma_suresi} for y in MENU]),
                use_container_width=True, hide_index=True
            )
            colA, colB, colC = st.columns([1.2, 1, 0.8])
            with colA:
                sec = st.selectbox("Ürün Seç", [y.isim for y in MENU])
            with colB:
                adet = st.number_input("Adet", 1, 20, 1)
            with colC:
                if st.button("➕ Sepete Ekle", use_container_width=True):
                    y = next(x for x in MENU if x.isim == sec)
                    st.session_state.sepetler[masa_no].extend([y] * int(adet))
                    st.success(f"Eklendi: {sec} x{adet}")

        with right:
            st.subheader("Sepet")
            sepet = st.session_state.sepetler[masa_no]
            if not sepet:
                st.info("Sepet boş.")
                return

            st.dataframe(
                pd.DataFrame([{"Ürün": y.isim, "Fiyat": y.fiyat} for y in sepet]),
                use_container_width=True, hide_index=True
            )

            b1, b2 = st.columns(2)
            with b1:
                if st.button("🗑️ Sepeti Temizle", use_container_width=True):
                    st.session_state.sepetler[masa_no] = []
                    st.rerun()

            with b2:
                if st.button("✅ Siparişi Onayla", use_container_width=True):
                    ok, errors, warnings = StockService.validate_order(sepet)

                    if not ok:
                        st.error("Sipariş alınamadı ❌ (stok yetersiz)")
                        for e in errors:
                            st.write(e)
                        st.stop()

                    # stok düş
                    StockService.commit_order(sepet)

                    # mutfağa gönder
                    KitchenService.add_orders(st.session_state.aktif_siparisler, masa_no, user["isim"], sepet)

                    st.session_state.sepetler[masa_no] = []
                    st.success("Sipariş alındı ✅ Stok güncellendi 🔥")

                    if warnings:
                        st.warning(" / ".join(warnings))

                    st.rerun()

import streamlit as st
import pandas as pd
from services.kitchen_service import KitchenService

class MutfakPage:
    def render(self):
        st.title("👨‍🍳 Mutfak")
        KitchenService.flush_ready_to_csv(st.session_state.aktif_siparisler)

        active = st.session_state.aktif_siparisler
        if not active:
            st.info("Aktif sipariş yok.")
            return

        df = pd.DataFrame([{
            "Masa": o.masa_no,
            "Ürün": o.yemek.isim,
            "Durum": o.status,
            "Kalan(sn)": o.eta_seconds,
            "Garson": o.garson_adi
        } for o in active])

        st.dataframe(df, use_container_width=True, hide_index=True)

        if st.button("🧹 Hazırları Temizle", use_container_width=True):
            st.session_state.aktif_siparisler = [o for o in active if o.status != "HAZIR!"]
            st.rerun()

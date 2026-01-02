import streamlit as st
import pandas as pd
from services.stock_service import StockService, STOK_DOSYA

class StokPage:
    def render(self):
        st.title("📦 Stok Kontrolü (Yönetici)")
        st.caption(f"Dosya: `{STOK_DOSYA}`")

        df = StockService.load_df().copy()
        df["Durum"] = df.apply(lambda r: "❗ Kritik" if int(r["Miktar"]) <= int(r["Esik"]) else "✅ Normal", axis=1)

        st.info("Miktar <= Esik olursa uyarı verir. Miktar yetmezse garson siparişi ENGELLENİR.")

        edited = st.data_editor(
            df[["Malzeme", "Miktar", "Esik", "Durum"]],
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Malzeme": st.column_config.TextColumn("Malzeme", required=True),
                "Miktar": st.column_config.NumberColumn("Miktar", min_value=0, step=1, required=True),
                "Esik": st.column_config.NumberColumn("Esik", min_value=0, step=1, required=True),
                "Durum": st.column_config.TextColumn("Durum", disabled=True),
            },
        )

        c1, c2 = st.columns([0.4, 0.6])
        with c1:
            if st.button("💾 Kaydet", use_container_width=True):
                df2 = edited.copy()
                df2 = df2.dropna(subset=["Malzeme", "Miktar", "Esik"])
                df2["Malzeme"] = df2["Malzeme"].astype(str).str.strip()
                df2 = df2[df2["Malzeme"] != ""]
                df2["Miktar"] = pd.to_numeric(df2["Miktar"], errors="coerce").fillna(0).astype(int).clip(lower=0)
                df2["Esik"] = pd.to_numeric(df2["Esik"], errors="coerce").fillna(0).astype(int).clip(lower=0)
                StockService.save_df(df2[["Malzeme", "Miktar", "Esik"]])
                st.success("Kaydedildi ✅")
                st.rerun()

        with c2:
            st.caption("İpucu: Eşiği malzeme bazlı ayarla (örn. Domates 5, Dana Eti 5000gr vs).")

        st.divider()
        st.subheader("🛒 Yönetici Hızlı Stok Takviyesi")
        stok_map = StockService.load_map()
        malzeme = st.selectbox("Malzeme", sorted(list(stok_map.keys())))
        miktar_ekle = st.number_input("Eklenecek Miktar", min_value=1, step=1, value=1)

        if st.button("➕ Stoğa Ekle", use_container_width=True):
            StockService.admin_add_stock(malzeme, int(miktar_ekle))
            st.success(f"Stok güncellendi: {malzeme} +{miktar_ekle} ✅")
            st.rerun()

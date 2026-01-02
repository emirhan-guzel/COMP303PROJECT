import streamlit as st
from analiz import grafik_olustur, excel_raporu_indir
from services.analytics_service import AnalyticsService
from services.stock_service import StockService

class AdminDashboardPage:
    def render(self):
        st.title("📊 Yönetici Dashboard")
        st.markdown('<span class="badge">Analiz</span><span class="badge">AI + Stok</span>', unsafe_allow_html=True)

        # stok migrate
        _ = StockService.load_df()

        ciro, kar, sip, best = AnalyticsService.kpis_last30()
        a,b,c,d = st.columns(4)
        a.metric("Ciro(30g)", f"{ciro:,.0f} TL")
        b.metric("Kâr(30g)", f"{kar:,.0f} TL")
        c.metric("Sipariş", sip)
        d.metric("Top Ürün", best)

        st.divider()

        left, right = st.columns([1.25, 0.75])

        with left:
            st.subheader("🌌 Grafikler")
            st.pyplot(grafik_olustur(), use_container_width=True)

        with right:
            st.subheader("🚨 Kritik Stoklar")
            df_low = StockService.low_stock_list()
            kritik = df_low[df_low["Durum"] == "❗ Kritik"][["Malzeme", "Miktar", "Esik", "Durum"]]
            if kritik.empty:
                st.success("Kritik stok yok ✅")
            else:
                st.dataframe(kritik, use_container_width=True, hide_index=True, height=220)

            st.divider()
            st.subheader("🧠 Satın Alma Planı")
            stok_map = StockService.load_map()
            df_plan, df_kritik, yorumlar, df_ai = AnalyticsService.stock_plan(stok_map, guvenlik_orani=0.10)

            if df_ai is None or df_ai.empty:
                st.info("AI strateji için veri yok.")
            else:
                for y in yorumlar[:8]:
                    st.write(f"- {y}")

                st.dataframe(
                    df_plan.sort_values(by="Eksik", ascending=False),
                    use_container_width=True, hide_index=True, height=260
                )

        st.divider()
        if st.button("📥 Excel Raporu Üret", use_container_width=True):
            fn = excel_raporu_indir()
            if fn:
                st.success(f"Excel üretildi: {fn}")
            else:
                st.error("Excel üretilemedi.")

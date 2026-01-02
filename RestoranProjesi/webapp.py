import streamlit as st

from ui.theme import apply_theme
from ui.auth import init_auth, login_view, logout_sidebar

from pages.garson_page import GarsonPage
from pages.mutfak_page import MutfakPage
from pages.admin_dashboard_page import AdminDashboardPage
from pages.stok_page import StokPage

from services.kitchen_service import ActiveOrderItem


st.set_page_config(
    page_title="GastroAnalyst AI",
    page_icon="🍽️",
    layout="wide"
)


def init_state():
    # Sepetler
    if "sepetler" not in st.session_state:
        st.session_state.sepetler = {i: [] for i in range(1, 13)}

    # Aktif masa
    if "aktif_masa" not in st.session_state:
        st.session_state.aktif_masa = 1

    # Mutfak aktif siparişler
    if "aktif_siparisler" not in st.session_state:
        st.session_state.aktif_siparisler: list[ActiveOrderItem] = []

    # Basit sayfa adı (logout key için yardımcı)
    if "page" not in st.session_state:
        st.session_state.page = "root"


def hide_sidebar_completely():
    # Login ekranında sidebar + toggle okunu tamamen kaldır
    st.markdown("""
    <style>
      [data-testid="stSidebar"] { display: none !important; }
      [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)


def main():
    apply_theme()
    init_state()
    init_auth()

    # LOGIN DEĞİLSE -> SADECE LOGIN EKRANI (sidebar yok)
    if not st.session_state.auth["logged_in"]:
        hide_sidebar_completely()
        login_view()
        return

    # LOGIN OLDU -> SIDEBAR + ROLE-BASED MENÜ
    user = st.session_state.auth["user"]
    st.session_state.page = "root"

    # ÇIKIŞ BUTONU: SADECE BURADA (tek yer!)
    logout_sidebar(key_suffix="sidebar")

    # Menü role göre
    with st.sidebar:
        st.markdown("## 🧭 Menü")

        if user["rol"] == "garson":
            pages = ["Garson Paneli", "Mutfak Ekranı"]
        else:
            pages = ["Yönetici Dashboard", "Stok Kontrolü", "Mutfak Ekranı"]

        page = st.radio("Sayfa", pages, key="nav_radio")

    # Sayfaları render et
    if page == "Garson Paneli":
        st.session_state.page = "garson"
        GarsonPage().render(user)

    elif page == "Mutfak Ekranı":
        st.session_state.page = "mutfak"
        MutfakPage().render()

    elif page == "Stok Kontrolü":
        # Buraya yönetici dışında zaten gelmiyor ama ekstra güvenlik:
        if user["rol"] != "yonetici":
            st.error("Bu sayfa sadece yöneticiye açık.")
            return
        st.session_state.page = "stok"
        StokPage().render()

    else:
        if user["rol"] != "yonetici":
            st.error("Bu sayfa sadece yöneticiye açık.")
            return
        st.session_state.page = "admin"
        AdminDashboardPage().render()


if __name__ == "__main__":
    main()

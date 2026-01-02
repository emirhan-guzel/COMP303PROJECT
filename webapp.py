import streamlit as st
from db_manager import init_db
from screens import login_page, waiter_page, admin_page

# Sayfa ayarları - Emirhan Güzel
st.set_page_config(page_title="GastroAnalyst AI", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")

init_db()

# Session State Kontrolü - Emirhan Güzel
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None

# Sidebar Gizleme/Gösterme CSS - Emirhan Güzel
if not st.session_state.logged_in:
    st.markdown("""<style>[data-testid="stSidebar"] { display: none; } .stApp { background-color: #f4f6f8; }</style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>
        [data-testid="stSidebar"] { display: block; background-color: #fff; border-right: 1px solid #ddd; } 
        div.stButton > button { background: linear-gradient(to right, #6a11cb, #2575fc); color: white; border-radius: 12px; border:none; padding:10px; }
        .stRadio > div { padding: 10px; background: #f8f9fa; border-radius: 10px; margin-bottom: 10px; }
    </style>""", unsafe_allow_html=True)

# YÖNLENDİRME MANTIĞI
if not st.session_state.logged_in:
    login_page.show()
else:
    # Sidebar Menüsü - Emirhan Güzel
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        st.caption(f"Rol: {st.session_state.role.upper()}")
        st.divider()
        
        secim = "Çıkış"
        if st.session_state.role == "admin":
            # Admin hepsini görür - Emirhan Güzel
            secim = st.radio("MENÜ", ["📊 Yönetim Paneli", "🍽️ Sipariş Ekranı", "👨‍🍳 Canlı Mutfak"])
        else:
            # Garson sadece operasyonu görür - Emirhan Güzel
            secim = st.radio("MENÜ", ["🍽️ Sipariş Ekranı", "👨‍🍳 Canlı Mutfak"])
            
        st.divider()
        if st.button("🚪 Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    # SEÇİME GÖRE EKRAN YÖNETİMİ
    # show() fonksiyonuna 'mode' parametresi gönderiyoruz ki tablar karışmasın - Emirhan Güzel
    if secim == "📊 Yönetim Paneli":
        admin_page.show()
    elif secim == "🍽️ Sipariş Ekranı":
        waiter_page.show(mode="siparis") # Sipariş modunda aç
    elif secim == "👨‍🍳 Canlı Mutfak":
        waiter_page.show(mode="mutfak")  # Mutfak modunda aç
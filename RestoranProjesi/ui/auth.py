import streamlit as st
import uuid

USERS = {
    "admin":  {"sifre": "1234", "rol": "yonetici", "isim": "Yönetici"},
    "ali":    {"sifre": "1111", "rol": "garson",   "isim": "Ali"},
    "ayse":   {"sifre": "2222", "rol": "garson",   "isim": "Ayşe"},
    "mehmet": {"sifre": "3333", "rol": "garson",   "isim": "Mehmet"},
}

def init_auth():
    if "auth" not in st.session_state:
        st.session_state.auth = {"logged_in": False, "user": None}

def login_view():
    st.title("🍽️ GastroAnalyst AI")
    st.markdown('<span class="badge">Python Only</span><span class="badge">COMP303 PROJECT</span>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.2, 0.9, 1.2])
    with c2:
        with st.form("login_form_unique"):
            username = st.text_input("Kullanıcı Adı", placeholder="kullanıcı adınızı girin")
            password = st.text_input("Şifre", type="password", placeholder="••••")
            ok = st.form_submit_button("Giriş Yap ✅", use_container_width=True)

        if ok:
            u = username.strip().lower()
            p = password.strip()
            if u in USERS and USERS[u]["sifre"] == p:
                st.session_state.auth = {"logged_in": True, "user": USERS[u]}
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre.")

def logout_sidebar(key_suffix: str = "global"):
    with st.sidebar:
        u = st.session_state.auth["user"]
        st.markdown(f"## 👤 {u['isim']}\n`{u['rol']}`")

        if "logout_btn_uid" not in st.session_state:
            st.session_state.logout_btn_uid = uuid.uuid4().hex

        btn_key = f"btn_logout_{key_suffix}_{st.session_state.logout_btn_uid}_{st.session_state.get('page','x')}"

        if st.button("Çıkış Yap 🚪", use_container_width=True, key=btn_key):
            st.session_state.auth = {"logged_in": False, "user": None}
            st.rerun()
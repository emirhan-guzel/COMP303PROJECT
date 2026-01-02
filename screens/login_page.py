import streamlit as st

# Kullanıcı veritabanı (Demo amaçlı sabit) - Emirhan Güzel
USERS = {
    "admin": "1234",   # Yönetici
    "ali": "1111",     # Garson
    "ayse": "2222",    # Garson
    "mehmet": "3333"   # Garson
}

def show():
    # Login formunu ortalamak için kolon yapısı - Emirhan Güzel
    c1, c2, c3 = st.columns([1, 1.5, 1])
    
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #6a11cb;'>GastroAnalyst Giriş</h1>", unsafe_allow_html=True)
        
        with st.container(border=True):
            user = st.text_input("Kullanıcı Adı")
            passwd = st.text_input("Şifre", type="password")
            
            # Giriş butonu ve doğrulama işlemi - Emirhan Güzel
            if st.button("GİRİŞ YAP", use_container_width=True):
                if user.lower() in USERS and USERS[user.lower()] == passwd:
                    st.session_state.logged_in = True
                    st.session_state.user = user.capitalize()
                    st.session_state.role = "admin" if user == "admin" else "garson"
                    st.rerun()
                else:
                    st.error("❌ Hatalı Kullanıcı Adı veya Şifre")
import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    html, body, [class*="css"] { color: #111827; }
    .stApp { background: #ffffff; }
    h1,h2,h3,h4,h5,h6 { color: #0f172a !important; }
    main * { color: #111827; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #151a2e 0%, #0f1324 100%); }
    [data-testid="stSidebar"] * { color: #e6e9f2 !important; }
    [data-testid="stSidebar"] label { color: #d6dbff !important; font-weight: 500; }
    [data-testid="stSidebar"] button {
      background: linear-gradient(135deg, #6c63ff, #7f78ff);
      color: #ffffff !important;
      border-radius: 12px;
      border: none;
      font-weight: 700;
    }

    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: #0f172a !important; }
    [data-testid="stDataFrame"] * { color: #0f172a !important; }

    .badge {
      display:inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px;
      border: 1px solid rgba(15,23,42,0.15); background: rgba(15,23,42,0.06); margin-right: 6px;
      color: #0f172a;
    }
    [data-testid="stSidebarNav"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

import streamlit as st

def make_sidebar():
    st.sidebar.markdown("### Menú")
    st.sidebar.page_link("pages/jugadoras.py", label="Estadísticas Globales", icon="🎾")
    st.sidebar.page_link("pages/individual.py", label="Tu Jugadora Favorita", icon="⭐")
    st.sidebar.page_link("pages/mapa.py", label="Distribución Geográfica", icon="🌍")
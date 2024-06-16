import streamlit as st
from time import sleep

st.set_page_config(layout="centered", page_icon = "🎾", page_title = "Inicio")

st.write("")
st.write("")
st.write("")
st.write("")


st.title('Visualización de Estadísticas de la Women\'s Tennis Association 🎾')

st.write("")
st.write("")
st.write("")

col1, col2 = st.columns([1.25, 2])
with col2:
    if st.button('Iniciar', type='primary'):
        st.balloons()
        sleep(2)
        st.switch_page("pages/jugadoras.py")

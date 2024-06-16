import streamlit as st
st.set_page_config(page_title="Estadísticas WTA", page_icon="🎾", layout="wide")
import pandas as pd
import plotly.express as px
from navigation import make_sidebar


COLOR = '#7b2cbf'
LIGHT_VIOLET = '#e0aaff'
LIGHT_VIOLET_2 = '#9d4edd'
DARK_VIOLET = '#5a189a'

@st.cache_data
def load_data():
    players = pd.read_csv("tennis_wta/wta_players_withrank.csv")
    stats = pd.read_csv("stats_and_rank.csv")
    return players, stats


def display_histogram(df, year):
    fig = px.histogram(df, x='height', title='Distribución de la altura')
    fig.update_traces(marker=dict(color=COLOR, line=dict(color='black', width=1)))
    fig.update_layout(xaxis_title='Centímetros', yaxis_title='Frequency')
    st.plotly_chart(fig)


def display_piechart(df, year):
    hand_counts = df['hand'].value_counts().reset_index()
    hand_counts.columns = ['hand', 'count']
    
    names = {}
    for i, row in hand_counts.iterrows():
        if row['hand'] == 'R':
            names['R'] = 'Derecha'
        elif row['hand'] == 'L':
            names['L'] = 'Izquierda'
        else:
            names['U'] = 'Unknown'

    fig = px.pie(hand_counts, values='count', names=names, title='Distribución por mano dominante',
                 color_discrete_sequence=[DARK_VIOLET, LIGHT_VIOLET, LIGHT_VIOLET_2])
    st.plotly_chart(fig)

def display_scatterplot(df, estadistica):

    if estadistica == 'Aces':
        y = 'ace'
    elif estadistica == 'Dobles Faltas':
        y = 'df'
    elif estadistica == '% Primer Servicio':
        y = '1stIn'
    elif estadistica == '% Punto Ganado con el 1er Saque':
        y = '1stWon'
    elif estadistica == '% Punto Ganado con el 2do Saque':
        y = '2ndWon'
    elif estadistica == 'Puntos de Break Salvados':
        y = 'bpSaved'
    
    fig = px.scatter(df, x='max_rank', y=y, hover_name=df["player_name"], title=f'Relación entre {estadistica} y Ranking Máximo del Año')
    fig.update_traces(marker=dict(line=dict(width=1, color=COLOR)))
    fig.update_layout(xaxis_title='Ranking Máximo', yaxis_title=y)
    st.plotly_chart(fig)

if __name__ == "__main__":

    make_sidebar()

    players, stats = load_data()

    st.sidebar.markdown("### Parámetros de Visualización")

    year = st.sidebar.select_slider("Año", options=[year for year in range(2015, 2024)], value=2023)

    top = st.sidebar.radio("Top", options=["TOP 10", "TOP 50", "TOP 100", "TOP 500", "Todas las jugadoras"], index = 4)

    if top == "TOP 10":
        rank = 10
    elif top == "TOP 50":
        rank = 50
    elif top == "TOP 100":
        rank = 100
    elif top == "TOP 500":
        rank = 500
    else:
        rank = None

    if rank is not None:
        stats = stats[stats['max_rank'] <= rank]
        players = players[players['max_rank'] <= rank]

    st.title('Características de las jugadoras')

    estadistica = st.selectbox("Estadística", ["Aces", "Dobles Faltas", "% Primer Servicio", 
                                               "% Punto Ganado con el 1er Saque", "% Punto Ganado con el 2do Saque",
                                             "Puntos de Break Salvados"])
    display_scatterplot(stats[stats['year'] == year], estadistica)

    col1, col2 = st.columns(2)
    with col1:
        display_histogram(players[players['year'] == year], str(year))
    with col2:
        display_piechart(players[players['year'] == year], str(year))


import streamlit as st
import pandas as pd
import plotly.express as px
import flag
import pycountry
from navigation import make_sidebar

st.set_page_config(page_title="Tu Jugadora Favorita", page_icon="⭐", layout="wide")

COLOR = '#7b2cbf'
LIGHT_VIOLET = '#e0aaff'
LIGHT_VIOLET_2 = '#9d4edd'
DARK_VIOLET = '#5a189a'


@st.cache_data
def load_data():
    players = pd.read_csv("tennis_wta/wta_players_withrank.csv")
    matches = pd.read_csv("tennis_wta/wta_matches.csv")
    stats = pd.read_csv("stats_and_rank.csv")
    rankings = pd.read_csv("wta_rankings.csv")
    return players, matches, stats, rankings


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
    
    fig = px.scatter(df, x='max_rank', y=y, hover_name=df["player_name"], title=f'Relación entre {estadistica} y Ranking Máximo de Año')
    fig.update_traces(marker=dict(line=dict(width=1, color=COLOR)))
    fig.update_layout(xaxis_title='Ranking Máximo', yaxis_title=y)
    st.plotly_chart(fig)

def plot_rank_or_points_changes(player_data, player_id, year):
    player_data['ranking_date'] = pd.to_datetime(player_data['ranking_date'], format='%Y%m%d')

    # Get only the ones from year
    player_data = player_data[player_data['ranking_date'].dt.year == year]

    player_data = player_data[player_data['player'] == player_id]
        

    fig = px.line(player_data, x='ranking_date', y='points', 
                  title=f'Evolución de los Puntos del Ranking en {year}',
                  labels={'ranking_date': 'Fecha', 'points': 'Puntos'},
                  hover_data={'rank': True}, color_discrete_sequence=[COLOR]
    )
    
    st.plotly_chart(fig)


def plot_accumulative_wins_losses(player_data, player_id, year, surface):
    player_data['tourney_date'] = pd.to_datetime(player_data['tourney_date'], format='%Y%m%d')
    player_data['year'] = player_data['tourney_date'].dt.year

    year_data = player_data[player_data['year'] == year]

    year_data = year_data.sort_values(by='tourney_date')

    if surface != "Todas las superfícies":
        year_data = year_data[year_data['surface'] == surface]
    # Calculate cumulative wins and losses
    year_data['win'] = year_data['winner_id'] == player_id
    year_data['loss'] = year_data['loser_id'] == player_id

    year_data['victorias'] = year_data['win'].cumsum()
    year_data['derrotas'] = year_data['loss'].cumsum()
    

    cumulative_data = year_data[['tourney_date', 'victorias', 'derrotas']].melt(id_vars='tourney_date', var_name='Resultados', value_name='count')

    color_discrete_map = {'victorias': DARK_VIOLET, 'derrotas': LIGHT_VIOLET}

    fig = px.line(cumulative_data, x='tourney_date', y='count', color='Resultados', 
                  title=f'Acumulación de Victorias y Derrotas en el año {year}',
                  labels={'tourney_date': 'Semana del torneo', 'count': 'Partidos', 'Resultados': 'Resultados'},
                  color_discrete_map=color_discrete_map,)
    
    st.plotly_chart(fig)

def plot_win_loss_by_opponent_rank(player_data, player_id, year, surface):
    player_data = player_data[player_data['year'] == year]

    if surface != "Todas las superfícies":
        player_data = player_data[player_data['surface'] == surface]

    #Keep the columns where the winner or the loser is the player
    player_data = player_data[(player_data['winner_id'] == player_id) | (player_data['loser_id'] == player_id)]

    player_data['opponent_rank'] = player_data.apply(
        lambda row: row['loser_rank'] if row['winner_id'] == player_id else row['winner_rank'], axis=1)
    player_data['player_rank'] = player_data.apply(
        lambda row: row['winner_rank'] if row['winner_id'] == player_id else row['loser_rank'], axis=1)
    
    player_data['result'] = player_data.apply(
        lambda row: 'Victoria' if row['winner_id'] == player_id else 'Derrota', axis=1)

    color_discrete_map = {'Victoria': DARK_VIOLET, 'Derrota': LIGHT_VIOLET}

    fig = px.scatter(player_data, x='tourney_date', y='opponent_rank', color='result',
                     title=f'Distribución de las Victorias y Derrotas por Ranking del Oponente',
                     labels={'opponent_rank': 'Ranking del Oponente', 'tourney_date': 'Semana del Torneo'},
                     hover_data={'result': True, 'opponent_rank': True},
                     color_discrete_map=color_discrete_map)
    
    st.plotly_chart(fig)


def iso3_to_iso2(iso3_code):

    country = pycountry.countries.get(alpha_3=iso3_code)
    if country is not None:
        return country.alpha_2
    return None



if __name__ == "__main__":
    
    make_sidebar()
    st.sidebar.markdown("### Parámetros de Visualización")


    players, matches, stats, rankings = load_data()


    year = st.sidebar.selectbox('Selecciona un año', players['year'].unique()[::-1], index = 0)
    players_year = players[players['year'] == year]
    jugadora = st.sidebar.selectbox('Selecciona una jugadora', players_year['name'].unique(), index = 6)
    player_id = players[players['name'] == jugadora]['player_id'].values[0]


    iso2_code = iso3_to_iso2(players[players["name"] == jugadora]["country"].values[0])
    # Convert ISO3 country code to flag emoji
    if iso2_code is not None:
        flag_emoji = flag.flag(iso2_code)
    else:
        flag_emoji = ""


    st.title(f'Análisis de {jugadora} {flag_emoji}')

    col1, col2, col3, col4 = st.columns([0.15, 0.20, 0.10, 0.55])
    with col1:
        st.markdown(f'**Altura:** {players[players["name"] == jugadora]["height"].values[0]} cm')
    with col2:
        st.markdown(f'**Mano dominante:** {players[players["name"] == jugadora]["hand"].values[0]}')
    with col3:
        st.markdown(f'**País:** {players[players["name"] == jugadora]["country"].values[0]}')
    with col4:
        # Rank in the selected year
        player_ranking = min(players[players["name"] == jugadora]["max_rank"].values)

        if pd.isnull(player_ranking):
            player_ranking = "desconocido"
        else:
            player_ranking = int(player_ranking)
        st.markdown(f'**Ranking máximo de su carrera:** {player_ranking}')

    
    if jugadora:
        if year < 1984:
            st.warning("Todavía no existían los rankings de la WTA!")
        plot_rank_or_points_changes(rankings, player_id, year)


        st.divider()

        surface = st.selectbox('Filtra por superfície', ["Todas las superfícies", "Hard", "Clay", "Grass"], index = 0)

        plot_accumulative_wins_losses(matches, player_id, year, surface)
        plot_win_loss_by_opponent_rank(matches, player_id, year, surface)


    


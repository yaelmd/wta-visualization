import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import json
from navigation import make_sidebar

COLOR = '#7b2cbf'
LIGHT_VIOLET = '#e0aaff'
LIGHT_VIOLET_2 = '#9d4edd'
DARK_VIOLET = '#5a189a'

st.set_page_config(page_title="Distribución Geográfica", page_icon="🌍", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("num_players.csv")
    top_10 = pd.read_csv("num_players_top10.csv")
    top_50 = pd.read_csv("num_players_top50.csv")
    top_100 = pd.read_csv("num_players_top100.csv")
    top_500 = pd.read_csv("num_players_top500.csv")
    players = pd.read_csv("tennis_wta/wta_players_withrank.csv")
    stats = pd.read_csv("stats_and_rank.csv")
    with open('countries.geojson', 'r') as f:
        data = json.load(f)
    return df, top_10, top_50, top_100, top_500, players, stats, data

def display_map(df, geojson,year):
    # Initialize a Folium map
    map = folium.Map(location=[20, 0], zoom_start=1.5, scrollWheelZoom=False, tiles='CartoDB positron')
    
    year = str(year)

    df[year] = df[year].astype(int)

    bin_min = df[year].min()
    bin_max = df[year].max()
    
    bins = [0]
    i = 1
    while i < bin_max and i <= 20:
        bins.append(i)
        if i == 1:
            i += 4
        else:
            i += 5
    bins.append(bin_max) 

    if len(bins) < 4:
        bins = 4  

    choropleth = folium.Choropleth(
            geo_data=geojson,
            data=df,
            columns = ["country", year],
            key_on="feature.properties.ISO_A3",
            line_opacity=0.5,
            highlight=True,
            fill_color="RdPu",
            bins=bins,
            legend_name="Players in year",
            nan_fill_color="gray",
            nan_fill_opacity=0.05,
            show=True
        )
    choropleth.add_to(map)
    
    for feature in choropleth.geojson.data['features']:
        country_name = feature['properties']["ISO_A3"]
        feature['properties']['num_players'] = 'Players : ' + str(int(df.loc[df["country"] == country_name, year].values[0]) if country_name in df["country"].unique() else 0)

        
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['ISO_A3', 'num_players'], labels=False)
    )
    
    st_map = folium_static(map, width=700, height=450)


# Example usage
if __name__ == "__main__":
    make_sidebar()

    st.sidebar.markdown("### Parámetros de Visualización")

    num_players, top10, top50, top100, top500, players, stats, geojson = load_data()
    

    st.title('Jugadoras por país')
    

    year = st.sidebar.select_slider("Año", options=[year for year in range(1968, 2024)], value=2023)

    top = st.sidebar.radio("Top", options=["TOP 10", "TOP 50", "TOP 100", "TOP 500", "Todas las jugadoras"], index = 4)

    if top == "TOP 10":
        map_data = top10
    elif top == "TOP 50":
        map_data = top50
    elif top == "TOP 100":
        map_data = top100
    elif top == "TOP 500":
        map_data = top500
    else:
        map_data = num_players
    
    display_map(map_data, geojson, year)

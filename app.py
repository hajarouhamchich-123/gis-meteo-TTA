
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import requests
import plotly.express as px
import pandas as pd

# --- CONFIG PAGE ---
st.set_page_config(
    page_title="🌤️ Météo - Tanger-Tétouan-Al Hoceïma",
    page_icon="🌍",
    layout="wide"
)

# --- DONNÉES ---
@st.cache_data
def charger_donnees():
    regions = gpd.read_file("data/Regions_WGS84.shp")
    provinces = gpd.read_file("data/Provinces_WGS84.shp")
    communes = gpd.read_file("data/communes_WGS84.shp")
    return regions, provinces, communes

regions, provinces, communes = charger_donnees()

# --- SIDEBAR DESIGN ---
st.sidebar.markdown("<h2 style='color:#FF4B4B;'>🌍 Explorer Tanger‑Tétouan‑Al Hoceïma</h2>", unsafe_allow_html=True)
st.sidebar.divider()

# Étape 1 : Région (même si une seule option)
liste_regions = ["Tanger-Tétouan-Al Hoceima"]
region_choisie = st.sidebar.selectbox("🌍 Région :", liste_regions)

# Étape 2 : Niveau choisi
niveau = st.sidebar.radio("📍 Niveau d'affichage :", ["Région", "Province", "Commune"], horizontal=True)

province_choisie = None
commune_choisie = None

# --- LOGIQUE DE SÉLECTION ---
if niveau == "Région":
    entite = regions[regions["libelle_fr"] == region_choisie]
    nom_entite = region_choisie
    zoom = 7

elif niveau == "Province":
    code_reg_tta = regions[regions["libelle_fr"] == region_choisie]["code_reg"].values[0]
    provinces_filtrees = provinces[provinces["code_reg"] == code_reg_tta]
    province_choisie = st.sidebar.selectbox("🏙️ Choisir une province :", sorted(provinces_filtrees["libelle_fr"].unique()))
    entite = provinces_filtrees[provinces_filtrees["libelle_fr"] == province_choisie]
    nom_entite = province_choisie
    zoom = 9

elif niveau == "Commune":
    code_reg_tta = regions[regions["libelle_fr"] == region_choisie]["code_reg"].values[0]
    provinces_filtrees = provinces[provinces["code_reg"] == code_reg_tta]
    province_choisie = st.sidebar.selectbox("🏙️ Choisir une province :", sorted(provinces_filtrees["libelle_fr"].unique()))
    communes_filtrees = communes[communes["FIRST_prov"] == province_choisie]
    commune_choisie = st.sidebar.selectbox("🏘️ Choisir une commune :", sorted(communes_filtrees["FIRST_com_"].unique()))
    entite = communes_filtrees[communes_filtrees["FIRST_com_"] == commune_choisie]
    nom_entite = commune_choisie
    zoom = 11

centre = entite.geometry.centroid.iloc[0]

# --- RÉSUMÉ ---
st.markdown(f"<h3 style='color:#FF4B4B;'>📍 Zone sélectionnée : <span style='color:#0066CC;'>{nom_entite}</span> ({niveau})</h3>", unsafe_allow_html=True)

# --- CARTE ---
st.subheader("🗺️ Carte interactive")
carte = folium.Map(location=[centre.y, centre.x], zoom_start=zoom, tiles="CartoDB positron")

folium.GeoJson(
    entite,
    name=niveau,
    style_function=lambda x: {"color": "#FF4B4B", "weight": 2.5, "fillOpacity": 0.1}
).add_to(carte)

folium.TileLayer(
    tiles="https://tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap",
    name="Relief (MNT)",
    overlay=True
).add_to(carte)

folium.LayerControl().add_to(carte)
st_folium(carte, width=1100, height=500)

st.divider()

# --- MÉTÉO ---
st.subheader("📊 Prévisions météo - 15 jours")

url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={centre.y}&longitude={centre.x}"
    f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
    f"&timezone=Africa%2FCasablanca"
    f"&forecast_days=16"
)

reponse = requests.get(url)
donnees = reponse.json()

df = pd.DataFrame({
    "Date": donnees["daily"]["time"],
    "Température max (°C)": donnees["daily"]["temperature_2m_max"],
    "Température min (°C)": donnees["daily"]["temperature_2m_min"],
    "Précipitations (mm)": donnees["daily"]["precipitation_sum"]
})
df["Date"] = pd.to_datetime(df["Date"])
df = df.iloc[1:16].reset_index(drop=True)

# --- AFFICHAGE JOUR COURANT ---
aujourdhui = df.iloc[0]
st.info(
    f"🌞 Aujourd'hui ({aujourdhui['Date'].date()}): "
    f"Min {aujourdhui['Température min (°C)']}°C | "
    f"Max {aujourdhui['Température max (°C)']}°C | "
    f"Pluie {aujourdhui['Précipitations (mm)']} mm"
)

# --- GRAPHIQUE ---
choix = st.sidebar.radio("📈 Type de graphique :", ["Température", "Précipitations"], horizontal=True)
if choix == "Température":
    fig = px.line(
        df, x="Date",
        y=["Température max (°C)", "Température min (°C)"],
        title=f"🌡️ Températures min & max sur 15 jours — {nom_entite}",
        markers=True,
        color_discrete_sequence=["#FF4B4B", "#0066CC"]
    )
else:
    fig = px.bar(
        df, x="Date", y="Précipitations (mm)",
        title=f"🌧️ Précipitations sur 15 jours — {nom_entite}",
        color_discrete_sequence=["#00BFFF"]
    )

fig.update_layout(height=400, template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# --- TABLEAU RÉCAP ---
st.subheader("📋 Tableau récapitulatif (15 jours)")
st.dataframe(df, use_container_width=True)

import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import requests
import plotly.express as px
import pandas as pd

@st.cache_data
def charger_donnees():
    regions = gpd.read_file("data/Regions_WGS84.shp")
    provinces = gpd.read_file("data/Provinces_WGS84.shp")
    communes = gpd.read_file("data/communes_WGS84.shp")
    return regions, provinces, communes

regions, provinces, communes = charger_donnees()

st.title("🗺️ Application Météo - Tanger-Tétouan-Al Hoceïma")

liste_regions = sorted(regions["libelle_fr"].unique())
region_choisie = st.selectbox("Choisissez une région :", liste_regions, key="sel_region")

provinces_filtrees = provinces[provinces["code_reg"] == regions[regions["libelle_fr"] == region_choisie]["code_reg"].values[0]]
liste_provinces = sorted(provinces_filtrees["libelle_fr"].unique())
province_choisie = st.selectbox("Choisissez une province :", liste_provinces, key="sel_province")

communes_filtrees = communes[communes["FIRST_prov"] == province_choisie]
liste_communes = sorted(communes_filtrees["FIRST_com_"].unique())
commune_choisie = st.selectbox("Choisissez une commune :", liste_communes, key="sel_commune")

st.subheader("🗺️ Carte interactive")
niveau = st.radio("Afficher le contour de :", ["Région", "Province", "Commune"], key="radio_carte")

if niveau == "Région":
    entite = regions[regions["libelle_fr"] == region_choisie]
    nom_entite = region_choisie
    zoom = 7
elif niveau == "Province":
    entite = provinces_filtrees[provinces_filtrees["libelle_fr"] == province_choisie]
    nom_entite = province_choisie
    zoom = 9
else:
    entite = communes_filtrees[communes_filtrees["FIRST_com_"] == commune_choisie]
    nom_entite = commune_choisie
    zoom = 11

st.write(f"📍 Entité affichée : **{nom_entite}**")

centre = entite.geometry.centroid.iloc[0]
carte = folium.Map(location=[centre.y, centre.x], zoom_start=zoom)

titre_html = "<div style='position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:1000;background-color:white;padding:8px 16px;border-radius:8px;border:2px solid red;font-size:14px;font-weight:bold;color:black;'>🗺️ " + nom_entite + "</div>"
carte.get_root().html.add_child(folium.Element(titre_html))

folium.GeoJson(
    entite,
    name=niveau,
    style_function=lambda x: {"color": "red", "weight": 3, "fillOpacity": 0}
).add_to(carte)

folium.TileLayer(
    tiles="https://tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap",
    name="Relief (MNT)",
    overlay=True
).add_to(carte)

legende_html = "<div style='position:fixed;bottom:30px;left:30px;z-index:1000;background-color:white;padding:10px;border-radius:8px;border:1px solid grey;font-size:13px;color:black;'><b>Légende</b><br><span style='color:red;'>——</span> Contour de la zone<br><span style='color:green;'>■</span> Relief (MNT)</div>"
carte.get_root().html.add_child(folium.Element(legende_html))

folium.LayerControl().add_to(carte)
st_folium(carte, width=700, height=500, key="carte_folium")

st.subheader("🌡️ Prévisions météo - 15 jours")

lat = centre.y
lon = centre.x

url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}&longitude={lon}"
    f"&daily=temperature_2m_max,precipitation_sum"
    f"&timezone=Africa%2FCasablanca"
    f"&forecast_days=16"
)

reponse = requests.get(url)
donnees = reponse.json()

df = pd.DataFrame({
    "Date": donnees["daily"]["time"],
    "Température (°C)": donnees["daily"]["temperature_2m_max"],
    "Précipitations (mm)": donnees["daily"]["precipitation_sum"]
})
df["Date"] = pd.to_datetime(df["Date"])
df = df.iloc[1:16].reset_index(drop=True)

parametre = st.radio(
    "Choisissez le paramètre :",
    ["Température (°C)", "Précipitations (mm)"],
    key="radio_meteo"
)

if parametre == "Température (°C)":
    fig = px.line(
        df, x="Date", y="Température (°C)",
        title=f"Température sur 15 jours — {nom_entite}",
        markers=True
    )
else:
    fig = px.bar(
        df, x="Date", y="Précipitations (mm)",
        title=f"Précipitations sur 15 jours — {nom_entite}"
    )

st.plotly_chart(fig, use_container_width=True, key="graphique_meteo")
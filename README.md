# Application Météo - Tanger-Tétouan-Al Hoceïma 🗺️

## Description
Application web géospatiale interactive développée avec Streamlit
pour l'affichage des prévisions météorologiques de la région 
Tanger-Tétouan-Al Hoceïma et ses unités territoriales.

## Fonctionnalités
- Navigation administrative : Région → Province → Commune
- Carte interactive avec contour et relief MNT (OpenTopoMap)
- Prévisions météo sur 15 jours (température et précipitations)
- Graphiques interactifs (courbe et histogramme)

## Sources de données
- Shapefiles : Découpage administratif du Maroc (HCP, WGS84)
- MNT : OpenTopoMap (tiles XYZ)
- Météo : Open-Meteo API (https://open-meteo.com)

## Technologies utilisées
- Python 3.14
- Streamlit
- GeoPandas
- Folium
- Plotly
- Requests

## Lancement local
streamlit run app.py

## Lien application déployée
https://gis-meteo-tta-lhjvheobdkpbxuf9wmb5lf.streamlit.app/
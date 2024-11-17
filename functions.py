import streamlit as st
import pandas as pd
import folium
import json
from io import BytesIO

# Colores de los departamentos
departamento_colores = {
    "AMAZONAS": "#FF6347", "ANCASH": "#32CD32", "APURIMAC": "#1E90FF", "AREQUIPA": "#FFD700",
    "AYACUCHO": "#8A2BE2", "CAJAMARCA": "#FF4500", "CALLAO": "#20B2AA", "CUSCO": "#D2691E",
    "HUANCAVELICA": "#ADFF2F", "HUANUCO": "#FF1493", "ICA": "#B8860B", "JUNIN": "#A52A2A",
    "LA LIBERTAD": "#A9A9A9", "LAMBAYEQUE": "#7FFF00", "LIMA": "#800000", "LORETO": "#9ACD32",
    "MADRE DE DIOS": "#4B0082", "MOQUEGUA": "#8B0000", "PASCO": "#2E8B57", "PIURA": "#B0C4DE",
    "PUNO": "#FF8C00", "SAN MARTIN": "#E0FFFF", "TACNA": "#00CED1", "TUMBES": "#FF00FF",
    "UCAYALI": "#F08080"
}

departamento_coordenadas = {
    "AMAZONAS": [-5.25, -78.257], "ANCASH": [-9.108, -77.7], "APURIMAC": [-13.9, -73.0],
    "AREQUIPA": [-15.8, -72.2], "AYACUCHO": [-14, -74.223], "CAJAMARCA": [-6.6, -78.7],
    "CUSCO": [-13.530, -71.6], "HUANCAVELICA": [-12.773, -75.2], "HUANUCO": [-9.5, -76.242],
    "ICA": [-14, -75.752], "JUNIN": [-11.332, -75.202], "LA LIBERTAD": [-7.8, -78.7],
    "LAMBAYEQUE": [-6.2, -79.929], "LIMA": [-11.6, -76.8], "LORETO": [-4.047, -75],
    "MADRE DE DIOS": [-11.8, -70.5], "MOQUEGUA": [-16.7, -71.0], "PASCO": [-10.1, -75.210],
    "PIURA": [-4.9, -80.5], "PUNO": [-14.4, -70.3], "SAN MARTIN": [-6.519, -76.756],
    "TACNA": [-17.5, -70.4], "TUMBES": [-3.566, -80.7], "UCAYALI": [-9.7, -73.5],
    "CALLAO": [-12.045, -77.135]
}

# Cargar archivo GeoJSON - Mapa
@st.cache_data
def load_geojson():
    with open("peru_departamental_simple.geojson", "r") as f:
        geojson_data = json.load(f)
    return geojson_data

# Cargar datos de gasto desde el CSV filtrado
@st.cache_data
def load_gasto_data():
    return pd.read_csv("gasto_total_por_departamento.csv")

# Crear el mapa interactivo
def create_map(geojson_data, gastos, selected_departamento=None):
    m = folium.Map(location=[-9.19, -75.015], zoom_start=5)     # Enfoque inicial

    for feature in geojson_data["features"]:                    # Por cada departamento en mapa GeoJSON
        dep_name = feature['properties']['NOMBDEP']             # Obtener nombre

        if dep_name == "CALLAO":                                # Conflicto de nombres en los archivos
            name = "PROVINCIA CONSTITUCIONAL DEL CALLAO"
        else:
            name = dep_name

        color = departamento_colores.get(dep_name, "#808080")   # Asociarlo a un color en diccionario

        line_color = "yellow" if dep_name == selected_departamento else "gray" # Si es igual a uno seleccionado
        weight = 4 if dep_name == selected_departamento else 2                  # Cambiar el color de contorno y peso

        folium.GeoJson(
            feature,                                        # Archivo GeoJSON
            style_function=lambda feature, color=color: {   # Características de coloración y transparencia
                'fillColor': color,
                'weight': weight,
                'opacity': 1,
                'color': line_color,
                'fillOpacity': 0.5
            },#gasto_data[gasto_data['Departamento'] == departamento]['Gasto_Total'].values[0]
            tooltip=dep_name,                               # Aparecer el nombre al pasar el cursor
            highlight_function=lambda x: {'weight': 3, 'color': 'blue'},    # Resaltar color al pasar el cursor
            name="Departamento",                            # Nombre de capa en el mapa
        ).add_to(m)                                         # Añadir cada caractaerísica nueva a la variable "m"

        # Formato de números abcd
        a = int(gastos.loc[gastos["Departamento"] == name].values[0][1])
        b = 10 ** (len(str(a)) - 2)
        c = int(a / b) / 10
        d = (str(c) + "x10^" + str((len(str(a)) - 2)))

        folium.Marker(                                      # Añadir texto - Gasto total
            location=departamento_coordenadas[dep_name],    # Coordenadas
            icon=folium.DivIcon(                            # Descripción
                html=f"""
                <div style="font-size: 10px; font-weight: bold; color: black;">
                    {d}
                </div>
                """,
                icon_size=(0, 0))                           # Eliminar marcador
        ).add_to(m)

    map_html = BytesIO()                # Crear un archivo en memoria RAM
    m.save(map_html, close_file=False)  # Escribe el código HTML desde la variable "m"
    map_html.seek(0)                    # Ajustar puntero desde el comienzo, como leer código desde línea 1
    return map_html                     # Retornar mapa creado
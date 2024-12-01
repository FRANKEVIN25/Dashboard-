import streamlit as st
import pandas as pd
import json
import folium
import Graphics
from io import BytesIO
from streamlit_option_menu import option_menu


file = open("Other/colores.csv", "r")  # Abrir el archivo de colores
colores = {}  # Diccionario vacío
for line in file:  # Leer cada línea
    line = line.split(",")  # Eliminar comas y añadir al diccionario
    colores[line[0]] = line[1].split("\n")[0]

file = open("Other/coordenadas.csv", "r")  # Abrir el archivo de coordenadas
coordenadas = {}  # Diccionario vacío
for line in file:  # Leer cada línea
    line = line.split(",")  # Eliminar comas y añadir al diccionario
    coordenadas[line[0]] = [float(line[1]), float(line[2].split("\n")[0])]


def _format_large_number(number):
    """Formatear números grandes de manera legible"""
    if number == 0:
        return "0"
    magnitude = int(f"{abs(number):e}".split('e')[1])
    scaled_num = number / (10 ** magnitude)
    return f"{scaled_num:.1f}x10^{magnitude}"


def _add_department_to_map(map_obj, feature, line_color, weight, name, gastos, year):
    """Añadir departamento al mapa con detalles personalizados"""
    folium.GeoJson(
        feature,
        style_function=lambda f, c=colores.get(name, "#808080"): {
            'fillColor': c,
            'weight': weight,
            'opacity': 1,
            'color': line_color,
            'fillOpacity': 0.5
        },
        highlight_function=lambda x: {'weight': 3, 'color': 'blue'},
        name="Departamento"
    ).add_to(map_obj)

    # Añadir marcador de gasto total
    department_data = gastos.loc[gastos["Departamento"] == name]
    if not department_data.empty:
        temporal = gastos["Departamento"]
        temporal = pd.concat([temporal, gastos["y_"+str(year)]], axis=1)

        total_gasto = temporal[temporal["Departamento"] == name]["y_"+str(year)]
        formatted_gasto = _format_large_number(int(total_gasto))

        folium.Marker(
            location=coordenadas[feature['properties']['NOMBDEP']],
            icon=folium.DivIcon(
                html=f"""
                <div style="font-size: 10px; font-weight: bold; color: black;">
                    {formatted_gasto}
                </div>
                """
            )
        ).add_to(map_obj)


def create_map(geojson_data, gastos, selected_departamento=None):
    year = Graphics.crear_cinta_de_opciones([year for year in range(2012, 2024)])


    """Crear mapa interactivo con características personalizadas"""
    m = folium.Map(location=[-9.19, -75.015], zoom_start=5)

    for feature in geojson_data["features"]:
        dep_name = feature['properties']['NOMBDEP']
        name = "PROVINCIA CONSTITUCIONAL DEL CALLAO" if dep_name == "CALLAO" else dep_name

        line_color = "yellow" if dep_name == selected_departamento else "gray"
        weight = 4 if dep_name == selected_departamento else 2

        _add_department_to_map(
            m, feature, line_color, weight, name, gastos, year
        )

    map_html = BytesIO()
    m.save(map_html, close_file=False)
    map_html.seek(0)
    return map_html


def render_map():
    mapa = json.load(open("Other/peru_departamental_simple.geojson", "r"))
    gastos = pd.read_csv("Gasto-Anual/Gasto-Anual-2012-2023.csv")

    map_html = create_map(mapa, gastos, selected_departamento=None)

    st.components.v1.html(map_html.getvalue(), height=600)

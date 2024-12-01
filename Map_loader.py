import streamlit as st
import pandas as pd
import json
import folium
import Graphics
from io import BytesIO

file = open("Other/colores.csv", "r")           # Abrir el archivo de colores
colores = {}                                    # Diccionario vacío
for line in file:                               # Leer cada línea
    line = line.split(",")                      # Eliminar comas y añadir al diccionario
    colores[line[0]] = line[1].split("\n")[0]

file = open("Other/coordenadas.csv", "r")       # Abrir el archivo de coordenadas
coordenadas = {}                                # Diccionario vacío
for line in file:                               # Leer cada línea
    line = line.split(",")                      # Eliminar comas y añadir al diccionario
    coordenadas[line[0]] = [float(line[1]), float(line[2].split("\n")[0])]


def _format_large_number(number):                       # Cambiar el formato de números a notación científica
    if number == 0:
        return "0"
    magnitude = int(f"{abs(number):e}".split('e')[1])   # Exponente
    scaled_num = number / (10 ** magnitude)             # Mantissa
    return f"{scaled_num:.1f}x10^{magnitude}"           # Retornar número convertido a texto

def _add_department_to_map(map_obj, feature, line_color, weight, name, gastos, year):
    # Obtener el gasto total para el departamento en el año seleccionado
    department_data = gastos.loc[gastos["Departamento"] == name]
    total_gasto = 0
    if not department_data.empty:
        total_gasto = int(department_data["y_"+str(year)])
    formatted_gasto = _format_large_number(total_gasto)

    # Crear un estilo personalizado para el departamento
    def style_function(feature):
        return {
            'fillColor': colores.get(name, "#808080"), 
            'weight': weight, 
            'opacity': 1, 
            'color': line_color, 
            'fillOpacity': 0.5
        }
    
    # Crear un objeto GeoJson con información emergente
    geo_json = folium.GeoJson(
        feature, 
        style_function=style_function,
        highlight_function=lambda x: {'weight': 3, 'color': 'blue'},
        #tooltip=folium.Tooltip(f"{name}: {formatted_gasto}"),  # Mostrar información al pasar el mouse
        popup=folium.Popup(f"Gasto en {name} ({year}): {formatted_gasto}", max_width=300),  # Mostrar al hacer clic
        name="Departamento"
    ).add_to(map_obj)

    # Agregar un marcador con la información de gasto
    folium.Marker(
        location=coordenadas[feature['properties']['NOMBDEP']],
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size: 10px; 
                font-weight: bold; 
                color: black; 
                background-color: rgba(255,255,255,0.7);
                padding: 2px;
                border-radius: 3px;
                display: none;
            " class="dept-expense">
                {formatted_gasto}
            </div>
            """,
            class_name=f"expense-{name.replace(' ', '-')}"
        )
    ).add_to(map_obj)

def create_map(geojson_data, gastos, selected_departamento=None):
    year = Graphics.crear_cinta_de_opciones([year for year in range(2012, 2024)])  # Selección de años

    m = folium.Map(location=[-9.19, -75.015], zoom_start=5)  # Inicializar mapa apuntando al Perú

    for feature in geojson_data["features"]:
        dep_name = feature['properties']['NOMBDEP']
        name = "PROVINCIA CONSTITUCIONAL DEL CALLAO" if dep_name == "CALLAO" else dep_name

        line_color = "gray" if dep_name == selected_departamento else "blue"
        weight = 4 if dep_name == selected_departamento else 2

        _add_department_to_map(m, feature, line_color, weight, name, gastos, year)

    map_html = BytesIO()
    m.save(map_html, close_file=False)
    map_html.seek(0)
    return map_html                                               # Retornar mapa


def render_map():                                                   # Crear mapa
    mapa = json.load(open("Other/peru_departamental_simple.geojson", "r"))  # Abrir los archivos necesarios
    gastos = pd.read_csv("Gasto-Anual/Gasto-Anual-2012-2023.csv")

    map_html = create_map(mapa, gastos, selected_departamento=None)         # Convertir mapa a html

    st.components.v1.html(map_html.getvalue(), height=600)                  # Colocarlo


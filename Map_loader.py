import streamlit as st
import pandas as pd
import json
import folium
import Graphics
from io import BytesIO

# Cargar archivos CSV
file = open("Other/colores.csv", "r")
colores = {}
for line in file:
    line = line.split(",")
    colores[line[0]] = line[1].split("\n")[0]

file = open("Other/coordenadas.csv", "r")
coordenadas = {}
for line in file:
    line = line.split(",")
    coordenadas[line[0]] = [float(line[1]), float(line[2].split("\n")[0])]

file = open("Other/informacion_de_region", "r")
informacion= {}
for line in file:
    line = line.split(",")
    informacion[line[0]] = [float(line[1]), float(line[2].split("\n")[0])]

# Cargar información de regiones
def cargar_informacion_regiones():
    try:
        info_regiones = pd.read_csv("Other/informacion_de_region.csv")
        return dict(zip(info_regiones['Region'], info_regiones['Informacion']))
    except Exception as e:
        print(f"Error al cargar información de regiones: {e}")
        return {}

# Formatear números de manera legible
def format_number(number):
    return "{:,.2f}".format(number).replace(",", "X").replace(".", ",").replace("X", ".")

def _format_large_number(number):
    """Convertir número a formato legible sin notación científica"""
    if number == 0:
        return "0"
    return format_number(number)

def _add_department_to_map(map_obj, feature, line_color, weight, name, gastos, year, info_regiones):
    # Obtener el gasto total para el departamento en el año seleccionado
    department_data = gastos.loc[gastos["Departamento"] == name]
    total_gasto = 0
    if not department_data.empty:
        total_gasto = int(department_data["y_"+str(year)])
    formatted_gasto = _format_large_number(total_gasto)
    
    # Obtener información adicional de la región
    informacion_region = info_regiones.get(name, "Información no disponible")

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
        popup=folium.Popup(f"""
        <div style='width: 300px;'>
            <h4>{name}</h4>
            <p><strong>Gasto en {year}: S/ {formatted_gasto}</strong></p>
            <p>{informacion_region}</p>
        </div>
        """, max_width=300),
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

def create_map(geojson_data, gastos, info_regiones, selected_departamento=None):
    year = Graphics.crear_cinta_de_opciones([year for year in range(2012, 2024)])  # Selección de años

    m = folium.Map(location=[-9.19, -75.015], zoom_start=5)  # Inicializar mapa apuntando al Perú

    for feature in geojson_data["features"]:
        dep_name = feature['properties']['NOMBDEP']
        name = "PROVINCIA CONSTITUCIONAL DEL CALLAO" if dep_name == "CALLAO" else dep_name

        line_color = "gray" if dep_name == selected_departamento else "blue"
        weight = 4 if dep_name == selected_departamento else 2

        _add_department_to_map(m, feature, line_color, weight, name, gastos, year, info_regiones)

    map_html = BytesIO()
    m.save(map_html, close_file=False)
    map_html.seek(0)
    return map_html

def render_map():
    # Cargar información de regiones
    info_regiones = cargar_informacion_regiones()
    
    mapa = json.load(open("Other/peru_departamental_simple.geojson", "r"))
    gastos = pd.read_csv("Gasto-Anual/Gasto-Anual-2012-2023.csv")

    map_html = create_map(mapa, gastos, info_regiones, selected_departamento=None)
    st.components.v1.html(map_html.getvalue(), height=600)

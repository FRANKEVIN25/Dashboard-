import json
from io import BytesIO
import streamlit as st
import pandas as pd
import folium

class PublicSpendingMapUtilities:
    def __init__(self):
        self.departamento_colores = self._setup_departamento_colors()
        self.departamento_coordenadas = self._setup_departamento_coordinates()

    def _setup_departamento_colors(self):
        """Definir un diccionario de colores para departamentos"""
        return {
            "AMAZONAS": "#FF6347", "ANCASH": "#32CD32", "APURIMAC": "#1E90FF",
            "AREQUIPA": "#FFD700", "AYACUCHO": "#8A2BE2", "CAJAMARCA": "#FF4500",
            "CALLAO": "#20B2AA", "CUSCO": "#D2691E", "HUANCAVELICA": "#ADFF2F",
            "HUANUCO": "#FF1493", "ICA": "#B8860B", "JUNIN": "#A52A2A",
            "LA LIBERTAD": "#A9A9A9", "LAMBAYEQUE": "#7FFF00", "LIMA": "#800000",
            "LORETO": "#9ACD32", "MADRE DE DIOS": "#4B0082", "MOQUEGUA": "#8B0000",
            "PASCO": "#2E8B57", "PIURA": "#B0C4DE", "PUNO": "#FF8C00",
            "SAN MARTIN": "#E0FFFF", "TACNA": "#00CED1", "TUMBES": "#FF00FF",
            "UCAYALI": "#F08080"
        }

    def _setup_departamento_coordinates(self):
        """Definir coordenadas para cada departamento"""
        return {
            "AMAZONAS": [-5.25, -78.257], "ANCASH": [-9.108, -77.7],
            "APURIMAC": [-13.9, -73.0], "AREQUIPA": [-15.8, -72.2],
            "AYACUCHO": [-14, -74.223], "CAJAMARCA": [-6.6, -78.7],
            "CUSCO": [-13.530, -71.6], "HUANCAVELICA": [-12.773, -75.2],
            "HUANUCO": [-9.5, -76.242], "ICA": [-14, -75.752],
            "JUNIN": [-11.332, -75.202], "LA LIBERTAD": [-7.8, -78.7],
            "LAMBAYEQUE": [-6.2, -79.929], "LIMA": [-11.6, -76.8],
            "LORETO": [-4.047, -75], "MADRE DE DIOS": [-11.8, -70.5],
            "MOQUEGUA": [-16.7, -71.0], "PASCO": [-10.1, -75.210],
            "PIURA": [-4.9, -80.5], "PUNO": [-14.4, -70.3],
            "SAN MARTIN": [-6.519, -76.756], "TACNA": [-17.5, -70.4],
            "TUMBES": [-3.566, -80.7], "UCAYALI": [-9.7, -73.5],
            "CALLAO": [-12.045, -77.135]
        }

    @staticmethod
    @st.cache_data
    def load_geojson(path="peru_departamental_simple.geojson"):
        """Cargar archivo GeoJSON con caché"""
        with open(path, "r") as f:
            return json.load(f)

    @staticmethod
    @st.cache_data
    def load_gasto_data(path="gasto_total_por_departamento.csv"):
        """Cargar datos de gasto con caché"""
        return pd.read_csv(path)

    def _format_large_number(self, number):
        """Formatear números grandes de manera legible"""
        if number == 0:
            return "0"
        magnitude = int(f"{abs(number):e}".split('e')[1])
        scaled_num = number / (10 ** magnitude)
        return f"{scaled_num:.1f}x10^{magnitude}"

    def create_map(self, geojson_data, gastos, selected_departamento=None):
        """Crear mapa interactivo con características personalizadas"""
        m = folium.Map(location=[-9.19, -75.015], zoom_start=5)

        for feature in geojson_data["features"]:
            dep_name = feature['properties']['NOMBDEP']
            name = "PROVINCIA CONSTITUCIONAL DEL CALLAO" if dep_name == "CALLAO" else dep_name

            color = self.departamento_colores.get(dep_name, "#808080")
            line_color = "yellow" if dep_name == selected_departamento else "gray"
            weight = 4 if dep_name == selected_departamento else 2

            self._add_department_to_map(
                m, feature, color, line_color, weight, name, gastos
            )

        map_html = BytesIO()
        m.save(map_html, close_file=False)
        map_html.seek(0)
        return map_html

    def _add_department_to_map(self, map_obj, feature, color, line_color, weight, name, gastos):
        """Añadir departamento al mapa con detalles personalizados"""
        folium.GeoJson(
            feature,
            style_function=lambda f, c=color: {
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
            total_gasto = department_data.values[0][1]
            formatted_gasto = self._format_large_number(int(total_gasto))

            folium.Marker(
                location=self.departamento_coordenadas[feature['properties']['NOMBDEP']],
                icon=folium.DivIcon(
                    html=f"""
                    <div style="font-size: 10px; font-weight: bold; color: black;">
                        {formatted_gasto}
                    </div>
                    """
                )
            ).add_to(map_obj)

def load_geojson():
    """Función de compatibilidad para la app principal"""
    utils = PublicSpendingMapUtilities()
    return utils.load_geojson()

def load_gasto_data():
    """Función de compatibilidad para la app principal"""
    utils = PublicSpendingMapUtilities()
    return utils.load_gasto_data()

def create_map(geojson_data, gastos, selected_departamento=None):
    """Función de compatibilidad para la app principal"""
    utils = PublicSpendingMapUtilities()
    return utils.create_map(geojson_data, gastos, selected_departamento)

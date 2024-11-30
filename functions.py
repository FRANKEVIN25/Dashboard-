import json
from io import BytesIO
import streamlit as st
import pandas as pd
import folium


class PublicSpendingMapUtilities:
    def __init__(self):
        self.departamento_colores = self._setup_departamento_colors()
        self.departamento_coordenadas = self._setup_departamento_coordinates()

    @staticmethod
    def _setup_departamento_colors():
        """Definir un diccionario de colores para departamentos"""
        file = open("colores.csv", "r")     # Abrir el archivo de colores
        diccionario = {}                    # Diccionario vacío
        for line in file:                   # Leer cada línea
            line = line.split(",")          # Eliminar comas y añadir al diccionario
            diccionario[line[0]] = line[1].split("\n")[0]
        return diccionario                  # Retornar diccionario

    @staticmethod
    def _setup_departamento_coordinates():
        """Definir coordenadas para cada departamento"""
        file = open("coordenadas.csv", "r")  # Abrir el archivo de coordenadas
        diccionario = {}                    # Diccionario vacío
        for line in file:                   # Leer cada línea
            line = line.split(",")          # Eliminar comas y añadir al diccionario
            diccionario[line[0]] = [float(line[1]), float(line[2].split("\n")[0])]
        return diccionario                  # Retornar diccionario

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

    @staticmethod
    def _format_large_number(number):
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

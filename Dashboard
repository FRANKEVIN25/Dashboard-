import streamlit as st

from functions import load_geojson
from functions import load_gasto_data
from functions import create_map

# Título de página
st.set_page_config(page_title="Mapa del Gasto Público en Perú 🌍", page_icon="🌍", layout="wide")

# Título de la aplicación
st.title("Mapa Interactivo del Gasto Público en Perú - Año 2023 🌍")

# Columnas de la interfaz
col1, col2 = st.columns([1, 2], gap="medium")

# Cargar datos de gasto
gasto_data = load_gasto_data()

# Columna Izquierda: Menú de selección y gasto
with col1:
    st.header("Información de Gasto Público 📊") # Cabezal

    departamento = st.selectbox("Seleccione un departamento", gasto_data['Departamento'].unique()) # Selector

    # Obtener el gasto total del departamento seleccionado
    gasto_total = gasto_data[gasto_data['Departamento'] == departamento]['Gasto_Total'].values[0]

    # Mostrar el gasto total con formato atractivo
    st.subheader(f"Departamento: {departamento}")
    st.markdown("<hr style='border:1px solid #ddd;'>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size: 24px; font-weight: bold; color: #333;'>Gasto Total Anual:</div>"
        f"<div style='font-size: 32px; font-weight: bold; color: #FF6347;'>S/ {gasto_total:,.2f}</div>",
        unsafe_allow_html=True
    )

# Columna Derecha: Mapa Interactivo
with col2:
    geojson_data = load_geojson()
    map_html = create_map(geojson_data, gasto_data, selected_departamento=departamento)
    st.components.v1.html(map_html.getvalue(), height=600)

# Barra lateral con información adicional
st.sidebar.header("Información Adicional")
st.sidebar.markdown("""
    Este mapa muestra el gasto público por departamento en Perú para el año 2023.
    <br>Seleccione cualquier departamento en el menú para obtener detalles específicos.
    <br><br>Este proyecto fue desarrollado como una herramienta de visualización de datos para el análisis regional.
    """, unsafe_allow_html=True)

# Notificación para el usuario
st.sidebar.info("Seleccione un departamento para ver su gasto anual.")

import streamlit as st
import pandas as pd
import altair as alt
from functions import load_geojson, load_gasto_data, create_map

# Configuración de la página de Streamlit
st.set_page_config(page_title="Mapa del Gasto Público en Perú 🌍", page_icon="🌍", layout="wide")
st.title("Mapa Interactivo del Gasto Público en Perú - Año 2023 🌍")

# Cargar datos de gasto
gasto_data = load_gasto_data()

# Función para cargar datos de gasto mensual optimizado
@st.cache_data
def load_gasto_mensual():
    df = pd.read_csv("gasto_mensual_por_departamento.csv")
    # Asegurarnos de que las columnas son del tipo correcto
    df['Mes'] = df['Mes'].astype(int)
    df['Gasto_Mensual'] = df['Gasto_Mensual'].astype(float)
    return df

gasto_mensual_data = load_gasto_mensual()

# Eliminar el mes '0' en el dataframe de gasto mensual
gasto_mensual_data = gasto_mensual_data[gasto_mensual_data['Mes'] != 0]

col1, col2 = st.columns([1, 2], gap="medium")

with col1:
    st.header("Información de Gasto Público 📊")

    # Selector de departamento
    departamento = st.selectbox("Seleccione un departamento", gasto_data['Departamento'].unique())
    gasto_total = gasto_data[gasto_data['Departamento'] == departamento]['Gasto_Total'].values[0]

    st.subheader(f"Departamento: {departamento}")
    st.markdown("<hr style='border:1px solid #ddd;'>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size: 24px; font-weight: bold; color: #333;'>Gasto Total Anual:</div>"
        f"<div style='font-size: 32px; font-weight: bold; color: #FF6347;'>S/ {gasto_total:,.2f}</div>",
        unsafe_allow_html=True
    )

    # Filtrar los datos del departamento seleccionado para mostrar todos los meses
    datos_departamento = gasto_mensual_data[gasto_mensual_data['Departamento'] == departamento].copy()

    # Asegurarse de que los meses estén ordenados correctamente
    datos_departamento = datos_departamento.sort_values('Mes')

    # Mostrar los gastos mensuales en texto
    st.write("**Gastos Mensuales por Mes:**")
    for i, row in datos_departamento.iterrows():
        mes, gasto = row['Mes'], row['Gasto_Mensual']
        st.write(f"- Mes {mes}: S/ {gasto:,.2f}")

    # Crear el gráfico de barras de gasto mensual con colores diferentes por cada mes
    st.subheader("Gasto Mensual")

    # Verificar si hay datos para mostrar
    if not datos_departamento.empty:
        chart = alt.Chart(datos_departamento).mark_bar().encode(
            x=alt.X('Mes:O',
                    title='Mes',
                    sort=None),  # Mantener el orden natural de los meses
            y=alt.Y('Gasto_Mensual:Q',
                    title='Gasto (S/)',
                    scale=alt.Scale(zero=True)),
            color=alt.Color('Mes:O',  # Asignar un color único por mes
                           scale=alt.Scale(scheme='category20'),  # Usar una escala de colores
                           legend=None),  # No mostrar leyenda de color
            tooltip=[
                alt.Tooltip('Mes:O', title='Mes'),
                alt.Tooltip('Gasto_Mensual:Q', title='Gasto', format=',.2f')
            ]
        ).properties(
            width='container',
            height=300,
            title=f"Gasto Mensual - {departamento}"
        )

        # Mostrar el gráfico
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No hay datos disponibles para mostrar el gráfico.")

with col2:
    geojson_data = load_geojson()
    map_html = create_map(geojson_data, gasto_data, selected_departamento=departamento)
    st.components.v1.html(map_html.getvalue(), height=600)

# Información adicional en la barra lateral
st.sidebar.header("Información Adicional")
st.sidebar.markdown(""" 
    Este mapa muestra el gasto público por departamento en Perú para el año 2023.
    <br>Seleccione cualquier departamento en el menú para obtener detalles específicos.
    <br><br>Este proyecto fue desarrollado como una herramienta de visualización de datos para el análisis regional.
    """, unsafe_allow_html=True)

st.sidebar.info("Seleccione un departamento para ver su gasto mensual y anual.")

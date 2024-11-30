import streamlit as st
import pandas as pd
import altair as alt
from functions import load_geojson, load_gasto_data, create_map
from streamlit_option_menu import option_menu
import Graphics


def colocar_css(nombre):                        # Leer archivo css
    file = open(nombre, "r", encoding="utf-8")  # Abrir con encodificación utf-8
    lines = ""
    for line in file:                           # Copiar las líneas
        lines = lines + line
    st.markdown(lines, unsafe_allow_html=True)  # Colocar las líneas como css y cerrar archivo
    file.close()


class PublicSpendingApp:
    def __init__(self):                         # Inicialización
        self._configure_page()                  # Configurar página
        self._load_data()                       # Carga de datos
        self._setup_navigation_menu()           # Instalación del menú de navegación

    @staticmethod                               # Modificación aquí, pycharm me lo sugirió ** ELIMINAR COMENTARIO **
    def _configure_page():
        """Configuración inicial de la página de Streamlit"""
        st.set_page_config(
            page_title="Mapa del Gasto Público en Perú 🌍",
            page_icon="🌍",
            layout="wide"
        )
        st.title("Visualización del Gasto Público en Perú - Año 2023 🌍")

    def _load_data(self):
        """Cargar datos de gasto"""
        try:                                    # Intentar cargar datos de gastos
            self.gasto_data = load_gasto_data()
            self.gasto_mensual_data = self._load_gasto_mensual()
        except Exception as e:                  # De lo contrario, mensaje de error
            st.error(f"Error al cargar los datos: {e}")
            self.gasto_data = pd.DataFrame()
            self.gasto_mensual_data = pd.DataFrame()

    @staticmethod
    @st.cache_data
    def _load_gasto_mensual():
        """Cargar datos de gasto mensual optimizado"""
        try:                                                        # Intentar cargar datos
            df = pd.read_csv("gasto_mensual_por_departamento.csv")      # Abrir csv
            df['Mes'] = df['Mes'].astype(int)                           # Conversión a entero
            df['Gasto_Mensual'] = df['Gasto_Mensual'].astype(float)     # Conversión a flotante
            return df[df['Mes'] != 0]                                   # Devolver valores diferentes a cero
        except Exception as e:                                      # De lo contrario, mensaje de error
            st.error(f"Error al cargar datos de gasto mensual: {e}")
            return pd.DataFrame()

    def _setup_navigation_menu(self):
        """Configurar menú de navegación horizontal"""
        selected = option_menu(
            menu_title=None,
            options=["Página principal", "Gráficas de Gasto", "Comparativo", "Información"],
            icons=["house", "bar-chart", "filter", "info-circle"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={"container": {"max-width": "300%", "padding": "10px 0"}}
        )

        if selected == "Página principal":                          # Mostrar contenido según la opción seleccionada
            self._render_map_page()
        elif selected == "Gráficas de Gasto":
            Graphics.mostrar_gasto_mensual_region()
        elif selected == "Comparativo":
            self._render_comparative_page()
        elif selected == "Información":
            self._render_info_page()

    def _render_map_page(self):
        """Renderizar página principal con mapa interactivo"""
        st.header("Mapa Interactivo del Gasto Público en Perú")     # Cabecera
        if self.gasto_data.empty:                                   # Verificar que los datos no estén vacíos
            st.warning("No se pudieron cargar los datos de gasto.")
            return
        try:                                                        # Intentar crear mapa
            geojson_data = load_geojson()                               # Cargar archivo de mapa
            map_html = create_map(                                      # Crear mapa interactivo
                geojson_data,
                self.gasto_data,
                selected_departamento=st.session_state.get('selected_departamento', None)
            )
            st.components.v1.html(map_html.getvalue(), height=600)
        except Exception as e:                                      # O mandar mensaje de error
            st.error(f"Error al cargar el mapa interactivo: {e}")


    def _render_comparative_page(self):
        """Renderizar la página comparativa de gasto público"""
        st.header("Comparativo de Gasto Público")

        # Selector de tipo de comparación
        comparativo_tipo = st.radio(
            "Seleccione el tipo de comparación:",
            options=["Gasto Total Anual", "Gasto Mensual"]
        )

        if comparativo_tipo == "Gasto Total Anual":
            # Comparativo de gasto total anual entre departamentos
            Graphics.mostrar_gasto_anual()
        elif comparativo_tipo == "Gasto Mensual":
            # Comparativo de gasto mensual entre departamentos
            Graphics.mostrar_gasto_mensual()


    @staticmethod                           # SUGERENCIA DE PYCHARM **ELIMINAR COMENTARIO**
    def _render_info_page():
        colocar_css("CSS/style.css")            # Leer archivo CSS de estilos

        col1, col2 = st.columns(2)          # Crear columnas de los autores

        with col1:
            colocar_css("CSS/autores_1.css")    # Archivo de autores 1
        with col2:
            colocar_css("CSS/autores_2.css")    # Archivo de autores 2

        colocar_css("CSS/info.css")             # Colocar información adicional del proyecto


if __name__ == "__main__":
    PublicSpendingApp()

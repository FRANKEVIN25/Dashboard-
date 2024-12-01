import streamlit as st
from streamlit_option_menu import option_menu
import Graphics
import Map_loader


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
            Map_loader.render_map()
        elif selected == "Gráficas de Gasto":
            Graphics.mostrar_gasto_mensual_region()
        elif selected == "Comparativo":
            self._render_comparative_page()
        elif selected == "Información":
            self._render_info_page()

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

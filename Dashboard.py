import streamlit as st
import pandas as pd
import altair as alt
from functions import load_geojson, load_gasto_data, create_map
from streamlit_option_menu import option_menu


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
            self._render_graphs_page()
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

    def _render_graphs_page(self):
        """Renderizar gráficos de gastos"""
        st.header("Gráficas Comparativas de Gasto Público")         # Cabecera
        if self.gasto_data.empty or self.gasto_mensual_data.empty:  # Verificar que los datos no estén vacíos
            st.warning("No hay datos disponibles para graficar.")
            return

        col1, col2 = st.columns([1, 2], gap="medium")               # Crear columnas
        with col1:
            self._render_department_selector()                      # Selector de departamentos
        with col2:
            # Mensaje de instrucciones
            st.write("Seleccione un departamento en el menú de la izquierda para ver gráficos.")

            # Obtener departamento seleccionado y mostrar gráfico de barras
            selected_departamento = st.session_state.get('selected_departamento', None)
            if selected_departamento:
                self._render_monthly_bar_chart(selected_departamento)

    def _render_department_selector(self):
        """Selector de departamento con información detallada"""
        if self.gasto_data.empty or 'Departamento' not in self.gasto_data.columns:  # Verificar que no esté vacío
            st.warning("No hay datos de departamentos disponibles.")
            return

        departamento = st.selectbox(                                # Selector de departamentos
            "Seleccione un departamento",
            self.gasto_data['Departamento'].unique()
        )
        st.session_state['selected_departamento'] = departamento    # Guardar en el estado de la sesión
        try:
            gasto_total = self.gasto_data[
                self.gasto_data['Departamento'] == departamento         # Utilizar archivo de gastos anuales
                ]['Gasto_Total'].values[0]
            st.subheader(f"Departamento: {departamento}")               # Títulos y cabeceras
            st.markdown(f"*Gasto Total Anual:* S/ {gasto_total:,.2f}")
            self._render_monthly_expenses(departamento)                 # Renderizar gastos mensuales
        except Exception as e:                                      # En caso de error mandar advertencia
            st.error(f"Error al mostrar datos: {e}")

    def _render_monthly_expenses(self, departamento):
        """Mostrar gastos mensuales"""
        datos_departamento = self.gasto_mensual_data[               # Utilizar archivo de gastos mensuales
            self.gasto_mensual_data['Departamento'] == departamento
            ].sort_values('Mes')
        if datos_departamento.empty:                                # Advertir en caso de que estén vacíos
            st.warning(f"No hay datos mensuales para {departamento}")
            return
        st.write("*Gastos Mensuales:*")
        for _, row in datos_departamento.iterrows():                # Escribir los datos que contienen los gastos
            st.write(f"- Mes {row['Mes']}: S/ {row['Gasto_Mensual']:,.2f}")

    def _render_monthly_bar_chart(self, departamento):
        """Crear gráfico de barras de gasto mensual con colores sólidos"""
        datos_departamento = self.gasto_mensual_data[               # Utilizar archivo de gastos mensuales
            self.gasto_mensual_data['Departamento'] == departamento
        ].sort_values('Mes')

        if datos_departamento.empty:                                # Advertir si los datos están vacíos
            st.warning("No hay datos disponibles para el gráfico.")
            return

        # Crear el gráfico de barras con colores sólidos
        bar_chart = alt.Chart(datos_departamento).mark_bar().encode(
            x=alt.X('Mes:O', title='Mes'),
            y=alt.Y('Gasto_Mensual:Q', title='Gasto (S/)'),
            color=alt.Color('Mes:O',
                            scale=alt.Scale(
                                range=['red', 'green', 'blue', 'orange', 'purple',
                                       'brown', 'pink', 'yellow', 'cyan', 'magenta',
                                       'gray', 'white']
                            ),
                            title='Mes'),
            tooltip=[alt.Tooltip('Mes:O', title='Mes'),
                     alt.Tooltip('Gasto_Mensual:Q', format=',.2f', title='Gasto (S/)')]
        ).properties(
            title=f"Gasto Mensual - {departamento}",
            height=500  # Ajustar la altura del gráfico
        ).configure_title(
            fontSize=18, anchor='start', color='gray'
        )

        # Mostrar el gráfico de barras
        st.altair_chart(bar_chart, use_container_width=True)

        # Crear el gráfico circular de pastel
        pie_chart = alt.Chart(datos_departamento).mark_arc(stroke='black', strokeWidth=2).encode(
            theta=alt.Theta('Gasto_Mensual:Q', title='Porcentaje de Gasto'),
            color=alt.Color('Mes:O',
                            scale=alt.Scale(
                                range=['red', 'green', 'blue', 'orange', 'purple',
                                       'brown', 'pink', 'yellow', 'cyan', 'magenta',
                                       'gray', 'white']
                            ),
                            title='Mes'),
            tooltip=[alt.Tooltip('Mes:O', title='Mes'),
                     alt.Tooltip('Gasto_Mensual:Q', format=',.2f', title='Gasto (S/)')]
        ).properties(
            title=f"Distribución Porcentual del Gasto Mensual - {departamento}",
            height=500,  # Altura del gráfico circular
            width=500    # Ancho del gráfico circular
        ).configure_title(
            fontSize=16, anchor='middle', color='gray'
        )

        # Mostrar el gráfico de pastel
        st.altair_chart(pie_chart, use_container_width=True)

        # Espacio adicional después de los gráficos
        st.markdown("<br>", unsafe_allow_html=True)


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
            self._render_total_comparison()
        elif comparativo_tipo == "Gasto Mensual":
            # Comparativo de gasto mensual entre departamentos
            self._render_monthly_comparison()


    def _render_total_comparison(self):
        """Mostrar gráfico comparativo de gasto total anual"""
        if self.gasto_data.empty:
            st.warning("No hay datos disponibles para el gasto total anual.")
            return

        # Crear el gráfico de barras comparativo
        bar_chart = alt.Chart(self.gasto_data).mark_bar().encode(
            x=alt.X('Departamento:O', title='Departamento', sort='-y'),
            y=alt.Y('Gasto_Total:Q', title='Gasto Total Anual (S/)'),
            color=alt.Color('Departamento:O', scale=alt.Scale(scheme='inferno'), title='Departamento'),
            tooltip=[alt.Tooltip('Departamento:O', title='Departamento'),
                     alt.Tooltip('Gasto_Total:Q', format=',.2f', title='Gasto Total (S/)')]
        ).properties(
            title="Comparativo de Gasto Total Anual por Departamento",
            height=500
        ).configure_title(
            fontSize=18, anchor='start', color='gray'
        )

        st.altair_chart(bar_chart, use_container_width=True)


    def _render_monthly_comparison(self):
        """Mostrar gráfico comparativo de gasto mensual entre departamentos"""
        if self.gasto_mensual_data.empty:
            st.warning("No hay datos disponibles para el gasto mensual.")
            return

        # Selector de mes
        meses = sorted(self.gasto_mensual_data['Mes'].unique())
        selected_mes = st.selectbox("Seleccione un mes para comparar:", options=["Todos"] + meses)

        # Filtrar datos según el mes seleccionado
        if selected_mes != "Todos":
            datos_filtrados = self.gasto_mensual_data[
                self.gasto_mensual_data['Mes'] == selected_mes
                ]
            titulo = f"Comparativo de Gasto Mensual por Departamento - Mes {selected_mes}"
        else:
            datos_filtrados = self.gasto_mensual_data
            titulo = "Comparativo de Gasto Mensual por Departamento (Todos los Meses)"

        if datos_filtrados.empty:
            st.warning("No hay datos para la selección realizada.")
            return

        # Crear el gráfico de barras apilado o normal según la selección
        bar_chart = alt.Chart(datos_filtrados).mark_bar().encode(
            x=alt.X('Departamento:O', title='Departamento'),
            y=alt.Y('Gasto_Mensual:Q', title='Gasto Mensual (S/)'),
            color=alt.Color('Mes:O', scale=alt.Scale(scheme='inferno'), title='Mes' if selected_mes == "Todos" else None),
            tooltip=[
                alt.Tooltip('Departamento:O', title='Departamento'),
                alt.Tooltip('Mes:O', title='Mes'),
                alt.Tooltip('Gasto_Mensual:Q', format=',.2f', title='Gasto Mensual (S/)')
            ]
        ).properties(
            title=titulo,
            height=500
        ).configure_title(
            fontSize=18, anchor='start', color='gray'
        )

        st.altair_chart(bar_chart, use_container_width=True)

    @staticmethod                           # SUGERENCIA DE PYCHARM **ELIMINAR COMENTARIO**
    def _render_info_page():
        colocar_css("style.css")            # Leer archivo CSS de estilos

        col1, col2 = st.columns(2)          # Crear columnas de los autores

        with col1:
            colocar_css("autores_1.css")    # Archivo de autores 1
        with col2:
            colocar_css("autores_2.css")    # Archivo de autores 2

        colocar_css("info.css")             # Colocar información adicional del proyecto


if __name__ == "__main__":
    PublicSpendingApp()

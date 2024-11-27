import streamlit as st
import pandas as pd
import altair as alt
from functions import load_geojson, load_gasto_data, create_map
from streamlit_option_menu import option_menu

class PublicSpendingApp:
    def __init__(self):
        self._configure_page()
        self._load_data()
        self._setup_navigation_menu()

    def _configure_page(self):
        """Configuración inicial de la página de Streamlit"""
        st.set_page_config(
            page_title="Mapa del Gasto Público en Perú 🌍",
            page_icon="🌍",
            layout="wide"
        )
        st.title("Visualización del Gasto Público en Perú - Año 2023 🌍")

    def _load_data(self):
        """Cargar datos de gasto"""
        try:
            self.gasto_data = load_gasto_data()
            self.gasto_mensual_data = self._load_gasto_mensual()
        except Exception as e:
            st.error(f"Error al cargar los datos: {e}")
            self.gasto_data = pd.DataFrame()
            self.gasto_mensual_data = pd.DataFrame()

    @staticmethod
    @st.cache_data
    def _load_gasto_mensual():
        """Cargar datos de gasto mensual optimizado"""
        try:
            df = pd.read_csv("gasto_mensual_por_departamento.csv")
            df['Mes'] = df['Mes'].astype(int)
            df['Gasto_Mensual'] = df['Gasto_Mensual'].astype(float)
            return df[df['Mes'] != 0]
        except Exception as e:
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

        # Mostrar contenido según la opción seleccionada
        if selected == "Página principal":
            self._render_map_page()
        elif selected == "Gráficas de Gasto":
            self._render_graphs_page()
        elif selected == "Comparativo":
            self._render_comparative_page()
        elif selected == "Información":
            self._render_info_page()

    def _render_map_page(self):
        """Renderizar página principal con mapa interactivo"""
        st.header("Mapa Interactivo del Gasto Público en Perú")
        if self.gasto_data.empty:
            st.warning("No se pudieron cargar los datos de gasto.")
            return
        try:
            geojson_data = load_geojson()
            map_html = create_map(
                geojson_data,
                self.gasto_data,
                selected_departamento=st.session_state.get('selected_departamento', None)
            )
            st.components.v1.html(map_html.getvalue(), height=600)
        except Exception as e:
            st.error(f"Error al cargar el mapa interactivo: {e}")

    def _render_graphs_page(self):
        """Renderizar gráficos de gastos"""
        st.header("Gráficas Comparativas de Gasto Público")
        if self.gasto_data.empty or self.gasto_mensual_data.empty:
            st.warning("No hay datos disponibles para graficar.")
            return

        col1, col2 = st.columns([1, 2], gap="medium")
        with col1:
            self._render_department_selector()
        with col2:
            st.write("Seleccione un departamento en el menú de la izquierda para ver gráficos.")

    def _render_department_selector(self):
        """Selector de departamento con información detallada"""
        if self.gasto_data.empty or 'Departamento' not in self.gasto_data.columns:
            st.warning("No hay datos de departamentos disponibles.")
            return

        departamento = st.selectbox(
            "Seleccione un departamento",
            self.gasto_data['Departamento'].unique()
        )
        try:
            gasto_total = self.gasto_data[
                self.gasto_data['Departamento'] == departamento
            ]['Gasto_Total'].values[0]
            st.subheader(f"Departamento: {departamento}")
            st.markdown(f"**Gasto Total Anual:** S/ {gasto_total:,.2f}")
            self._render_monthly_expenses(departamento)
            self._render_monthly_bar_chart(departamento)
        except Exception as e:
            st.error(f"Error al mostrar datos: {e}")

    def _render_monthly_expenses(self, departamento):
        """Mostrar gastos mensuales"""
        datos_departamento = self.gasto_mensual_data[
            self.gasto_mensual_data['Departamento'] == departamento
        ].sort_values('Mes')
        if datos_departamento.empty:
            st.warning(f"No hay datos mensuales para {departamento}")
            return
        st.write("**Gastos Mensuales:**")
        for _, row in datos_departamento.iterrows():
            st.write(f"- Mes {row['Mes']}: S/ {row['Gasto_Mensual']:,.2f}")

    def _render_monthly_bar_chart(self, departamento):
        """Crear gráfico de barras de gasto mensual"""
        datos_departamento = self.gasto_mensual_data[
            self.gasto_mensual_data['Departamento'] == departamento
        ].sort_values('Mes')
        if datos_departamento.empty:
            st.warning("No hay datos disponibles para el gráfico.")
            return
        chart = alt.Chart(datos_departamento).mark_bar().encode(
            x=alt.X('Mes:O', title='Mes'),
            y=alt.Y('Gasto_Mensual:Q', title='Gasto (S/)'),
            tooltip=[alt.Tooltip('Mes:O'), alt.Tooltip('Gasto_Mensual:Q', format=',.2f')]
        ).properties(title=f"Gasto Mensual - {departamento}")
        st.altair_chart(chart, use_container_width=True)

    def _render_comparative_page(self):
        st.header("Comparativo de Gasto Público")

    def _render_info_page(self):
        st.header("Información del Proyecto")
        st.markdown("**Proyecto de Visualización del Gasto Público en el Perú 2023.**")

if __name__ == "__main__":
    PublicSpendingApp()

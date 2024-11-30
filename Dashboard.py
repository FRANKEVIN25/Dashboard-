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

        # Crear columnas para selector y mensaje
        col1, col2 = st.columns([1, 2], gap="medium")
        with col1:
            self._render_department_selector()
        with col2:
            # Mensaje de instrucciones
            st.write("Seleccione un departamento en el menú de la izquierda para ver gráficos.")

            # Obtener departamento seleccionado y mostrar gráfico de barras
            selected_departamento = st.session_state.get('selected_departamento', None)
            if selected_departamento:
                self._render_monthly_bar_chart(selected_departamento)

    def _render_department_selector(self):
        """Selector de departamento con información detallada"""
        if self.gasto_data.empty or 'Departamento' not in self.gasto_data.columns:
            st.warning("No hay datos de departamentos disponibles.")
            return

        departamento = st.selectbox(
            "Seleccione un departamento",
            self.gasto_data['Departamento'].unique()
        )
        st.session_state['selected_departamento'] = departamento  # Guardar en el estado de la sesión
        try:
            gasto_total = self.gasto_data[
                self.gasto_data['Departamento'] == departamento
                ]['Gasto_Total'].values[0]
            st.subheader(f"Departamento: {departamento}")
            st.markdown(f"*Gasto Total Anual:* S/ {gasto_total:,.2f}")
            self._render_monthly_expenses(departamento)
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
        st.write("*Gastos Mensuales:*")
        for _, row in datos_departamento.iterrows():
            st.write(f"- Mes {row['Mes']}: S/ {row['Gasto_Mensual']:,.2f}")

    def _render_monthly_bar_chart(self, departamento):
        """Crear gráfico de barras de gasto mensual con colores sólidos"""
        datos_departamento = self.gasto_mensual_data[
            self.gasto_mensual_data['Departamento'] == departamento
        ].sort_values('Mes')

        if datos_departamento.empty:
            st.warning("No hay datos disponibles para el gráfico.")
            return

        # Crear el gráfico con colores sólidos
        chart = alt.Chart(datos_departamento).mark_bar().encode(
            x=alt.X('Mes:O', title='Mes'),
            y=alt.Y('Gasto_Mensual:Q', title='Gasto (S/)'),
            color=alt.Color('Mes:O',
                            scale=alt.Scale(
                                range=['red', 'green', 'blue', 'orange', 'purple',
                                       'brown', 'pink', 'yellow', 'cyan', 'magenta',
                                       'gray', 'black']
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

        st.altair_chart(chart, use_container_width=True)

        # Agregar espacio adicional después del gráfico
        st.markdown("<br>", unsafe_allow_html=True)  # Espacio adicional debajo del gráfico

    def _render_comparative_page(self):
        st.header("Comparativo de Gasto Público")


    def _render_info_page(self):
        # Custom CSS for enhanced styling
        st.markdown("""
        <style>
        .info-header {
            background-color: #1f4e79; 
            color: white; 
            padding: 30px; 
            border-radius: 15px; 
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .info-header h1 {
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .info-header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .section-title {
            color: #1f4e79;
            border-bottom: 2px solid #1f4e79;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        .author-card {
            background-color: #f4f4f4;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)

        # Main Header
        st.markdown("""
        <div class="info-header">
            <h1>Información del Proyecto</h1>
            <p>Proyecto de Visualización del Gasto Público en el Perú 2023</p>
        </div>
        """, unsafe_allow_html=True)

        # Authors Section
        st.markdown("<h2 class='section-title'>👥 Autores del Proyecto</h2>", unsafe_allow_html=True)
        
        # Create columns for author cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="author-card">
                <h3>Frank Kevin Jauregui Bendezu</h3>
                <p><i>Investigador Principal</i></p>
                <p>Responsable de la recopilación y análisis de datos de gasto público.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="author-card">
                <h3>John Kenneth Karita</h3>
                <p><i>Analista de Datos</i></p>
                <p>Especialista en visualización y procesamiento de información estadística.</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="author-card">
                <h3>Jesus Anselmo Morales Alvarado</h3>
                <p><i>Coordinador de Investigación</i></p>
                <p>Supervisión metodológica y estructuración del proyecto.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="author-card">
                <h3>Jheyson Smith Anselmo Castañeda Tello</h3>
                <p><i>Desarrollador de Visualizaciones</i></p>
                <p>Implementación de herramientas interactivas y diseño de interfaz.</p>
            </div>
            """, unsafe_allow_html=True)

        # Existing Sections with Improved Formatting
        st.markdown("<h2 class='section-title'>📘 ¿Qué son los gastos públicos?</h2>", unsafe_allow_html=True)
        st.write("""
        Los **gastos públicos** son las inversiones y gastos realizados por el gobierno para satisfacer 
        las necesidades de la sociedad, como salud, educación, infraestructura, seguridad, entre otros.
        """)

        st.markdown("<h2 class='section-title'>🇵🇪 Gasto Público en el Perú</h2>", unsafe_allow_html=True)
        st.markdown("""
        En el Perú, el gasto público se realiza a través de **tres niveles de gobierno**:
        - 🏛️ **Gobierno Nacional:** Responsable de políticas nacionales y grandes proyectos.
        - 🌍 **Gobiernos Regionales:** Encargados de la administración de servicios como salud y educación en su ámbito territorial.
        - 🏘️ **Gobiernos Locales:** Gestionan obras y servicios básicos en los municipios.
        """)

        st.markdown("<h2 class='section-title'>✨ Enfoques del Presupuesto 2023</h2>", unsafe_allow_html=True)
        st.markdown("""
        Para el año 2023, el gasto público en el Perú se ha enfocado principalmente en sectores clave:
        - 🎓 **Educación:** Incremento en infraestructura educativa y acceso a tecnologías.
        - 🏥 **Salud:** Fortalecimiento del sistema de salud post-pandemia.
        - 🚧 **Infraestructura:** Construcción de carreteras, obras de agua potable y proyectos de energía.
        """)

        st.markdown("<h2 class='section-title'>📊 Distribución Presupuestal 2023</h2>", unsafe_allow_html=True)
        st.markdown("""
        Según el Ministerio de Economía y Finanzas (MEF):
        - 📘 **Educación:** Representa aproximadamente el **17%** del presupuesto total.
        - 🏥 **Salud:** Cerca del **11%** del gasto total.
        - 🚧 **Infraestructura:** Un **12%** dirigido a mejorar la conectividad.
        """)

        st.markdown("<h2 class='section-title'>💰 Fuentes de Financiamiento</h2>", unsafe_allow_html=True)
        st.write("""
        Los gastos públicos se financian principalmente mediante:
        - 🏦 **Impuestos:** Como el IGV e Impuesto a la Renta.
        - ⛏️ **Canon y Regalías:** Por explotación de minerales y recursos naturales.
        - 💳 **Deuda Pública:** Emisión de bonos y préstamos internacionales.
        """)

        st.markdown("<h2 class='section-title'>🚩 Desafíos Actuales</h2>", unsafe_allow_html=True)
        st.markdown("""
        - ⚙️ **Ejecución Presupuestal:** Dificultades de gobiernos locales para ejecutar el presupuesto asignado.
        - ❌ **Corrupción:** Desvío de recursos públicos.
        - 🌍 **Desigualdad Regional:** Brechas de inversión entre regiones.
        """)

        # Footer with Information Sources
        st.markdown("""
        <hr style="border:1px solid #ccc; margin-top: 30px;">
        <div style="text-align:center; margin-top: 20px;">
            <h3>🌐 Fuentes de Información</h3>
            <p>
                <a href="https://www.mef.gob.pe" target="_blank" style="margin: 0 10px;">Ministerio de Economía y Finanzas</a> | 
                <a href="https://www.mef.gob.pe/es/presupuesto-publico" target="_blank" style="margin: 0 10px;">Presupuesto Público del Perú</a> | 
                <a href="https://www.inei.gob.pe" target="_blank" style="margin: 0 10px;">INEI: Estadísticas del Gasto Público</a>
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    PublicSpendingApp()

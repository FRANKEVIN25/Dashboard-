import streamlit as st
import pandas as pd
import altair as alt
from streamlit_option_menu import option_menu

meses = {"ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
         "JUL": 7, "AGO": 8, "SET": 9, "OCT": 10, "NOV": 11, "DIC": 12}

meses_2 = {1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 5: "MAY", 6: "JUN",
         7: "JUL", 8: "AGO", 9: "SET", 10: "OCT", 11: "NOV", 12: "DIC"}

departamentos = ["AMAZONAS", "ANCASH", "APURIMAC", "AREQUIPA",
                 "AYACUCHO", "CAJAMARCA", "CUSCO", "HUANCAVELICA",
                 "HUANUCO", "ICA", "JUNIN", "LA LIBERTAD",
                 "LAMBAYEQUE", "LIMA", "LORETO", "MADRE DE DIOS",
                 "MOQUEGUA", "PASCO", "PIURA", "PUNO",
                 "SAN MARTIN", "TACNA", "TUMBES", "UCAYALI",
                 "CALLAO"]

colores = ['black', 'brown', 'red', 'orange', 'yellow', 'green',
           'blue', 'magenta', '#404040', '#F0F0F0', 'gold', 'silver']


def crear_cinta_de_opciones(opciones):  # Crear una cinta de opciones, información proporcionada en el parámetro
    return option_menu(menu_title=None, options=opciones, menu_icon="cast", default_index=0,
                       orientation="horizontal", styles={"container": {"max-width": "300%", "padding": "10px 0"}})


def crear_tabla(datos):                 # Crear una tabla, convierte de pandas a html y lo coloca como css
    html_table = datos.to_html(index=False)
    st.markdown(f"""
        <div style="max-height: 600px; overflow-y: auto; font-size: 14px;">
            {html_table}
        </div>
    """, unsafe_allow_html=True)


def crear_grafico(datos, selected, titulo, tipo):
    if tipo == 1:     # Gasto anual por departamento. Múltiples colores, ningún código específico
        graph = alt.Chart(datos).mark_bar().encode(
            x=alt.X('Departamento:O', title='Departamento', sort='-y'),
            y=alt.Y("y_" + str(selected) + ":Q", title='Gasto Total Anual (S/)'),
            color=alt.Color('Departamento:O', scale=alt.Scale(scheme='inferno'),
                            legend=None, title='Departamento'),
            tooltip=[alt.Tooltip('Departamento:O', title='Departamento'),
                     alt.Tooltip("y_" + str(selected) + ":Q", format=',.2f', title='Gasto Total (S/)')]
        ).properties(title=titulo, height=640).configure_title(fontSize=18, anchor='start', color='gray')

    elif tipo == 2:       # Gasto mensual por departamento. Monocromático o múltiples colores, depende de la selección
        graph = alt.Chart(datos).mark_bar().encode(
            x=alt.X('Departamento:O', title='Departamento'),
            y=alt.Y('Monto:Q', title='Gasto Mensual (S/)'),
            color=alt.Color('Mes:O', scale=alt.Scale(scheme='inferno'),
                            title='Mes' if selected == "TODOS" else None),
            tooltip=[alt.Tooltip('Departamento:O', title='Departamento'),
                     alt.Tooltip('Mes:O', title='Mes'),
                     alt.Tooltip('Gasto_Mensual:Q', format=',.2f', title='Gasto Mensual (S/)')]
        ).properties(title=titulo, height=500).configure_title(fontSize=18, anchor='start', color='gray')

    elif tipo == 3:     # Gasto mensual de un solo departamento. Gráfico de barras, código de colores de resistencia
        graph = alt.Chart(datos).mark_bar().encode(
            x=alt.X('Mes:O', title='Mes'),
            y=alt.Y('Monto:Q', title='Gasto (S/)'),
            color=alt.Color('Mes:O', scale=alt.Scale(range=colores), title='Mes'),
            tooltip=[alt.Tooltip('Mes:O', title='Mes'),
                     alt.Tooltip('Monto:Q', format=',.2f', title='Gasto (S/)')]
        ).properties(title=titulo, height=500).configure_title(fontSize=18, anchor='start', color='gray')

    else:               # Gasto mensual de un solo departamento. Gráfico circular, código de colores de resistencia
        graph = alt.Chart(datos).mark_arc(stroke='black', strokeWidth=2).encode(
            theta=alt.Theta('Monto:Q', title='Porcentaje de Gasto'),
            color=alt.Color('Mes:O', scale=alt.Scale(range=colores), title='Mes'),
            tooltip=[alt.Tooltip('Mes:O', title='Mes'),
                     alt.Tooltip('Monto:Q', format=',.2f', title='Gasto (S/)')]
        ).properties(
            title=f"Distribución Porcentual del Gasto Mensual - {selected}", height=500, width=500
        ).configure_title(fontSize=16, anchor='middle', color='gray')

    st.altair_chart(graph, use_container_width=True)    # Mostrar cualquier opción seleccionado


def mostrar_gasto_anual():
    selected = crear_cinta_de_opciones([year for year in range(2012, 2024)])

    gasto_anual = pd.read_csv("Gasto-Anual/Gasto-Anual-2012-2023.csv")  # Abrir archivo, ordenar y seleccionar
    year = pd.concat([gasto_anual["Departamento"], gasto_anual["y_"+str(selected)]], axis=1)
    year = year.sort_values(by="y_"+str(selected), ascending=False)

    col1, col2 = st.columns([5, 2])                                     # Asignar columnas con diferentes proporciones
    with col1:                                                          # Colocar gráfico de barras
        crear_grafico(year, selected, "Comparativo de Gasto Total Anual por Departamento", 1)
    with col2:                                                          # Convertir dataframe a tabla html y mostrar
        year["y_"+str(selected)] = year["y_"+str(selected)].apply(lambda x: f"{x:,.2f}")
        crear_tabla(year)


def mostrar_gasto_mensual():
    year_sel = crear_cinta_de_opciones([year for year in range(2012, 2024)])    # Selección de años y meses
    month_sel = crear_cinta_de_opciones(["TODOS"] + [element for element in meses])

    gasto_mensual = pd.read_csv("Gasto-Mensual/" + str(year_sel) + "-Gasto-Mensual-Por-Region.csv")  # Abrir csv

    if month_sel != "TODOS":                                                    # Mostrar gráfico apilado (año entero)
        datos_filtrados = gasto_mensual[gasto_mensual['Mes'] == meses[month_sel]]
        titulo = f"Comparativo de Gasto Mensual por Departamento - Mes {month_sel}"

    else:                                                                       # Mostrar gráfico normal (un mes)
        datos_filtrados = gasto_mensual
        titulo = "Comparativo de Gasto Mensual por Departamento (Todos los Meses)"

    if datos_filtrados.empty:                                                   # Verificar que no esté vacío
        st.warning("No hay datos para la selección realizada.")
        return

    crear_grafico(datos_filtrados, month_sel, titulo, 2)                    # Crear gráfico de barras


def mostrar_gasto_mensual_region():
    year_sel = crear_cinta_de_opciones([year for year in range(2012, 2024)])    # Selección de años

    gasto_mensual = pd.read_csv("Gasto-Mensual/" + str(year_sel) + "-Gasto-Mensual-Por-Region.csv")  # Abrir csv
    col1, col2, col3 = st.columns([1, 2, 2], gap="medium")                      # Crear columnas

    with col1:
        departamento = st.selectbox("Seleccione un departamento", departamentos)    # Selección de departamentos

        temporal = (gasto_mensual[gasto_mensual['Departamento'] == departamento].sort_values('Mes'))    # Filtrado
        temporal = pd.concat([temporal["Mes"], temporal["Monto"]], axis=1)
        temporal["Mes"] = temporal["Mes"].apply(lambda x: meses_2[int(x)])
        temporal["Monto"] = temporal["Monto"].apply(lambda x: f"{x:,.2f}")

        crear_tabla(temporal)                                                   # Mostrar datos filtrados
    with col2:
        datos_departamento = gasto_mensual[gasto_mensual['Departamento'] == departamento].sort_values(by="Mes")

        """Crear gráfico de barras de gasto mensual con colores sólidos"""
        if datos_departamento.empty:                                            # Verificar que no esté vacío
            st.warning("No hay datos disponibles para el gráfico.")
            return

        crear_grafico(datos_departamento, departamento, f"Gasto Mensual - {departamento}", 3)  # De barras
    with col3:
        crear_grafico(datos_departamento, departamento,
                      f"Distribución Porcentual del Gasto Mensual - {departamento}", 4)  # Gráfico de pastel

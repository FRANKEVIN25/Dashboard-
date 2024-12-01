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


def crear_cinta_de_opciones(opciones):
    return option_menu(  # Barra de opciones, años
        menu_title=None,
        options=opciones,  # Opciones de los años, su selección devolverá un entero
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={"container": {"max-width": "300%", "padding": "10px 0"}}
    )


def mostrar_gasto_anual():
    selected = crear_cinta_de_opciones([year for year in range(2012, 2024)])

    gasto_anual = pd.read_csv("Gasto-Anual\Gasto-Anual-2012-2023.csv")  # Abrir archivo, ordenar y seleccionar
    year = pd.concat([gasto_anual["Departamento"], gasto_anual["y_"+str(selected)]], axis=1)
    year = year.sort_values(by="y_"+str(selected), ascending=False)

    bar_chart = alt.Chart(year).mark_bar().encode(              # Crear gráfico de barras comparativo
        x=alt.X('Departamento:O', title='Departamento', sort='-y'),
        y=alt.Y("y_"+str(selected)+":Q", title='Gasto Total Anual (S/)'),

        color=alt.Color('Departamento:O', scale=alt.Scale(scheme='inferno'),    # Colores de cada departamento
                        legend=None, title='Departamento'),

        tooltip=[alt.Tooltip('Departamento:O', title='Departamento'),           # Qué mostrar al pasar el mouse
                 alt.Tooltip("y_"+str(selected)+":Q", format=',.2f', title='Gasto Total (S/)')]
    ).properties(
        title="Comparativo de Gasto Total Anual por Departamento",                       # Título de la gráfica
        height=640
    ).configure_title(
        fontSize=18, anchor='start', color='gray'
    )

    col1, col2 = st.columns([5, 2])                             # Asignar columnas con diferentes proporciones
    with col1:                                                  # Colocar gráfico de barras
        st.altair_chart(bar_chart, use_container_width=True)
    with col2:                                                  # Convertir dataframe a tabla html y mostrar
        year["y_"+str(selected)] = year["y_"+str(selected)].apply(lambda x: f"{x:,.2f}")
        html_table = year.to_html(index=False)

        st.markdown(f"""
            <div style="max-height: 600px; overflow-y: auto; font-size: 14px;">
                {html_table}
            </div>
        """, unsafe_allow_html=True)


def mostrar_gasto_mensual():
    """Mostrar gráfico comparativo de gasto mensual entre departamentos"""
    year_sel = crear_cinta_de_opciones([year for year in range(2012, 2024)])

    month_sel = crear_cinta_de_opciones(["TODOS", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                                         "JUL", "AGO", "SET", "OCT", "NOV", "DIC"])

    gasto_mensual = pd.read_csv("Gasto-Mensual/" + str(year_sel) + "-Gasto-Mensual-Por-Region.csv")

    if month_sel != "TODOS":
        datos_filtrados = gasto_mensual[
            gasto_mensual['Mes'] == meses[month_sel]
            ]
        titulo = f"Comparativo de Gasto Mensual por Departamento - Mes {month_sel}"

    else:
        datos_filtrados = gasto_mensual
        titulo = "Comparativo de Gasto Mensual por Departamento (Todos los Meses)"

    if datos_filtrados.empty:
        st.warning("No hay datos para la selección realizada.")
        return

    # Crear el gráfico de barras apilado o normal según la selección
    bar_chart = alt.Chart(datos_filtrados).mark_bar().encode(
        x=alt.X('Departamento:O', title='Departamento'),
        y=alt.Y('Monto:Q', title='Gasto Mensual (S/)'),
        color=alt.Color('Mes:O', scale=alt.Scale(scheme='inferno'), title='Mes' if month_sel == "TODOS" else None),
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


def mostrar_gasto_mensual_region():
    year_sel = crear_cinta_de_opciones([year for year in range(2012, 2024)])

    gasto_mensual = pd.read_csv("Gasto-Mensual/" + str(year_sel) + "-Gasto-Mensual-Por-Region.csv")
    col1, col2, col3= st.columns([1, 2, 2], gap="medium")  # Crear columnas


    with col1:
        departamento = st.selectbox(  # Selector de departamentos
            "Seleccione un departamento",
            departamentos)

        temporal = (gasto_mensual[gasto_mensual['Departamento'] == departamento].sort_values('Mes'))
        temporal = pd.concat([temporal["Mes"], temporal["Monto"]], axis=1)
        temporal["Mes"] = temporal["Mes"].apply(lambda x: meses_2[int(x)])
        temporal["Monto"] = temporal["Monto"].apply(lambda x: f"{x:,.2f}")

        html_table = temporal.to_html(index=False)

        st.markdown(f"""
            <div style="max-height: 600px; overflow-y: auto; font-size: 14px;">
                {html_table}
            </div>
        """, unsafe_allow_html=True)


    with col2:
        datos_departamento = gasto_mensual[               # Utilizar archivo de gastos mensuales
            gasto_mensual['Departamento'] == departamento
        ].sort_values(by="Mes")

        """Crear gráfico de barras de gasto mensual con colores sólidos"""
        if datos_departamento.empty:                                # Advertir si los datos están vacíos
            st.warning("No hay datos disponibles para el gráfico.")
            return

        # Crear el gráfico de barras con colores sólidos
        bar_chart = alt.Chart(datos_departamento).mark_bar().encode(
            x=alt.X('Mes:O', title='Mes'),
            y=alt.Y('Monto:Q', title='Gasto (S/)'),
            color=alt.Color('Mes:O',
                            scale=alt.Scale(
                                range=['black', 'brown', 'red', 'orange',
                                       'yellow', 'green', 'blue', 'magenta',
                                       '#404040', '#F0F0F0', 'gold', 'silver']
                            ),
                            title='Mes'),
            tooltip=[alt.Tooltip('Mes:O', title='Mes'),
                     alt.Tooltip('Monto:Q', format=',.2f', title='Gasto (S/)')]
        ).properties(
            title=f"Gasto Mensual - {departamento}",
            height=500  # Ajustar la altura del gráfico
        ).configure_title(
            fontSize=18, anchor='start', color='gray'
        )

            # Mostrar el gráfico de barras
        st.altair_chart(bar_chart, use_container_width=True)


    with col3:
            # Crear el gráfico circular de pastel
        pie_chart = alt.Chart(datos_departamento).mark_arc(stroke='black', strokeWidth=2).encode(
            theta=alt.Theta('Monto:Q', title='Porcentaje de Gasto'),
            color=alt.Color('Mes:O',
                            scale=alt.Scale(
                                range=['black', 'brown', 'red', 'orange',
                                       'yellow', 'green', 'blue', 'magenta',
                                       '#404040', '#F0F0F0', 'gold', 'silver']
                            ),
                            title='Mes'),
            tooltip=[alt.Tooltip('Mes:O', title='Mes'),
                     alt.Tooltip('Monto:Q', format=',.2f', title='Gasto (S/)')]
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
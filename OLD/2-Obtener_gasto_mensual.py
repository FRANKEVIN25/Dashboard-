import pandas as pd


def obtener_gasto_mensual(entrada, salida):
    # Tipos de datos de cada columna
    d_types = {0: 'int16', 1: 'int8', 2: 'str', 3: 'str', 4: 'str', 5: 'str', 6: 'str', 7: 'str', 8: 'str', 9: 'str',
               10: 'str', 11: 'str', 12: 'str', 13: 'str', 14: 'str', 15: 'str', 16: 'str', 17: 'int64', 18: 'int64',
               19: 'str', 20: 'int64', 21: 'str', 22: 'int64', 23: 'str', 24: 'int64', 25: 'str', 26: 'str', 27: 'str',
               28: 'str', 29: 'str', 30: 'str', 31: 'str', 32: 'str', 33: 'str', 34: 'str', 35: 'str', 36: 'str',
               37: 'str', 38: 'str', 39: 'str', 40: 'str', 41: 'str', 42: 'str', 43: 'int64', 44: 'str', 45: 'int64',
               46: 'int64', 47: 'str', 48: 'int64', 49: 'str', 50: 'int64', 51: 'str', 52: 'int64', 53: 'str',
               54: 'int64', 55: 'str', 56: 'int64', 57: 'float64', 58: 'float64', 59: 'float64', 60: 'float64',
               61: 'float64', 62: 'float64'}

    resultados = {}  # Resultados acumulados, departamento y monto
    contador = 1  # Número de parte

    for chunk in pd.read_csv(entrada, dtype=d_types, chunksize=524288):  # Abrir en chunks
        gasto_por_departamento = chunk.groupby(['DEPARTAMENTO_EJECUTORA_NOMBRE', 'MES_EJE'])['MONTO_DEVENGADO'].sum()  # resultado

        for departamento, monto in gasto_por_departamento.items():  # Por cada línea en resultado
            if departamento in resultados:  # Si está en diccionario, sumar
                resultados[departamento] = resultados[departamento] + monto
            else:  # Si no, crear un valor asociado
                resultados[departamento] = monto

        print("Parte " + str(contador) + " completado.")  # Indicar al usuario el avance
        contador += 1

    departamento = []
    mes = []
    monto = []

    for element in resultados:
        if element[0] != " " and element[1] != 0:
            departamento.append(element[0])
            mes.append(element[1])
            monto.append(resultados[element])

    resultado_df = pd.DataFrame({"Departamento": departamento, "Mes": mes, "Monto": monto})

    resultado_df = resultado_df.sort_values(by=["Departamento", "Mes"])

    resultado_df.to_csv(salida, index=False)
    print("Archivo "+entrada+" convertido exitosamente a "+salida)


for i in range(2012, 2024, 1):
    obtener_gasto_mensual(str(i)+"-Gastos.csv", str(i)+"-Gasto-Mensual-Por-Region.csv")
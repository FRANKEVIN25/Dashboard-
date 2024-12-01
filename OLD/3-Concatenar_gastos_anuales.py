import pandas as pd

gasto_anual = pd.read_csv("Gasto-Anual/2012-Gasto-Total-Por-Region.csv")    # Abrir el primer archivo
gasto_anual.columns = ["Departamento", "y_2012"]                            # Apuntar al primer año, 2012

for i in range(2013, 2024, 1):                                              # Recorrer desde ahí hasta 2023
    temporal = pd.read_csv("Gasto-Anual/"+str(i)+"-Gasto-Total-Por-Region.csv")
    temporal.columns = ["Departamento", "y_"+str(i)]
    gasto_anual = pd.concat([gasto_anual, temporal["y_"+str(i)]], axis=1)   # Concatenar todos los años

gasto_anual.to_csv("Gasto-Anual-2012-2023.csv")                             # Guardar el archivo

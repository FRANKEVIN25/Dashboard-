from descargar import descargar
from obtener_gasto_total import obtener_gasto_total

descargar()

for i in range(2012, 2024, 1):
    obtener_gasto_total(str(i)+"-Gastos.csv", str(i)+"-Gasto-Total-Por-Region.csv")
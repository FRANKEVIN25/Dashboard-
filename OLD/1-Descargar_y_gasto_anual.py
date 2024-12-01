from descargar import descargar
from obtener_gasto_total import obtener_gasto_total

#descargar() # 12:18 → 14:24 = 2:06 horas

for i in range(2016, 2024, 1):
    obtener_gasto_total(str(i)+"-Gastos.csv", str(i)+"-Gasto-Total-Por-Region.csv") # 14:25 → 14:55 = 30 minutos

# Tiempo total de ejecución: 2:36 horas

# specs: 8 GB DDR4 2000MHz & HDD 7200RPM?

# ADDITIONAL FEATURES COMRADES! ↓

#-Diferencia entre monto inicial asignado y monto devengado
#-Cantidad de gastos desde 2012-2024
#-Gasto total 2012-2024
#-Peso de los datasets
#-Cantidad de gastos por región (ya está mensual, podría ser anual)
#-tipos de gastos?


"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: In this project are proposed two investment strategies to manage one million pesos,
# -- pasive and active.                                                                                  -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: lizette98                                                                                   -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/lizette98/myst_if708857_lab1                                         -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

#------------ Paso 1: Lista de archivos a leer y guardarlos en diccionario

import data as dt
import functions as fn
import plotly.express as px

#Lista de archivos a leer (DATA)
archivos = dt.archivos
#Imprimir los primeros nombres de los archivos
print(archivos[0:6])

#Leer archivos y guardarlos en diccionario
data_archivos = dt.data_archivos
#Imprimir las primeras 6 llaves del diccionario de archivos
print(list(data_archivos.keys())[0:6])

#------------- Paso 2: Vector de fechas (FUNCTIONS)
dates = fn.func_fechas(p_archivos=archivos)

#Imprimir primeras 5 t_fechas
print(dates['t_fechas'][0:4])
#Imprimir primeras 5 i_fechas
print(dates['i_fechas'][0:4])


#------------- Paso 3: Vector Tickers para yahoo finance (FUNCTIONS)
global_tickers = fn.func_tickers(p_archivos=archivos, p_data_archivos=data_archivos)

#Imprimir tickers
print(global_tickers[0:8])

#------------- Paso 4: Descargar y acomodar precios históricos (FUNCTIONS)
precios = fn.func_precios(p_global_tickers=global_tickers, p_dates=dates)
precios.head()


#------------- Paso 5:Postura inicial y evolución de la postura inversion pasiva(FUNCTIONS)
df_pasiva = fn.f_pi_pasiva(p_data_archivos=data_archivos, p_arch0=archivos[0], p_precios=precios, p_archivos=archivos, p_dates=dates)
df_pasiva.head()

fig = px.line(df_pasiva, x='timestamp', y='capital')
fig.show()

#----- Evolución de la postura inversion activa

#----- Medidas de atribucion al desempeño
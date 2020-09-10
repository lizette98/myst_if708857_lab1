
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

#Todo esto va en procesos

import data as dt
import functions as fn

#Lista de archivos a leer
archivos = dt.archivos
#Imprimir los primeros nombres de los archivos
print(archivos[0:6])

#Leer archivos y guardarlos en diccionario
data_archivos = dt.data_archivos
#Imprimir las primeras 6 llaves del diccionario de archivos
print(list(data_archivos.keys())[0:6])

#--------------Vector de fechas
dates = fn.func_fechas(p_archivos=archivos)

#Imprimir primeras 5 t_fechas
print(dates['t_fechas'][0:4])
#Imprimir primeras 5 i_fechas
print(dates['i_fechas'][0:4])


#-----Vector Tickers para yfinance
global_tickers = fn.func_tickers(p_archivos=archivos, p_data_archivos=data_archivos)

#Imprimir tickers
print(global_tickers[0:8])

#----Descargar y acomodar precios históricos

#----Postura inicial

#----- Evolución de la postura inversion pasiva

#----- Evolución de la postura inversion activa

#----- Medidas de atribucion al desempeño
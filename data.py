
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

#importar librerias
import pandas as pd
import numpy as np
import yfinance as yf
import time as time
from os import listdir, path
from os.path import isfile, join


import functions as fn

pd.set_option('display.expand_frame_rep', False)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

#Leer archivos
abspath = path.abspath('files/NAFTRAC_holdings')
#Lista de todos los archivos en la carpeta
#Comprension de listas
archivos = [f[8:-4] for f in listdir(abspath) if isfile(join(abspath, f))]
#Ordenar archivos cronologicamente
archivos = ['NAFTRAC_' + i.strftime('%d%m%y') for i in sorted(pd.to_datetime(archivos))]


#Leer archivos y guardarlos en diccionario

#Diccionario para almacenar todos los datos
data_archivos = {}

for i in archivos:
    # Los lee despues de los primeros dos renglones
    data = pd.read_csv('files/NAFTRAC_holdings/' + i + '.csv', skiprows=2, header=None)
    # Renombrar columnas
    data.columns = list(data.iloc[0, :])
    # Quitar columnas que no sean nan
    data = data.loc[:, pd.notnull(data.columns)]
    # Quitar renglon repetido y resetear índice, que empiece en 0
    data = data.iloc[1:-1].reset_index(drop=True, inplace=False)
    # Quitar comas en precios
    data['Precio'] = [i.replace(',', '') for i in data['Precio']]
    #Quitar * en tickers
    data['Ticker'] = [i.replace('*', '') for i in data['Ticker']]
    # Hacer conversiones de tipos de columnas a numerico
    convert_dict = {'Ticker': str, 'Nombre': str, 'Peso (%)': float, 'Precio': float}
    data = data.astype(convert_dict)

    # Convertir a decimal la columna de peso (%)
    data['Peso (%)'] = data['Peso (%)']/100
    # Guardar en diccionario
    data_archivos[i] = data
# -----------------------------------------------------------------------------------------------------

#Construir el vector de dates a partir del vector de nombres
#Funcion para obtener dates
dates = fn.func_fechas(p_archivos=archivos)

#------- Funcion para tickers
global_tickers = fn.func_tickers(p_archivos=archivos, p_data_archivos=data_archivos)

#-------Descargar y acomodar precios
precios = fn.func_precios(p_global_tickers=global_tickers, p_dates=dates)

#tomar solo las dates de interes
#tomar solo las columnas de interes
#transponer matriz para tener x: dates, y: precios
#multiplicar matriz de precios por matriz de pesos
#hacer suma de cada columna para obtener valor de mercado

#----- Posicion inicial
k = 1000000
c = 0.00125
param = {'k': k, 'c': c}
p_i_pasiva = fn.p_i_pasiva(p_data_archivos=data_archivos, p_arch0=archivos[0], p_precios=precios, p_param=param)


#---------------------Evolucion de la posicion (para mandarlo a todos los meses)
df_pasiva = fn.func_df_pasiva(p_dates=dates, p_archivos=archivos, p_precios=precios, p_param=param, p_i_pasiva=p_i_pasiva)
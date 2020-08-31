
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import pandas as pd
from os import listdir, path
from os.path import isfile, join
import numpy as np
import yfinance as yf
import time as time

pd.set_option('display.expand_frame_rep', False)

# Leer archivos
abspath = path.abspath('files/NAFTRAC_holdings')
#Lista de todos los archivos en la carpeta
#Comprensión de listas
archivos = [f[:-4] for f in listdir(abspath) if isfile(join(abspath, f))]

#Leer archivos y guardarlos en diccionario

#Diccionario para almacenar todos los datos
data_archivos = {}

for i in archivos:
    i = archivos[0]

    #Los lee después de los primeros dos renglones
    data = pd.read_csv('files/NAFTRAC_holdings/'+ archivos[0] + '.csv', skiprows=2, header=None)

    #Renombrar columnas
    data.columns = list(data.iloc[0, :])

    #Quitar columnas que no sean nan
    data = data.loc[:, pd.notnull(data.columns)]
    #Quitar renglon repetido y resetear índice, que empiece en 0
    data = data.iloc[1:-1].reset_index(inplace=False, drop=True)
    #Quitar comas en columna de precios
    #ERROR!!!!!
    data['Precio'] = [i.replace(',', '') for i in data['Precio']]

    data['Ticker'] = [i.replace('*', '') for i in data['Ticker']]

    #Hacer conversiones de tipos de columnas a numerico
    #ERROR!!!!!
    convert_dict = {'Ticker': str, 'Nombre': str, 'Peso (%)': float, 'Precio': float}
    data = data.astype(convert_dict)

    #Convertir a decimal la columna de peso (%)
    data['Peso (%)'] = data['Peso (%)']/100

    #Guardar en diccionario
    data_archivos[i] = data
# -----------------------------------------------------------------------------------------------------

# Construir el vector de fechas a partir del vector de nombres
#Etiquetas en dataframe y para yfinance
t_fechas = [i.strftime('%d-%m-%Y') for i in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]

# lista con fechas ordenadas (para usarse como  indexadores de archivos)
i_fechas = [j.strftime('%d%m%y') for j in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]

# Descargar y acomodar datos
tickers = []
for i in archivos:
    # i = archivos[11]
    l_tickers = list(data_archivos[i]['Ticker'])
    print(l_tickers)
    [tickers.append(i + '.MX') for i in l_tickers]
global_tickers = np.unique(tickers).tolist()

# Obtener posiciones históricas
#global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers]
#global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers]
global_tickers = [i.replace('LIVERPOLC.1.MX', 'LIVERPOLC-1.MX') for i in global_tickers]

# eliminar MXN, USD, KOFL
[global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX']]

#Nota: Cuando se utiliza KOF, ese % o ponderación la pasamos CASH

inicio = time.time()
data = yf.download(global_tickers, start="2017-08-21", end="2020-08-21", actions=False, group_by="close", interval='1d',
                   auto_adjust=True, prepost=False, threads=False)
print('se tardo', time.time() - inicio, 'segundos')

#tomar solo las fechas de interes
#tomar solo las columnas de interes
#transponer matriz para tener x: fechas, y: precios
#multiplicar matriz de precios por matriz de pesos
#hacer suma de cada columna para obtener valor de mercado

#posicion inicial

#capital inicial

k = 1000000

#comisiones por transaccion
c = 0.00125

data_archivos[archivos[0]]['Ticker']

data_archivos[archivos[0]]['Peso (%)'] * (k//data_archivos[archivos[0]]['Peso (%)'])



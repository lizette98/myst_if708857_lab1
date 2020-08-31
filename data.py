
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
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

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
    data = pd.read_csv('files/NAFTRAC_holdings/'+ i + '.csv', skiprows=2, header=None)
    #Renombrar columnas
    data.columns = list(data.iloc[0, :])
    #Quitar columnas que no sean nan
    data = data.loc[:, pd.notnull(data.columns)]
    #Quitar renglon repetido y resetear índice, que empiece en 0
    data = data.iloc[1:-1].reset_index(drop=True, inplace=False)
    #Quitar comas en columna de precios
    data['Precio'] = [i.replace(',', '') for i in data['Precio']]

    data['Ticker'] = [i.replace('*', '') for i in data['Ticker']]

    #Hacer conversiones de tipos de columnas a numerico
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
    # i = archivos[0]
    l_tickers = list(data_archivos[i]['Ticker'])
    #print(l_tickers)
    [tickers.append(i + '.MX') for i in l_tickers]
global_tickers = np.unique(tickers).tolist()

# Obtener posiciones históricas
#global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers]
#global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers]
global_tickers = [i.replace('LIVERPOLC.1.MX', 'LIVERPOLC-1.MX') for i in global_tickers]

# eliminar MXN, USD, KOFL
[global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX', 'KOFUBL.MX', 'BSMXB.MX']]

#Nota: Cuando se utiliza KOF, ese % o ponderación la pasamos CASH
#Contar tiempo que tarda
inicio = time.time()
#Descarga de precios de yfinance
data = yf.download(global_tickers, start="2017-08-21", end="2020-08-21", actions=False, group_by="close", interval='1d',
                   auto_adjust=True, prepost=False, threads=False)
print('se tardo', time.time() - inicio, 'segundos')

#Convertir columna de fechas
data_close = pd.DataFrame({i: data[i]['Close'] for i in global_tickers})

#Tomar solo fechas de interes (Teoría de conjuntos)
ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(i_fechas)))

#Localizar todos los precios
precios = data_close.iloc[[int(np.where(data_close.index.astype(str) == i)[0]) for i in ic_fechas]]

#Ordenar columnas lexicográficamente
precios = precios.reindex(sorted(precios.columns), axis=1)


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

#Vector de comisiones históricas
comisiones = []

#Obtener posición inicial (los % de KOFL, KOFUBL, BSMXB, USD asignarlos a CASH (eliminados))
c_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'MXN', 'USD']
#Diccionario para resultado final
inv_pasiva = {'timestamp': ['05-01-2018'], 'capital': [k]}

#Falta revisar que el archivo sea del 1er mes
pos_datos = data_archivos[archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Nombre', 'Peso (%)']]

#Extraer la lista de activos a eliminar
i_activos = list(pos_datos[list(pos_datos['Ticker'].isin(c_activos))].index)

#Eliminar los activos del dataframe
pos_datos.drop(i_activos, inplace = True)

#Resetear el index
pos_datos.reset_index(inplace=True, drop = True)

#Agregar .MX para empatar precios
pos_datos['Ticker'] = pos_datos['Ticker'] + '.MX'

#Corregir tickers en datos
pos_datos['Ticker'] = pos_datos['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')
pos_datos['Ticker'] = pos_datos['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
pos_datos['Ticker'] = pos_datos['Ticker'].replace('GFREGIOO.MX', 'RA.X')

#Precios necesarios para la posición
pos_datos['Precio'] = np.array(precios.iloc[0, [i in pos_datos['Ticker'].to_list() for i in
                                                precios.columns.to_list()]])

#Capital destinado por acción = proporción del capital - comisiones por la posición
pos_datos['Capital'] = pos_datos['Peso (%)']*k - pos_datos['Peso (%)']*k*c

#pos_datos['Titulos']

#pos_datos['Titulos']

#pos_datos['Postura']

#pos_datos['Comisión']

#pos_value

#pos_comission




data_archivos[archivos[0]]['Ticker']

data_archivos[archivos[0]]['Peso (%)'] * (k//data_archivos[archivos[0]]['Peso (%)'])




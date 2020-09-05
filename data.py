
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
    #i = archivos[0]
    # Los lee despues de los primeros dos renglones
    data = pd.read_csv('files/NAFTRAC_holdings/' + i + '.csv', skiprows=2, header=None)
    # Renombrar columnas
    data.columns = list(data.iloc[0, :])
    # Quitar columnas que no sean nan
    data = data.loc[:, pd.notnull(data.columns)]
    # Quitar renglon repetido y resetear índice, que empiece en 0
    data = data.iloc[1:-1].reset_index(drop=True, inplace=False)
    # Quitar comas en columna de precios
    data['Precio'] = [i.replace(',', '') for i in data['Precio']]

    data['Ticker'] = [i.replace('*', '') for i in data['Ticker']]
    # Hacer conversiones de tipos de columnas a numerico
    convert_dict = {'Ticker': str, 'Nombre': str, 'Peso (%)': float, 'Precio': float}
    data = data.astype(convert_dict)

    # Convertir a decimal la columna de peso (%)
    data['Peso (%)'] = data['Peso (%)']/100
    # Guardar en diccionario
    data_archivos[i] = data
# -----------------------------------------------------------------------------------------------------

# Construir el vector de fechas a partir del vector de nombres
#Etiquetas en dataframe y para yfinance
t_fechas = [i.strftime('%d-%m-%Y') for i in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]

# lista con fechas ordenadas (para usarse como  indexadores de archivos)
i_fechas = [j.strftime('%Y-%m-%d') for j in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]

# Descargar y acomodar datos
tickers = []
for i in archivos:
    # i = archivos[1]
    l_tickers = list(data_archivos[i]['Ticker'])
    [tickers.append(i + '.MX') for i in l_tickers]
global_tickers = np.unique(tickers).tolist()

# Obtener posiciones historicas
global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers]
global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers]
global_tickers = [i.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX') for i in global_tickers]

# eliminar MXN, USD, KOFL
[global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX', 'KOFUBL.MX', 'BSMXB.MX']]

#Nota: Cuando se utiliza KOF, ese % o ponderacion la pasamos CASH
#Contar tiempo que tarda
inicio = time.time()
#Descarga de precios de yfinance
data = yf.download(global_tickers, start="2018-01-30", end="2020-08-24", actions=False, group_by="close", interval='1d',
                   auto_adjust=False, prepost=False, threads=False)
print('se tardo', time.time() - inicio, 'segundos')

#Convertir columna de fechas
data_close = pd.DataFrame({i: data[i]['Close'] for i in global_tickers})

#Tomar solo fechas de interes (Teoria de conjuntos)
ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(i_fechas)))

#Localizar todos los precios
precios = data_close.iloc[[int(np.where(data_close.index.astype(str) == i)[0]) for i in ic_fechas]]

#Ordenar columnas lexicograficamente
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

#Vector de comisiones historicas
comisiones = []

#Obtener posicion inicial (los % de KOFL, KOFUBL, BSMXB, USD asignarlos a CASH (eliminados))
c_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'MXN', 'USD']
#Diccionario para resultado final
inv_pasiva = {'timestamp': ['30-01-2018'], 'capital': [k]}

pos_datos = data_archivos[archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Nombre', 'Peso (%)']]

#Extraer la lista de activos a eliminar
i_activos = list(pos_datos[pos_datos['Ticker'].isin(c_activos)].index)

#Eliminar los activos del dataframe
pos_datos.drop(i_activos, inplace=True)

#Resetear el index
pos_datos.reset_index(inplace=True, drop=True)

#Agregar .MX para empatar precios
pos_datos['Ticker'] = pos_datos['Ticker'] + '.MX'

#Corregir tickers en datos
pos_datos['Ticker'] = pos_datos['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')
pos_datos['Ticker'] = pos_datos['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
pos_datos['Ticker'] = pos_datos['Ticker'].replace('GFREGIOO.MX', 'RA.MX')

#------- Match de precios
#Fecha en la que se busca hacer el match de precios
match = 7
precios.index.to_list()[match]

#Precios necesarios para la posicion
#m1 = np.array(precios.iloc[match, [i in pos_datos['Ticker'].to_list() for i in precios.columns.to_list()]])
m2 = [precios.iloc[match, precios.columns.to_list().index(i)] for i in pos_datos['Ticker']]

#pos_datos['Precio_m1'] = m1
pos_datos['Precio'] = m2

#Capital destinado por acción = proporcion del capital - comisiones por la postura
pos_datos['Capital'] = pos_datos['Peso (%)']*k - pos_datos['Peso (%)']*k*c

#Cantidad de títulos por accion
pos_datos['Titulos'] = pos_datos['Capital']//pos_datos['Precio']

#Multiplicar los títulos de cada activo por el precio que tienes en ese mes
pos_datos['Postura'] = pos_datos['Titulos']*pos_datos['Precio']

#Calcular la comisión que pagas por ejecutar la postura
pos_datos['Comision'] = pos_datos['Postura']*c
pos_comision = pos_datos['Comision'].sum()

#Efectivo libre en la postura
#Capital - postura - comisión
pos_cash = k - pos_datos['Postura'].sum() - pos_comision

#la suma de las posturas (las de cada activo)
pos_value = pos_datos['Postura'].sum()

#Guardar en una lista el capital (valor de la postura total (suma de las posturas + cash))
inv_pasiva['timestamp'].append(t_fechas[0])
inv_pasiva['capital'].append(pos_value + pos_cash)

#---------------------Evolucion de la posicion (Inversion pasiva) (para mandarlo a todos los meses)
for arch in range(1, len(archivos)):
    #Actualizar la columna de precio en el mismo dataframe
    pos_datos['Precio'] = np.array(precios.iloc[arch, [i in pos_datos['Ticker'].to_list() for i in
                                                       precios.columns.to_list()]])

    #Valor de la postura por accion
    pos_datos['Postura'] = pos_datos['Titulos']*pos_datos['Precio']

    #Valor de la postura
    pos_value = pos_datos['Postura'].sum()

    #Actualizar lista de valores de cada llave en el diccionario
    inv_pasiva['timestamp'].append(t_fechas[arch])


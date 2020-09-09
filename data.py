
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
from os import listdir, path
from os.path import isfile, join
import numpy as np
import yfinance as yf
import time as time
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

#Construir el vector de fechas a partir del vector de nombres
#Funcion para obtener fechas
fechas = fn.func_fechas(p_archivos=archivos)

# Descargar y acomodar datos
tickers = []
for i in archivos:
    l_tickers = list(data_archivos[i]['Ticker'])
    [tickers.append(i + '.MX') for i in l_tickers]
global_tickers = np.unique(tickers).tolist()

# Obtener posiciones historicas
#Reemplazar tickers que han cambiado o son diferentes en yfinance
global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers]
global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers]
global_tickers = [i.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX') for i in global_tickers]

#Eliminar MXN, USD, KOFL
[global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX', 'KOFUBL.MX', 'BSMXB.MX']]

#Nota: Cuando se utiliza KOF, ese % o ponderacion la pasamos CASH
#Contar tiempo que tarda
inicio = time.time()
#Descarga de precios de yfinance
data = yf.download(global_tickers, start="2018-01-30", end="2020-08-24", actions=False, group_by="close", interval='1d',
                   auto_adjust=False, prepost=False, threads=True)
print('se tardo', round(time.time()-inicio, 2), 'segundos')

#Convertir columna de fechas
data_close = pd.DataFrame({i: data[i]['Close'] for i in global_tickers})

#Fechas de interes (Teoria de conjuntos)
ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(fechas['i_fechas'])))

#Localizar todos los precios
precios = data_close.iloc[[int(np.where(data_close.index == i)[0]) for i in ic_fechas]]

#Ordenar columnas lexicograficamente
precios = precios.reindex(sorted(precios.columns), axis=1)

#tomar solo las fechas de interes
#tomar solo las columnas de interes
#transponer matriz para tener x: fechas, y: precios
#multiplicar matriz de precios por matriz de pesos
#hacer suma de cada columna para obtener valor de mercado

#-----Posicion inicial
#capital inicial
k = 1000000

#comisiones por transaccion
c = 0.00125

#Vector de comisiones historicas
comisiones = []

#Obtener posicion inicial (los % de KOFL, KOFUBL, BSMXB, USD y MXN asignarlos a CASH (eliminados))
c_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'MXN', 'USD']
#Diccionario para resultado final
df_pasiva = {'timestamp': ['30-01-2018'], 'capital': [k]}

pos_datos = data_archivos[archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Nombre', 'Peso (%)']]

#Extraer la lista de activos a eliminar
del_activos = list(pos_datos[pos_datos['Ticker'].isin(c_activos)].index)

#Eliminar los activos del dataframe
pos_datos.drop(del_activos, inplace=True)

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

#pos_datos['Precio'] = m1
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
df_pasiva['timestamp'].append(fechas['t_fechas'][0])
df_pasiva['capital'].append(pos_value + pos_cash)

#---------------------Evolucion de la posicion (para mandarlo a todos los meses)
for arch in range(1, len(archivos)):
    #Actualizar la columna de precio en el mismo dataframe
    precios.index.to_list()[arch]

    # Precios necesarios para la posicion
    m2 = [precios.iloc[arch, precios.columns.to_list().index(i)] for i in pos_datos['Ticker']]
    pos_datos['Precio'] = m2

    #Valor de la postura por accion
    pos_datos['Postura'] = pos_datos['Titulos']*pos_datos['Precio']

    #Valor de la postura
    pos_value = pos_datos['Postura'].sum()

    #Actualizar lista de valores de cada llave en el diccionario
    df_pasiva['timestamp'].append(fechas['t_fechas'][arch])
    df_pasiva['capital'].append(pos_value + pos_cash)

#Dataframe final
df_pasiva = pd.DataFrame(df_pasiva)
#Rendimiento por mes
df_pasiva['rend'] = [0] + list(np.log(df_pasiva['capital']) - np.log(df_pasiva['capital'].shift(1)))[1:]
#Redondeos
df_pasiva['rend'] = round(df_pasiva['rend'], 4)
df_pasiva['capital'] = round(df_pasiva['capital'], 2)
#Rendimiento acumulado
df_pasiva['rend_acum'] = round(df_pasiva['rend'].cumsum(), 4)

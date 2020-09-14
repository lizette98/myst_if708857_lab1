
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: In this project are proposed two investment strategies to manage one million pesos,
# -- pasive and active.                                                                                  -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: lizette98                                                                                   -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/lizette98/myst_if708857_lab1                                         -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# Importar librerias
import pandas as pd
from os import listdir, path
from os.path import isfile, join

pd.set_option('display.expand_frame_rep', False)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Leer archivos
abspath = path.abspath('files/NAFTRAC_holdings')
# Lista de todos los archivos en la carpeta
# Comprension de listas
archivos = [f[8:-4] for f in listdir(abspath) if isfile(join(abspath, f))]
#Ordenar archivos cronologicamente
archivos = ['NAFTRAC_' + i.strftime('%d%m%y') for i in sorted(pd.to_datetime(archivos))]


# Leer archivos y guardarlos en diccionario

# Diccionario para almacenar todos los datos
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


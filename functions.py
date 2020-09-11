
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import pandas as pd
import numpy as np
import yfinance as yf
import time as time

def func_fechas(p_archivos):
    # Construir el vector de dates a partir del vector de nombres
    # Etiquetas en dataframe y para yfinance
    t_fechas = [i.strftime('%d-%m-%Y') for i in sorted([pd.to_datetime(i[8:]).date() for i in p_archivos])]

    # lista con dates ordenadas (para usarse como  indexadores de archivos)
    i_fechas = [j.strftime('%Y-%m-%d') for j in sorted([pd.to_datetime(i[8:]).date() for i in p_archivos])]

    #Retrun:
    func_fechas_r = {'i_fechas': i_fechas, 't_fechas': t_fechas}

    return func_fechas_r

#--------- Tickers para yfinance
def func_tickers(p_archivos, p_data_archivos):
    tickers = []
    for i in p_archivos:
        l_tickers = list(p_data_archivos[i]['Ticker'])
        [tickers.append(i + '.MX') for i in l_tickers]
    global_tickers = np.unique(tickers).tolist()

    # Obtener posiciones historicas
    # Reemplazar tickers que han cambiado o son diferentes en yfinance
    global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers]
    global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers]
    global_tickers = [i.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX') for i in global_tickers]

    # Eliminar MXN, USD, KOFL
    [global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX', 'KOFUBL.MX', 'BSMXB.MX']]

    return global_tickers

#-------- Descarga de precios de yfinance
def func_precios(p_global_tickers, p_dates):
    # Descargar y acomodar datos
    # Nota: Cuando se utiliza KOF, ese % o ponderacion la pasamos CASH
    # Contar tiempo que tarda
    inicio = time.time()
    # Descarga de precios de yfinance
    data = yf.download(p_global_tickers, start="2018-01-30", end="2020-08-24", actions=False, group_by="close",
                       interval='1d',
                       auto_adjust=False, prepost=False, threads=True)
    print('se tardo', round(time.time() - inicio, 2), 'segundos')

    # Convertir columna de dates
    data_close = pd.DataFrame({i: data[i]['Close'] for i in p_global_tickers})

    # Fechas de interes (Teoria de conjuntos)
    ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(p_dates['i_fechas'])))

    # Localizar todos los precios
    precios = data_close.iloc[[int(np.where(data_close.index == i)[0]) for i in ic_fechas]]

    # Ordenar columnas lexicograficamente
    precios = precios.reindex(sorted(precios.columns), axis=1)

    return precios

#------ Posicion inicial inversion pasiva
def p_i_pasiva(p_data_archivos, p_arch0, p_precios, p_param):
    # capital inicial
    k = 1000000
    # comisiones por transaccion
    c = 0.00125
    #Parametros
    p_param = {'capital': k, 'comision': c}
    # Vector de comisiones historicas
    comisiones = []

    # Obtener posicion inicial (los % de KOFL, KOFUBL, BSMXB, USD y MXN asignarlos a CASH (eliminados))
    c_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'MXN', 'USD']
    # Diccionario para resultado final
    df_pasiva = {'timestamp': ['30-01-2018'], 'capital': [k]}

    pos_datos = p_data_archivos[p_arch0].copy().sort_values('Ticker')[['Ticker', 'Nombre', 'Peso (%)']]

    # Extraer la lista de activos a eliminar
    del_activos = list(pos_datos[pos_datos['Ticker'].isin(c_activos)].index)

    # Eliminar los activos del dataframe
    pos_datos.drop(del_activos, inplace=True)

    # Resetear el index
    pos_datos.reset_index(inplace=True, drop=True)

    # Agregar .MX para empatar precios
    pos_datos['Ticker'] = pos_datos['Ticker'] + '.MX'

    # Corregir tickers en datos
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('GFREGIOO.MX', 'RA.MX')

    # ------- Match de precios
    # Fecha en la que se busca hacer el match de precios
    match = 7
    p_precios.index.to_list()[match]

    # Precios necesarios para la posicion
    # m1 = np.array(precios.iloc[match, [i in pos_datos['Ticker'].to_list() for i in precios.columns.to_list()]])
    m2 = [p_precios.iloc[match, p_precios.columns.to_list().index(i)] for i in pos_datos['Ticker']]

    # pos_datos['Precio_m1'] = m1
    pos_datos['Precio'] = m2

    # Capital destinado por acción = proporcion del capital - comisiones por la postura
    pos_datos['Capital'] = pos_datos['Peso (%)'] * k - pos_datos['Peso (%)'] * k * c

    # Cantidad de títulos por accion
    pos_datos['Titulos'] = pos_datos['Capital'] // pos_datos['Precio']

    # Multiplicar los títulos de cada activo por el precio que tienes en ese mes
    pos_datos['Postura'] = pos_datos['Titulos'] * pos_datos['Precio']

    # Calcular la comisión que pagas por ejecutar la postura
    pos_datos['Comision'] = pos_datos['Postura'] * c
    pos_comision = pos_datos['Comision'].sum()

    # la suma de las posturas (las de cada activo)
    pos_value = pos_datos['Postura'].sum()

    # Efectivo libre en la postura
    # Capital - postura - comisión
    pos_cash = k - pos_value - pos_comision

    return p_i_pasiva

#-------- Funcion para Dataframe Inversion pasiva
def func_df_pasiva(p_dates, p_archivos, p_precios, p_param, p_i_pasiva):

    df_pasiva = {'timestamp': ['30-01-2018'], 'capital': [p_param['k']]}
    # Guardar en una lista el capital (valor de la postura total (suma de las posturas + cash))
    df_pasiva['timestamp'].append(p_dates['t_fechas'][0])
    df_pasiva['capital'].append(p_i_pasiva['pos_value'] + p_i_pasiva['pos_cash'])

    # ---------------------Evolucion de la posicion (para mandarlo a todos los meses)
    for month in range(1, len(p_archivos)):
        # Actualizar la columna de precio en el mismo dataframe
        m2 = [p_precios.iloc[month, p_precios.columns.to_list().index(i)] for i in p_i_pasiva['pos_datos']['Ticker']]
        p_i_pasiva['pos_datos']['Precio'] = m2

        # Valor de la postura por accion
        p_i_pasiva['pos_datos']['Postura'] = p_i_pasiva['pos_datos']['Titulos'] * p_i_pasiva['pos_datos']['Precio']

        # Valor de la postura
        pos_value = p_i_pasiva['pos_datos']['Postura'].sum()

        # Actualizar lista de valores de cada llave en el diccionario
        df_pasiva['timestamp'].append(p_dates['t_fechas'][month])
        df_pasiva['capital'].append(pos_value + p_i_pasiva['pos_cash'])

    # Dataframe final
    df_pasiva = pd.DataFrame(df_pasiva)
    # Rendimiento por mes
    df_pasiva['rend'] = [0] + list((df_pasiva['capital'] / df_pasiva['capital'].shift(1)) - 1)[1:]
    # Redondeos
    df_pasiva['rend'] = round(df_pasiva['rend'], 4)
    df_pasiva['capital'] = round(df_pasiva['capital'], 2)
    # Rendimiento acumulado
    df_pasiva['rend_acum'] = round(df_pasiva['rend'].cumsum(), 4)

    return df_pasiva
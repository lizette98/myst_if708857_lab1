
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: In this project are proposed two investment strategies to manage one million pesos,
# -- pasive and active.                                                                                  -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: lizette98                                                                                   -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/lizette98/myst_if708857_lab1                                         -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import pandas as pd
import numpy as np
import yfinance as yf
import time as time


def func_fechas(p_archivos):
    """
    Funcion para construir el vector de fechas,
    para descarga de precios en yfinance y otra como indezadora de archivos.

    Parameters
    ----------
    p_archivos: list
            Lista con los nombres de los archivos a leer.

    Returns
    -------
    func_fechas_r: dict
            Diccionario con las fechas en los 2 formatos.
            {'t_fechas': t_fechas, 'i_fechas': i_fechas}
    """
    # Construir el vector de dates a partir del vector de nombres
    # Etiquetas en dataframe y para yfinance
    t_fechas = [i.strftime('%d-%m-%Y') for i in sorted([pd.to_datetime(i[8:]).date() for i in p_archivos])]

    # lista con dates ordenadas (para usarse como  indexadores de archivos)
    i_fechas = [j.strftime('%Y-%m-%d') for j in sorted([pd.to_datetime(i[8:]).date() for i in p_archivos])]

    #Retrun:
    func_fechas_r = {'i_fechas': i_fechas, 't_fechas': t_fechas}

    return func_fechas_r

# --------- Tickers para yfinance


def func_tickers(p_archivos, p_data_archivos):
    """
    Funcion para construir el vector de ticker,
    para descarga de precios en yfinance.

    Parameters
    ----------
    p_archivos: list
            Lista con los nombres de los archivos a leer.

    p_data_archivos:dict
            Diccionario con los archivos a leer.
    Returns
    -------
    global_tickers: list
            Lista con todos los tickers a utilizar.
        """
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

# -------- Descarga de precios de yfinance


def func_precios(p_global_tickers, p_dates):
    """
    Funcion para decargar y acomodar los precios desde yfinance.

    :param
    p_global_tickers: list
                Lista con todos los tickers a utilizar.
    :param
    p_dates: dict
                Diccionario con las fechas en los 2 formatos.
               {'t_fechas': t_fechas, 'i_fechas': i_fechas}
    :return:
    precios: DataFrame
                Dataframe con todos los precios necesarios.
    """
    # Descargar y acomodar datos
    # Contar tiempo que tarda
    inicio = time.time()
    # Descarga de precios de yfinance
    data = yf.download(p_global_tickers, start="2018-01-30", end="2020-08-24", actions=False, group_by="close",
                       interval='1d',
                       auto_adjust=False, prepost=False, threads=True)
    print('tardo', round(time.time() - inicio, 2), 'segundos')

    # Convertir columna de dates
    data_close = pd.DataFrame({i: data[i]['Close'] for i in p_global_tickers})

    # Fechas de interes (Teoria de conjuntos)
    ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(p_dates['i_fechas'])))

    # Localizar todos los precios
    precios = data_close.iloc[[int(np.where(data_close.index == i)[0]) for i in ic_fechas]]

    # Ordenar columnas lexicograficamente
    precios = precios.reindex(sorted(precios.columns), axis=1)

    return precios

# ------- Funcion para posicion inicial en Inversion Pasiva


def f_pi_pasiva(p_data_archivos, p_arch0, p_precios, p_archivos, p_dates):
    """
    Funcion para la creacion y evolucion de la posicion inicial en Inversion pasiva.

    :param
    p_data_archivos: dict
                Diccionario con los archivos a leer.

    :param p_arch0: value on list
                Primer archivo a leer en la lista de archivos.

    :param p_precios: DataFrame
                Dataframe con todos los precios necesarios.

    :param p_archivos: list
                Lista con los nombres de los archivos a leer.
    :param p_dates: dict
                Diccionario con las fechas en los 2 formatos.
               {'t_fechas': t_fechas, 'i_fechas': i_fechas}
    :return:
    df_pasiva: DataFrame
                DataFrame con la evolucion de la posicion en inversion pasiva.
    """
    # -----Posicion inicial
    # capital inicial
    k = 1000000

    # comisiones por transaccion
    c = 0.00125

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
    match = 0
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

#------Datraframe final de Inversion Pasiva
    for month in range(0, len(p_archivos)):
        # Actualizar la columna de precio en el mismo dataframe
        p_precios.index.to_list()[month]
        m2 = [p_precios.iloc[match, p_precios.columns.to_list().index(i)] for i in pos_datos['Ticker']]
        pos_datos['Precio'] = m2

        # Valor de la postura por accion
        pos_datos['Postura'] = pos_datos['Titulos'] * pos_datos['Precio']

        # Valor de la postura
        pos_value = pos_datos['Postura'].sum()

        # Actualizar lista de valores de cada llave en el diccionario
        df_pasiva['timestamp'].append(p_dates['t_fechas'][month])
        df_pasiva['capital'].append(pos_value + pos_cash)

        match = match + 1

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

# ------Inversion Activa


def func_inv_activa(p_data_archivos, p_arch0, p_precios, p_global_tickers, p_dates):
    """
    Funcion para crear la estrategia de inversión activa.

    :param
    p_data_archivos: dict
                Diccionario con los archivos a leer.

    :param p_arch0: value on list
                Primer archivo a leer en la lista de archivos.

    :param p_precios: DataFrame
                Dataframe con todos los precios necesarios.

    :param p_global_tickers: list
                Lista con todos los tickers a utilizar.

    :param p_archivos: list
                Lista con los nombres de los archivos a leer.
    :param p_dates: dict
                Diccionario con las fechas en los 2 formatos.
               {'t_fechas': t_fechas, 'i_fechas': i_fechas}
    :return:
    df_activa: DataFrame
                DataFrame con la evolucion de la posicion en inversion activa.
    """
    # capital inicial
    k = 1000000

    # comisiones por transaccion
    c = 0.00125

    # Vector de comisiones historicas
    comisiones = []

    # Diccionario para resultado final
    df_activa = {'timestamp': ['30-01-2018'], 'capital': [k]}

    df_activa = p_data_archivos[p_arch0].copy().sort_values('Peso (%)', ascending=False)[
        ['Ticker', 'Nombre', 'Peso (%)']]
    # Extraer la lista de activos a eliminar
    c_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'MXN', 'USD']
    del_activos = list(df_activa[df_activa['Ticker'].isin(c_activos)].index)

    # Eliminar los activos del dataframe
    df_activa.drop(del_activos, inplace=True)

    # Resetear el index
    df_activa.reset_index(inplace=True, drop=True)

    # Agregar .MX para empatar precios
    df_activa['Ticker'] = df_activa['Ticker'] + '.MX'

    # Corregir tickers en datos
    df_activa['Ticker'] = df_activa['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')
    df_activa['Ticker'] = df_activa['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
    df_activa['Ticker'] = df_activa['Ticker'].replace('GFREGIOO.MX', 'RA.MX')

    # Se asigna la mitad del capital al activo con mas peso (AMXL)
    df_activa['Peso (%)'][0] = df_activa['Peso (%)'][0] / 2

    # ------- Match de precios
    # Fecha en la que se busca hacer el match de precios
    match = 0
    p_precios.index.to_list()[match]

    # Precios necesarios para la posicion
    m2 = [p_precios.iloc[match, p_precios.columns.to_list().index(i)] for i in df_activa['Ticker']]

    df_activa['Precio'] = m2

    # Capital destinado por acción = proporcion del capital - comisiones por la postura
    df_activa['Capital'] = df_activa['Peso (%)'] * k - df_activa['Peso (%)'] * k * c

    # Cantidad de títulos por accion
    df_activa['Titulos'] = df_activa['Capital'] // df_activa['Precio']

    # Multiplicar los títulos de cada activo por el precio que tienes en ese mes
    df_activa['Postura'] = df_activa['Titulos'] * df_activa['Precio']

    # Calcular la comisión que pagas por ejecutar la postura
    df_activa['Comision'] = df_activa['Postura'] * c
    comision = df_activa['Comision'].sum()

    # la suma de las posturas (las de cada activo)
    pos_value_act = df_activa['Postura'].sum()

    # Efectivo libre en la postura
    # Capital - postura - comisión
    pos_cash_act = k - pos_value_act - comision

    # Precios para activo con mayor ponderacion
    inicio = time.time()
    # Descarga de precios de yfinance
    data_act = yf.download(p_global_tickers, start="2018-01-30", end="2020-08-24", actions=False, group_by="close",
                           interval='1d',
                           auto_adjust=False, prepost=False, threads=True)
    print('tardo', round(time.time() - inicio, 2), 'segundos')

    # Precios en Open y Close para las ordenes de compra
    AMXL = data_act['AMXL.MX'][['Open', 'Close']]

    # Convertir columna de dates
    data_close = pd.DataFrame({i: data_act[i]['Close'] for i in p_global_tickers})
    data_open = pd.DataFrame({i: data_act[i]['Open'] for i in p_global_tickers})

    # Fechas de interes (Teoria de conjuntos)
    ic_fechas_act = sorted(list(set(data_close.index.astype(str).tolist()) & set(p_dates['i_fechas'])))

    # Localizar todos los precios
    AMXL = AMXL.iloc[[int(np.where(data_close.index == i)[0]) for i in ic_fechas_act]]

    # -------------Rebalanceo
    # (el porcentaje de capital que destinas a la operacion, y este capital es el que está libre como CASH al momento de detectar una compra)
    kc = 0.10
    # (cuando el precio baje xp% o mas, el precio de apertura es igual o mayor que el precio de cierre en xp% o mas)
    xp = -0.01

    # Diccionario para Historico de operaciones
    operaciones = [{'timestamp': ['30-01-2018'], 'titulos_totales': df_activa['Titulos'][0],
                    'titulos_compra': df_activa['Titulos'][0],
                    'precio': df_activa['Precio'][0], 'comision': df_activa['Comision'][0],
                    'comision_acum': df_activa['Comision'][0]}]

    return df_activa
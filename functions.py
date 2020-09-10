
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

def func_fechas(p_archivos):
    # Construir el vector de dates a partir del vector de nombres
    # Etiquetas en dataframe y para yfinance
    t_fechas = [i.strftime('%d-%m-%Y') for i in sorted([pd.to_datetime(i[8:]).date() for i in p_archivos])]

    # lista con dates ordenadas (para usarse como  indexadores de archivos)
    i_fechas = [j.strftime('%Y-%m-%d') for j in sorted([pd.to_datetime(i[8:]).date() for i in p_archivos])]

    #Retrun:
    func_fechas_r = {'i_fechas': i_fechas, 't_fechas': t_fechas}

    return func_fechas_r

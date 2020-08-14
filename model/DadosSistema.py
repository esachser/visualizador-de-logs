# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import datetime

dataHoraVarNome = 'datetime'
sentidoATR = 1
sentidoASG = 2

class DataError(Exception):
    pass

class DadoSistema():

    def __init__(self, df):
        super(DadoSistema,self).__init__()

        self.__df__ = df
        global dataHoraVarNome
        dataH = None

        for column in self.__df__:
            if isinstance(self.__df__[column][0], str):
                try:
                    self.__df__[column] = pd.to_datetime(self.__df__[column])
                    dataH = column if dataH is None else dataH
                    self.__df__[column + "_dia"] = self.__df__[column].dt.day
                    self.__df__[column + "_mes"] = self.__df__[column].dt.month
                    self.__df__[column + "_ano"] = self.__df__[column].dt.year
                    self.__df__[column + "_hora"] = self.__df__[column].dt.hour
                    self.__df__[column + "_minuto"] = self.__df__[column].dt.minute
                    self.__df__[column + "_segundo"] = self.__df__[column].dt.second
                except Exception as e:
                    print(e)
                    self.__df__.drop([column], axis=1, inplace=True)

    def getHeader(self):
        return sorted(self.__df__.axes[1])

    @staticmethod
    def fromDataFrame(df):
        return DadoSistema(df)

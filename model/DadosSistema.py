# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import datetime

dataHoraVarNome = 'DataHora_PLC'
sentidoATR = 1
sentidoASG = 2

class DataError(Exception):
    pass

class DadoSistema():

    def __init__(self, df, findTravels=True):
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

        if findTravels:
            if hasattr(self.__df__, dataHoraVarNome):
                self.__df__.sort_values(by=dataHoraVarNome, inplace=True)
            elif dataH is not None:
                self.__df__.sort_values(by=dataH, inplace=True)
                dataHoraVarNome = dataH

            self.__datas__ = set()
            self.__fromATRij__ = dict()
            self.__fromASGij__ = dict()


            if hasattr(self.__df__, dataHoraVarNome):
                self.__separaDatas__()

            # Separa as viagens. Terá que descobrir se é A100 e A200
            if hasattr(self.__df__, 'A100_Sentido') and hasattr(self.__df__, 'A100_ATO') and hasattr(self.__df__, dataHoraVarNome) and hasattr(self.__df__, 'A100_Posicao'):
                diffSentidoA100 = self.__df__.A100_Sentido.diff(1)
                diffATOA100 = self.__df__.A100_ATO.diff(-1)
                self.__fromATRij__ = \
                    dict(self.__separaViagens__(diffATOA100, diffSentidoA100, self.__df__.A100_Sentido, -1, -sentidoATR, 'A100_Posicao', 864.5, 52.5, 1.5))
                self.__fromASGij__ = \
                    dict(self.__separaViagens__(diffATOA100, diffSentidoA100, self.__df__.A100_Sentido, -1, -sentidoASG, 'A100_Posicao', 52.5, 864.5, 1.5))


            if hasattr(self.__df__, 'A200_Sentido') and hasattr(self.__df__, 'A200_ATO') and hasattr(self.__df__, dataHoraVarNome) and hasattr(self.__df__, 'A200_Posicao'):
                diffSentidoA200 = self.__df__.A200_Sentido.diff(1)
                diffATOA200 = self.__df__.A200_ATO.diff(-1)
                self.__A200fromATRij__ = \
                    dict(self.__separaViagens__(diffATOA200, diffSentidoA200, self.__df__.A200_Sentido, -1, -sentidoATR, 'A200_Posicao', 864.5, 52.5, 1.5))
                self.__A200fromASGij__ = \
                    dict(self.__separaViagens__(diffATOA200, diffSentidoA200, self.__df__.A200_Sentido, -1, -sentidoASG, 'A200_Posicao', 52.5, 864.5, 1.5))

                for key, val in self.__A200fromASGij__.items():
                    self.__fromASGij__[key] = val

                for key, val in self.__A200fromATRij__.items():
                    self.__fromATRij__[key] = val



    def __separaDatas__(self):
        # separa as datas
        for data in self.__df__[dataHoraVarNome]:
            self.__datas__.add(pd.datetime.date(data))

    def __separaViagens__(self, diffinicio, difffim, vecSentido,  valInicio, valFim, posAttr, posIni, posEnd, accept):
        flagi = (diffinicio == valInicio) & (vecSentido == 0)
        flagf = difffim == valFim

        indi = self.__df__[flagi].index.tolist()
        indf = self.__df__[flagf].index.tolist()

        # Vamos pegar viagens de atr para asg
        indi = list(filter(lambda i: i < indf[-1], indi))
        indif = [(i, list(filter(lambda k: k > i, indf))[0]) for i in indi]
        eqif = list(filter(lambda i: indif[i][1] == indif[i+1][1], range(len(indif)-1)))
        indif = [indif[k] for k in filter(lambda i: i not in eqif, range(0, len(indif)))]

        indif = list(filter(lambda p: abs(self.__df__[posAttr].loc[p[0]] - posIni) <= accept and abs(self.__df__[posAttr].loc[p[1]] - posEnd) <= accept, indif))

        # separar horário da viagem
        horif = [self.__df__[dataHoraVarNome].loc[i] for i,j in indif]
        tempoViagem = [self.__df__[dataHoraVarNome].loc[j] - self.__df__[dataHoraVarNome].loc[i] for i,j in indif]
        s = zip(indif, tempoViagem)
        return zip(horif, s)

    def getTodasDatas(self):
        return sorted(self.__datas__)

    def getDataHoraViagensATR(self):
        return sorted(self.__fromATRij__.keys())

    def getViagensATR(self):
        return self.__fromATRij__

    def getTempoViagemATR(self, datahora):
        return self.__fromATRij__[datahora][1]

    def getDataHoraViagensASG(self):
        return sorted(self.__fromASGij__.keys())

    def getTempoViagemASG(self, datahora):
        return self.__fromASGij__[datahora][1]

    def getViagensASG(self):
        return self.__fromASGij__

    def getHeader(self):
        return sorted(self.__df__.axes[1])

    @staticmethod
    def fromDataFrame(df, findTravels=True):
        return DadoSistema(df, findTravels)

# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import datetime

dataHoraVarNome = 'DataHora_PLC'
sentidoATR = 1
sentidoASG = 2

class DataError(Exception):
    pass

class DadoSistema(pd.DataFrame):

    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False):
        super(DadoSistema,self).__init__(data, index, columns, dtype, copy)

        global dataHoraVarNome

        dataH = None

        for column in self:
            if isinstance(self[column][0], str):
                try:
                    self[column] = pd.to_datetime(self[column])
                    dataH = column if dataH is None else dataH
                    self[column + "_dia"] = self[column].dt.day
                    self[column + "_mes"] = self[column].dt.month
                    self[column + "_ano"] = self[column].dt.year
                    self[column + "_hora"] = self[column].dt.hour
                    self[column + "_minuto"] = self[column].dt.minute
                    self[column + "_segundo"] = self[column].dt.second
                    #self[column + "_data"] = pd.to_datetime([d.isoformat() for d in self[column].dt.date])
                    #self[column + "_tempo"] = pd.to_datetime([t.isoformat() for t in self[column].dt.time])
                except Exception as e:
                    print(e)
                    self.drop([column], axis=1, inplace=True)

        if hasattr(self, dataHoraVarNome):
            self.sort_values(by=dataHoraVarNome, inplace=True)
        elif dataH is not None:
            self.sort_values(by=dataH, inplace=True)
            dataHoraVarNome = dataH

        self.__datas__ = set()

        self.__fromATRij__ = dict()
        self.__fromASGij__ = dict()


        if hasattr(self, dataHoraVarNome):
            self.__separaDatas__()

        # Separa as viagens. Terá que descobrir se é A100 e A200
        if hasattr(self, 'A100_Sentido') and hasattr(self, 'A100_ATO') and hasattr(self, dataHoraVarNome) and hasattr(self, 'A100_Posicao'):
            diffSentidoA100 = self.A100_Sentido.diff(1)
            diffATOA100 = self.A100_ATO.diff(-1)
            self.__fromATRij__ = \
                dict(self.__separaViagens__(diffATOA100, diffSentidoA100, self.A100_Sentido, -1, -sentidoATR, 'A100_Posicao', 864.5, 52.5, 1.5))
            self.__fromASGij__ = \
                dict(self.__separaViagens__(diffATOA100, diffSentidoA100, self.A100_Sentido, -1, -sentidoASG, 'A100_Posicao', 52.5, 864.5, 1.5))


        if hasattr(self, 'A200_Sentido') and hasattr(self, 'A200_ATO') and hasattr(self, dataHoraVarNome) and hasattr(self, 'A200_Posicao'):
            diffSentidoA200 = self.A200_Sentido.diff(1)
            diffATOA200 = self.A200_ATO.diff(-1)
            self.__A200fromATRij__ = \
                dict(self.__separaViagens__(diffATOA200, diffSentidoA200, self.A200_Sentido, -1, -sentidoATR, 'A200_Posicao', 864.5, 52.5, 1.5))
            self.__A200fromASGij__ = \
                dict(self.__separaViagens__(diffATOA200, diffSentidoA200, self.A200_Sentido, -1, -sentidoASG, 'A200_Posicao', 52.5, 864.5, 1.5))

            for key, val in self.__A200fromASGij__.items():
                self.__fromASGij__[key] = val

            for key, val in self.__A200fromATRij__.items():
                self.__fromATRij__[key] = val



    def __separaDatas__(self):
        # separa as datas
        for data in self[dataHoraVarNome]:
            self.__datas__.add(pd.datetime.date(data))

    def __separaViagens__(self, diffinicio, difffim, vecSentido,  valInicio, valFim, posAttr, posIni, posEnd, accept):
        flagi = (diffinicio == valInicio) & (vecSentido == 0)
        flagf = difffim == valFim

        indi = self[flagi].index.tolist()
        indf = self[flagf].index.tolist()

        # Vamos pegar viagens de atr para asg
        indi = list(filter(lambda i: i < indf[-1], indi))
        indif = [(i, list(filter(lambda k: k > i, indf))[0]) for i in indi]
        eqif = list(filter(lambda i: indif[i][1] == indif[i+1][1], range(len(indif)-1)))
        indif = [indif[k] for k in filter(lambda i: i not in eqif, range(0, len(indif)))]

        indif = list(filter(lambda p: abs(self[posAttr].loc[p[0]] - posIni) <= accept and abs(self[posAttr].loc[p[1]] - posEnd) <= accept, indif))

        # separar horário da viagem
        horif = [self[dataHoraVarNome].loc[i] for i,j in indif]
        tempoViagem = [self[dataHoraVarNome].loc[j] - self[dataHoraVarNome].loc[i] for i,j in indif]
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
        return sorted(self.axes[1])

    @staticmethod
    def fromDataFrame(df):
        return DadoSistema(df)

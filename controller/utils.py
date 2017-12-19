# -*- coding: utf-8 -*-

from collections import OrderedDict
import pandas as pd
from model.DadosSistema import DadoSistema
import csv
import numpy as np

arquivosCarregados = OrderedDict()
allDataFrames = pd.DataFrame()
allDadoSistema = DadoSistema.fromDataFrame(allDataFrames)

def carregaArquivo(arquivo):
    # Faz o carregamento de um arquivo qualquer
    global allDataFrames
    global allDadoSistema
    result = 'Arquivo carregado com sucesso'
    if not arquivo in arquivosCarregados:
        try:
            df = pd.read_csv(arquivo, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            if df.count(axis=1)[0] <= 1:
                df = pd.read_csv(arquivo)
                if hasattr(df, 'LocalDate') and hasattr(df, 'LocalTime'):
                    df['DataHora_PLC'] = df['LocalDate'] + ' ' + df['LocalTime']
                    df.drop(['LocalDate', 'LocalTime'], axis=1, inplace=True)

            arquivosCarregados[arquivo] = True
            nallDataFrames = pd.concat([allDataFrames, df], ignore_index = True)
            try:
                allDadoSistema = DadoSistema.fromDataFrame(nallDataFrames.copy())
                allDataFrames = nallDataFrames
            except MemoryError as m:
                print("Memory Error")
                arquivosCarregados.pop(arquivo)
                allDadoSistema = DadoSistema.fromDataFrame(allDataFrames)
                result = 'Memória insuficiente'

            # print(allDadoSistema.describe())
        except:
            result = 'Erro ao abrir ou processar arquivo'
    else:
        result = 'Este arquivo já foi carregado'

    return result


def getDatasArquivo(arquivo):
    # Retorna todas as datas do arquivo em questão, que já deve estar carregado
    global allDadoSistema
    try:
        res = allDadoSistema.getTodasDatas()
    except:
        res = None

    return res

def getDatasHorasATRparaASG(arquivo):
    # Retorna as datas de ATR para ASG do arquivo em questão, que já deve estar carregado
    global allDadoSistema
    try:
        res = DadoSistema.getDataHoraViagensATR(allDadoSistema)
    except:
        res = None

    return res


def getDatasHorasASGparaATR(arquivo):
    # Retorna as datas de ASG para ATR do arquivo em questão, que já deve estar carregado
    global allDadoSistema
    try:
        res = DadoSistema.getDataHoraViagensASG(allDadoSistema)
    except:
        res = None

    return res

def getHeader(arquivo):
    # Retorna os nomes dos dados que foram carregados
    global allDadoSistema
    try:
        res = DadoSistema.getHeader(allDadoSistema)
    except:
        res = None

    return res

def getInicioFimViagensATRparaASG(arquivo):
    # Retorna os nomes dos dados que foram carregados
    global allDadoSistema
    try:
        datasHoras = DadoSistema.getDataHoraViagensATR(allDadoSistema)
        res = [(horario, horario + DadoSistema.getTempoViagemATR(allDadoSistema, horario))for horario in sorted(datasHoras)]
    except:
        res = None

    return res

def getInicioFimViagensASGparaATR(arquivo):
    # Retorna os nomes dos dados que foram carregados
    global allDadoSistema
    try:
        datasHoras = DadoSistema.getDataHoraViagensASG(allDadoSistema)
        res = [(horario, horario + DadoSistema.getTempoViagemASG(allDadoSistema, horario))for horario in sorted(datasHoras)]
    except:
        res = None

    return res

def getDictHoraDataHoraATRparaASG(arquivo):
    global allDadoSistema
    try:
        datasHoras = DadoSistema.getDataHoraViagensATR(allDadoSistema)
        datas = sorted(set(map(lambda dh: pd.datetime.date(dh), datasHoras)))
        res = OrderedDict()
        for data in datas:
            horariosData = filter(lambda d: pd.datetime.date(d) == data, datasHoras)
            res[data] = [(pd.datetime.time(horario), DadoSistema.getTempoViagemATR(allDadoSistema, horario)) for horario in horariosData]
    except:
        res = None

    return res


def getDictHoraDataHoraASGparaATR(arquivo):
    global allDadoSistema
    try:
        datasHoras = DadoSistema.getDataHoraViagensASG(allDadoSistema)
        datas = sorted(set(map(lambda dh: pd.datetime.date(dh), datasHoras)))
        res = OrderedDict()
        for data in datas:
            horariosData = filter(lambda d: pd.datetime.date(d) == data, datasHoras)
            res[data] = [(pd.datetime.time(horario), DadoSistema.getTempoViagemASG(allDadoSistema, horario)) for horario in horariosData]
    except:
        res = None

    return res

def getValoresX(strValor, strQuery):
    global allDadoSistema
    res = None
    # print('Aqui')
    if strValor in allDadoSistema.axes[1]:
        # print('Achou')
        try:
            res = allDadoSistema.query(strQuery)[strValor].dropna()
        except:
            res = allDadoSistema[strValor]
    return res

def getValoresXY(strValorX, strQueryX, strValorY, strQueryY):
    global allDadoSistema
    res = pd.Series()
    res.name = strValorY
    # print('Aqui')
    # print(allDadoSistema[strValorY].dtypes)
    if strValorX in allDadoSistema.axes[1] and strValorY in allDadoSistema.axes[1] and np.issubdtype(allDadoSistema[strValorY], np.number):
        try:
            res = allDadoSistema.query(strQueryX)
        except:
            res = allDadoSistema

        try:
            res = res.query(strQueryY)
        except:
            pass

        res = pd.Series(index=res.loc[:,strValorX].tolist(), data=res.loc[:,strValorY].tolist()).dropna().sort_index()
        res.name = strValorY
    return res

def varExists(strVar):
    global allDadoSistema
    if strVar in allDadoSistema.axes[1]:
        return True
    return False

def varXYExists(strX, strY):
    global allDadoSistema
    if strX in allDadoSistema.axes[1] and strY in allDadoSistema.axes[1]:
        return True
    return False

def getViagensATRparaASG(arquivo):
    global allDadoSistema
    try:
        res = DadoSistema.getViagensATR(allDadoSistema)
    except:
        res = None

    return res

def getViagensASGparaATR(arquivo):
    global allDadoSistema
    try:
        res = DadoSistema.getViagensASG(allDadoSistema)
    except:
        res = None

    return res

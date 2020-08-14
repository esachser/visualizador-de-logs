# -*- coding: utf-8 -*-

from collections import OrderedDict
import pandas as pd
from model.DadosSistema import DadoSistema
import csv
import numpy as np
import traceback
import gc

arquivosCarregados = OrderedDict()
allDadoSistema = DadoSistema.fromDataFrame(pd.DataFrame())

def carregaArquivo(arquivo):
    # Faz o carregamento de um arquivo qualquer
    # global allDataFrames
    global allDadoSistema
    result = 'Arquivo carregado com sucesso'
    if not arquivo in arquivosCarregados:
        try:
            df = pd.read_csv(arquivo, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            if df.count(axis=1)[0] <= 1:
                df = pd.read_csv(arquivo)
                # Adequação de arquivos antigos aos novos
                if hasattr(df, 'LocalDate') and hasattr(df, 'LocalTime'):
                    df['DataHora_PLC'] = df['LocalDate'] + ' ' + df['LocalTime']
                    df.drop(['LocalDate', 'LocalTime'], axis=1, inplace=True)

            novoDado = DadoSistema.fromDataFrame(df, False)
            arquivosCarregados[arquivo] = True
            try:
                allDadoSistema = DadoSistema.fromDataFrame(novoDado.__df__.append(allDadoSistema.__df__, ignore_index=True, sort=False))
            except MemoryError as m:
                print("Memory Error")
                arquivosCarregados.pop(arquivo)
                result = 'Memória insuficiente'

            gc.collect()
        except:
            traceback.print_exc()
            result = 'Erro ao abrir ou processar arquivo'
    else:
        result = 'Este arquivo já foi carregado'

    return result

def carregaArquivos(arquivos):
    # Faz o carregamento de um arquivo qualquer
    # global allDataFrames
    global allDadoSistema
    result = ['Arquivo carregado com sucesso']*len(arquivos)
    dfs = []
    for i in range(len(arquivos)):
        arquivo = arquivos[i]
        if not arquivo in arquivosCarregados:
            try:
                df = pd.read_csv(arquivo, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                if df.count(axis=1)[0] <= 1:
                    df = pd.read_csv(arquivo)
                    # Adequação de arquivos antigos aos novos
                    if hasattr(df, 'LocalDate') and hasattr(df, 'LocalTime'):
                        df['DataHora_PLC'] = df['LocalDate'] + ' ' + df['LocalTime']
                        df.drop(['LocalDate', 'LocalTime'], axis=1, inplace=True)

                novoDado = DadoSistema.fromDataFrame(df, False)
                arquivosCarregados[arquivo] = True
                dfs.append(novoDado.__df__)
            except:
                traceback.print_exc()
                result[i] = 'Erro ao abrir ou processar arquivo'
        else:
            result[i] = 'Este arquivo já foi carregado'

    try:
        allDadoSistema = DadoSistema.fromDataFrame(allDadoSistema.__df__.append(dfs, ignore_index=True, sort=False))
    except MemoryError as m:
        print("Memory Error")
        for arquivo in arquivos: arquivosCarregados.pop(arquivo)
        result = ['Memória insuficiente']*len(arquivos)

    for i in range(len(arquivos)):
        result[i] = arquivos[i].split('/')[-1] + ": " + result[i]

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
    if strValor in allDadoSistema.__df__.axes[1]:
        # print('Achou')
        try:
            res = allDadoSistema.__df__.query(strQuery)[strValor].dropna()
        except:
            res = allDadoSistema.__df__[strValor]
    return res

def getValoresXY(strValorX, strQueryX, strValorY, strQueryY):
    global allDadoSistema
    res = pd.Series()
    res.name = strValorY
    # print('Aqui')
    # print(allDadoSistema[strValorY].dtypes)
    if strValorX in allDadoSistema.__df__.axes[1] and strValorY in allDadoSistema.__df__.axes[1] and np.issubdtype(allDadoSistema.__df__[strValorY], np.number):
        try:
            res = allDadoSistema.__df__.query(strQueryX)
        except:
            res = allDadoSistema.__df__

        try:
            res = res.query(strQueryY)
        except:
            pass

        res = pd.Series(index=res.loc[:,strValorX].tolist(), data=res.loc[:,strValorY].tolist()).dropna().sort_index()
        res.name = strValorY
    return res

def varExists(strVar):
    global allDadoSistema
    if strVar in allDadoSistema.__df__.axes[1]:
        return True
    return False

def varXYExists(strX, strY):
    global allDadoSistema
    if strX in allDadoSistema.__df__.axes[1] and strY in allDadoSistema.__df__.axes[1]:
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

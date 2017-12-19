# -*- coding: utf-8 -*-

import json

import pandas as pd

class PlotType(object):
    ALL = 255
    NONE = 0
    LINEPLOT = 1
    SCATTERPLOT = 2

    @staticmethod
    def isLinePlot(value):
        return (value & PlotType.LINEPLOT) > 0

    @staticmethod
    def isScatterPlot(value):
        return (value & PlotType.SCATTERPLOT) > 0

class XOption(object):
    def __init__(self, strVariavel = 'DataHora_PLC', strQuery = ''):
        self.strVariavel = strVariavel
        self.strQuery = strQuery


class YOptions(object):
    def __init__(self, strVariavel = None, color = None, strQuery = '', plotType = PlotType.LINEPLOT):
        self.strVariavel = strVariavel
        self.color = color
        self.strQuery = strQuery
        self.plotType = plotType

class Plot(object):
    def __init__(self, x = XOption('DataHora_PLC',''), y = [], grid = True):
        super(Plot, self).__init__()
        self.x = x
        self.y = y
        self.grid = grid


class Tab(object):
    def __init__(self, name = 'Plot', maxPlots = 3, plots = [], share = False):
        super(Tab, self).__init__()
        self.name = name
        self.maxPlots = maxPlots
        self.plots = plots
        self.share = share


def createDefaultInfos():
    # infos = list()
    # datef = pd.to_datetime("2016-08-30 14:16:00")

    query1 = '(DataHora_PLC >= "2016-08-30 14:07:00") & (DataHora_PLC <= "2016-08-30 14:11:00")'
    query2 = '(DataHora_PLC >= "2016-08-30 14:11:00") & (DataHora_PLC <= "2016-08-30 14:16:00")'

    plts = [Plot(XOption('A100_Posicao', ''), 
                 [YOptions('A100_Velocidade', [0,0,255], '', PlotType.ALL)]), 
            Plot(XOption('A100_Posicao', 'A100_Posicao > 200.0'), 
                 [YOptions('A100_Velocidade', [255,0,0], query1, PlotType.ALL), 
                  YOptions('A100_Velocidade', [255,0,255], query2, PlotType.ALL)])]
    plts2 = [Plot(y = [YOptions('A100_Velocidade', [0,255,255], ''), YOptions('A200_Velocidade', [0,255,0], '')])]
    # return [Tab(plots=plts, share = True), Tab(name = 'Plot2', plots = plts2)]
    return [Tab(plots = [Plot()])]

def loadConfigFile(fileToRead):
    try:
        with open(fileToRead, 'r') as f:
            ts = json.load(f)
            res = list()
            for t in ts:
                name = t['name']
                maxPlots = t['maxPlots']
                sharex = t['sharex']
                plots = list()
                for p in t['plots']:
                    xvar = p['xOptions']['xVariavel']
                    xquery = p['xOptions']['xQuery']
                    grid = p['grid']
                    items = list()
                    for y in p['yOptions']:
                        yvar = y['strVariavel']
                        yquery = y['strQuery']
                        color = y['color']
                        pltType = y['plotType']
                        items.append(YOptions(yvar, color, yquery, pltType))
                    plots.append(Plot(XOption(xvar, xquery), items, grid))
                res.append(Tab(name, maxPlots, plots, sharex))

    except Exception as e:
        res = createDefaultInfos()

    return res

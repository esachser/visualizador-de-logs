# -*- coding: utf-8 -*-

import numpy as np
import pyqtgraph as pg
import controller.utils as controller
import pandas as pd
import datetime
import rx
import functools as f
from PyQt5 import QtCore, QtGui, QtWidgets
import weakref
import traceback
from options.info import PlotType
import time
import random


class PlotMenu(QtWidgets.QMenu):

    sigRemovePlot = QtCore.pyqtSignal()
    sigAddPlot = QtCore.pyqtSignal()

    def __init__(self, plotPresenter):
        QtWidgets.QMenu.__init__(self)

        self.plotPresenter = weakref.ref(plotPresenter)

        self.setTitle("ViewBox options")

        self.viewAll = QtWidgets.QAction("Resetar eixos", self)
        self.viewAll.triggered.connect(self.autoRange)
        self.addAction(self.viewAll)


        self.addPlot = QtWidgets.QAction("Adicionar curva", self)
        self.addPlot.triggered.connect(self.addNewPlot)
        self.addAction(self.addPlot)

        self.removePlot = QtWidgets.QAction("Remover gráfico", self)
        self.removePlot.triggered.connect(self.sigRemovePlot.emit)
        self.addAction(self.removePlot)


    def addNewPlot(self):
        items = PlotMenu.__xVarValues__

        item, ok = QtWidgets.QInputDialog.getItem(self, "Escolha a variável",
            "Variáveis", items, 0, False)

        if ok and item:
            nPlotItemPresenters = len(self.plotPresenter().plotItemPresenters)
            color = [random.randint(0,255), random.randint(0,255), random.randint(0,255)]
            self.plotPresenter().plotView.plot.vb.enableAutoRange(axis = pg.ViewBox.YAxis)
            self.plotPresenter().addPlotItem(item, '', color, PlotType.LINEPLOT)
            self.plotPresenter().plotView.plot.vb.disableAutoRange()
            self.sigAddPlot.emit()
            if nPlotItemPresenters == 0 and not self.plotPresenter().plotView.shx:
                self.autoRange()


    def autoRange(self):
        self.plotPresenter().plotView.plot.vb.autoRange()

    @staticmethod
    def setXVarOptions(values):
        PlotMenu.__xVarValues__ = values


TS_MULT_us = 1e6

def int2dt(ts, ts_mult=TS_MULT_us):
    return(datetime.datetime.utcfromtimestamp(float(ts)/ts_mult))

def int2td(ts, ts_mult=TS_MULT_us):
    return(datetime.timedelta(seconds=float(ts)/ts_mult))


class MyAxisItem(pg.AxisItem):
    def __init__(self, isTime, *args, **kwargs):
        super(MyAxisItem, self).__init__(showValues = True,*args, **kwargs)
        self.isTime = isTime

    def to_datetime(self, value):
        try:
            v = pd.to_datetime(value)
            r = v.strftime('%H:%M:%S\n%d/%m/%y')
        except:
            r = ''

        return r


    def tickStrings(self, values, scale, spacing):
        if self.logMode:
            return self.logTickStrings(values, scale, spacing)

        places = max(0, np.ceil(-np.log10(spacing*scale)))
        strings = []
        for v in values:
            vs = v * scale
            if self.isTime:
                vstr = self.to_datetime(vs)
            else:
                if abs(vs) < .001 or abs(vs) >= 10000:
                    vstr = "%g" % vs
                else:
                    vstr = ("%%0.%df" % places) % vs
            strings.append(vstr)
        return strings


class InfoPlotItem(QtCore.QObject):

    sigMouseClick = QtCore.pyqtSignal()
    sigDoubleClick = QtCore.pyqtSignal()

    def __init__(self, plot, yvalues, sharex, grid, time = False):
        super(InfoPlotItem, self).__init__()
        QtCore.QObject.__init__(self)
        self.plot = plot
        self.ycp = yvalues
        self.vLine = pg.InfiniteLine(angle=90)
        self.xtext = pg.TextItem(color = (50,50,50), anchor=(0.5, 1))
        self.legend = self.plot.addLegend(offset=(0,1))
        self.shx = sharex is not None
        self.xTime = time
        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60,
                                    slot=lambda evt: self.mouseMoved(evt[0]))
        self.y = dict()

        self.plot.scene().sigMouseClicked.connect(self.mouseClicked)
        self.plot.vb.sigYRangeChanged.connect(lambda a, b: self.setxtextPosition())



    def restartLegend(self):
        self.legend.scene().removeItem(self.legend)
        self.legend = self.plot.addLegend(offset=(0,1))

    def startDataPlots(self):
        for (y, t) in self.y.values():
            self.plot.removeItem(t)
            del t
        self.y = dict()
        self.plot.clear()
        self.restartLegend()
        self.plot.addItem(self.vLine, ignoreBounds=True)
        self.plot.addItem(self.xtext, ignoreBounds=True)


    def prepareData(self, v, c, pt):
        x = v.index
        y = v

        self.xTime = x.dtype == 'datetime64[ns]'
        self.plot.getAxis('bottom').isTime = self.xTime

        nx = list(map(lambda val: val.value, x.tolist())) if self.xTime else x.tolist()

        color = (c[0], c[1], c[2])

        lpen = c if PlotType.isLinePlot(pt) else None
        s = 'o' if PlotType.isScatterPlot(pt) else None

        # if self.xTime:
        #     import numpy as np
        #     v0 = x.get_values()[0]
        #     myx = (x - v0) / np.timedelta64(1, 'h')
        #     print(y.name, np.trapz(y.tolist(), myx.get_values()))

        return (nx, y, lpen, s, color)


    def plotItem(self, v, c, pt):
        nx, y, lpen, s, color = self.prepareData(v, c, pt)

        plotItem =  self.plot.plot(nx, y.tolist(), name = y.name,
                               pen = lpen,
                               symbol = s, symbolPen = color, symbolBrush = color, symbolSize = 5)


        ti = pg.TextItem()
        ti.setColor(c)
        self.y[plotItem] = (v, ti)
        if len(nx)>0:
            self.plot.addItem(ti, ignoreBounds = True)
            ti.setPos(nx[0], y.tolist()[0])
        return plotItem

    def atualizaItem(self, item, v, c, pt):
        nx, y, lpen, s, color = self.prepareData(v, c, pt)

        [v[1].setText(y.name) for v in filter(lambda s: s[0].item == item, self.legend.items)]
        old, l = self.y[item]
        l.setColor(c)
        if len(nx)>0 and not l in self.plot.items:
            self.plot.addItem(l, ignoreBounds = True)
            l.setPos(nx[0], y.tolist()[0])
        self.y[item] = (v, l)

        item.setData(nx, y.tolist(), name = y.name,
                               pen = lpen,
                               symbol = s, symbolPen = color, symbolBrush = color, symbolSize = 5)

    def removeLegenda(self, item):
        legenda = [v for v in filter(lambda s: s[0].item == item, self.legend.items)][0]
        self.legend.items.remove(legenda)
        self.legend.layout.removeItem(legenda[0])
        legenda[0].close()
        self.legend.layout.removeItem(legenda[1])
        legenda[1].close()
        self.legend.updateSize()
        del legenda

    def showGrid(self, grid):
        self.plot.showGrid(x = grid, y = grid)

    def mouseMoved(self, evt):
        pos = evt#[0]  ## using signal proxy turns original arguments into a tuple

        if self.plot.sceneBoundingRect().contains(pos) or self.shx:
            mousePoint = self.plot.vb.mapSceneToView(pos)

            # if self.xTime:
            #     print("xtime")

            try:
                x = pd.to_datetime(int(mousePoint.x())) if self.xTime else round(mousePoint.x(), 1)
            except:
                x = None

            if not x is None:
                if self.xTime:
                    xstr = x.strftime('%H:%M:%S')
                else:
                    xstr = str(round(x, 3))
                self.xtext.setHtml("<div style='background-color: rgba(250, 250, 250, 60);'>{}</div>".format(xstr))
                self.xtext.setPos(mousePoint.x(), self.plot.vb.viewRect().top())

                for (y, t) in self.y.values():
                    try:
                        val = y[x]
                    except:
                        if self.xTime and x is datetime.datetime or not self.xTime and np.isnan(x):
                            val = np.NaN
                        else:
                            try:
                                mY = mousePoint.y()
                                diff = (np.abs(y.index - x)).argsort()[0]
                                val = y.ix[y.index[diff]]
                            except:
                                val = np.NaN

                    if isinstance(val, pd.Series):
                        mY = mousePoint.y()
                        cho = None
                        for valor in val:
                            if cho is None or abs(valor - mY) < abs(cho - mY):
                                cho = valor
                        val = cho
                    val = round(val, 3)

                    text = '' if np.isnan(val) else '{}'.format(val)
                    t.setText(text)
                    t.setHtml("<div style='background-color: rgba(250, 250, 250, 100);'>{}</div>".format(text))
                    if not np.isnan(val):
                        t.setPos(mousePoint.x(), float(val))

            self.vLine.setPos(mousePoint.x())

    def setxtextPosition(self):
        mousePoint = self.xtext.pos()
        try:
            x = pd.to_datetime(int(mousePoint.x())) if self.xTime else round(mousePoint.x(), 1)
        except:
            x = None

        if not x is None:
            if self.xTime:
                xstr = x.strftime('%H:%M:%S')
            else:
                xstr = str(round(x, 3))
                
            self.xtext.setHtml("<div style='background-color: rgba(250, 250, 250, 60);'>{}</div>".format(xstr))
            self.xtext.setPos(mousePoint.x(), self.plot.vb.viewRect().top())


    def mouseClicked(self, evt):
        pos = evt.scenePos()
        if (evt.buttons() & QtCore.Qt.LeftButton) and self.plot.sceneBoundingRect().contains(pos):
            if evt.double():
                self.sigDoubleClick.emit()
            else:
                self.sigMouseClick.emit()


class PlotPresenter:
    """A união entre o plot view e o lógico"""
    def __init__(self, plotView, plotViewModel, plotItemPresenters):
        self.plotView = plotView
        self.plotViewModel = plotViewModel
        self.plotItemPresenters = plotItemPresenters

        self.__onInit__ = True

        self.plotView.plot.vb.menu = PlotMenu(self)

        self.plotViewModel.xVariavelBehavior.subscribe(self.initData)
        self.plotViewModel.xQueryBehavior.subscribe(self.initData)

        for plotItemPresenter in self.plotItemPresenters:
            # print('PlotItem' ,time.strftime('%Y:%m:%d %H:%M:%S'))
            plotItemPresenter.plotItemViewModel.strVariavelBehavior.subscribe(f.partial(PlotPresenter.atualizaPlot, self, plotItemPresenter))
            plotItemPresenter.plotItemViewModel.strQueryBehavior.subscribe(f.partial(PlotPresenter.atualizaPlot, self, plotItemPresenter))
            plotItemPresenter.plotItemViewModel.colorBehavior.subscribe(f.partial(PlotPresenter.atualizaPlot, self, plotItemPresenter))
            plotItemPresenter.plotItemViewModel.plotTypeBehavior.subscribe(f.partial(PlotPresenter.atualizaPlot, self, plotItemPresenter))

        self.__onInit__ = False
        self.initData(None)

    def initData(self, bla):
        if self.__onInit__:
            return
        # print('InitData' ,time.strftime('%Y:%m:%d %H:%M:%S'))
        self.plotView.startDataPlots()

        for plotItemPresenter in self.plotItemPresenters:
            self.startPlotItemView(plotItemPresenter)

        self.plotView.plot.vb.autoRange(items = [plotItemPresenter.plotItemView for plotItemPresenter in self.plotItemPresenters])


    def startPlotItemView(self, plotItemPresenter):
        if self.__onInit__:
            return
        # print('startPlotItemView' ,time.strftime('%Y:%m:%d %H:%M:%S'))
        plotItemPresenter.plotItemView = self.plotView.plotItem(controller.getValoresXY(self.plotViewModel.xVariavel, self.plotViewModel.xQuery,
                                                                plotItemPresenter.plotItemViewModel.strVariavel, plotItemPresenter.plotItemViewModel.strQuery),
                                                plotItemPresenter.plotItemViewModel.color, plotItemPresenter.plotItemViewModel.plotType)


    def atualizaPlot(self, pltItemPres, bla):
        if self.__onInit__:
            return
        # print('atualizaPlot' ,time.strftime('%Y:%m:%d %H:%M:%S'))
        self.plotView.atualizaItem(pltItemPres.plotItemView,
            controller.getValoresXY(self.plotViewModel.xVariavel, self.plotViewModel.xQuery,
                pltItemPres.plotItemViewModel.strVariavel, pltItemPres.plotItemViewModel.strQuery),
            pltItemPres.plotItemViewModel.color, pltItemPres.plotItemViewModel.plotType)

    def addPlotItem(self, strVar, strQ, color, pltType):
        if not controller.varExists(strVar):
            return
        self.__onInit__ = True
        pltItemVM = PlotItemViewModel(strVar, strQ, color, pltType)
        pltItemPres = PlotItemPresenter(None, pltItemVM)
        pltItemPres.plotItemViewModel.strVariavelBehavior.subscribe(f.partial(PlotPresenter.atualizaPlot, self, pltItemPres))
        pltItemPres.plotItemViewModel.strQueryBehavior.subscribe(f.partial(PlotPresenter.atualizaPlot, self, pltItemPres))
        pltItemPres.plotItemViewModel.colorBehavior.subscribe(f.partial(PlotPresenter.atualizaPlot, self, pltItemPres))
        pltItemPres.plotItemViewModel.plotTypeBehavior.subscribe(f.partial(PlotPresenter.atualizaPlot, self, pltItemPres))
        self.plotItemPresenters.append(pltItemPres)
        self.__onInit__ = False
        self.startPlotItemView(pltItemPres)
        self.atualizaPlot(pltItemPres, None)


    def removePlotItemPresenter(self, plotItemPresenter):
        self.plotItemPresenters.remove(plotItemPresenter)
        self.plotView.removeLegenda(plotItemPresenter.plotItemView)
        v = self.plotView.y.get(plotItemPresenter.plotItemView)
        if v is not None:
            self.plotView.plot.removeItem(v[1])
        self.plotView.y.pop(plotItemPresenter.plotItemView)
        self.plotView.plot.removeItem(plotItemPresenter.plotItemView)
        plotItemPresenter.plotItemViewModel.dispose()
        del plotItemPresenter.plotItemViewModel
        del plotItemPresenter

    def toJSON(self):
        return {
            'grid': self.plotViewModel.grid,
            'xOptions': {
                'xVariavel': self.plotViewModel.xVariavel,
                'xQuery': self.plotViewModel.xQuery
            },
            'yOptions': [pltItPres.toJSON() for pltItPres in self.plotItemPresenters]
        }

class PlotItemPresenter:
    """A união entre o plot view e o lógico"""
    def __init__(self, plotItemView, plotItemViewModel):
        self.plotItemView = plotItemView
        self.plotItemViewModel = plotItemViewModel

    def toJSON(self):
        return  {
            'strVariavel': self.plotItemViewModel.strVariavel,
            'strQuery': self.plotItemViewModel.strQuery,
            'color': self.plotItemViewModel.color,
            'plotType': self.plotItemViewModel.plotType
        }

class PlotItemAero(pg.PlotItem):
    """docstring for PlotItemAero"""
    def __init__(self, *args, **kwargs):
        super(PlotItemAero, self).__init__(*args, **kwargs)
        self.border = None

    def setBorder(self, *args, **kwargs):
        self.border = pg.mkPen(*args, **kwargs)
        self.update()

    def paint(self, p, *args):
        QtWidgets.QGraphicsWidget.paint(self, p, *args)
        if self.border is not None:
            p.setPen(self.border)
            p.drawRect(self.boundingRect())





def processPlot(window, options):
    xstr = options.x.strVariavel
    xqstr = options.x.strQuery

    

    if not controller.varExists(xstr):
        return None

    x = controller.getValoresX(xstr, xqstr)

    if x is None:
        return None
    # print('InitPlot' ,time.strftime('%Y:%m:%d %H:%M:%S'))
    # plot = window.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')}) if x.dtypes == 'datetime64[ns]' else window.addPlot()
    plot = PlotItemAero(axisItems={'bottom': MyAxisItem(isTime = (x.dtypes == 'datetime64[ns]'), orientation='bottom')})
    # print('MiddlePlot' ,time.strftime('%Y:%m:%d %H:%M:%S'))
    window.addItem(plot)
    nplot = InfoPlotItem(plot, None, None, options.grid, time = (x.dtypes == 'datetime64[ns]'))
    # print('EndPlot' ,time.strftime('%Y:%m:%d %H:%M:%S'))

    plotVM = PlotViewModel(xstr, xqstr, options.grid)
    plotVM.gridBehavior.subscribe(nplot.showGrid)

    plotItemPresenters = \
        [PlotItemPresenter(None, PlotItemViewModel(pltItem.strVariavel, pltItem.strQuery, pltItem.color, pltItem.plotType))
        for pltItem in options.y if controller.varXYExists(xstr, pltItem.strVariavel)]

    return PlotPresenter(nplot, plotVM, plotItemPresenters)


class PlotViewModel:
    def __init__(self, xVariavel, xQuery, grid):
        self.xVariavelBehavior = rx.subjects.BehaviorSubject(xVariavel)
        self.xQueryBehavior = rx.subjects.BehaviorSubject(xQuery)
        self.gridBehavior = rx.subjects.BehaviorSubject(grid)
        # Fazer parte dos itens
        # self.plotItems = [ for pltItem in items]
        # Itens

    def dispose(self):
        self.xVariavelBehavior.dispose()
        self.xQueryBehavior.dispose()
        self.gridBehavior.dispose()

    def _get_xVariavel_(self):
        return self.xVariavelBehavior.value

    def _set_xVariavel_(self, value):
        if value != self.xVariavelBehavior.value:
            self.xVariavelBehavior.on_next(value)

    xVariavel = property(_get_xVariavel_, _set_xVariavel_)

    def _get_xQuery_(self):
        return self.xQueryBehavior.value

    def _set_xQuery_(self, value):
        if value != self.xQueryBehavior.value:
            self.xQueryBehavior.on_next(value)

    xQuery = property(_get_xQuery_, _set_xQuery_)

    def _get_grid_(self):
        return self.gridBehavior.value

    def _set_grid_(self, value):
        if value != self.gridBehavior.value:
            self.gridBehavior.on_next(value)

    grid = property(_get_grid_, _set_grid_)


class PlotItemViewModel:
    def __init__(self, strVariavel, strQuery, color, plotType):
        self.strVariavelBehavior = rx.subjects.BehaviorSubject(strVariavel)
        self.strQueryBehavior = rx.subjects.BehaviorSubject(strQuery)
        self.colorBehavior = rx.subjects.BehaviorSubject(color)
        self.plotTypeBehavior = rx.subjects.BehaviorSubject(plotType)

    def dispose(self):
        self.strVariavelBehavior.dispose()
        self.strQueryBehavior.dispose()
        self.colorBehavior.dispose()
        self.plotTypeBehavior.dispose()

    def _get_strVariavel_(self):
        return self.strVariavelBehavior.value

    def _set_strVariavel_(self, value):
        if value != self.strVariavelBehavior.value:
            self.strVariavelBehavior.on_next(value)

    strVariavel = property(_get_strVariavel_, _set_strVariavel_)

    def _get_strQuery_(self):
        return self.strQueryBehavior.value

    def _set_strQuery_(self, value):
        if value != self.strQueryBehavior.value:
            self.strQueryBehavior.on_next(value)

    strQuery = property(_get_strQuery_, _set_strQuery_)

    def _get_color_(self):
        return self.colorBehavior.value

    def _set_color_(self, value):
        if value[0] != self.colorBehavior.value[0] or value[1] != self.colorBehavior.value[1] or value[2] != self.colorBehavior.value[2]:
            self.colorBehavior.on_next(value)

    color = property(_get_color_, _set_color_)

    def _get_plotType_(self):
        return self.plotTypeBehavior.value

    def _set_plotType_(self, value):
        if value != self.plotTypeBehavior.value:
            self.plotTypeBehavior.on_next(value)

    plotType = property(_get_plotType_, _set_plotType_)

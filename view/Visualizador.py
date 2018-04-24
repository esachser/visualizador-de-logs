# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QStyle
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
import sys
import os
import functools as f
import pyqtgraph as pg
pgname = os.path.dirname(sys.argv[0])
progname = os.path.dirname(pgname)
sys.path.insert(0, progname)
import controller.utils as controller
# from mplCanvas import MplCanvas
from options.info import createDefaultInfos
import options.info as opt
from view.pyqtCanvas import processPlot, PlotMenu
from view.mainViewModel import TabViewModel, TabPresenter, saveTabPresenters

import view.configWidgets as configWidgets

import time

MAX_NUMBER_OF_PLOTS_PER_TAB = 6
CONFIG_FILE = '{}\configFile.json'.format(pgname)
ICON_FILE = '{}\VisIcon.ico'.format(pgname)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Visualizador de logs')
        self.setMinimumSize(1080,720)

        fileinf = QtCore.QFileInfo(QtGui.QApplication.instance().arguments()[0])

        self.setWindowIcon(QtGui.QFileIconProvider().icon(fileinf))
        # self.setWindowIcon(QtGui.QIcon(ICON_FILE))

        self.tabPresenters = []

        self.information = opt.loadConfigFile(CONFIG_FILE)

        menuBar = QtGui.QMenuBar(self)

        self.criaMenuArquivo(menuBar)
        self.criaMenuEditar(menuBar)
        self.criaMenuOpcoes(menuBar)
        self.setMenuBar(menuBar)

        self.main_widget = QtWidgets.QWidget(self)

        # Cria tab para configuração do plot
        self.widgetConfigPlot = configWidgets.WidgetConfig(None)
        self.widgetConfigPlot.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)

        self.tabWidgetPlots = QtWidgets.QTabWidget(self)
        # self.tabWidgetPlots.cl



        # Cria o layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.tabWidgetPlots)

        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)

        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'w')

        # self.widgetConfigPlot.sigRemovePlot.connect(lambda: self.removerPlot(self.widgetConfigPlot.plotPresenter))
        self.widgetConfigPlot.setEnabled(False)

        self.__firstFile__ = True



    def criaMenuArquivo(self, menuBar):
        arquivoToolBar = self.addToolBar("Arquivo")
        menuArquivo = menuBar.addMenu('Arquivo')
        actAbrir = QtGui.QMenu.addAction(menuArquivo, self.style().standardIcon(QStyle.SP_DialogOpenButton), '&Abrir')
        QtGui.QAction.setToolTip(actAbrir, u'Abrir arquivo csv para análise')
        QtGui.QAction.setShortcuts(actAbrir, QtGui.QKeySequence.Open)
        actAbrir.triggered.connect(self.escolheArquivoAbrir)
        arquivoToolBar.addAction(actAbrir)

        QtGui.QMenu.addSeparator(menuArquivo)

        actSair = QtGui.QMenu.addAction(menuArquivo, self.style().standardIcon(QStyle.SP_DialogCloseButton), '&Sair')
        QtGui.QAction.setShortcut(actSair, QtGui.QKeySequence.Close)
        actSair.triggered.connect(lambda: self.close())


    def criaMenuEditar(self, menuBar):
        menuEditar = menuBar.addMenu('Editar')

        self.actAdicionarTab = menuEditar.addAction('&Adicionar Tab')
        QtGui.QAction.setDisabled(self.actAdicionarTab, True)
        self.actAdicionarTab.triggered.connect(self.adicionarTab)

        self.actAdicionarPlot = menuEditar.addAction('&Adicionar Gráfico')
        QtGui.QAction.setDisabled(self.actAdicionarPlot, True)
        self.actAdicionarPlot.triggered.connect(self.adicionarPlot)

        menuEditar.addSeparator()

        self.actRemoverTab = menuEditar.addAction('&Remover Tab')
        self.actRemoverTab.setDisabled(True)
        self.actRemoverTab.triggered.connect(self.removerTab)

        editToolBar = self.addToolBar("Editar")
        editToolBar.addAction(self.actAdicionarTab)
        editToolBar.addAction(self.actRemoverTab)

        edit2ToolBar = self.addToolBar("Gráficos")
        edit2ToolBar.addAction(self.actAdicionarPlot)


    def criaMenuOpcoes(self, menuBar):
        menuOps = menuBar.addMenu('Opções')

        self.actCarregarOps = menuOps.addAction('&Carregar configuração de Gráficos')
        QtGui.QAction.setDisabled(self.actCarregarOps, True)
        self.actCarregarOps.triggered.connect(self.carregarOps)

        self.actSalvarOps = menuOps.addAction('&Salvar configuração de Gráficos')
        QtGui.QAction.setDisabled(self.actSalvarOps, True)
        self.actSalvarOps.triggered.connect(self.salvarOps)

        opsToolBar = self.addToolBar("Opções")
        opsToolBar.addAction(self.actCarregarOps)
        opsToolBar.addAction(self.actSalvarOps)


    def salvarOps(self):
        filename, end = QtWidgets.QFileDialog.getSaveFileName(self, 'Salvar configuração',
                                    QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation),
                                    '*.json')

        if filename is not '':
            saveTabPresenters(self.tabPresenters, filename)


    def carregarOps(self):
        filename, end = QtWidgets.QFileDialog.getOpenFileName(self, 'Carregar configuração',
                                    QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation),
                                    '*.json')

        if filename is not '':
            self.information = opt.loadConfigFile(filename)
            self.main_widget.layout().removeWidget(self.tabWidgetPlots)
            self.tabWidgetPlots.close()
            self.tabPresenters.clear()

            # Reinicializa tudo

            self.tabWidgetPlots = QtWidgets.QTabWidget(self)
            self.main_widget.layout().addWidget(self.tabWidgetPlots)

            nitems = sum([len(t.plots) for t in self.information])

            pgbar = QtWidgets.QProgressDialog('Carregando arquivo', '', 0, nitems, self)
            pgbar.setWindowTitle("Carregamento")
            pgbar.setWindowModality(QtCore.Qt.WindowModal)
            pgbar.setMinimumDuration(50)
            pgbar.setCancelButton(None)
            pgbar.show()

            idxpg = 0
            pgbar.setValue(idxpg)
            pgbar.show()

            QtCore.QCoreApplication.processEvents()

            for t in self.information:
                self.carregaTab(t)
                idxpg += 1
                pgbar.setValue(idxpg)
                pgbar.show()

            # print("Fim tab", time.strftime('%Y-%m-%d %H:%M:%S'))
            self.tabWidgetPlots.setCurrentIndex(0)
            self.tabWidgetPlots.currentChanged.connect(self.currentTabChanged)
            self.currentTabChanged(0)
            pgbar.close()


    def setConfigPlot(self, plotPresenter):
        self.widgetConfigPlot.setPlotPresenterToConfig(plotPresenter)

    def adicionarTab(self):
        self.carregaTab(opt.Tab(plots = [opt.Plot()]))
        self.tabWidgetPlots.setCurrentIndex(self.tabWidgetPlots.count() - 1)


    def removerTab(self):
        if self.tabWidgetPlots.count() <= 1:
            QtGui.QMessageBox.warning(self, 'Erro', 'Deve haver no mínimo uma tab aberta!')
            return

        currentTabIndex = self.tabWidgetPlots.currentIndex()
        currentTabPresenter = self.tabPresenters[currentTabIndex]

        for plotPresenter in currentTabPresenter.plotPresenters:
            currentTabPresenter.plotPresenters.remove(plotPresenter)
            currentTabPresenter.tabView.removeItem(plotPresenter.plotView.plot)
            self.destroiPlot(plotPresenter)

        self.tabPresenters.remove(currentTabPresenter)

        self.tabWidgetPlots.removeTab(currentTabIndex)
        currentTabPresenter.tabView.close()
        del currentTabPresenter.tabViewModel
        del currentTabPresenter


    def currentTabChanged(self, i):
        self.widgetConfigPlot.setPlotPresenterToConfig(self.tabPresenters[i].plotPresenters[0])

    def removerPlot(self, plotToRemove):
        if plotToRemove is None:
            return

        for tabPres in self.tabPresenters:
            if plotToRemove in tabPres.plotPresenters:
                if len(tabPres.plotPresenters) <= 1:
                    QtGui.QMessageBox.warning(self, 'Erro', 'Cada tab deve ter no mínimo um plot!')
                    return
                tabPres.plotPresenters.remove(plotToRemove)
                tabPres.tabView.removeItem(plotToRemove.plotView.plot)
                firstNewPlot = tabPres.plotPresenters[0]
                break


        self.widgetConfigPlot.setPlotPresenterToConfig(firstNewPlot)
        self.destroiPlot(plotToRemove)



    def destroiPlot(self, plotToRemove):
        plotToRemove.plotViewModel.dispose()
        plotToRemove.plotView.sigMouseClick.disconnect()
        plotToRemove.plotView.sigDoubleClick.disconnect()
        for pltItemPres in plotToRemove.plotItemPresenters:
            plotToRemove.removePlotItemPresenter(pltItemPres)

        # plotToRemove.plotView.plot.close()
        del plotToRemove.plotViewModel
        del plotToRemove.plotView
        del plotToRemove

    def adicionarPlot(self):
        currentTabIndex = self.tabWidgetPlots.currentIndex()
        if currentTabIndex < 0:
            return

        currentTabPresenter = self.tabPresenters[currentTabIndex]
        plot = opt.Plot()
        if not controller.varExists(plot.x.strVariavel):
            plot.x.strVariavel = self.header[0]
        p = processPlot(currentTabPresenter.tabView, plot)
        if currentTabPresenter.tabViewModel.sharex and len(currentTabPresenter.plotPresenters) > 0:
            p.plotViewModel.xVariavel = currentTabPresenter.plotPresenters[0].plotViewModel.xVariavel
            p.plotViewModel.xQuery = currentTabPresenter.plotPresenters[0].plotViewModel.xQuery
        currentTabPresenter.plotPresenters.append(p)
        currentTabPresenter.tabView.nextRow()

        p.plotView.plot.vb.menu.sigRemovePlot.connect(f.partial(self.removerPlot, p))
        p.plotView.plot.vb.menu.sigAddPlot.connect(f.partial(self.widgetConfigPlot.setPlotPresenterToConfig, p))
        p.plotView.sigMouseClick.connect(f.partial(self.setConfigPlot, p))
        p.plotView.sigDoubleClick.connect(self.widgetConfigPlot.activateWindow)
        p.plotViewModel.xVariavelBehavior.subscribe(f.partial(self.changeAllXVar, p, currentTabPresenter.plotPresenters, currentTabPresenter.tabViewModel))
        p.plotViewModel.xQueryBehavior.subscribe(f.partial(self.changeAllXQuery, p, currentTabPresenter.plotPresenters, currentTabPresenter.tabViewModel))
        currentTabPresenter.tabViewModel.sharex = currentTabPresenter.tabViewModel.sharex
        # currentTabPresenter.tabViewModel.sharex = !currentTabPresenter.tabViewModel.sharex



    def escolheArquivoAbrir(self):
        import time
        # Pensar em como fazer para receber vários arquivos como entrada
        arquivo = QtWidgets.QFileDialog.getOpenFileNames(self, u'Escolha o csv',
                                                    QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation),
                                                    '*.csv')
        if arquivo[0]:
            # print (arquivo)
            # Calcula dados da progressDialog
            if self.__firstFile__:
                nitems = sum([len(t.plots) for t in self.information])
            else:
                nitems = sum([len(t.plotPresenters) for t in self.tabPresenters])

            pgbar = QtWidgets.QProgressDialog('Carregando arquivo', '', 0, nitems + 1, self)
            pgbar.setWindowTitle("Carregamento")
            pgbar.setWindowModality(QtCore.Qt.WindowModal)
            pgbar.setMinimumDuration(50)
            pgbar.setCancelButton(None)
            pgbar.show()

            idxpg = 0
            pgbar.setValue(idxpg)
            pgbar.show()

            QtCore.QCoreApplication.processEvents()

            # print('Init', time.strftime('%Y-%m-%d %H:%M:%S'))
            res = "\n".join([controller.carregaArquivo(str(strfilename)) for strfilename in arquivo[0]])

            # # Coloca dados na listwidget
            # print('Arquivo', time.strftime('%Y-%m-%d %H:%M:%S'))
            self.header = controller.getHeader(arquivo) or list()

            PlotMenu.setXVarOptions(self.header)
            self.widgetConfigPlot.setXVarOptions(self.header)
            self.widgetConfigPlot.setViagensATR(controller.getInicioFimViagensATRparaASG(arquivo))
            self.widgetConfigPlot.setViagensASG(controller.getInicioFimViagensASGparaATR(arquivo))

            idxpg += 1
            pgbar.setValue(idxpg)
            pgbar.show()

            if self.__firstFile__:
                for t in self.information:
                    self.carregaTab(t)
                    idxpg += 1
                    pgbar.setValue(idxpg)
                    pgbar.show()

                # print("Fim tab", time.strftime('%Y-%m-%d %H:%M:%S'))
                self.tabWidgetPlots.setCurrentIndex(0)
                self.tabWidgetPlots.currentChanged.connect(self.currentTabChanged)
                self.currentTabChanged(0)

                QtGui.QAction.setEnabled(self.actAdicionarTab, True)
                QtGui.QAction.setEnabled(self.actAdicionarPlot, True)
                QtGui.QAction.setEnabled(self.actRemoverTab, True)
                QtGui.QAction.setEnabled(self.actSalvarOps, True)
                QtGui.QAction.setEnabled(self.actCarregarOps, True)

                self.widgetConfigPlot.setEnabled(True)
                self.__firstFile__ = False
            else:
                for tab in self.tabPresenters:
                    for plotPresenter in tab.plotPresenters:
                        plotPresenter.initData(None)
                        idxpg += 1
                        pgbar.setValue(idxpg)
                        pgbar.show()


            # idxpg += 1
            # pgbar.setValue(idxpg)
            pgbar.close()
            QtGui.QMessageBox.warning(self,'Carregamento do arquivo', res)
            self.widgetConfigPlot.show()
            self.widgetConfigPlot.activateWindow()
            self.widgetConfigPlot.setFocus()


        else:
            print('Operacao cancelada')

    def change_shareX(self, tab, i):
        tab.sharex = (i != 0)

    def changeSharing(self, plots, value):
        if len(plots) <= 1:
            return

        b, l = (True, plots[0].plotView.plot) if value else (False, None)

        for p in plots:
            p.plotView.shx = b
            p.plotView.plot.setXLink(l)

        currentTabIndex = self.tabWidgetPlots.currentIndex()
        currentTabPresenter = self.tabPresenters[currentTabIndex]

        self.changeAllXVar(plots[0], plots, currentTabPresenter.tabViewModel, plots[0].plotViewModel.xVariavel)
        self.changeAllXQuery(plots[0], plots, currentTabPresenter.tabViewModel, plots[0].plotViewModel.xQuery)

    def changeAllXVar(self, plotPresenter, plotPresenters, tabViewModel, xVar):
        if not tabViewModel.sharex:
            return

        for pltPres in plotPresenters:
            if pltPres.plotViewModel.xVariavel != xVar:
                pltPres.plotViewModel.xVariavel = xVar

    def changeAllXQuery(self, plotPresenter, plotPresenters, tabViewModel, xQuery):
        if not tabViewModel.sharex:
            return

        for pltPres in plotPresenters:
            if pltPres.plotViewModel.xQuery != xQuery:
                pltPres.plotViewModel.xQuery = xQuery



    def carregaTab(self, t):
        # print("No inicio")
        tbwidget = QtGui.QWidget(self)
        lay = QtGui.QVBoxLayout(tbwidget)
        toolbar = QtGui.QToolBar(self)
        lay.addWidget(toolbar)
        win = pg.GraphicsLayoutWidget(self)
        lay.addWidget(win)
        tbwidget.setLayout(lay)
        self.tabWidgetPlots.addTab(tbwidget, t.name)

        # print("No meio")
        plotPresenters = []
        for plot in t.plots:
            # print()
            # print('Plot' ,time.strftime('%Y:%m:%d %H:%M:%S'))
            p = processPlot(win, plot)
            if p is not None:
                plotPresenters.append(p)
                win.nextRow()

        # print("Carregou")
        tabVM = TabViewModel(t.share, t.maxPlots, t.name)


        def change_maxPlots(tab, val):
            # print(tab.maxPlots)
            tab.maxPlots = val


        chkBox = QtGui.QCheckBox('Compartilhar eixo X', toolbar)
        toolbar.addWidget(chkBox)
        toolbar.addSeparator()

        for plotPresenter in plotPresenters:
            plotPresenter.plotView.plot.vb.menu.sigRemovePlot.connect(f.partial(self.removerPlot, plotPresenter))
            plotPresenter.plotView.plot.vb.menu.sigAddPlot.connect(f.partial(self.widgetConfigPlot.setPlotPresenterToConfig, plotPresenter))
            plotPresenter.plotView.sigMouseClick.connect(f.partial(self.setConfigPlot, plotPresenter))
            plotPresenter.plotView.sigDoubleClick.connect(self.widgetConfigPlot.activateWindow)
            plotPresenter.plotViewModel.xVariavelBehavior.subscribe(f.partial(self.changeAllXVar, plotPresenter, plotPresenters, tabVM))
            plotPresenter.plotViewModel.xQueryBehavior.subscribe(f.partial(self.changeAllXQuery, plotPresenter, plotPresenters, tabVM))

        tabVM.nameBehavior.subscribe(f.partial(QtGui.QTabWidget.setTabText, self.tabWidgetPlots, self.tabWidgetPlots.count() - 1))

        self.tabPresenters.append(TabPresenter(win, tabVM, plotPresenters))
        tabVM.sharexBehavior.subscribe(chkBox.setChecked)
        tabVM.sharexBehavior.subscribe(f.partial(self.changeSharing, plotPresenters))
        chkBox.stateChanged.connect(f.partial(self.change_shareX, tabVM))

        if len(plotPresenters) == 0:
            self.tabWidgetPlots.setCurrentIndex(self.tabWidgetPlots.count() - 1)
            self.adicionarPlot()

    def closeEvent(self, evt):
        # print('close')
        hasToClose = True
        if len(self.tabPresenters) > 0:
            quit_msg = "Salvar configuração atual de plots?"
            reply = QtWidgets.QMessageBox.question(self, 'Salvar',
                             quit_msg,
                             QtWidgets.QMessageBox.Yes |  QtWidgets.QMessageBox.No |  QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Escape, 
                             QtWidgets.QMessageBox.Cancel)

            if reply ==  QtWidgets.QMessageBox.Yes:
                saveTabPresenters(self.tabPresenters, CONFIG_FILE)
            elif reply ==  QtWidgets.QMessageBox.No:
                pass
            else:
                hasToClose = False
        
        if hasToClose:
            self.widgetConfigPlot.close()
            evt.accept()
        else:
            evt.ignore()


def start():
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(int(start() or 0))

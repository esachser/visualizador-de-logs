# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QStyle
from PyQt5.QtCore import Qt
from view.pyqtCanvas import PlotPresenter, PlotViewModel
from options.info import PlotType
import functools as f
from PyQt5.QtWidgets import QWidget, QInputDialog
from PyQt5 import QtWidgets


class WidgetConfig(QtWidgets.QWidget):
	"""docstring for WidgetConfig"""
	sigRemovePlot = QtCore.pyqtSignal()

	def __init__(self, parent):
		super(WidgetConfig, self).__init__(parent)
		self.setWindowTitle("Configuração")
		vLayoutConfig = QtWidgets.QVBoxLayout()

		
		widgetXVar = QtWidgets.QWidget(self)
		widgetXVar.setLayout(QtWidgets.QHBoxLayout())
		widgetXVar.layout().addWidget(QtWidgets.QLabel('Variável X: '))
		self.xVarConfig = QtWidgets.QComboBox(self)
		widgetXVar.layout().addWidget(self.xVarConfig, stretch = 1)
		vLayoutConfig.addWidget(widgetXVar)

		# self.xVarConfig.setAutoCompletion(True)

		groupBoxXQuery = QtWidgets.QGroupBox('X Query', self)
		groupBoxXQuery.setLayout(QtWidgets.QVBoxLayout())

		self.xQueryConfig = QtWidgets.QLineEdit(self)
		groupBoxXQuery.layout().addWidget(self.xQueryConfig, stretch = 1)
		# vLayoutConfig.addWidget(widgetXQuery)

		vLayoutConfig.addWidget(groupBoxXQuery, stretch = 0)

		self.chkBoxGrid = QtWidgets.QCheckBox('Habilitar grid', self)
		vLayoutConfig.addWidget(self.chkBoxGrid)

		self.tabWidgetPlotItemConfig = QtWidgets.QTabWidget(self)
		vLayoutConfig.addWidget(self.tabWidgetPlotItemConfig, stretch = 1)

		# self.exportButton = QtWidgets.QPushButton('Exportar imagem')
		# self.addPlotButton = QtWidgets.QPushButton('Nova Curva')
		# self.removePlotButton = QtWidgets.QPushButton('Remover Gráfico')

		self.__plotTypes__ = ['Pontos', 'Linhas', 'Pontos + Linhas']
		self.__plotValues__ = [PlotType.SCATTERPLOT, PlotType.LINEPLOT, PlotType.ALL]

		self.setLayout(vLayoutConfig)
		self.plotViewModel = None
		self.__setXVar__ = False

	def setXVarOptions(self, values):
		self.__setXVar__ = True
		self.xVarConfig.clear()
		self.xVarConfig.addItems(values)
		self.__xVarValues__ = values
		if self.plotViewModel is not None:
			self.xVarConfig.setCurrentIndex(self.__xVarValues__.index(self.plotViewModel.xVariavel))
		self.__setXVar__ = False


	def setPlotPresenterToConfig(self, plotPresenter):
		isnull = self.plotViewModel
		if isnull is not None and hasattr(self.plotPresenter, "plotView"):
			self.plotPresenter.plotView.plot.setBorder(None)
		self.plotItemViewModelList = [plotItemPresenter.plotItemViewModel for plotItemPresenter in plotPresenter.plotItemPresenters]
		self.plotViewModel = plotPresenter.plotViewModel
		self.plotPresenter = plotPresenter
		if isnull is not None:
			self.xVarConfig.currentIndexChanged.disconnect()
			self.xQueryConfig.editingFinished.disconnect()
			self.chkBoxGrid.stateChanged.disconnect()

		self.xVarConfig.setCurrentIndex(self.__xVarValues__.index(self.plotViewModel.xVariavel))
		self.xQueryConfig.setText(self.plotViewModel.xQuery)
		self.chkBoxGrid.setChecked(self.plotViewModel.grid)
		self.plotPresenter.plotView.plot.setBorder(color='b', width=2, style=Qt.DashDotLine)
		self.startConfigOperations()
		self.resetTab()

	def startConfigOperations(self):
		if not hasattr(self, '__xVarValues__'):
			return

		def changeXVar(i):
			# print("Xvar")
			if not self.__setXVar__:
				self.plotViewModel.xVariavel = self.__xVarValues__[i]
		self.xVarConfig.currentIndexChanged.connect(changeXVar)
		
		def changeXQuery():
			# print("XQuery")
			self.plotViewModel.xQuery = self.xQueryConfig.text()
		self.xQueryConfig.editingFinished.connect(changeXQuery)
		
		def changeGrid(v):
			self.plotViewModel.grid = (v != 0)
		self.chkBoxGrid.stateChanged.connect(changeGrid)

	def resetTab(self):
		self.tabWidgetPlotItemConfig.clear()

		for plotItemVM in self.plotItemViewModelList:
			widgetPlotItem = QtWidgets.QWidget()
			widgetPlotItem.setLayout(QtWidgets.QVBoxLayout())

			widgetYVar = QtWidgets.QWidget(self)
			widgetYVar.setLayout(QtWidgets.QHBoxLayout())
			widgetYVar.layout().addWidget(QtWidgets.QLabel('Variável Y: '))
			yVarConfig = QtWidgets.QComboBox(self)
			yVarConfig.addItems(self.__xVarValues__)
			yVarConfig.setCurrentIndex(self.__xVarValues__.index(plotItemVM.strVariavel))
			def changeYVar(plotItemViewModel, i):
				plotItemViewModel.strVariavel = self.__xVarValues__[i]
				self.tabWidgetPlotItemConfig.setTabText(self.tabWidgetPlotItemConfig.currentIndex(), plotItemViewModel.strVariavel)
			yVarConfig.currentIndexChanged.connect(f.partial(changeYVar, plotItemVM))
			widgetYVar.layout().addWidget(yVarConfig)
			widgetPlotItem.layout().addWidget(widgetYVar)


			groupBoxYQuery = QtWidgets.QGroupBox('Y Query', self)
			groupBoxYQuery.setLayout(QtWidgets.QVBoxLayout())

			yQueryConfig = QtWidgets.QLineEdit(self)
			groupBoxYQuery.layout().addWidget(yQueryConfig, stretch = 1)

			def changeYQuery(plotItemViewModel, yQueryConfig):
				plotItemViewModel.strQuery = yQueryConfig.text()

			yQueryConfig.setText(plotItemVM.strQuery)

			yQueryConfig.editingFinished.connect(f.partial(changeYQuery, plotItemVM, yQueryConfig))

			widgetPlotItem.layout().addWidget(groupBoxYQuery, stretch = 1)

			chooseColorButton = QtWidgets.QPushButton('Escolher cor da curva')
			def repaint(plotItemViewModel, chooseColorButton):
				color = QtGui.QColor(plotItemViewModel.color[0], plotItemViewModel.color[1], plotItemViewModel.color[2])
				chooseColorButton.setStyleSheet("QWidget { background-color: %s}" % color.name())

			def chooseColor(plotItemViewModel, chooseColorButton):
				initialColor = QtGui.QColor(plotItemViewModel.color[0], plotItemViewModel.color[1], plotItemViewModel.color[2])
				color = QtGui.QColorDialog.getColor(initial = initialColor)
				if color.isValid():
					plotItemViewModel.color = [color.red(), color.green(), color.blue()]
					repaint(plotItemViewModel, chooseColorButton)

			repaint(plotItemVM, chooseColorButton)
			chooseColorButton.clicked.connect(f.partial(chooseColor, plotItemVM, chooseColorButton))

			widgetPlotItem.layout().addWidget(chooseColorButton)

			widgetPlotType = QtWidgets.QWidget(self)
			widgetPlotType.setLayout(QtWidgets.QHBoxLayout())
			widgetPlotType.layout().addWidget(QtWidgets.QLabel('Tipo de plot: '))
			plotTypeConfig = QtWidgets.QComboBox(self)
			plotTypeConfig.addItems(self.__plotTypes__)
			# plotTypeConfig.setCurrentIndex(self.__xVarValues__.index(plotItemVM.strVariavel))
			plotTypeConfig.setCurrentIndex(self.__plotValues__.index(plotItemVM.plotType))
			def changePlotType(plotItemViewModel, i):
				plotItemViewModel.plotType = self.__plotValues__[i]
			plotTypeConfig.currentIndexChanged.connect(f.partial(changePlotType, plotItemVM))
			widgetPlotType.layout().addWidget(plotTypeConfig, stretch = 1)
			widgetPlotItem.layout().addWidget(widgetPlotType)

			def removePlot(plotItemViewModel):
				pltItemPres = [plt for plt in filter(lambda plt: plt.plotItemViewModel == plotItemViewModel, self.plotPresenter.plotItemPresenters)][0]
				self.plotPresenter.removePlotItemPresenter(pltItemPres)
				self.setPlotPresenterToConfig(self.plotPresenter)
			
			removeButton = QtWidgets.QPushButton('Remover Curva')
			removeButton.clicked.connect(f.partial(removePlot, plotItemVM))

			widgetPlotItem.layout().addWidget(removeButton)

			self.tabWidgetPlotItemConfig.addTab(widgetPlotItem, plotItemVM.strVariavel)



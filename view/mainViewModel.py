# -*- coding: utf-8 -*-

from rx.subject import BehaviorSubject
import json

class TabPresenter:
	"""docstring for TabPresenter"""
	def __init__(self, tabView, tabViewModel, plotPresenters):
		self.tabView = tabView
		self.tabViewModel = tabViewModel
		self.plotPresenters = plotPresenters

	def dispose(self):
		self.tabViewModel.dispose()

	def toJSON(self):
		return {
			'sharex' : self.tabViewModel.sharex,
			'maxPlots' : self.tabViewModel.maxPlots,
			'name': self.tabViewModel.name,
			'plots' : [plotPres.toJSON() for plotPres in self.plotPresenters]
		}


def saveTabPresenters(tabPresenters, fileToSave):
	try:
		with open(fileToSave, 'w') as f:
			json.dump([tabPresenter.toJSON() for tabPresenter in tabPresenters], f, indent = True)
	except Exception:
		pass


class TabViewModel:
	"""Informação global da tab"""

	def __init__(self, share_x, max_plots, name):
		self.sharexBehavior = BehaviorSubject(share_x)
		self.maxPlotsBehavior = BehaviorSubject(max_plots)
		self.nameBehavior = BehaviorSubject(name)

	def dispose(self):
		self.sharexBehavior.dispose()
		self.maxPlotsBehavior.dispose()
		self.nameBehavior.dispose()


	def _get_sharex_(self):
		return self.sharexBehavior.value

	def _set_sharex_(self, s):
		self.sharexBehavior.on_next(s)

	sharex = property(_get_sharex_, _set_sharex_)

	def _get_maxPlots_(self):
		return self.maxPlotsBehavior.value

	def _set_maxPlots_(self, m):
		self.maxPlotsBehavior.on_next(m)

	maxPlots = property(_get_maxPlots_, _set_maxPlots_)

	def _get_name_(self):
		return self.nameBehavior.value

	def _set_name_(self, value):
		self.nameBehavior.on_next(value)

	name = property(_get_name_, _set_name_)

		
		



# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore

# Código para TabBar editavel
class TabBar(QtWidgets.QTabBar):
    
    sigChangeName = QtCore.pyqtSignal([int, 'QString'])

    def __init__(self, parent):
        QtWidgets.QTabBar.__init__(self, parent)
        self._editor = QtWidgets.QLineEdit(self)
        self._editor.setWindowFlags(QtCore.Qt.Popup)
        self._editor.setFocusProxy(self)
        self._editor.editingFinished.connect(self.handleEditingFinished)
        self._editor.installEventFilter(self)

    def eventFilter(self, widget, event):
        if ((event.type() == QtCore.QEvent.MouseButtonPress and
             not self._editor.geometry().contains(event.globalPos())) or
            (event.type() == QtCore.QEvent.KeyPress and
             event.key() == QtCore.Qt.Key_Escape)):
            self._editor.hide()
            return True
        return QtWidgets.QTabBar.eventFilter(self, widget, event)

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.editTab(index)

    def editTab(self, index):
        rect = self.tabRect(index)
        self._editor.setFixedSize(rect.size())
        self._editor.move(self.parent().mapToGlobal(rect.topLeft()))
        self._editor.setText(self.tabText(index))
        if not self._editor.isVisible():
            self._editor.show()

    def handleEditingFinished(self):
        index = self.currentIndex()
        if index >= 0:
            self._editor.hide()
            if self._editor.text() != self.tabText(index):
                self.setTabText(index, self._editor.text())
                self.sigChangeName.emit(index, self._editor.text())

class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.setTabBar(TabBar(self))
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtCore import Qt, pyqtSignature
from PyQt4.QtGui import QIcon, QPushButton, QTabWidget, QWidget

from profit.lib import Signals
from profit.widgets.accountdisplay import AccountDisplay
from profit.widgets.connectiondisplay import ConnectionDisplay
from profit.widgets.executionsdisplay import ExecutionsDisplay
from profit.widgets.messagedisplay import MessageDisplay
from profit.widgets.orderdisplay import OrderDisplay
from profit.widgets.plot import Plot
from profit.widgets.portfoliodisplay import PortfolioDisplay
from profit.widgets.tickerdisplay import TickerDisplay



def tabWidgetMethod(cls):
    def method(self, item):
        widget = cls(self.session, self)
        index = self.addTab(widget, item.text(0))
        self.setCurrentIndex(index)
        return index
    return method


class CloseTabButton(QPushButton):
    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)
        self.setIcon(QIcon(':images/icons/tab_remove.png'))
        self.setFlat(True)


class CentralTabs(QTabWidget):
    def __init__(self, parent=None):
        QTabWidget.__init__(self, parent)
        self.connect(self.window(), Signals.itemDoubleClicked,
                     self.on_itemClicked)
        self.session = None
        self.closeTabButton = closeTabButton = CloseTabButton(self)
        self.setCornerWidget(closeTabButton, Qt.TopRightCorner)
        connect = self.connect
        connect(closeTabButton, Signals.clicked, self.on_closeTabButton_clicked)
        connect(self, Signals.currentChanged, self.on_currentChanged)
        connect(self.window(), Signals.sessionCreated, self.on_created)

    def canClose(self, index):
        title = str(self.tabText(self.currentIndex()))
        if title in ('connection', ):
            if self.session and self.session.isConnected:
                return False
        return True

    def on_currentChanged(self, index):
        self.closeTabButton.setEnabled(self.canClose(index))

    def on_connectedTWS(self):
        self.on_currentChanged(self.currentIndex())

    def on_disconnectedTWS(self):
        self.closeTabButton.setEnabled(True)

    @pyqtSignature('')
    def on_closeTabButton_clicked(self):
        index = self.currentIndex()
        widget = self.widget(index)
        self.removeTab(index)
        widget.setAttribute(Qt.WA_DeleteOnClose)
        widget.close()

    def on_created(self, session):
        self.session = session
        connect = self.connect
        connect(session, Signals.connectedTWS, self.on_connectedTWS)
        connect(session, Signals.disconnectedTWS, self.on_disconnectedTWS)

    def on_itemClicked(self, item, col):
        value = str(item.text(0))
        try:
            call = getattr(self, 'on_%sClicked' % value.lower())
            index = call(item)
        except (AttributeError, TypeError, ), exc:
            print '## session item create exception:', exc
        else:
            self.setTabIcon(index, item.icon(0))

    def on_connectionClicked(self, item):
        items = [(str(self.tabText(i)), i) for i in range(self.count())]
        items = dict(items)
        text = str(item.text(0))
        if text in items:
            idx = items[text]
        else:
            idx = self.addTab(ConnectionDisplay(self.session, self), text)
        self.setCurrentIndex(idx)
        return idx

    on_accountClicked = tabWidgetMethod(AccountDisplay)
    on_executionsClicked = tabWidgetMethod(ExecutionsDisplay)
    on_messagesClicked = tabWidgetMethod(MessageDisplay)
    on_ordersClicked = tabWidgetMethod(OrderDisplay)
    on_portfolioClicked = tabWidgetMethod(PortfolioDisplay)

    def on_tickersClicked(self, item):
        widget = TickerDisplay(self.session, self)
        index = self.addTab(widget, item.text(0))
        self.setCurrentIndex(index)
        self.connect(widget, Signals.symbolPlotFull, self.on_symbolPlot)
        self.connect(widget, Signals.symbolPlotLine, self.on_symbolPlot)
        return index

    def on_symbolPlot(self, item, *args):
        symbol = str(item.text())
        tickerId = item.tickerId
        widget = Plot(self.session, symbol, tickerId, self, *args)
        index = self.addTab(widget, symbol)
        self.setTabIcon(index, item.icon())
        self.setCurrentIndex(index)
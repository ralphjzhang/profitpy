#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtGui import QFrame

from profit.widgets.ui_tradeindicator import Ui_TradeIndicatorDisplay


class TradeIndicatorDisplay(QFrame, Ui_TradeIndicatorDisplay):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)

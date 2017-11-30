#-*-coding:utf-8-*-
import sys,os
from PyQt4 import QtGui,Qt,QtCore
from PyQt4.QtCore import SIGNAL,QString
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

try:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
except ImportError:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
    
class MplCanvas(FigureCanvas):
    '''
        描述：将matplotlib的figure嵌入到Qt中
        成员：
        figure:画图的窗口，是matplotlib中的figure对象
        axes:画布，matplotlib.Axes对象
        方法：这些方法可以重新实现
        getSnn:返回画的曲线，是s11.s21,s12,或者s22
        getDrawedLineType:S,群时延
        getFigure: 返回figure对象
        使用：
                得到axes直接进行画图
    '''
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi) 
        self.axes = self.figure.add_subplot(111)
        self.axes.hold(False)
        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)

        FigureCanvas.updateGeometry(self)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.createPopMenu()

    def createPopMenu(self):
        #actions
        self.popmenu = QtGui.QMenu(self)
        self.snn_ac_group = QtGui.QActionGroup(self.popmenu)
        self.snn_ac_group.setExclusive(True)

        self.ac_s11 = QtGui.QAction('S11',self.popmenu)
        self.ac_s21 = QtGui.QAction('S21',self.popmenu)
        self.ac_s12 = QtGui.QAction('S12',self.popmenu)
        self.ac_s22 = QtGui.QAction('S22',self.popmenu)
        snn_actions = [self.ac_s11, self.ac_s21,
                       self.ac_s12, self.ac_s22]

        for ac in snn_actions:
            ac.setCheckable(True)
            self.snn_ac_group.addAction(ac)
        self.ac_s11.setChecked(True)
        self.popmenu.addActions(snn_actions)

        self.ac_delay = QtGui.QAction('show delay', self.popmenu)
        self.ac_phase = QtGui.QAction('show phase', self.popmenu)
        self.ac_expanded = QtGui.QAction('show expanded', self.popmenu)
        self.type_ac_group = QtGui.QActionGroup(self.popmenu)
        types_actions = [self.ac_delay, self.ac_phase,
                         self.ac_expanded]
        for ac in types_actions:
            ac.setCheckable(True)
            self.type_ac_group.addAction(ac)
        self.ac_phase.setChecked(True)
        self.popmenu.addActions(types_actions)
        self.setShowPopMenu(True)
    def setShowPopMenu(self,isShow):
        if isShow:
            self.connect(self,
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                    self.show_popmenu)
        else:
            self.disconnect(self,
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                    self.show_popmenu)

    def show_popmenu(self, pos):
        self.popmenu.popup(self.mapToGlobal(pos))

    def getSnn(self):
        snn =self.snn_ac_group.checkedAction().text()
        if snn == 'S11':
            return 1
        elif snn == 'S21':
            return 2
        elif snn == 'S12':
            return 3
        else:
            return 4

    def getDrawedLineType(self):
        linetype = self.type_ac_group.checkedAction().text()
        if linetype == 'show delay':
            return 'delay'
        elif linetype == 'show phase':
            return 'phase'
        elif linetype == 'show expanded':
            return 'expanded'

    def getFigure(self):
        return self.figure

if __name__ == '__main__':
    pass
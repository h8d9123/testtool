#-*-coding:utf-8-*-
import sys,os
from PyQt4 import QtGui,Qt,QtCore
import mplcanvas
class MainWindow(QtGui.QMainWindow):
    def __init__(self,parent = None):
        super(MainWindow, self).__init__(parent)
        self.setupUi()
    def setupUi(self):
        
        #设置中部显示区
        self.createMenu()
        self.centralWidget = QtGui.QFrame(self)
        self.centralWidget.setFrameStyle(QtGui.QFrame.Box|QtGui.QFrame.Raised)
        self.centralWidget.setLineWidth(1)
        vbox = QtGui.QVBoxLayout(self.centralWidget)
        self.setCentralWidget(self.centralWidget)
        self.mplwidget = mplcanvas.MplCanvas()
        vbox.addWidget(self.mplwidget)
        
        #创建下部的显示区
        self.dockWidgetDown = QtGui.QDockWidget(self)
        frame1 = QtGui.QFrame(self.dockWidgetDown)
        frame1.setFrameStyle(QtGui.QFrame.Box|QtGui.QFrame.Raised)
        frame1.setLineWidth(1)
        self.dockWidgetDown.setWidget(frame1)
        hbox_state = QtGui.QHBoxLayout(frame1)
        self.stateDialog = QtGui.QDialog()
        hbox_state.addWidget(self.stateDialog)
        self.dockWidgetDown.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(QtCore.Qt.BottomDockWidgetArea), self.dockWidgetDown)
        
        #创建右部的设置区域
        self.dockWidgetRight = QtGui.QDockWidget(self)
        frame1 = QtGui.QFrame(self.dockWidgetRight)
        frame1.setFrameStyle(QtGui.QFrame.Box|QtGui.QFrame.Raised)
        frame1.setLineWidth(1)
        self.dockWidgetRight.setWidget(frame1)
        hbox_control = QtGui.QHBoxLayout(frame1)
        self.controlDialog = QtGui.QDialog()
        hbox_control.addWidget(self.controlDialog)
        self.dockWidgetDown.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(QtCore.Qt.RightDockWidgetArea), self.dockWidgetRight)
        
        pass
    def createMenu(self):
        self.createAction()
        self.filemenu = self.menuBar().addMenu('&File')
        self.toolMenu = self.menuBar().addMenu('&Tool')
        
        acts = [self.openAct, self.SaveAct]
        for act in acts:
            self.filemenu.addAction(act)
    
        acts = [self.plotAct, self.showSpec]
        for act in acts:
            self.toolMenu.addAction(act)
        pass
    def createAction(self):
        self.openAct = QtGui.QAction('&Open', self)
        self.SaveAct = QtGui.QAction('&Save', self)
        
        self.plotAct = QtGui.QAction('&Plot', self)
        
        self.showSpec = QtGui.QAction('Show Spec',self)
        pass
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dlg = MainWindow()
    dlg.show()
    sys.exit(app.exec_())
    
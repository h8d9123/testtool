#-*-coding:utf-8-*-
import sys,os
from PyQt4 import QtGui,Qt,QtCore
import mplcanvas
import wr34dialogs
import connectdialog
import logging
from resource import icon_rc,icons
import processwr34

class MainWindow(QtGui.QMainWindow):
    def __init__(self,parent = None):
        super(MainWindow, self).__init__(parent)
        self.connector = None
        self.cf_bw = None
        self.ch_J = None
        self.setupUi()
        self.connectInit()
    def setupUi(self):
        
        #设置中部显示区
        self.createMenu()
        self.createToolBar()
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
        vbox_state = QtGui.QVBoxLayout(frame1)
        self.tabWnd = QtGui.QTabWidget()
        self.specWnd = QtGui.QTextEdit()
        self.tabWnd.addTab(self.specWnd, "Spec")
        vbox_state.addWidget(self.tabWnd)
        
        self.dockWidgetDown.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(QtCore.Qt.BottomDockWidgetArea), self.dockWidgetDown)
        
        #创建右部的设置区域
        self.dockWidgetRight = QtGui.QDockWidget(self)
        frame1 = QtGui.QFrame(self.dockWidgetRight)
        frame1.setFrameStyle(QtGui.QFrame.Box|QtGui.QFrame.Raised)
        frame1.setLineWidth(1)
        self.dockWidgetRight.setWidget(frame1)
        vbox_control = QtGui.QVBoxLayout(frame1)
        self.controlDialog = wr34dialogs.QWR34SaveDialog(self)
        vbox_control.addWidget(self.controlDialog)
        vbox_control.addStretch()
        self.dockWidgetDown.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(QtCore.Qt.RightDockWidgetArea), self.dockWidgetRight)
        
        pass
    def createMenu(self):
        self.createAction()
        self.filemenu = self.menuBar().addMenu('&File')
        self.toolMenu = self.menuBar().addMenu('&Tool')
        self.graphMenu = self.menuBar().addMenu('Graph')
        
        acts = [self.actOpen, self.actSave,self.actConnect, self.actDisConnect]
        for act in acts:
            self.filemenu.addAction(act)
    
        acts = [self.actPlot]
        for act in acts:
            self.toolMenu.addAction(act)
        acts = [self.homeAct,self.backAct, self.upAct, self.downAct, self.nextAct, self.zoomInAct, 
                self.zoomOutAct,self.lineAct,self.savePicAct, self.panAct]
        for act in acts:
            self.graphMenu.addAction(act)
        pass
    
    def createAction(self):
        self.actOpen = QtGui.QAction(QtGui.QIcon(':/images/open.png'),'&Open', self,triggered=self.onActOpenTriggered)
        self.actSave = QtGui.QAction(QtGui.QIcon(':/images/save.png'),'&Save', self,triggered=self.onActSaveTriggered)
        
        self.actPlot = QtGui.QAction(QtGui.QIcon(":/icon/Graph.png"),'&Plot', self,triggered=self.onActPlotTriggered)
        self.backAct = QtGui.QAction(QtGui.QIcon(":/icon/Back.png"), '&Back',self)
        self.upAct = QtGui.QAction(QtGui.QIcon(":/icon/Up.png"), '&Up',self)
        self.downAct = QtGui.QAction(QtGui.QIcon(":/icon/Down.png"), '&Down',self)
        self.nextAct = QtGui.QAction(QtGui.QIcon(":/icon/Next.png"), '&Next',self)
        self.zoomInAct = QtGui.QAction(QtGui.QIcon(":/icon/Zoom_In.png"), '&Zoom In',self)
        self.zoomOutAct = QtGui.QAction(QtGui.QIcon(":/icon/Zoom_Out.png"), '&Zoom Out',self)
        
        self.homeAct = QtGui.QAction(QtGui.QIcon(":/icon/home.png"), '&Home',self)
        self.borderAct = QtGui.QAction(QtGui.QIcon(":/icon/border.png"), '&Range',self)
        self.lineAct = QtGui.QAction(QtGui.QIcon(":/icon/line.png"), '&Lines',self)
        self.savePicAct = QtGui.QAction(QtGui.QIcon(":/icon/savepic.png"), '&Save Picture',self)
        self.panAct = QtGui.QAction(QtGui.QIcon(":/icon/pan.png"), '&Pan',self)
        
        self.actShowSpec = QtGui.QAction('Show Spec',self,triggered=self.onActShowSpecTriggered)
        self.actConnect = QtGui.QAction(QtGui.QIcon(':/images/connect.png'),'Connect',self,triggered=self.onActConnectTriggered)
        self.actDisConnect = QtGui.QAction(QtGui.QIcon(':/images/disconnect.png'),'Disconnect',self,triggered=self.onActDisconnectTriggered)
        pass
    def createToolBar(self):
        fileBar = self.addToolBar("File")
        toolBar = self.addToolBar("Tool")
        graphBar = self.addToolBar("Graph")
        acts = [self.actOpen, self.actSave,self.actConnect, self.actDisConnect]
        for act in acts:
            fileBar.addAction(act)
        acts = [self.actPlot]
        for act in acts:
            toolBar.addAction(act)
        acts = [self.homeAct,self.backAct, self.upAct, self.downAct, self.nextAct, self.zoomInAct, 
                self.zoomOutAct,self.lineAct,self.savePicAct, self.panAct]
        for act in acts:
            graphBar.addAction(act)
        pass
    
    def connectInit(self):
        toolbar = self.mplwidget.toolbar
        self.zoomInAct.triggered.connect(toolbar.zoom)
        self.backAct.triggered.connect(toolbar.back)
        self.nextAct.triggered.connect(toolbar.forward)
        self.homeAct.triggered.connect(toolbar.home)
        self.borderAct.triggered.connect(toolbar.configure_subplots)
        self.savePicAct.triggered.connect(toolbar.save_figure)
        self.panAct.triggered.connect(toolbar.pan)
        self.lineAct.triggered.connect(toolbar.edit_parameters)
    def onActOpenTriggered(self):
        inputdir = r'.\db'
        if not os.path.exists(os.path.abspath(inputdir)):
            inputdir = '..\db'
        excelName = str(QtGui.QFileDialog.getOpenFileName(None, caption='Open',directory = inputdir, filter='excel(*.xlsx)'))
        if len(excelName) != 0:
            self.cf_bw = processwr34.getInputFrequency(excelName)
            self.ch_J = processwr34.getchAndJIndex(excelName)
    def getCFBW(self):
        if self.cf_bw != None:
            return self.cf_bw
    def getCHAndJIndex(self):
        if self.ch_J is not None:
            return self.ch_J
    def onActSaveTriggered(self):
        pass
    
    def onActPlotTriggered(self):
        dlg = wr34dialogs.QWR34PlotDialog(self)
        dlg.show()
        dlg.exec_()
        
    def getMplCanvas(self):
        return self.mplwidget
    
    def getConnector(self):
        return self.connector
    
    def onActShowSpecTriggered(self):
        pass
    
    def onActConnectTriggered(self):
        ipConfigDlg = connectdialog.QIPConfigDialog(self)
        ipConfigDlg.setModal(True)
        ipConfigDlg.show()
        if ipConfigDlg.exec_() == QtGui.QDialog.Accepted:
            self.connector = ipConfigDlg.getConnector()
            
    def onActDisconnectTriggered(self):
        # disconnect from an instrument
        if self.connector:
            self.connector.close()
            logging.info('disconnected the instrument')
    
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dlg = MainWindow()
    dlg.show()
    sys.exit(app.exec_())
    
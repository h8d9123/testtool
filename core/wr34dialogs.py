#-*-coding:utf-8-*-
import os, sys
from PyQt4 import QtGui,QtCore,Qt
from PyQt4.QtCore import QString
import logging
import processs2p
import numpy as np
def formatS2pName(chanel, temparature):
    return 'T_%s_%s.s2p'%(temparature,chanel)

class QWR34SaveDialog(QtGui.QWidget):
    NOCHOOSEDIRECTORY = 0
    NOCONNECTINSTRUMENT = 1
    def __init__(self, parent = None):
        super(self.__class__, self).__init__(parent)
        self.chanelCount = 8
        self.temparatureCount = 3
        self.temparatures=[ '-20', '25', '60']
        self.setupUI()
    def setupUI(self):
        self.setWindowTitle('WR34')
        hbox_dirName = QtGui.QHBoxLayout()
        hbox_dirName.addWidget(QtGui.QLabel("S2p Dir:"))
        self.le_dirName = QtGui.QLineEdit('')
        self.btn_chooseDir = QtGui.QPushButton("Choose")
        hbox_dirName.addWidget(self.le_dirName)
        hbox_dirName.addWidget(self.btn_chooseDir)
        #choose chanel
        rb_chanels = [QtGui.QRadioButton('ch_%s'%(i+1)) for i in range(self.chanelCount)]
        grid_chanels = QtGui.QGridLayout()
        self.btngroup_chanel = QtGui.QButtonGroup()
        for i in range(self.chanelCount):
            grid_chanels.addWidget(rb_chanels[i], int(i/4+1), i%4)
            rb_chanels[i].setCheckable(True)
            rb_chanels[i].clicked.connect(self.onRadioBtnChanelClicked)
            self.btngroup_chanel.addButton(rb_chanels[i])
        rb_chanels[0].setChecked(True)
        
        gbox_chanels = QtGui.QGroupBox('Chanel')
        gbox_chanels.setLayout(grid_chanels)
        
        rb_temparature = [QtGui.QRadioButton(self.temparatures[i]) for i in range(self.temparatureCount)]
        hbox_temparature = QtGui.QHBoxLayout()
        self.btngroup_temparature = QtGui.QButtonGroup()
        for i in range(self.temparatureCount):
            hbox_temparature.addWidget(rb_temparature[i])
            rb_temparature[i].setCheckable(True)
            rb_temparature[i].clicked.connect(self.onRadioBtnTemparatureClicked)
            self.btngroup_temparature.addButton(rb_temparature[i])
        rb_temparature[1].setChecked(True)
        gbox_temparature = QtGui.QGroupBox()
        gbox_temparature.setLayout(hbox_temparature)
        
        hbox_saveS2p = QtGui.QHBoxLayout()
        hbox_saveS2p.addWidget(QtGui.QLabel("S2p Name:"))
        self.le_s2pName = QtGui.QLineEdit('')
        self.btn_saveS2p = QtGui.QPushButton("Save")
        hbox_saveS2p.addWidget(self.le_s2pName)
        hbox_saveS2p.addWidget(self.btn_saveS2p)
        
        
        vbox = QtGui.QVBoxLayout(self)
        vbox.addLayout(hbox_dirName)
        vbox.addWidget(gbox_chanels)
        vbox.addWidget(gbox_temparature)
        vbox.addLayout(hbox_saveS2p)
        
        self.connectInit()#binds signal and callback functions
        self.onRadioBtnChanelClicked()
    def connectInit(self):
        self.btn_chooseDir.clicked.connect(self.onBtnChooseClicked)
        self.btn_saveS2p.clicked.connect(self.onBtnSaveClicked)
    def onBtnSaveClicked(self):
        self.connector = self.parent().getConnector() if self.parent() else None
        if self.connector==None:
            self.showError(self.NOCONNECTINSTRUMENT)
            return
        
        dirName = str(self.le_dirName.text())
        if len(dirName)=='0':
            self.showError(self.NOCHOOSEDIRECTORY)
            return
        self.onRadioBtnChanelClicked()
        s2pName = self.le_s2pName
        s2pPath = os.path.join(dirName,s2pName)
        
    
        if s2pName in os.listdir(self.template_dir):
            flag = QtGui.QMessageBox.question(None, "?", "overwrite %s"%s2pName, buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if flag != QtGui.QMessageBox.Yes:
                return
        tmpfile = self.connector.recvs2p()
        if tmpfile is None:
            return
        with open(s2pPath,'w') as fid:
            fid.write(tmpfile)
            fid.close()
            logging.info('the %s was stored'%(s2pName))

    def onBtnChooseClicked(self):
        workdir = str(QtGui.QFileDialog.getExistingDirectory(parent=None, caption=QString("Choose a directory saving S2ps")))
        if len(workdir) != 0:
            self.le_dirName.setText(workdir)
            
    def onRadioBtnChanelClicked(self):
        chanel = self.btngroup_chanel.checkedButton().text()
        temparature = self.btngroup_temparature.checkedButton().text()
        s2pName = formatS2pName(chanel, temparature)
        self.le_s2pName.setText(s2pName)
        
    def onRadioBtnTemparatureClicked(self):
        self.onRadioBtnChanelClicked()
        
    def showError(self, errNum):
        msg={}
        msg[self.NOCHOOSEDIRECTORY]="please choose a directory firstly"
        msg[self.NOCONNECTINSTRUMENT]='"please connect instrument"'
        QtGui.QMessageBox.information(self, "Tips", msg[errNum])
        
class QWR34PlotDialog(QtGui.QDialog):
    NOCHOOSEDIRECTORY = 0
    DIRECTORYNOTVALID = 1
    S2PFILENOTEXIST = 2
    def __init__(self, parent = None):
        super(self.__class__, self).__init__(parent)
        self.chanelCount = 8
        self.temparatureCount = 3
        self.snnName = ['S11','S21','S12','S22']
        self.temparatures=[ '-20', '25', '60']
        self.snnColor = ['black','blue','green','red']
        self.linemarker = ['-.','-','--']
        self.lineType = ['S', 'Group delay']
        self.dirName = None
        self.setupUI()
        isDebug = True
        self.cf_bw = False
        self.selectedTemparatures = None
        self.selectedChanels = None
        isDebug=True
        if isDebug:
            self.qadir=os.path.abspath(r'..\qa\WR34NewFltnew')
        else:
            self.qadir = '.'
            
    def setupUI(self):
        self.setWindowTitle('WR34')
        hbox_dirName = QtGui.QHBoxLayout()
        hbox_dirName.addWidget(QtGui.QLabel("S2p Dir:"))
        self.le_dirName = QtGui.QLineEdit('')
        self.btn_chooseDir = QtGui.QPushButton("Choose")
        hbox_dirName.addWidget(self.le_dirName)
        hbox_dirName.addWidget(self.btn_chooseDir)
        #choose chanel
        cb_chanels = [QtGui.QCheckBox('ch_%s'%(i+1)) for i in range(self.chanelCount)]
        grid_chanels = QtGui.QGridLayout()
        self.btngroup_chanel = QtGui.QButtonGroup()
        self.btngroup_chanel.setExclusive(False)
        for i in range(self.chanelCount):
            grid_chanels.addWidget(cb_chanels[i], int(i/4+1), i%4)
            cb_chanels[i].setCheckable(True)
            cb_chanels[i].clicked.connect(self.onCheckBtnChanelClicked)
            self.btngroup_chanel.addButton(cb_chanels[i])
        cb_chanels[0].setChecked(True)
        
        gbox_chanels = QtGui.QGroupBox('Chanel')
        gbox_chanels.setLayout(grid_chanels)
        
        cb_temparature = [QtGui.QCheckBox(self.temparatures[i]) for i in range(self.temparatureCount)]
        hbox_temparature = QtGui.QHBoxLayout()
        self.btngroup_temparature = QtGui.QButtonGroup()
        self.btngroup_temparature.setExclusive(False)
        for i in range(self.temparatureCount):
            hbox_temparature.addWidget(cb_temparature[i])
            cb_temparature[i].setCheckable(True)
            cb_temparature[i].clicked.connect(self.onCheckBtnTemparatureClicked)
            self.btngroup_temparature.addButton(cb_temparature[i])
        cb_temparature[1].setChecked(True)
        gbox_temparature = QtGui.QGroupBox('Temparature')
        gbox_temparature.setLayout(hbox_temparature)
        
        cb_snn = [QtGui.QCheckBox(v) for v in self.snnName]
        hbox_snn= QtGui.QHBoxLayout()
        self.btngroup_snn = QtGui.QButtonGroup()
        self.btngroup_snn.setExclusive(False)
        for i in range(len(self.snnName)):
            hbox_snn.addWidget(cb_snn[i])
            cb_snn[i].setCheckable(True)
            cb_snn[i].clicked.connect(self.onCheckBtnSnnClicked)
            self.btngroup_snn.addButton(cb_snn[i])
        cb_snn[0].setChecked(True)
        gbox_snn = QtGui.QGroupBox('S parameter')
        gbox_snn.setLayout(hbox_snn)
        
        rb_lineType = [QtGui.QRadioButton(v) for v in self.lineType]
        hbox_lineType = QtGui.QHBoxLayout()
        self.btngroup_lineType = QtGui.QButtonGroup()
        for i in range(len(self.lineType)):
            hbox_lineType.addWidget(rb_lineType[i])
            rb_lineType[i].setCheckable(True)
            rb_lineType[i].clicked.connect(self.onRadioBtnLineTypeClicked)
            self.btngroup_lineType.addButton(rb_lineType[i])
        rb_lineType[0].setChecked(True)
        gbox_lineType = QtGui.QGroupBox('Line Type')
        gbox_lineType.setLayout(hbox_lineType)
        
        vbox = QtGui.QVBoxLayout(self)
        vbox.addLayout(hbox_dirName)
        vbox.addWidget(gbox_chanels)
        vbox.addWidget(gbox_temparature)
        vbox.addWidget(gbox_snn)
        vbox.addWidget(gbox_lineType)
        
        
        self.connectInit()#binds signal and callback functions
        #self.onCheckBtnChanelClicked()
    def connectInit(self):
        self.btn_chooseDir.clicked.connect(self.onBtnChooseClicked)
        
    

    def onBtnChooseClicked(self):
        workdir = str(QtGui.QFileDialog.getExistingDirectory(parent=None, 
                                                             caption=QString("Choose a directory saving S2ps"),
                                                             directory = self.qadir))
        if len(workdir) != 0:
            self.le_dirName.setText(workdir)
            
    def onCheckBtnChanelClicked(self):
        self.selectedChanels = [str(btn.text()) for btn in self.btngroup_chanel.buttons() if btn.isChecked()]
        self.mydraw()
        
    def onCheckBtnSnnClicked(self):
        self.selectedSnn = [str(btn.text()) for btn in self.btngroup_snn.buttons() if btn.isChecked()]
        self.mydraw()
        
    def onCheckBtnTemparatureClicked(self):
        self.selectedTemparatures = [str(btn.text()) for btn in self.btngroup_temparature.buttons() if btn.isChecked()]
        self.mydraw()
        
    def onRadioBtnLineTypeClicked(self):
        self.ltype = str(self.btngroup_lineType.checkedButton().text())
        self.mydraw()
        
    def showError(self, errNum):
        msg={}
        msg[self.NOCHOOSEDIRECTORY]="please choose a directory firstly."
        msg[self.DIRECTORYNOTVALID] = "directory is not valid!"
        msg[self.S2PFILENOTEXIST] = "s2p file does not exist!"
        QtGui.QMessageBox.information(self, "Tips", msg[errNum])

    def mydraw(self):
        if self.parent() is None:
            return
        self.axes = self.parent().getMplCanvas().axes if self.parent() else None
        self.updatedata()
        self.cf_bw = self.parent().getCFBW()
        if not self.axes: 
            
            return
        self.axes.clear()
        
        fNames = []
        self.workdir = str(self.le_dirName.text())
        if not os.path.exists(self.workdir):
            self.showError(self.DIRECTORYNOTVALID)
            return
     
        for ch in self.selectedChanels:
            for t in self.selectedTemparatures:
                fNames.append(os.path.join(self.workdir, formatS2pName(ch, t)))
                if not os.path.exists(fNames[-1]):
                    print fNames[-1]
                    self.showError(self.S2PFILENOTEXIST)
                    return
      
        for fname in fNames:
            for snn in self.selectedSnn:
                idx = self.selectedSnn.index(snn)+1
                #range should be given
                if self.ltype == 'S':
                    self.plotS(self.axes,idx,fname)
                if self.ltype == 'Group delay':
                    self.plotGroupDelay(self.axes, idx, fname)
                self.axes.hold(True)
        self.parent().getMplCanvas().draw()
                    
    def plotS(self, axes, idx, fname):
        print fname
        idxMarker = 0
        for i in range(len(self.temparatures)):
            if self.temparatures[i] in fname:
                idxMarker = i
        s2p = processs2p.ReadS2p(fname)
        freq = np.real(s2p[:, 0])
        print idx
        axes.plot(freq, 20*np.log10(np.abs(s2p[:,idx])),color=self.snnColor[idx-1],
                  linestyle=self.linemarker[idxMarker])
        pass
    
    def plotGroupDelay(self,axes, idx, fname):
        pass
    
    def updatedata(self):
        self.selectedChanels = [str(btn.text()) for btn in self.btngroup_chanel.buttons() if btn.isChecked()]
        self.selectedSnn = [str(btn.text()) for btn in self.btngroup_snn.buttons() if btn.isChecked()]
        self.selectedTemparatures = [str(btn.text()) for btn in self.btngroup_temparature.buttons() if btn.isChecked()]
        self.ltype = str(self.btngroup_lineType.checkedButton().text())
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dlg = QWR34PlotDialog()
    dlg.show()
    sys.exit(app.exec_())
    pass
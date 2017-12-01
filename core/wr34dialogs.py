#-*-coding:utf-8-*-
import os, sys
from PyQt4 import QtGui,QtCore,Qt
from PyQt4.QtCore import QString
import logging
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
        rb_chanels = [QtGui.QRadioButton('ch%s'%(i+1)) for i in range(self.chanelCount)]
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
        self.connector = self.parent().connector if self.parent() else None
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
        s2pName = 'T_%s_%s.s2p'%(temparature,chanel)
        self.le_s2pName.setText(s2pName)
        
    def onRadioBtnTemparatureClicked(self):
        self.onRadioBtnChanelClicked()
        
    def showError(self, errNum):
        msg={}
        msg[self.NOCHOOSEDIRECTORY]="please choose a directory firstly"
        msg[self.NOCONNECTINSTRUMENT]='"please connect instrument"'
        QtGui.QMessageBox.information(self, "Tips", msg[errNum])
        
            

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dlg = QWR34SaveDialog()
    dlg.show()
    sys.exit(app.exec_())
    pass
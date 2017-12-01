import os, sys
from PyQt4 import QtGui,QtCore,Qt
from PyQt4.QtCore import QString
import logging
import instrument_io
class RegValidator(object):
    '''
    description: offers some Validators, which can limit the inputed string
    '''
    def get_freq_validator(self):
        '''
        Return: a QRegExpValidator. the valid string :number + unit, unit cantains
                'GHZ,KHZ,MHZ,HZ', ignores case sensitivity
                eg. 1khz,1KHz
        '''
        freq_pattern = r'^\d+\.?\d*((GHZ)|(MHZ)|(KHZ)|(HZ))$'
        reg1 = QtCore.QRegExp(freq_pattern, 0)
        return QtGui.QRegExpValidator(reg1)
    @staticmethod
    def get_ip_validator():
        ip_pattern = r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))'
        reg1 = QtCore.QRegExp(ip_pattern)
        return QtGui.QRegExpValidator(reg1)

class QIPConfigDialog(QtGui.QDialog):
    def __init__(self,parent = None):
        super(self.__class__, self).__init__(parent)
        self.setWindowTitle("IP Config")
        
        gbox_gpib_socket = QtGui.QGroupBox('TYPE')
        hbox_gpib_socket = QtGui.QHBoxLayout(gbox_gpib_socket)
        self.rb_socket = QtGui.QRadioButton('TCPIP')
        self.rb_gpib = QtGui.QRadioButton('GPIB')
        hbox_gpib_socket.addWidget(self.rb_socket)
        self.rb_socket.setCheckable(True)
        self.rb_socket.setCheckable(True)
        hbox_gpib_socket.addWidget(self.rb_gpib)
        gbox_gpib_socket.setLayout(hbox_gpib_socket)
        
        hbox_gpib = QtGui.QHBoxLayout()
        hbox_gpib.addWidget(QtGui.QLabel("GPIB:"))
        self.cbx_gpibAddress = QtGui.QComboBox()
        hbox_gpib.addWidget(self.cbx_gpibAddress)
        
        self.ipLabel   = QtGui.QLabel("IP  :")
        self.portLabel = QtGui.QLabel("Port:")
        self.ip = QtGui.QLineEdit(self)
        self.port = QtGui.QLineEdit(self)
        self.buttonConnect = QtGui.QPushButton('Connect', self)
        self.buttonConnect.clicked.connect(self.handleConnect)

        layout = QtGui.QGridLayout()
        layout.addWidget(self.ipLabel, 0, 0)
        layout.addWidget(self.ip, 0, 1)
        layout.addWidget(self.portLabel, 1, 0)
        layout.addWidget(self.port, 1, 1)
        layout.addWidget(self.buttonConnect, 2, 1)
        self.lb_state = QtGui.QLabel("")
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(gbox_gpib_socket)
        vbox.addLayout(hbox_gpib)
        vbox.addLayout(layout)
        vbox.addWidget(self.lb_state)

        self.ip.setValidator(RegValidator.get_ip_validator())
        self.port.setValidator(QtGui.QIntValidator())

        settings = QtCore.QSettings("XIM", "CATS")
        ips = settings.beginReadArray("ips")
        self.historyIPs = []
        for i in range(ips):
            settings.setArrayIndex(i)
            ip = settings.value('ip').toString()
            port = settings.value('port').toString()
            self.historyIPs.append((ip, port))

        settings.endArray()

        logging.debug('historyIPs %s', self.historyIPs)
        if len(self.historyIPs) > 0:
            (self.ipAddress, self.portNum) = self.historyIPs[0]
        else:
            self.ipAddress = '192.168.1.250'
            self.portNum = 5001

        logging.debug('ip %s port %d'%(self.ipAddress, int(self.portNum)))

        if len(self.historyIPs) > 0:
            completer = QtGui.QCompleter()
            self.ip.setCompleter(completer)
            ipModel = QtGui.QStringListModel()
            ipModel.setStringList([str(item[0]) for item in self.historyIPs])
            completer.setModel(ipModel)

        self.ip.setText(self.ipAddress)
        self.port.setText('%s'%self.portNum)
        self.compoentInit()
    def compoentInit(self):
        
        self.rb_socket.setChecked(True)
        #rm = visa.ResourceManager()
        #insts = rm.list_resources()
        #self.cbx_gpibAddress.addItems(insts)
        self.rb_socket.clicked.connect(self.on_rb_socket_clicked)
        #self.rb_gpib.clicked.connect(self.on_rb_gpib_clicked)
        self.on_rb_socket_clicked()
    def on_rb_socket_clicked(self):
        if self.rb_socket.isChecked():
            self.ip.setEnabled(True)
            self.port.setEnabled(True)
            self.cbx_gpibAddress.setEnabled(False)
            
    def on_rb_gpib_clicked(self):
        if self.rb_gpib.isChecked():
            self.ip.setEnabled(False)
            self.port.setEnabled(False)
            self.cbx_gpibAddress.setEnabled(True)


    def handleConnect(self):
        self.ipAddress = self.ip.text()
        self.portNum = int(self.port.text())

        logging.info('Connecting to %s:%d'%(self.ipAddress, self.portNum))
        
        
        if self.rb_socket.isChecked():
            #self.connector = SCPIConnector.SCPIConnector(self.ipAddress, self.portNum)
            self.connector = instrument_io.SCPIConnector(self.ipAddress, self.portNum)
            if self.connector.isConnected():
                logging.info('Connect successfully done')
                settings = QtCore.QSettings("XIM", "CATS")
                settings.beginWriteArray("ips")
                settings.setArrayIndex(0)
                logging.debug('setting %s %d'%(self.ipAddress, self.portNum))
                settings.setValue('ip', self.ipAddress)
                settings.setValue('port', str(self.portNum))
    
                i = 1
                for ip,port in self.historyIPs:
                    if ip == self.ipAddress and port == str(self.portNum):
                        continue
                    settings.setArrayIndex(i)
                    settings.setValue('ip', ip)
                    settings.setValue('port', port)
                    i += 1
    
                settings.endArray()
    
                self.accept()
            else:
                QtGui.QMessageBox.warning(self, 'Error', 'Connection failed, please check the IP/Port setting')
        if self.connector.isConnected():
            self.lb_state.setText('OK')
        else:
            self.lb_state.setText('False')
    def getConnector(self):
        return self.connector
if __name__ =='__main__':
    app = QtGui.QApplication(sys.argv)
    dlg = QIPConfigDialog()
    dlg.show()
    sys.exit(app.exec_())
    pass
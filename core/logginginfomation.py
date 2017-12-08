#-*-coding:utf-8-*-
import logging
from PyQt4 import QtCore,QtGui
class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super(self.__class__, self).__init__()
        self.widget = QtGui.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class StateDialog(QtGui.QDialog, QPlainTextEditLogger):
    def __init__(self, parent = None):
        super(StateDialog, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle('Debugging State')

        logTextBox = QPlainTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logTextBox.setLevel(logging.INFO)
        #
        '''
        fh = logging.FileHandler('main.log.bz2', encoding='bz2')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(fh)
        '''
        logging.getLogger().setLevel(logging.DEBUG)
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(logTextBox.widget)


if __name__ == '__main__':
    pass
#coding=utf-8
import socket
import time
import logging
import platform

class SCPIConnector(object):
    def __init__(self,address,port,connect_type='TCPIP'):
        self.type = connect_type
        self.address = address
        self.port = port
        self.isCreated=True
        self.buffer_size = 2048
        self.isCreated = False
        self.isMacOS = (platform.system()=='Darwin')
        self.connect()
    def connect(self):
        if self.isCreated:
            return
        self.vna=None
        logging.info('connecting ...')
        
        if self.type=='TCPIP':
            try:
                self.vna = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.vna.settimeout(3)
                self.vna.connect((self.address, self.port))
                #self.vna= ik.generic_scpi.SCPIInstrument.open_tcpip(self.address,self.port)
            except socket.error, e:
                print e
                logging.info('%s'%e)
                logging.info('connection to %s:%s failed!'%(self.address, self.port))
                return
        logging.info('connection connection succeeded')
        self.isCreated = True
    def recvs2p(self):
        '''
        description: s2p file must terminated with '\r\n\n'
        Return: return a string
        '''
        if not self.isCreated:
            logging.info('please connect to the instrument')
            return

        self.send(':mmem:store "temp.s2p"')
        self.send(':mmem:tran? "temp.s2p"')
        logging.info('The s2p file is being read...')

        tmp = ''
        while True:
                if self.type =='TCPIP':
                    s = self.vna.recv(self.buffer_size)
                    tmp += s
                    #logging.info('recv %s with len %d'% (s, len(s)))
                    #logging.debug('total len %d'%len(tmp))
                    logging.debug('last %s' % s[-3:])
        
                    if s[-3:] == '\r\n\n':
                        break
                    #not terminated with '\r\n\n' and time out
                    if not s:
                        break

        self.send(':mmem:del "temp.s2p"')
        logging.info('The s2p file was read successfully with length %d'%len(tmp) )
        return tmp
    def send(self, command):
        if self.isCreated:
            if self.type=='TCPIP':
                self.vna.send("*OPC?\n")
                status = self.vna.recv(1024)
                #print [status]
                if status!='+1\n':
                    #logging.info("the vna is busy!,vna status number:%s"%status)
                    pass
                cmd = '%s\n'%command
                self.vna.send(cmd)
                logging.debug('sending %s to instrument'%cmd)
        else:
            logging.info('please connect to the instrument')
    def isConnected(self):
        return self.isCreated
    def close(self):
        self.vna.close()
        logging.info('connection closed')
        self.isCreated = False
    def dump(self):
        logging.debug('Connector info: Type %s ip %s port %d buffer_size %d isCreated %s' % (self.type, self.address, self.port, self.buffer_size, self.isCreated))

#coding =utf-8
import SocketServer
import os
import sys


class MyTCPHandler(SocketServer.StreamRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        print 'new connection'
        self.trans_cmd_cnt = 0

        while True:
            # self.rfile is a file-like object created by the handler;
            # we can now use e.g. readline() instead of raw recv() calls
            self.data = self.rfile.readline().strip()
            #print "{} wrote:".format(self.client_address[0])
            print self.data
            # Likewise, self.wfile is a file-like object used to write back
            # to the client
            if self.data != '':
                self.processcmd(self.data)
            else:
                print 'No data received, break the connection'
                break


    def processcmd(self, cmd):
        print [cmd]
        if cmd=='*OPC?':
            self.wfile.write("+1\n")
            return
        if cmd == '*IDN?':
            self.data = 'ok\n'
            self.wfile.write(self.data)
            return
        elif cmd == ':mmem:tran? "temp.s2p"':
            fname = os.path.abspath(r'..\qa\WR34NewFltnew\T_-20_J_1.s2p')
            hfile = open(fname, 'r')
            self.data = hfile.read()
            hfile.close()
            print 'sending back data with length', len(self.data)
            self.wfile.write(self.data+'\r\n\n')
        elif cmd == ':mmem:store? "temp.s2p"':
            print 'ignore', cmd
            print 'trans cnt', self.trans_cmd_cnt
        else:
            print 'ignore unknown command', cmd
            print 'trans cnt', self.trans_cmd_cnt

if __name__ == "__main__":
    HOST, PORT = "localhost", 5001
    #HOST, PORT = "192.168.1.136", 5001

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print server.server_address
    print 'waiting for connecting ...'
    server.serve_forever()

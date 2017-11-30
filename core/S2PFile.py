'''
process s2p file
'''
import os
import sys
import numpy as np
import processs2p
import logging
from math import cos,sin
class S2PFile:
    def __init__(self, file):
        """
        Description: Initialize S2P file, extracts all infos we need
        Args:
             file: may be a path, or a string represents the data read from instrument
        """
        logging.debug('Parsing S2PFile %s'%file)
        if os.path.exists(file) :
            self.__init_with_file(file)
        else:
            self.__init_with_content(file)
        logging.debug('Parsing S2PFile done')

    def __init_with_file(self, fname):
        with open(fname) as f:
            self.__init_with_content(f.read())

    def __init_with_content(self, content):
        """

        """
        strTemp = content
        # count of '#'
        cntTemp = strTemp.count('#')
        # search the index of '#'
        indexTemp = []
        start = 0
        for i in range(cntTemp):
            tmp = strTemp.find('#',start)
            if tmp == -1:
                print 'NO "#",the format of s2p file is valid '
            indexTemp.append(tmp)
            start = tmp+1

        endOfRow = strTemp.find('\n',indexTemp[-1])
        #strFlagRow record flag of s2p file,like this,# Hz S  RI   R 50
        strFlagRow = strTemp[indexTemp[-1]:endOfRow]
        strFlagRow = strFlagRow.upper()
        #strTemp record the the data after  '# Hz S  RI   R 50'
        strTemp = strTemp[endOfRow+1:]
        flagArray = strFlagRow.split()

        if(flagArray[1] == 'GHZ'):
            factor = 10**9
        elif(flagArray[1] == 'MHZ'):
            factor = 10**6
        elif(flagArray[1] == 'KHZ'):
            factor = 10**3
        elif(flagArray[1] == 'HZ'):
            factor = 1

        strTemp2 = ''
        endOfRow = -1
        startOfRow = 0
        while endOfRow != len(strTemp)-1:
            endOfRow = strTemp.find('\n',endOfRow+1,-1)
            str1 = strTemp[startOfRow:endOfRow+1]
            str2 = str1.split()
            if len(str2) == 9:
                strTemp2 = strTemp2+str1
                startOfRow = endOfRow+1
            else:
                startOfRow = endOfRow+1

            if endOfRow<0:
                break

        strTemp = strTemp2
        # search all '\n' in data area
        indexTemp = []
        endOfRow = -1
        while endOfRow != len(strTemp)-1:
            endOfRow = strTemp.find('\n',endOfRow+1,-1)
            if endOfRow<0:
                break
            indexTemp.append(endOfRow)

        rMatrix = np.zeros((len(indexTemp),5),dtype=complex)

        if flagArray[3] == 'MA':
            startOfRow = 0
            for row in range(len(indexTemp)):
                currentRow = strTemp[startOfRow:indexTemp[row]]
                tmpArray = currentRow.split()
                for i in range(9):
                    tmpArray[i] = float(tmpArray[i])
                rMatrix[row,0] = tmpArray[0]*factor
                for i in range(1,5):
                    rMatrix[row][i] = tmpArray[2*i-1]*cos(tmpArray[2*i]/180*3.1415926)+1j*tmpArray[2*i-1]*sin(tmpArray[2*i]/180*3.1415926)
                startOfRow = indexTemp[row]+1

        elif flagArray[3] == 'RI':
            startOfRow = 0
            for row in range(len(indexTemp)):
                currentRow = strTemp[startOfRow:indexTemp[row]]
                tmpArray = currentRow.split()
                for i in range(9):
                    tmpArray[i] = float(tmpArray[i])
                rMatrix[row,0] = tmpArray[0]*factor
                for i in range(1,5):
                    rMatrix[row,i] = tmpArray[2*i-1] + 1j * tmpArray[2*i]
                startOfRow = indexTemp[row] + 1
        elif flagArray[3] == 'DB':
            startOfRow = 0
            for row in range(len(indexTemp)):
                currentRow = strTemp[startOfRow:indexTemp[row]]
                tmpArray = currentRow.split()
                for i in range(9):
                    tmpArray[i] = float(tmpArray[i])
                rMatrix[row,0] = tmpArray[0]*factor
                for i in range(1,5):
                    rMatrix[row,i] = 10**(tmpArray[2*i-1]/20)*cos(tmpArray[2*i]/180*3.1415926)+1j*10**(tmpArray[2*i-1]/20)*sin(tmpArray[2*i]/180*3.1415926)
                startOfRow = indexTemp[row] + 1


        self.matrix = rMatrix

if __name__ == "__main__":
    s2p = S2PFile(os.path.abspath(os.path.join(os.getcwd(), '../../qa/template/TM0.s2p')))

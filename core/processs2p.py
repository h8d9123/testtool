#-*- coding = utf-8 -*-
from math import sin
from math import cos
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import copy

def ReadS2p(filepath):
    """Read a s2p file.

    Args:
        filepath: the path of s2p file, eg,r'xxxxxx\s2pfilename.s2p'

    Returns:
        A matrix by M*5, where M is the dim of row of data in s2p file
        [frequency, s11, s12, s21, s22], frequency, s11,s12,s13,s14 are line array.
    """
    
    hFile = open(filepath,'r')
    if hFile == IOError:
        print 'failed to open file'
        
    strTemp = hFile.read()
    hFile.close()
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
        
    
    return rMatrix

def get_phase(s2pmatrix, lineid):
    '''
    Description: calculates the S parameters' phase(unit:degree)
    Args: 
        s2pmatrix: a Nx5 matrix, the first column is frequency, others are s11,s21,s12,s22
        lineid:  is a number list, the valid numbers are (1,2,3,4),the number, 0, presents the
                first column, that's frequency, etc
    Return:returns a list,the length is same as the list,lineid.
            eg,lineid = [1,3], return [s11_phase, s12_phase]
                
    '''
    freq = np.real(s2pmatrix[:, 0])
    phase = []
    for k in lineid:
        line = s2pmatrix[:, k]
        phase_tmp = np.angle(line, True)
        phase.append(phase_tmp)
    return phase

def get_snn(s2pmatrix, line_id):
    '''
    Description: calculates the S parameters' absolute value(unit:DB)
    Args: 
        s2pmatrix: a Nx5 matrix, the first column is frequency, others are s11,s21,s12,s22
        lineid:  is a number list, the valid numbers are (1,2,3,4),the number, 0, presents the
                first column, that's frequency, etc
    Return:returns a list,the length is same as the list,lineid.
            eg,lineid = [1,3], return [s11_abs, s12_abs]
                
    '''
    freq = np.real(s2pmatrix[:, 0])
    snn = []
    for k in line_id:
        line = 20*np.log10(np.abs(s2pmatrix[:, k]))
        snn.append(line)
    return snn

def get_delay(s2pmatrix, line_id):
    '''
    Description: calculates the S parameters' absolute value,
        formula: delay = -1 * np.diff(phase) / step / 360 * 10**9
    Args: 
        s2pmatrix: a Nx5 matrix, the first column is frequency, others are s11,s21,s12,s22
        lineid:  is a number list, the valid numbers are (1,2,3,4),the number, 0, presents the
                first column, that's frequency, etc
    Return:returns a list,the length is same as the list,lineid.
            eg,lineid = [1,3], return [s11_abs, s12_abs]
    Note:1.the lenth the returned frequency is (N-1), the delay too.
         2. the roll-back point isn't deleted
    
    '''
    freq = np.real(s2pmatrix[:, 0])
    delay = []
    phases = get_phase(s2pmatrix,line_id)
    step = freq[1] - freq[0]
    for phase in phases:
        tmp = -1 * np.diff(phase) / step / 360 * 10**9
        delay.append(tmp)
    freq_delay = (freq[0:-1] + freq[1:])/2
    return freq_delay,delay

def get_max_value(start_freq,end_freq,freq_array,data_array):
    '''
    description:
        finds the max value of data_array in the range ,(start_freq, end_freq)
    Args: 
        start_freq: the start  of the frequency range
        end_freq: the end  of the frequency range
        freq_array: an array
        data_array: an array,the length of freq_array is same as data_array
                    data can be snn, delay, phase
    Returns: the max value,a number
    '''
    assert(start_freq >= freq_array[0] and end_freq<=freq_array[-1]),'get_max_value():out of range'
    ius = interpolate.UnivariateSpline(freq_array,data_array, s=0)
    x = np.linspace(start_freq, end_freq, 400)
    y = ius(x)
    
    max = np.max(y)
    return max

def get_y(x, freq_array, data_array):
    ''''
    description:
        finds the value y corresponding x in frequency array 
    Args: 
        x: an array,contains some frequency values
        freq_array: an array
        data_array: an array,the length of freq_array is same as data_array
                    data can be snn, delay, phase
    Returns:an array,contains the values y. 
    '''
    min = np.min(x)
    max = np.max(x)
    step = freq_array[1]-freq_array[0]
    assert(min >= freq_array[0] and max <= freq_array[-1]),'get_y:out of range'
    #ius = interpolate.UnivariateSpline(freq_array,data_array, s=0)
    #y = ius(x)
    y = np.zeros(len(x))
    for i in range(len(x)):
        index = (x[i]-freq_array[0])/step
        y[i] = data_array[index]
    return y

def get_x(y, start_freq, end_freq, freq_array, data_array):
    '''
    description:
        finds the frequency x corresponding y in data array 
        in the range,(start_freq, end_freq)
    Args: 
        start_freq: the start  of the frequency range
        end_freq: the end  of the frequency range
        freq_array: an array
        data_array: an array,the length of freq_array is same as data_array
                    data can be snn, delay, phase
    Returns:an array,contains frequency or null array,if y isn't found.
        
        
    '''
    assert(start_freq >= freq_array[0] and end_freq<=freq_array[-1]),'get_x():out of range'
    x1 = np.linspace(start_freq, end_freq, 800)
    ius = interpolate.UnivariateSpline(freq_array,data_array, s=0)
    y2 = ius(x1)
    y1 = y2 -y
    freq = []
    for k in range(1,len(y1)-1):
        if y1[k]*y1[k-1]<0:
            freq.append(x1[k])

    return freq

def get_BW(s2pmatrix, ref_loss = 1 ):
    freq_array = np.real(s2pmatrix[:, 0])
    data_array = get_snn(s2pmatrix, [2])
    max = np.max(data_array)
    freq = get_x(max - ref_loss, freq_array[0], freq_array[-1], freq_array, data_array[0])
    return freq

def get_attenuation_loss(freqs,s2pmatrix):
    freq_array = np.real(s2pmatrix[:, 0])
    data_array = get_snn(s2pmatrix, [2])
    y = get_y(freqs, freq_array, data_array[0])
    return y
    pass
#--------------------------------------------------------------------------
#gets values in excel use these functions above
#--------------------------------------------------------------------------

def get_return_loss_max(start_freq,end_freq,s2pmatrix):
    freq_array = np.real(s2pmatrix[:, 0])
    data_array = get_snn(s2pmatrix, [1,4])
    max1 = get_max_value(start_freq, end_freq, freq_array, data_array[0])
    max2 = get_max_value(start_freq, end_freq, freq_array, data_array[1])
    if max1>max2:
        return max1
    else:
        return max2

def get_insertion_loss_max(start_freq,end_freq,s2pmatrix):
    freq_array = np.real(s2pmatrix[:, 0])
    data_array = get_snn(s2pmatrix, [2])
    max = get_max_value(start_freq, end_freq, freq_array, data_array[0])
    return max

def get_isolation_loss_max(start_freq,end_freq,s2pmatrix):
    freq_array = np.real(s2pmatrix[:, 0])
    data_array = get_snn(s2pmatrix, [3])
    max = get_max_value(start_freq, end_freq, freq_array, data_array[0])
    return max
    
def get_attenuation_loss_max(start_freq, end_freq, s2pmatrix):
    freq_array = np.real(s2pmatrix[:, 0])
    data_array = get_snn(s2pmatrix, [2])
    max = get_max_value(start_freq, end_freq, freq_array, data_array[0])
    return max
    pass

def get_1db_bw(s2pmatrix):
    freq = get_BW(s2pmatrix, 1)
    return freq[1]-freq[0]

#-------------------------------------
def get_expanded_phase(phase0):
    phase = copy.deepcopy(phase0)
    flipcount=0
    for k in range(1,len(phase)-1):
        if (phase[k]-phase[k-1])>1 :
            phase[k:] -=360
    return phase
def delete_loadphase(m1, m2):
    freq = np.real(m1[:, 0])
    theta1 = np.angle(m1[:, 1], True)
    theta2 = np.angle(m1[:, 4], True)
    s11 = m2[:, 1] * np.exp(-1j * theta1 / 180.0 * np.pi)
    s21 = m2[:, 2] * np.exp(-0.5j * (theta1+theta2) / 180.0 * np.pi)
    s12 = m2[:, 3] * np.exp(-0.5j * (theta1+theta2) / 180.0 * np.pi)
    s22 = m2[:, 4] * np.exp(-1j*theta2/180.0*np.pi)

    gama = s11 + s21 * s12 / (1 + s22)
    return gama
    
    
if __name__ == "__main__":
  
    pass
    

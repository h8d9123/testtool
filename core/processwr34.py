#-*-coding:utf-8-*-
from PyQt4 import QtGui,QtCore,Qt
import openpyxl as pyxl
import numpy as np
import os

CHANNEL_COUNT = 8
CHANNEL_1 = 3
IL = 0
ILVAR = 1
ILRIP = 2
ILRIPR = 3
GDRIP1 = 4
GDRIPR1 = 5
GDRIP2 = 6
GDRIPR2 = 7
RJ = 8
RL = 9
CPRL=10
COLSPEC =   2
COLT1   =   3
COLT2   =   4
COLT3   =   5
COLPASSORFAIL = 6

def parseSpecStr(spec):
    '''
    Desp:解析指标,判断大于小于，以及指标，忽略单位
    Args:
        spec: 字符串， <=/>= + 指标 + 单位， 类似 ，≤0.15dB/MHz
        返回：
            返回指标值
        问题：
        <=和>= 未解决，与编码有关
    '''
    endIdx = 1
    for i in range(1,len(spec)):
        if str(spec[1]) == '+' or str(spec[1]) == '-':
            continue
        if spec[i].isdigit() or str(spec[i]) == '.':
            continue
        else:
            endIdx = i
            break
    #isSmall = 1 if ord(spec[0])==ord('≤') else 0
    if len(spec[1:endIdx])==0:
        return 0
    v = float(str(spec[1:endIdx]))
    return v
    

class WR34Filter(object):
    def __init__(self,stdExcellName,sheetName=None):
        self.chanelCount = CHANNEL_COUNT    #通道个数
        self.rowStep = 11       #每个通道对应的数据行数
        self.stdExcelName = stdExcellName   #指标模板-->output_wr34.xlsx
        self.wb = pyxl.load_workbook(self.stdExcelName)
        #获取工作表
        if sheetName is None:
            self.ws = self.wb.active
        else:
            if sheetName in self.wb.get_sheet_names():
                self.ws = self.wb.get_sheet_by_name(sheetName)
            else:
                self.ws = self.active
        #每一个通道需要写入的指标位置， 即对应的行坐标
        self.specName = [IL,ILRIP,ILRIPR,GDRIP1,GDRIPR1,GDRIP2,GDRIPR2,RJ,RL,CPRL]
        #温度对应的列
        self.colTemparaturs = [COLT1, COLT2, COLT3]
        #记录每个通道的各个指标，矩阵大小： 通道数 x 每个通道数据的个数
        self.specLim = np.zeros(shape = (self.chanelCount, self.rowStep))
        #记录是>= 还是<=
        self.isSmallEqual = np.ones(self.rowStep)
        self.isSmallEqual[-3:]=0
        
        self.readSpecLimition()
    def readSpecLimition(self):
        '''
        Desp:
                        从模板中读取每一个指标对应的范围
        '''
        for ch in range(self.chanelCount):
            for r in range(self.rowStep):
                #第 ch 个通道， 每一个通道的数据行数为 rowstep, 起始行CHANEL_1, r:每个通道的第r个数据项
                row_excel = ch*self.rowStep + CHANNEL_1 + r
                spec = self.ws[row_excel][COLSPEC].value
                v = parseSpecStr(spec)
                self.specLim[ch, r] = v
        #print self.specLim
    def writeSpecToExcel(self, targetExcel, chanel,colTemperature, specs):
        wb = None
        ws = None
        
        if os.path.exists(targetExcel): #如果excel存在,则写入目标文件，否则利用模板文件另存为新的目标文件
            wb = pyxl.load_workbook(targetExcel)
            ws = wb.active
        else:
            wb = self.wb
            ws = self.ws
        #写入从s2p得到的 通道chanel, 和温度对应的行中
        specName = self.specName
        for idxName in specName:
            #第 chanel 个通道， 每一个通道的数据行数为 rowstep, 起始行CHANEL_1, r:每个通道的第r个数据项
            row_excel = (chanel-1)*self.rowStep + CHANNEL_1 + idxName
            ws[row_excel][colTemperature].value = specs[idxName]
        vec =[]
        row_excel = (chanel-1)*self.rowStep + CHANNEL_1
        for col in self.colTemparaturs:
            tmp = ws[row_excel][col].value
            if tmp!='' and tmp is not None:
                print [tmp]
                vec.append(float(tmp))
            else:
                vec.append(0)
        ws[row_excel + 1][self.colTemparaturs[0]].value = np.max(vec) - np.min(vec)
        
        
        #判断当前通道的数据是否达标
        self.checkPassOrFail(ws, chanel)
        #如果excel文件已经打开则报异常，提示关闭再保存
        try:
            wb.save(targetExcel)
        except IOError,e:
            if e.args[0]==13:
                QtGui.QMessageBox.warning(None,"error","Please Close %s, firstly"%(e.filename))
            return False
        
        return True
    def checkPassOrFail(self, ws,chanel):
        specName = self.specName
        for idxName in specName:
            #第 chanel 个通道， 每一个通道的数据行数为 rowstep, 起始行CHANEL_1, r:每个通道的第r个数据项
            row_excel = (chanel-1)*self.rowStep + CHANNEL_1 + idxName
            #从表格读取同一通道不同温度下的实际值，若为空则为 -1
            vec = []
            for col in self.colTemparaturs:
                v = ws[row_excel][col].value
                v = float(v) if v !='' and  v!=None else -1
                vec.append(v)
            if self.isSmallEqual[idxName]==1:
                ws[row_excel][COLPASSORFAIL].value = 'PASS' if np.max(vec)<=self.specLim[chanel - 1, idxName] and np.min(vec)!=-1 else 'FAIL'
            else:
                ws[row_excel][COLPASSORFAIL].value = 'PASS' if np.min(vec)>=self.specLim[chanel - 1, idxName] and np.min(vec)!=-1 else 'FAIL'
        row_excel = (chanel-1)*self.rowStep + CHANNEL_1
        t = ws[row_excel + 1][self.colTemparaturs[0]].value
        if t!='' and t!=None:
            if float(t) <=self.specLim[chanel -1, ILVAR]:
                ws[row_excel+1][COLPASSORFAIL].value = 'PASS'
            else:
                ws[row_excel+1][COLPASSORFAIL].value = 'Fail'
        else:
            ws[row_excel+1][COLPASSORFAIL].value = 'Fail'
        pass

def getInputFrequency(excelName):
    def parseStr(s):
        endIdx = 0
        for i in range(0,len(s)):
            if s[i].isdigit() or str([i]) == '.':
                continue
            else:
                endIdx = i
                break
        if len(s[0:endIdx])==0:
            return 0
        
        #默认MHz钻转为Hz
        v = float(str(s[0:endIdx]))*10**6
        return v
    wb = pyxl.load_workbook(excelName)
    ws = wb.active
    vec_cf_bw = np.zeros(shape = (CHANNEL_COUNT, 3))
    starRow = 2
    for r in range(CHANNEL_COUNT):
        v1 = ws[r + starRow][2].value
        vec_cf_bw[r,0] =parseStr(v1)
        v2 = ws[r+starRow][3].value
        vec_cf_bw[r,1] = parseStr(v2)
        v3 = ws[r+starRow][4].value
        vec_cf_bw[r,2] = parseStr(v3)
    #print vec_cf_bw
    return vec_cf_bw

def getchAndJIndex(excelName):
    wb = pyxl.load_workbook(excelName)
    ws = wb.active
    vec_cf_bw = np.zeros(shape = (CHANNEL_COUNT, 2))
    starRow = 2
    v=[1 for i in range(CHANNEL_COUNT)]
    for r in range(CHANNEL_COUNT):
        v1 = ws[r + starRow][1].value
        v[r]=int(v1[1:])
    return v
        
        
        
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    stdExcel = r'..\db\output_WR34.xlsx'
    tarExcel = r'..\qa\outputDir\out1.xlsx'
    inputExcel = r'..\db\input_WR34.xlsx'
    wr34 = WR34Filter(stdExcel)
    specs = np.zeros(11);
    ch = 2
    colT =COLT1
    #wr34.writeSpecToExcel(tarExcel, ch, colT, specs)
    vecs = getInputFrequency(inputExcel)
    vv = getchAndJIndex(inputExcel)
    print vv.index(8)
    sys.exit(app.exec_())
    pass
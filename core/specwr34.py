#-*-coding:utf-8-*-
'''
Created on 2017.12.1

@author: win
'''
#from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import math


#from et_xmlfile.tests.common_imports import path2url
from math import sin
from math import cos
from scipy import interpolate
import copy
import processs2p

def getitems(iter, BW0, BW1, path):
    f0 = [27725*10**6,27975*10**6,28225*10**6,28475*10**6,28725*10**6,28975*10**6,29625*10**6,29875*10**6]
    S2p = processs2p.ReadS2p(path)   
    fre = S2p[:,0]
    S21 = S2p[:,2]
    
    Lam = np.zeros(len(S21))
    for i in range(len(S21)):
        Lam[i] = 20*np.log10(abs(S21[i]))  
    
    f1 = S2p[0][0]
    fu = S2p[len(S2p)-1][0] 
    step = np.real(S2p[1][0] - S2p[0][0])
    fbu0 = f0[iter] + BW0/2.0
    fbl0 = f0[iter] - BW0/2.0
    idxu0 = round(abs((fbu0 - f1)/step + 1))
    idxl0 = round(abs((fbl0 - f1)/step + 1))

    s21 = 0
    for jter in range(int(idxl0-1),int(idxu0)):
        s21 = abs(S21[jter]**2) + s21 
        Lamav = 10*math.log10(s21/(idxu0-idxl0+1))
        
    Lrip = max(Lam[int(idxl0-1):int(idxu0)]) - min(Lam[int(idxl0-1):int(idxu0)])     
    lripr = Lam[int(idxl0-1):int(idxu0)]
    LripR = max(np.diff(lripr)/step*10**6)
    
    rl = np.zeros(int(idxu0-idxl0+1))
    for jter in range(int(idxl0-1), int(idxu0), 1):
        rl[jter-int(idxl0-1)] = 20*math.log10(abs(S2p[jter][4]))
        RL = max(rl)

    cprl = np.zeros(int(idxu0-idxl0+1))
    for jter in range(int(idxl0-1), int(idxu0), 1):
        cprl[jter-int(idxl0-1)] = 20*math.log10(abs(S2p[jter][1]))
    CPRL = max(cprl)
    
    gd1 = np.diff(np.angle(S21[int(idxl0-1):int(idxu0)]))
    gd2 = np.diff(fre[int(idxl0-1):int(idxu0)])
    GD = np.zeros(len(gd1))
    for i in range(len(gd1)):
        GD[i] = -gd1[i]/np.real(gd2[i])/2.0/math.pi*10**9
    
    for kter in range(len(GD)-2):
        if kter==1:
            if np.abs(GD[kter])>np.abs(GD[kter+1]*10):
                GD[kter]=GD[kter+1]
        else:
            if np.abs(GD[kter])>np.abs((GD[kter-1]+GD[kter+1])*10):
                GD[kter]=(GD[kter-1]+GD[kter+1])/2     
                
    GDrip = max(GD) - min(GD)   
    GDripR = max(np.diff(GD)/step*10**6) 
    
    fbu01 = f0[iter] + BW1/2.0
    fbl01 = f0[iter] - BW1/2.0
    idxu01 = round((fbu01 - fbl0)/step + 1)
    idxl01 = round((fbl01 - fbl0)/step + 1)
    GD1 = GD[int(idxl01-1):int(idxu01)]
    
    GDrip1= max(GD1) - min(GD1) 
    GDripR1 = max(np.diff(GD1)/step*10**6) 
    
    
    
    if iter != 0:
        fbu01=f0[iter-1]+BW0/2
        fbl01=f0[iter-1]-BW0/2
        idxu01=round((fbu01-f1)/step+1)
        idxl01=round((fbl01-f1)/step+1)
        
        s21 = 0
        for jter in range(int(idxl01-1),int(idxu01)):
            s21 = abs(S21[jter]**2) + s21
        Rjav1=10*math.log10(s21/(idxu01-idxl01+1))
    
    if iter != 7:
        fbu02=f0[iter+1]+BW0/2
        fbl02=f0[iter+1]-BW0/2
        idxu02=round((fbu02-f1)/step+1)
        idxl02=round((fbl02-f1)/step+1)
        
        s21 = 0
        for jter in range(int(idxl02-1),int(idxu02)):
            s21 = abs(S21[jter]**2) + s21
        Rjav2=10*math.log10(s21/(idxu02-idxl02+1))
    
    if iter == 0:
        Rjav = Rjav2-Lamav
    elif iter == 7:
        Rjav = Rjav1-Lamav
    else:
        Rjav = (Rjav1+Rjav2)/2 - Lamav
        
    
    return [abs(Lamav),Lrip,np.real(LripR),GDrip1,np.real(GDripR1),GDrip,np.real(GDripR),abs(Rjav),abs(RL),abs(CPRL)] 
if __name__ == "__main__":
    
    M = getitems(0, 230*10**6, 216*10**6,r'..\qa\WR34NewFltnew\T_-20_ch_8.s2p')
    print np.round(M,2)
  
    
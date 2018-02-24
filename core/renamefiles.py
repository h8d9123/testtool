import os

import sys

import shutil

def renamefiles(dirpath):
    tardir = os.path.join(dirpath,'newfiles')
    if not os.path.exists(tardir):
        os.mkdir(tardir)
    for T in ['25','60']:
        print dirpath
        
        fs = os.listdir(os.path.join(dirpath,T))
        for f in fs:
            oldName = os.path.join(dirpath, T, f)
            fn = os.path.splitext(f)[0]
            ch = fn[-1]
            newName = os.path.join(tardir,'T_%s_J_%s.s2p'%(T,ch))
            print oldName
            print newName
            shutil.copyfile(oldName,newName)
    
    T='20'
  
    fs = os.listdir(os.path.join(dirpath,T))
    for f in fs:
        oldName = os.path.join(dirpath,T, f)
        fn = os.path.splitext(f)[0]
        ch = fn[-1]
        newName = os.path.join(tardir,'T_-%s_J_%s.s2p'%(T,ch))
        print oldName
        print newName
        shutil.copyfile(oldName,newName)
    
    pass
if __name__ =='__main__':
    if len(sys.argv) == 2:
        renamefiles(sys.argv[1])
    else:
        print 'the formath is renamefiles s2pdir'
    pass
import os,sys
def pack2ot3(srcdir,cmd):
    for dirpath,dirname, files in os.walk(srcdir):
        for fname in files:
            if os.path.splitext(fname)[1]=='.py':
                srcFName = os.path.abspath(os.path.join(dirpath,fname))
                print [r"%s %s"%(cmd,srcFName)]
                os.system(r"%s %s"%(cmd,srcFName))
    pass
if __name__ == '__main__':
    print sys.argv
    pack2ot3(r'..\py3core', r"C:\Users\wanghz\Anaconda3\Scripts\2to3.exe")
    pass
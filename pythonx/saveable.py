import marshal
import os

class CSave(object):
    def __init__(self,sFile):
        self.m_DBFile=sFile

    def Save(self):
        return None

    def Load(self,dData):
        pass

    def WriteData(self):
        dData=self.Save()
        oFile=file(self.m_DBFile,"wb")
        marshal.dump(dData,oFile)
        oFile.close()

    def ReadData(self):
        if not os.path.isfile(self.m_DBFile):
            return
        oFile=file(self.m_DBFile,"rb")
        dData=marshal.load(oFile)
        oFile.close()
        self.Load(dData)


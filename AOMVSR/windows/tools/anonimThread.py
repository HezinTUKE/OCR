from PyQt5.QtCore import *
import time
import os

from AOMVSR.ocrtools.ocr import *
from globs import *
from AOMVSR.windows.tools.dialogGUI import DialogTool

class AnonTool(QObject):
    progress = pyqtSignal(str)
    finish = pyqtSignal()
    num = 0
    files = [ os.path.join('\\OCR\\anonimizovane subory', file) for file in os.listdir('\\OCR\\anonimizovane subory') ]
    sorted_files = sorted(files, key=lambda t: os.stat(t).st_mtime)

    def __init__(self):
        super().__init__()
        self._dirSrc = '\\OCR\\anonimizovane subory'
        self.anonFile = None
        self.pause = True
        self.ocr = ToolsOCR()
        self.dialog = DialogTool()
        self.live = True
        
        try : self.idx = settings.value('img idx')
        except : self.idx = 0

    def setPause(self, pause = True):
        self.pause = pause

    def run(self):
        if self.idx == None : self.idx = 0
        while self.live:
            try :
                self.num = len(os.listdir(self._dirSrc))
                self.anonFile = self.sorted_files[self.idx]
                        
                self.progress.emit(os.path.join(self._dirSrc, self.anonFile))

                self.pause = True

                while self.pause : time.sleep(0)   
            except : print('Exception was catched location anonimThread.py, func : run')

    def stopAnonimize(self) : 
        self.setPause(pause=False)
        self.live = False
        self.finish.emit()

    def setNav(self, top = True):        
        if top : 
            if self.idx == self.num - 1 : self.idx = 0
            else : self.idx += 1
        else : 
            if self.idx == 0 : self.idx = self.num - 1
            else : self.idx -= 1

        settings.setValue('img idx', self.idx)

        self.setPause(pause=False)
        fullImgPATH = os.path.join(self._dirSrc, os.listdir(self._dirSrc)[self.idx])
        return fullImgPATH
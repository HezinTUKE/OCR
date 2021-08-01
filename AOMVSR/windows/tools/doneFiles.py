from AOMVSR.windows.ImageWindow import ImageWindow
from PyQt5.QtCore import QObject, pyqtSignal
import os
from globs import *

class ProcessImgs(QObject):
    
    progress = pyqtSignal(str)
    finish = pyqtSignal()
    path = '\\OCR\\anonimizovane subory\\'

    def __init__(self):
        super().__init__()

    def processFiles(self, processRects):
        listDir = os.listdir(self.path)
        for file in listDir : 
            filePath = os.path.join(self.path, file)
            base = os.path.splitext(file)[0]
            if base in fileList:
                outPath = fileList[base]
                win = ImageWindow()
                win.setImgPath(filePath,filePath)
                if processRects : win.procRects()
                win.saveAnonImg()
                win.showNormal()
                win.close()
                self.progress.emit(f'SUBOR {os.path.join(outPath, file)} BOL ULOZENY')

        self.finish.emit()
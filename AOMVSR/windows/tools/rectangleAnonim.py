from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QWidget

import globs

class RectanglePaint(QWidget):

    def __init__(self, nameOfFile):
        super().__init__()
        self.dict = {}
        self.nameOfFile = nameOfFile

    def addRectangle(self, word, x, y, w, h):
        rect = QRectF(x, y, w, h)
        # if word in self.dict : word = f'{word}({len(self.dict)})' 
        if self.nameOfFile in globs.obdlznik.keys() :
            dictObdl = globs.obdlznik[self.nameOfFile]
            if word in dictObdl.keys() : word = f'{word}({len(self.dict)})'
            
        self.dict[word] = rect
    
    def setRectangle(self):
        globs.obdlznik[self.nameOfFile] = self.dict
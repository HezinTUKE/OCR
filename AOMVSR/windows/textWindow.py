#Okno ktore zobrazi textovy format suboru (pomocou OCR)

from PyQt5.QtWidgets import *
import os

class TextWindow(QWidget):
    def __init__(self):
        super().__init__()
        tvLayout = QGridLayout(self)

        self.txt = None

        #OVERWRITE BUTTON
        self.btnSave = QPushButton('Uložiť')
        self.btnSave.setObjectName('btnSave')
        self.btnSave.clicked.connect(self.overwriteFile)
        
        self.file = None

        self.txtArea = QPlainTextEdit(self)

        tvLayout.addWidget(self.btnSave, 1, 0)
        tvLayout.addWidget(self.txtArea,2, 0)

    #Pred tym ako sa otvori dane okno tak do txtArea sa zapise text
    def readFile(self, file):
        self.file = file
        f = open(file, 'r')
        textOCR = f.read()
        self.txtArea.setPlainText(textOCR)
        f.close()

    #Ked stlacime ulozit tak subor sa prepise
    def overwriteFile(self):
        if os.path.exists(self.file):
            f = open(self.file, 'w')
            f.write(self.txtArea.toPlainText())
            f.close()
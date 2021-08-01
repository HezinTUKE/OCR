from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt
from globs import *

class PopUpLoad( QWidget ):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.setFixedSize(600, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        
        self.label = QLabel(self)
        self.labelTxt = QLabel(self)

        self.movie = QMovie(LOAD_GIF)

        layout.addWidget(self.label)
        layout.addWidget(self.labelTxt)

        self.setLayout(layout)

    def initWindow(self):
        self.label.setMovie(self.movie)
        self.movie.start()

    def setLabelTxt(self, txt) : self.labelTxt.setText(txt)

    def stopPopUp(self):
        self.movie.stop()
        self.close()
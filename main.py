from PyQt5.QtWidgets import QApplication

from AOMVSR.windows.mainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication([])
    w = MainWindow()
    w.showMaximized()
    app.exec()
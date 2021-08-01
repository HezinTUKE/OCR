# okno ktore zodpoveda za TreeView

from posixpath import splitext
from AOMVSR.windows.ImageWindow import ImageWindow
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import *

import os

from PyQt5 import QtCore

from AOMVSR.windows.tools.TVGenerator import TreeGenerator
from AOMVSR.windows.tools.dialogGUI import *
from AOMVSR.windows.tools.loadPopUpWindow import PopUpLoad
from globs import *

class TreeViewWindow(QWidget):

    count = 0

    def __init__(self):
        super().__init__()
        tvLayout = QGridLayout(self)

        self.setMouseTracking(True)

        #POCET PREJDENNYCH ADRESAROV + SUBOROV
        self.countLbl = QLabel(self)
        self.countLbl.setText('Preslo suborov: 0')
        #CESTA SUBORA KTORY PREBIEHA
        self.pathLbl = QLabel(self)
        self.pathLbl.setText('')

        #TREE VIEW (ADRESARY + SUBORY)
        self.SrcModel = QStandardItemModel(0, 2)
        self.SrcModel.setHorizontalHeaderLabels(['Adresar', 'Cas', 'Status'])

        self.OutModel = QStandardItemModel(0, 2)
        self.OutModel.setHorizontalHeaderLabels(['Adresar', 'Cas', 'Status'])

        self.bar = QProgressBar(self)
        self.bar.setValue(0)

        #Vlakno
        self.generatorThread = QThread()

        self.SrcTview = QTreeView(self)
        self.SrcTview.setHorizontalScrollBar(QScrollBar(self.SrcTview))
        self.SrcTview.setModel(self.SrcModel)
        self.SrcTview.header().setDefaultSectionSize(350)
        
        self.OutTview = QTreeView(self)
        self.OutTview.setHorizontalScrollBar(QScrollBar(self.OutTview))
        self.OutTview.setModel(self.OutModel)
        self.OutTview.header().setDefaultSectionSize(350)
        self.OutTview.viewport().installEventFilter(self)

        print(f'TYPE : {type(self.SrcModel)}')

        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.SrcTview)
        splitter1.addWidget(self.OutTview)
        
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(splitter1)
        splitter.addWidget(self.bar)
        
        tvLayout.addWidget(self.countLbl, 0, 0)
        tvLayout.addWidget(self.pathLbl, 1, 0)
        tvLayout.addWidget(splitter)

        self._dirOut = None #Adresar v ktorom sa nachadzju sady
        self._dirSrc = None #Ciewlovy adresar 
        self.run = False #Bezi(True) / nebezi(False) davka
        self.treeGenerator = None #Trieda pomocou ktorej sa generuje TreeView 
        self.mainWindow = None #Hlavne okno, cez neho vieme manipulovat toolbar
        self.popUpLoad = PopUpLoad()

        if stav == 2 : self.popUpLoad.show()

    def _run(self) : self.run = not self.run

    def setDirs(self, _dirSrc, _dirOut) :
        src = settings.value('src dir')
        out = settings.value('out dir')
        self._dirSrc = _dirSrc.replace('/', '\\') if stav == 0 else src.replace('/', '\\')
        self._dirOut = _dirOut.replace('/', '\\') if stav == 0 else out.replace('/', '\\')

    def setMW(self, mainWindow) : self.mainWindow = mainWindow

    def buildTreeView(self):
        if self.run == False : self._run()
        self._dirSrc = self._dirSrc

        self.SrcModel.removeRows(0, self.SrcModel.rowCount())
        self.OutModel.removeRows(0, self.OutModel.rowCount())

        self.treeGenerator =  TreeGenerator(model = self.SrcModel, outmodel = self.OutModel, _dirSrc = self._dirSrc, _dirOut = self._dirOut) 

        self.treeGenerator.moveToThread(self.generatorThread) #Pripojime vlakno
        self.generatorThread.setTerminationEnabled(True) 

        self.generatorThread.started.connect(self.treeGenerator.startProcess) #pomocou vlakna ziskame signal ze generovanie treeview sa zacalo
        self.treeGenerator.finished.connect(self.generatorThread.quit) #pomocou vlakna ziskame signal ze generovanie treeview sa skoncilo
        self.treeGenerator.finished.connect(self.generatorThread.wait) #pomocou vlakna ziskame signal ze generovanie treeview sa skoncilo
        self.treeGenerator.finished.connect(lambda : self.mainWindow._stopDavka(extra = False))
        self.treeGenerator.finished.connect(self.popUpLoad.stopPopUp)
        self.treeGenerator.progress.connect(self.accept_signal) #pomocou vlakna budeme ziskavat kde bezi generovanie

        self.generatorThread.start()

    def endDavka(self):
        self.SrcModel.removeRows(0, self.SrcModel.rowCount())
        self.OutModel.removeRows(0, self.OutModel.rowCount())

    def stopBuildTreeView(self) : self.treeGenerator.stopProcess()

    def accept_signal(self, _str):
        if _str != None :
            if _str != 'Prebieha priprava dat':
                if _str.split()[0] == 'progress' : 
                    self.count = int(_str.split()[-1])
                    self.pathLbl.setText(_str)    
                else:
                    progress = int(_str.split()[-1])
                    self.countLbl.setText(f'Preslo suborov: {progress}')
                    self.pathLbl.setText(_str)

                    if stav == 2: 
                        self.popUpLoad.initWindow()
                        self.popUpLoad.setLabelTxt(f'{_str.split(",")[0]}')
                            
                    try : prcnt =  progress / (self.count / 100)
                    except ZeroDivisionError: print('Exception')
 
                    self.bar.setValue(prcnt)
            else :
                self.pathLbl.setText(_str)

    #Pri kliknuti pravym tlacidkom mysi na prvok TreeView (LEN ked je to subor) sa otvori PopUp Menu
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.RightButton :
                try :
                    item = self.OutTview.selectedIndexes()[0].data()
                    base , ext = os.path.splitext(item)

                    fullPath = None
                        
                    if '_converted' in base : fullPath = os.path.join(fileList[base.replace('_converted', '')], item)
                    elif '.txt' == ext : fullPath = os.path.join(fileList[base], item)
                    else : 
                        for f in os.listdir('\\OCR\\anonimizovane subory'):
                            if base == os.path.splitext(f)[0] :
                                fullPath = os.path.join('\\OCR\\anonimizovane subory', f)
                                break

                    print(f'fullPath {fullPath}')
                    
                    if os.path.exists(fullPath) and self.run:

                        contextMenu = QMenu(self)

                        openAct = contextMenu.addAction(f'Otvorit {item}')

                        action = contextMenu.exec_(event.globalPos())
                        
                        ext = os.path.splitext(item)[1]

                        if action == openAct :
                            if ext == '.txt' : self.mainWindow.display(1, data = fullPath)
                            elif ext == '.jpg':
                                self.mainWindow.display(2, data = fullPath)

                except Exception : print('Exception is catched !!!')
        return QtCore.QObject.event(obj, event)
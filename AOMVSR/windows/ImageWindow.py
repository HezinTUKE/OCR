#Okno pomocou ktoreho vieme vidit obrazovku anonimizovanu / neanonimizovanu
from os import path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from AOMVSR.windows.tools.anonimThread import *
from AOMVSR.windows.tools.paintScrollArea import *

from globs import *

class ImageWindow(QWidget):

    #PREMENNA KTORA SLUZI NA ANONIMIZACIU 
    paint = False
    #START - zaciatok obdlznika , STOP - konecny uhol obdlznika
    start = stop = QPoint()
    label = path = None 
    lastPath = None
    dialog = DialogTool()

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        
        layout = QVBoxLayout(self)

        self.runANonim = False
        self.thread = QThread()
        self.anonim = None
        self.mainWindow = None
        
        btnLayout = QGridLayout(self)  
        
        self.buttonBackImg = QPushButton('Naspat')
        self.buttonBackImg.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowLeft')))

        self.buttonNextImg = QPushButton('Dalej')
        self.buttonNextImg.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowRight')))

        self.buttonEnd = QPushButton('Dokoncit')
        self.buttonEnd.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogCancelButton')))

        self.buttonRestore = QPushButton('Restore')
        self.buttonRestore.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_BrowserReload')))
        
        self.buttonSave = QPushButton('Ulozit')
        self.buttonSave.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogSaveButton')))

        self.buttonAnonim = QPushButton('Anonimizacia')
        self.buttonAnonim.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogResetButton')))

        self.buttonAnonimObdlznik = QPushButton('Prejst obdlzniky')
        
        self.histBackBtn = QPushButton()
        self.histBackBtn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaSeekBackward')))

        self.btnBrush = QPushButton('Naskicovať')

        self.buttonBackImg.clicked.connect(lambda : self.setNav(next=False))
        self.buttonNextImg.clicked.connect(lambda : self.setNav(next=True))
        self.buttonEnd.clicked.connect(lambda : self.setRunAnonim(runAnonim = False))

        self.buttonAnonim.clicked.connect(self.setPaint)
        self.buttonSave.clicked.connect(self.saveAnonImg)
        self.buttonRestore.clicked.connect(self.restoreImg)
        self.buttonAnonimObdlznik.clicked.connect(self.anonRect)
        self.btnBrush.clicked.connect(self.procRects)
        self.histBackBtn.clicked.connect(self.backHistory)
                                                                                                                                                                                                                            
        btnLayout.addWidget(self.buttonBackImg, 0,0)
        btnLayout.addWidget(self.buttonNextImg, 0,1)
        
        btnLayout.addWidget(self.buttonRestore, 0,2)
        btnLayout.addWidget(self.buttonSave, 0,3)
        btnLayout.addWidget(self.buttonAnonim, 0,4)
        btnLayout.addWidget(self.buttonAnonimObdlznik, 0, 5)
        btnLayout.addWidget(self.btnBrush, 1, 1)
        btnLayout.addWidget(self.histBackBtn, 1, 0)

        self.fileLabel = QLabel(self)

        btnLayout.addWidget(self.fileLabel)

        layout.addLayout(btnLayout)

        self.pix = QPixmap()
        self.area = QScrollArea()
        self.area.setBackgroundRole( QPalette.ColorRole.Dark)
        
        layout.addWidget(self.area)
        
    def setImgPath(self, canvas, imgPath):
        self.label = None
        self.path = imgPath
        if self.fileLabel is not None : self.fileLabel.setText(self.path.split('\\')[-1])
        qitem =  self.getCustomItem(imgPath)

        if qitem is not None : self.fileLabel.setStyleSheet(f'background-color: {qitem.getState()}; border: 1px solid black')
        else : self.fileLabel.setStyleSheet('background-color: lightgreen; border: 1px solid black') 

        label = DrawLabel(canvas, imgPath)
        self.area.setWidget(label)
        self.label = label

    def setVisibleBtns(self, visible):
        self.buttonBackImg.setVisible(visible)
        self.buttonNextImg.setVisible(visible)
        
    def procAnonim(self):
        if self.thread.isRunning() : 
            self.setVisibleBtns(visible=True) 
            self.setImgPath(self.lastPath)
            return
        
        self.anonim = AnonTool()
        p = os.listdir('\\OCR\\anonimizovane subory')[0]
        if not self.thread.isRunning(): self.setImgPath(p, p)
        
        self.setRunAnonim(runAnonim = True)
        self.setVisibleBtns(True)
        self.anonim.moveToThread(self.thread)
        self.thread.setTerminationEnabled(True)

        self.thread.started.connect(self.anonim.run)
        self.anonim.finish.connect(self.thread.quit)
        self.anonim.finish.connect(self.thread.wait)
        self.anonim.finish.connect(lambda : self.setRunAnonim(runAnonim=False))
        self.anonim.finish.connect(lambda : self.setBtns(enableBack=False, enableNext=False))
        self.anonim.finish.connect(lambda : self.mainWindow.runAnonim.setEnabled(False))
        self.anonim.progress.connect(self.setImgSignal)

        self.thread.start()
    
    def setRunAnonim(self, runAnonim): 
        self.runANonim = runAnonim 
        if not runAnonim and self.thread.isRunning(): self.anonim.stopAnonimize()

    def setImgSignal(self, file):
        self.setImgPath(file, file)

    def setNav(self, next):
        if self.anonim != None :
            self.buttonAnonimObdlznik.setEnabled(True)
            self.lastPath = self.anonim.setNav(top=next)

    def setPaint(self):
        self.label.setPaint()

    def saveAnonImg(self):
        self.label.savePixmap()
        qitem = self.getCustomItem(self.path)

        if qitem is not None : qitem.setBrush('green', True)
        continueDavka = True if settings.value('continue') == 'true' else False
        self.fileLabel.setStyleSheet('background-color: green; border: 1px solid black')
        # if len(qitemsRed) == 0 and len(qitemsYellow) == 0 : 
        #     self.dialog.dialogQuestion(self, info = 'Chcete dokoncit davku ?', title = 'Vsetke subory boly spracovane', funcExec=self.stopDavka)
        
    def stopDavka(self):
        settings.setValue('continue', False)
        # self.mainWindow.
        self.close()
        self.mainWindow.clearTree()

    def setBtns(self, enableBack=True, enableNext=True):
        self.buttonBackImg.setEnabled(enableBack)
        self.buttonNextImg.setEnabled(enableNext)

    def setMainWindow(self, mainWindow) : 
        self.mainWindow = mainWindow

    def restoreImg(self):
        self.buttonAnonimObdlznik.setEnabled(True)
        self.setImgPath(self.path, self.path)

    def anonRect(self):
        state = self.label.anonimRectangle()
        self.buttonAnonimObdlznik.setEnabled(state)

    def getCustomItem(self, path):
        for red in qitemsRed : 
            if red.getAnonFile() == path : return red
        for yellow in qitemsYellow : 
            if yellow.getAnonFile() == path : return yellow

    def procRects(self): self.label.procRects()

    def backHistory(self) :
        try :  
            path, allRects = self.label.getHistoryBack()
            rects = historyVal[ os.path.basename(path) ]
            self.setImgPath(path, self.path)
            if len(rects) > 0 :  
                self.label.setListRects(rects)
                if len(allRects) > 0 : self.label.setListRects(allRects)
            else : self.label.setListRects(allRects)
            os.remove(path)
        except : print('Exception was catched location ImageWindow.py, func : backHistory')

    def closeEvent(self, event) :
        for i in os.listdir('\\OCR\\history') : os.remove( os.path.join('\\OCR\\history', i) )
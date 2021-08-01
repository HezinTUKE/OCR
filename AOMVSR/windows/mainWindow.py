#Hlavne okno

from AOMVSR.windows.tools.doneFiles import ProcessImgs
from AOMVSR.windows.tools.xmlTool import ToolXML
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from globs import *
from AOMVSR.windows.tools.dialogGUI import *

from AOMVSR.windows.TreeViewWindow import TreeViewWindow
from AOMVSR.windows.textWindow import TextWindow
from AOMVSR.windows.ImageWindow import ImageWindow

class MainWindow(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.dialog = DialogTool()
        #ADRESAR PRE DAVKU
        self._dirSrc = None
        #CIELOVY ADRESAR
        self._dirOut = None

        self.setObjectName('mainWindow')
        try:
            self.setStyleSheet(open("\\OCR\\AOMVSR\\styles\\Windows.qss", "r").read())
            self._dirSrc = settings.value('src dir')
            self._dirOut = settings.value('out dir')
        except Exception :
            print('Exception')
        
        self.anonFiles = []

        #TOOL BAR (CIAPKA)
        self.toolBar = QToolBar()
        treeAction = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogDetailedView'))), 'Strom', self)
        self.toolBar.addAction(treeAction)
        treeAction.triggered.connect(lambda : self.stack.setCurrentIndex(0)) 

        self.openZdrojAction = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_DirIcon'))), 'Otvoriť adresar', self)
        self.openZdrojAction.triggered.connect(self._openDir)
        self.toolBar.addAction(self.openZdrojAction)

        self.openCielAction = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_DirLinkIcon'))), 'Vybrat cielovy adresar', self)
        self.openCielAction.triggered.connect(self._openUploadDir)
        self.toolBar.addAction(self.openCielAction)

        self.runAction = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogApplyButton'))), 'Spustiť davku', self)
        self.runAction.triggered.connect(lambda : self.dialog.dialogQuestion(self, info = 'Urcite chcete spustit davku ?', title='Spustenie davky', funcExec= self._runDavka))
        self.toolBar.addAction(self.runAction)
        self.runAction.setEnabled(False)

        self.runAnonim = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogContentsView'))), 'Spustit anonimizaciu', self)
        self.runAnonim.triggered.connect(self._runAnonimizacia)
        self.toolBar.addAction(self.runAnonim)
        self.runAnonim.setEnabled(False)

        self.stopAction = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_BrowserStop'))), 'Zastaviť davku', self)
        self.stopAction.triggered.connect( lambda : self.dialog.dialogQuestion(self, info = 'Urcite chcete dokoncit davku ?', title = 'Zastavit davku', funcExec=self._stopDavka))
        self.stopAction.setEnabled(False)
        self.toolBar.addAction(self.stopAction)

        self.doneAction = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogCancelButton'))), 'Dokoncit davku', self)
        self.doneAction.triggered.connect( lambda : self.dialog.dialogQuestion(self, info = 'Urcite chcete spracovat csetke subory ?', title='Spracovat davku', funcExec= lambda : self.processDavka(True), funcCancel= lambda : self.processDavka(False)))
        self.doneAction.setEnabled(False)
        self.toolBar.addAction(self.doneAction)
        #--------------------------------------------------------

        #TREEVIEW 
        # try :
        #     self.tvWindow = settings.value('src model')        
        # except : self.tvWindow = ()

        self.tvWindow = TreeViewWindow()
        self.tvWindow.setMW(self)

        self.txtWindow = TextWindow()

        self.imgWindow = ImageWindow()
        self.imgWindow.setMainWindow(mainWindow=self)

        self.stack = QStackedWidget()

        self.stack.addWidget(self.tvWindow)
        self.stack.addWidget(self.txtWindow)
        self.stack.addWidget(self.imgWindow)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toolBar)

        mainLayout = QHBoxLayout()
        self.layout.addWidget(self.stack)
        mainLayout.addLayout(self.layout)

        self.setLayout(mainLayout)
        # self.tvWindow.setMW(self)

        if stav != 0 : self._runDavka()

    def _openDir(self):
        self._dirSrc = QFileDialog.getExistingDirectory(None, 'Vyberte zdrojovy adresar', '{}:\\'.format(DISK), 
                                                        QFileDialog.ShowDirsOnly)
        self.setRun()

    def _openUploadDir(self):
        self._dirOut = QFileDialog.getExistingDirectory(None, 'Vyberte cielovy adresar', '{}:\\'.format(DISK), 
                                                        QFileDialog.ShowDirsOnly)
        self.setRun()
    
    #Spustit davku
    def _runDavka(self):
        self.stopAction.setEnabled(True)
        self.tvWindow.setDirs(self._dirSrc, self._dirOut)
        self.tvWindow.buildTreeView()
        self.runAction.setEnabled(False)
        self.runAnonim.setEnabled(False)
        self.doneAction.setEnabled(True)
        self.openCielAction.setEnabled(False)
        self.openZdrojAction.setEnabled(False)
        self.imgWindow.setRunAnonim(runAnonim=False)

        self.continueDavka = True

    #Zastavit davku
    def _stopDavka(self, extra = True): 
        settings.setValue('stav', 2)
        if len(os.listdir('\\OCR\\anonimizovane subory')) > 0 : self.runAnonim.setEnabled(True)
        if extra : self.tvWindow.stopBuildTreeView()
        self.stopAction.setEnabled(False)

    def _runAnonimizacia(self):
        win  = ImageWindow()
        win.procAnonim()
        win.setMainWindow(self)
        win.show()

    def display(self, idx, data = None):
        if idx == 1 :
            if data != None : 
                print(f'DATA !!!!!!!!!!!!!! {data}')
                self.txtWindow.readFile(data)
                self.stack.setCurrentIndex(idx)
        elif idx == 2 :
            if data != None :
                win = ImageWindow()
                win.setImgPath(data, data)
                win.setBtns(False, False)
                win.showNormal()

    # v pripade ze cielovy adresar a zdrojovy adresar su vybrate tak povolime tlacidko Spustit davku
    def setRun(self):
        if self._dirSrc != self._dirOut: self.runAction.setEnabled(bool(self._dirOut) & bool(self._dirSrc))
        else :
            if self._dirSrc != None or self._dirOut != None:
                self.dialog.dialogInfo(window=self, info='Adresare su rovnake', messageType=1)

    def closeEvent(self, event):
        self.writeRegister()

        if stav != 2:
            xml = ToolXML()
            xml.saveXML()

        # print(f'FILES : {fileList}')

    def processDavka(self, processRects):
        thread = QThread()

        processImg = ProcessImgs()
        processImg.moveToThread(thread)
        thread.setTerminationEnabled(True)

        thread.started.connect(lambda : processImg.processFiles(processRects))
        processImg.finish.connect(thread.quit)
        processImg.finish.connect(thread.wait)
        processImg.finish.connect(self.clearTree)
        processImg.progress.connect(self.accept_signal)
        
        thread.start()

    def accept_signal(self, _str):
        if _str != None : print(_str)

    def clearTree(self):
        self.tvWindow.endDavka()
        
        self.doneAction.setEnabled(False)
        self.runAnonim.setEnabled(False)
        self.openCielAction.setEnabled(True)
        self.openZdrojAction.setEnabled(True)

        qitemsYellow.clear()
        qitemsRed.clear()
        listOfFiles.clear()
        anonFiles.clear()
        fileList.clear()
        obdlznik.clear()
        historyVal.clear()
        greenPaths.clear()
        self.writeRegister()
        settings.setValue('stav', 0)

    def writeRegister(self):
        settings.setValue('src dir', self._dirSrc)
        settings.setValue('out dir', self._dirOut)
        settings.setValue('file list', fileList)
        settings.setValue('rects', obdlznik)
        settings.setValue('green paths', greenPaths)
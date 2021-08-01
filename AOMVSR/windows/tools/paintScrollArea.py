from AOMVSR.windows.tools.dialogGUI import DialogTool
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRectF, Qt, QPoint

import os
import globs

class DrawLabel(QtWidgets.QWidget):
    paint = False
    start = stop = center = QPoint()
    path = str
    right = None
    scale = move = False
    curIdx = 0
    arrImgHist = []
    
    def __init__(self, canvas : str, path : str):
        super().__init__()
        self.setMouseTracking(True)
        
        self.dialog = DialogTool()

        self.rects = self.words = []

        self.Name = path.split('\\')[-1]
        print('NAME : {}'.format(self.Name))
        
        if canvas == path :  
            if '_converted' not in self.Name :
                self.setLists(self.Name)
            else :
                NameOfFile = os.path.splitext(self.Name)[0].replace('_converted', '')
                for l in os.listdir('\\OCR\\anonimizovane subory') : 
                    if NameOfFile == os.path.splitext(l)[0] :
                        self.setLists(l)
                        break

        self.curRectIdx = 0

        self.rect = QRectF()

        self.path = path

        self.colorBrush = QtGui.QBrush()

        self.pen = QtGui.QPen()
        self.pen.setWidth(3)
        self.pen.setColor(QtGui.QColor(Qt.red))
        self.label = QtWidgets.QLabel()

        self.canvas = QtGui.QPixmap(canvas)        
        self.label.setPixmap(self.canvas)
        self.filledRects = []

    def setLists(self, name):
        if name in globs.obdlznik :
            self.words = [rect[0] for rect in globs.obdlznik[name].items() if rect[0] not in self.words]
            self.rects = [rect[1].normalized() for rect in globs.obdlznik[name].items() if rect[1] not in self.rects]
    
    def setListRects(self, rects : list):
        for rect in rects :
            if rect not in self.rects : 
                self.rects.append(rect.normalized())
                
    def mousePressEvent(self, e):
        if e.buttons() & Qt.LeftButton :
            if self.paint:
                self.writeHistory()
                self.curRectIdx += 1
                self.start = e.pos()
                self.stop = self.start
            else :
                if self.rect is None : return
                
                if e.y() <= self.rect.y() + self.rect.height() and e.y() >= self.rect.y() and self.repaint:
                
                    self.scale = True
                    if e.x() <= self.rect.x() + 5 and e.x() >= self.rect.x() - 5:
                        self.right = False
                        
                    elif  e.x() <= (self.rect.x() + self.rect.width()) + 5 and e.x() >= (self.rect.x() + self.rect.width()) - 5:
                        self.right = True  

                    else : 
                        self.move = True
                        self.center = e.pos()

                    if self.right != None : 
                        self.setCoordinats(self.rect)

        elif e.buttons() & Qt.RightButton : 
            if self.rect is None : return
            contextMenu = QtWidgets.QMenu(self)
            question = contextMenu.addAction('Anonimizovat')
            vymazat = contextMenu.addAction('Vymazat')            
            action = contextMenu.exec_(self.mapToGlobal(e.pos()))
            if action == question : self.drawRectangle()
            elif action == vymazat : self.removeRectangle() 
        self.update()    

    def mouseMoveEvent(self, e):

        if not (e.buttons() & Qt.LeftButton) and not (e.buttons() & Qt.RightButton) and not self.paint:

            self.rect = self.findCurrentRectangle(e)

            if self.rect is None : 
                self.setCursor(Qt.CursorShape.ArrowCursor)
                return
                
            if e.y() <= self.rect.y() + self.rect.height() and e.y() >= self.rect.y() and self.repaint:
                if ( e.x() <= self.rect.x() + 5 and e.x() >= self.rect.x() - 5 ) or ( e.x() <= (self.rect.x() + self.rect.width()) + 5 and e.x() >= (self.rect.x() + self.rect.width()) - 5):
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
                else: self.setCursor(Qt.CursorShape.SizeAllCursor)

        elif e.buttons() & Qt.LeftButton :
            if self.paint:
                self.stop = e.pos()
            else:
                if self.scale :

                    if self.rect is None: return

                    if self.right :  self.stop = e.pos()
                    else : self.start = e.pos()

                    if self.move : 
                        self.rect.moveCenter(e.pos())
                        self.rects[self.curIdx] = self.rect

            self.update()

    def mouseReleaseEvent(self, e):        
        if e.button() & Qt.LeftButton :
            painter = QtGui.QPainter(self.label.pixmap())
            
            if self.paint:
                # painter.setPen(self.pen)
                brush = QtGui.QBrush()
                # brush.setColor(QtGui.QColor('black'))
                brush.setStyle(Qt.SolidPattern)
                painter.setBrush(brush)
                rect = QRectF(self.start, self.stop)
                painter.drawRect(rect.normalized())
            else :
                if self.rect is None : return
                self.scale = self.move = False
                self.right = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                
            self.label.setPixmap(self.label.pixmap())

            self.start = self.stop = self.center = QPoint()
            
            self.update()

    def paintEvent(self, e):
        try :
            painter = QtGui.QPainter(self)
            painter.drawPixmap(QPoint(), self.label.pixmap())
            painter.setPen(self.pen)

            painter.drawRects(rect.normalized() for rect in self.rects if type(rect) is not str)

            if self.paint:
                rect = QRectF(self.start, self.stop)
                
                painter.drawRect(rect.normalized())
            else:
                if self.rect is None : return 

                if self.scale and self.right != None:
                    if self.right : self.rect.setRight(self.stop.x())
                    else : self.rect.setLeft(self.start.x())

                elif self.move : 
                    if not self.rect.isEmpty() : self.rects[self.curIdx] = self.rect 
            
            self.update()
        except : print('Exception was catched!!!')
    
    def sizeHint(self) -> QtCore.QSize:
        return self.canvas.size()

    def setPaint(self):
        self.paint = not self.paint
        if self.paint : self.setCursor(Qt.CursorShape.CrossCursor)
        else : self.setCursor(Qt.CursorShape.ArrowCursor)

    def savePixmap(self) :
        base = os.path.splitext(self.Name)[0]
        converted = False

        if '_converted' in base : 
            converted = True
            base = base.replace('_converted', '')
        
        print(globs.fileList)
        outPath = globs.fileList[base]

        img = self.label.pixmap().toImage()
        imgPATH = os.path.join(outPath, base + '.jpg')
        if os.path.exists(imgPATH) : os.remove(imgPATH)
        img.save(imgPATH)

        if converted : img.save(os.path.join('anonimizovane subory', self.Name))

    def findCurrentRectangle(self, e):
        self.curIdx = 0
        for rect in self.rects:
            if rect.contains(e.pos()) :
                self.setCoordinats(rect)
                return rect
            self.curIdx += 1
        return None

    def setCoordinats(self, rect):
        self.start = QPoint(int(rect.x()), int(rect.y()))
        self.stop = QPoint(int(rect.x() + rect.width()), int(rect.y() + rect.height()))
    
    def drawRectangle(self):
        self.writeHistory([self.rect])
        painter = QtGui.QPainter(self.label.pixmap())
        brush = QtGui.QBrush()
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
        painter.drawRect(self.rect.normalized())
        self.removeRectangle()
        self.update()

    def removeRectangle(self): 
        self.rects.remove(self.rect)

    def anonimRectangle(self):
        try :
            self.rect = self.rects[self.curRectIdx]
            
            if self.rect.width() == 0.0 : return True
            
            self.curRectIdx += 1

            self.dialog.dialogQuestion(self, info=f'Chciete anonimizovat {self.words[self.curRectIdx-1]}', funcExec=self.drawRectangle,funcCancel=self.removeRectangle)
            if len(self.rects) == self.curRectIdx : return False
            else : return True

        except IndexError :
            print('IndexError was catched !!!')
            return True

    def procRects(self):
        self.writeHistory(self.rects.copy())
        painter = QtGui.QPainter(self.label.pixmap())
        self.colorBrush.setStyle(Qt.BrushStyle.SolidPattern)
        
        for r in self.rects : painter.fillRect(r, self.colorBrush)
        self.rects.clear()
        self.words.clear()
        self.update() 

    def getHistoryBack(self) -> bool  :
        dir = os.listdir('\\OCR\\history')
        return os.path.join('\\OCR\\history', dir[-1]), self.rects

    def writeHistory(self, rects = []) :
        dir = os.listdir('\\OCR\\history')
        img = self.label.pixmap().toImage()
        ext = os.path.splitext(self.Name)[1]
        fileName = f'hist({len(dir)}){ext}' # priklad hist(0).tiff
        globs.historyVal[fileName] = rects
        # print(globs.historyVal)
        img.save(os.path.join('\\OCR\\history', f'{fileName}'))

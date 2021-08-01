from os import curdir
from xml.etree.ElementTree import SubElement
from PyQt5.Qt import QIcon
from PyQt5.QtCore import *
from datetime import datetime

import shutil

from PyQt5.QtGui import QBrush

from globs import *
from AOMVSR.windows.tools.dialogGUI import *
from AOMVSR.ocrtools.ocr import ToolsOCR 
from AOMVSR.windows.tools.customItem import *
from AOMVSR.windows.tools.xmlTool import *

class TreeGenerator(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, model, outmodel, _dirSrc, _dirOut):
        super().__init__()

        self.ocrTool = ToolsOCR() 

        self._dirSrc = _dirSrc
        self._dirOut = _dirOut

        self.startDir = None        

        self.model = model
        self.outmodel = outmodel

        self.collect = []
        self.count = 0
        self.running = True

        self.currentDir = None
        self.brush = QBrush()

        self.docXml = ET.parse('model.xml')
        try  :
            self.root = self.docXml.getroot()[0]
        except : pass

    def generateTreeByXML(self, standardItemSrc = None, standardItemOut = None, root = None):
        levelSrc = CustomStandardItem()
        levelSrc.setIcon(QIcon(FOLDER_BMP))
        levelOut = CustomStandardItem()
        levelOut.setIcon(QIcon(FOLDER_BMP))

        itemXml = None  

        if root is None : 
            txt = self.root.text.encode('utf-8').decode('utf-8')

            levelSrc.setText(f'{txt} ( ZDROJOVY ADRESAR )')
            self.model.appendRow([levelSrc, CustomStandardItem(self.root.attrib['time'])])

            levelOut.setText(f'{txt} ( CIELOVY ADRESAR )')
            self.outmodel.appendRow([levelOut, CustomStandardItem(self.root.attrib['time'])])
            root = self.root

        else :
            txt = root.text.encode('utf-8').decode('utf-8')

            levelSrc.setText(f'{txt}')
            standardItemSrc.appendRow([levelSrc, CustomStandardItem(root.attrib['time'])])

            levelOut.setText(f'{txt}')
            standardItemOut.appendRow([levelOut, CustomStandardItem(root.attrib['time'])])

        self.collect.append(root.attrib['path'])
        self.currentDir = root.attrib['path']

        levelOut.setSrcFile(root.attrib['path'])

        self.tag = itemXml

        for item in root :
            txt = item.text.encode('utf-8')
            self.currentDir = item.attrib['path']
            
            if self.currentDir not in self.collect:
                
                if item.tag == 'file': 
                    fileItem = CustomStandardItem(txt.decode('utf-8'))
                    fileItem.setIcon(QIcon(TIFF_BMP))
                    levelSrc.appendRow([fileItem, CustomStandardItem(item.attrib['time'])])

                    rootItem = self.setFileItem(base=txt.decode('utf-8'))

                    levelOut.appendRow([rootItem, CustomStandardItem(item.attrib['time'])])

                    self.collect.append(self.currentDir)
                    self.count += 1
                    self.progress.emit(f'{self.currentDir}, Ok, {self.count}')                        

                    color = item.attrib['color']

                    anonPath = self.currentDir.replace(os.path.dirname(self.currentDir), '\\OCR\\anonimizovane subory')
                    # if os.path.exists(anonPath) : print(f'anon path :::: {anonPath}')
                    rootItem.setAnonFile(anonPath)
                    rootItem.setSrcFile(item.attrib['path'])
                    rootItem.setParentItem(levelOut)

                    if item.attrib['path'] in greenPaths : rootItem.setBrush('green', True)
                    else : rootItem.setBrush(color)

                elif item.tag == 'folder': 
                    if self.currentDir not in self.collect : self.generateTreeByXML(standardItemOut=levelOut, standardItemSrc=levelSrc, root=item)

    def generateTree(self, _dirFunc = None, standardItemSrc = None, standardItemOut = None, xml = None):

        if _dirFunc == None : _dirFunc = self._dirSrc
        
        newDir = _dirFunc.replace(self._dirSrc, self._dirOut)
        if not os.path.exists(newDir): os.mkdir(newDir)

        if not self.running : return   

        nameRoot = os.path.basename(_dirFunc)

        level0Src = CustomStandardItem(nameRoot)
        level0Src.setIcon(QIcon(FOLDER_BMP))

        level0Out = CustomStandardItem(nameRoot)
        level0Out.setIcon(QIcon(FOLDER_BMP))

        itemXml = None
        
        if standardItemOut is None  :             
            level0Src.setText(f'{level0Src.text()} ( ZDROJOVY ADRESAR )')
            level0Out.setText(f'{level0Out.text()} ( CIELOVY ADRESAR )')
            self.model.appendRow( [ level0Src, CustomStandardItem(self.getTime()) ] )
            self.outmodel.appendRow( [ level0Out, CustomStandardItem(self.getTime()), CustomStandardItem('Ready / Nespracovany') ] )
            itemXml = ET.SubElement(modelXML, 'root')
        
        else :         
            standardItemSrc.appendRow([level0Src, CustomStandardItem(self.getTime())])
            standardItemOut.appendRow([level0Out, CustomStandardItem(self.getTime()), CustomStandardItem('Ready / Nespracovany')])
            standardItemOut.setIcon(QIcon(FOLDER_BMP))
            itemXml = ET.SubElement(xml, 'folder')
        
        self.collect.append(_dirFunc)

        level0Out.setSrcFile(_dirFunc)
        itemXml.set('path' , _dirFunc)
        itemXml.set('time' , self.getTime())
        itemXml.text = f'{nameRoot}'
        # self.xmlTool.saveXML()

        for root, dirs, files in os.walk(_dirFunc, topdown = True):
            for file in files :
                fullFilePath = os.path.join(_dirFunc, file)
                if not self.running : return
                if os.path.exists(fullFilePath) and fullFilePath not in self.collect:
                    
                    base, ext = os.path.splitext(file)

                    if ext.lower() == '.tiff' or ext.lower() == '.tif':
                        imgURL = os.path.join(root, file)
                        
                        fileItem = CustomStandardItem(file )
                        fileItem.setIcon(QIcon(TIFF_BMP))
                        self.collect.append(fullFilePath)

                        level0Src.appendRow([ fileItem, CustomStandardItem(self.getTime())])

                        rootItem = self.setFileItem(base)

                        rootItem.setParentItem(level0Out)
                        rootItem.setSrcFile(fullFilePath)
                        rootItem.setXml(self.docXml)

                        if base in fileList : 
                            xmlTool = ToolXML()
                            
                            tag = xmlTool.findTagBySrcPath(imgURL) 

                            color = tag.attrib['color'] 

                            xmlFile = SubElement(itemXml, 'file')
                            xmlFile.set('path' , tag.attrib['path'])
                            xmlFile.set('time' , tag.attrib['time'])
                            xmlFile.set('color', color)
                            xmlFile.text = f'{base}'

                            if imgURL in greenPaths : rootItem.setBrush('green')
                            else : rootItem.setBrush(color)

                            if color == 'red' : qitemsRed.append(rootItem)
                            elif color == 'yellow' : qitemsYellow.append(rootItem)
                        else :

                            anon = self.ocrTool.getStringImage(file= file, _dirOut= newDir, imgURL = imgURL)

                            xmlFile = SubElement(itemXml, 'file')
                            xmlFile.set('path' , fullFilePath)
                            xmlFile.set('time' , self.getTime())
                            xmlFile.text = f'{base}'

                            if anon : 
                                xmlFile.set('color', 'red')
                                rootItem.setBrush('red')
                                qitemsRed.append(rootItem)
                            else : 
                                xmlFile.set('color', 'yellow')
                                rootItem.setBrush('yellow') 
                                qitemsYellow.append(rootItem)

                            self.saveXML()

                        rootItem.setAnonFile(os.path.join('\\OCR\\anonimizovane subory', file))

                        if rootItem.text() : level0Out.appendRow([rootItem, CustomStandardItem(self.getTime())])

                        self.count += 1
                        self.progress.emit(f'{fullFilePath}, Ok, {self.count}')

            if len(dirs) > 0:
                for dir in dirs :
                    next = os.path.join(_dirFunc, dir)
                    if not self.running : return
                    if os.path.exists(next) and next not in self.collect : 
                        self.generateTree(standardItemSrc=level0Src, standardItemOut=level0Out, _dirFunc=next , xml=itemXml) 

    def getTime(self):
        return datetime.now().strftime('%H:%M:%S')

    def startProcess(self):
        self.startDir = os.path.join(self._dirOut , self._dirSrc.split('\\')[-1])
        print(f'START DIR {self.startDir}')

        self._dirOut = self.startDir
        self.running = True
        self.countFiles()
        if stav == 0: 
            if os.path.exists(self.startDir):shutil.rmtree(self.startDir) 
            os.mkdir(self.startDir)
            
            for file in os.listdir('\\OCR\\anonimizovane subory'): os.remove(os.path.join('\\OCR\\anonimizovane subory' , file))

            settings.setValue('stav', 1) 
            self.generateTree()

        elif stav == 1: self.generateTree() 
        else : self.generateTreeByXML()
            
        settings.setValue('stav', 2)
        # self.saveXML()
        
        print('STOP')
        self.finished.emit()

    def countFiles(self):
        preCount = 0
        self.progress.emit('Prebieha priprava dat')
        for root, dirs, files in os.walk(self._dirSrc, topdown=True):
            for file in files : 
                ext = os.path.splitext(file)[1]
                if ext.lower() == '.tiff' or ext.lower() == '.tif':
                    preCount += 1
                    self.progress.emit(f'progress {preCount}')

    def stopProcess(self):
        self.running = False 
        self.finished.emit()

    def setFileItem(self, base)  :
        rootItem = CustomStandardItem(base)
        rootItem.setIcon(QIcon(FOLDER_BMP))

        imgItem = CustomStandardItem(base + '.jpg')
        imgItem.setIcon(QIcon(JPG_BMP))
        txtItem = CustomStandardItem(base + '.txt')
        txtItem.setIcon(QIcon(FILE_BMP))
        convertedItem = CustomStandardItem(base + '_converted.jpg')
        convertedItem.setIcon(QIcon(JPG_BMP))

        rootItem.appendRow([imgItem, CustomStandardItem(self.getTime())])
        rootItem.appendRow([convertedItem, CustomStandardItem(self.getTime())])
        rootItem.appendRow([txtItem, CustomStandardItem(self.getTime())])

        return rootItem

    def saveXML(self):
        data = ET.tostring(modelXML)
        file = open('model.xml', 'wb')
        file.write(data)
        file.close()
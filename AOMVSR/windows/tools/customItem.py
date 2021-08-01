'''
    state - red ( su nespracovane subory v ktorom sa naslo TČ / IBAN / RČ ) , yellow (su este nespracovane subory) , green (subor je spracovany)
    red > yellow > green
'''
from os import stat
from PyQt5.QtGui import QBrush, QColor, QStandardItem

from globs import *
from AOMVSR.windows.tools.xmlTool import *

class CustomStandardItem(QStandardItem):
    
    anonFile = None
    srcFile = None
    parentItem = None
    state = None
    xml = None

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setEditable(False)

    def setAnonFile(self, file) : self.anonFile = file

    def getAnonFile(self) : return self.anonFile

    def setParentItem(self, parentItem) : self.parentItem = parentItem 

    def setSrcFile(self, srcFile) : self.srcFile = srcFile

    def getSrcFile(self) : return self.srcFile  

    def getState(self) : return self.state

    def setXml(self, xml) : self.xml = xml

    def setState(self, state) :

        if self in qitemsRed : qitemsRed.remove(self)
        elif self in qitemsYellow : qitemsYellow.remove(self)

        if state == 'red' : 
            qitemsRed.append(self)
            self.state = 'red' 

        elif state == 'yellow' :             
            if self.getState() != 'red' : 
                qitemsYellow.append(self)
                self.state = 'yellow'  

        elif state == 'green' : 
            self.state = 'green'

        # if os.path.isdir(self.getSrcFile()) :  
        # if self.getAnonFile() is None
        # if self.parent() is not None :
        #     if state != 'green' : self.parent.insertColumn(2, [QStandardItem('Ready/Nespracovane')])
        #     else : self.parent.insertColumn(2, [QStandardItem('Ready/Vypracovane')])

        self.setBackground(QBrush(QColor(self.state)))

    def setBrush(self, color, change = False):
        toolXML = ToolXML()

        if color == 'green' : 
            if self in qitemsRed : qitemsRed.remove(self)
            elif self in qitemsYellow : qitemsYellow.remove(self)

            tag = toolXML.findTagBySrcPath(self.getSrcFile())
            if tag.attrib['path'] not in greenPaths : greenPaths.append(tag.attrib['path'])
            toolXML.editColorOfTag(tag, color)
            # toolXML.saveXML()
          
        self.setBackground(QBrush(QColor(color)))
        self.setState(color)

        parent = self.parentItem

        while parent is not None : 
            if change :
                tag = toolXML.findTagBySrcPath(parent.getSrcFile())

                newColor = toolXML.checkEditableTag(tag)
                toolXML.editColorOfTag(tag, newColor)
                parent.setBackground(QBrush(QColor(newColor)))                
                color = newColor
            
            parent.setState(color)           

            parent = parent.parent()
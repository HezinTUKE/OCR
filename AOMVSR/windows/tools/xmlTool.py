import xml.etree.ElementTree as ET
from globs import *

class ToolXML :

    def __init__(self) :
        self.docXml = ET.parse('model.xml')
        self.root = self.docXml.getroot()
        try : print(greenPaths)
        except : pass

    def findTagBySrcPath(self, path):
        for child in self.root.iter():
            print(f'CHILD : {child}')
            if 'path' in child.attrib and child.attrib['path'] == path : return child 
        return None             

    def editColorOfTag(self, tag, newColor):
        # print(tag.attrib)s
        print(f'TAG ::: {tag}')
        tag.set('color', newColor)
        self.docXml.write('model.xml')

    def checkEditableTag(self, tag):
        return_color = 'green'
        for child in tag.iter():
            if child == tag : continue
            elif 'path' in child.attrib and child.attrib['path'] in greenPaths:
                print('\033[95m' + 'Hello GREEN' + '\033[0m')
                self.editColorOfTag(child, 'green') 
                self.saveXML()
            elif 'color' in child.attrib :
                if child.attrib['color'] == 'red' : return 'red'
                else : 
                    if return_color != 'yellow' and child.attrib['color'] == 'green': return_color = 'green'
                    elif child.attrib['color'] == 'yellow' : return_color = 'yellow'
        return return_color 

    def saveXML(self):
        data = ET.tostring(modelXML)
        file = open('model.xml', 'wb')
        file.write(data)
        file.close()
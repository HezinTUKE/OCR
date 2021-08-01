from os import chdir
import xml.etree.ElementTree as ET
# from globs import *
import globs

class XMLParserModel():
    
    def __init__(self):
        self.modelXML = ET.Element('model')
        self.docXml = ET.parse('model.xml')
        try  :
            self.root = self.docXml.getroot()[0]
        except : pass

    def getModel(self) : return self.modelXML

    def getXmlParse(self) : return self.docXml

    def getRoot(self) : return self.root

    def saveModelWithGreen(self) : 
        # docXml = ET.parse('model.xml')
        # root = docXml.getroot()[0]
        self.saveModel()

        for child in self.root.iter():
            for tag in globs.greenPaths :
                if tag.attrib['path'] == child.attrib['path']:
                    # child = tag
                    child.set('color', 'green')
                    self.docXml.write('model.xml')
                    print(child.attrib)
                    self.saveModel()

    def saveModel(self) :
        data = ET.tostring(self.modelXML)
        file = open('model.xml', 'wb')
        file.write(data)
        # file.close()
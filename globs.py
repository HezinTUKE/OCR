import os
from PyQt5.QtCore import QSettings
from AOMVSR.windows.tools.XMLParser import XMLParserModel
import xml.etree.ElementTree as ET

#REGULAR EXPRETION PATTERNS
RC_PATTERN = r'[0-9]{6}/[0-9]{4}'
IBAN_PATTERN = r'\b[A-Z]{2}[0-9]+' #V PRIPADE KED POTREBNE KONTROLOVAT SLOVENSKY IBAN TAK ZMEN TO NA [A-Z]{2}[0-9]{22}
PHONE_PATTENR1 = r'[+][ ]?[0-9]{3}[ ]?[0-9]{3}[ ]?[0-9]{3}[ ]?[0-9]{3}'
PHONE_PATTENR2 = r'[0]{1}[ ]?[0-9]{3}[ ]?[0-9]{3}[ ]?[0-9]{3}'

#PATH TO PROJECT
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

#NAME OF HOCR FILE 
HOCR_FILE = 'file_hocr'

#ICONS PATH
FOLDER_BMP = '\\OCR\\AOMVSR\\icons\\folder.bmp'
FILE_BMP = '\\OCR\\AOMVSR\\icons\\file.bmp'
TIFF_BMP = '\\OCR\\AOMVSR\\icons\\tiff.bmp'
JPG_BMP = '\\OCR\\AOMVSR\\icons\\jpg.bmp'
LOAD_GIF = '\\OCR\\AOMVSR\\icons\\Loading_2.gif'

listOfFiles = {}
anonFiles = []
fileList = {}
obdlznik = {} # { NAZOV SUBORU : { slovo, obdlznik ( QRectF ) } }
historyVal = {}
greenPaths = []

settings = QSettings("QAppAOMV", 'Reg')

modelXML = ET.Element('model')
# xmlParser = XMLParserModel()

#0 - spustit davku, 1 - pokracovat z miesta na ktorom sa zastavla davka, 2 - nacitat davku z xml
stav = 0
endWriteXml = True

qitemsRed = []
qitemsYellow = []

try : 
    if settings.value('stav') is not None : stav = settings.value('stav') 
    if settings.value('file list') is not None : fileList = settings.value('file list')
    if settings.value('rects') is not None : obdlznik = settings.value('rects')
    if settings.value('green paths') is not None : greenPaths = settings.value('green paths')
except : pass

#DRIVES
DISK = PROJECT_PATH[0]
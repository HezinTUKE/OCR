from AOMVSR.windows.tools.xmlTool import ToolXML
from AOMVSR.windows.tools.rectangleAnonim import RectanglePaint
import pytesseract
import re

import os
import cv2

from PIL import Image
import PIL

from globs import *

pytesseract.pytesseract.tesseract_cmd = r'C:\\OCR\\AOMVSR\\tools\\Tesseract-OCR\\tesseract.exe'

class ToolsOCR():
    def __init__(self):
        self.dir = self.obdlznik = None
        self.dictCheck = {}

    # def getParsedHOCR(self):
    #     hocr_file = open('{}.hocr'.format(HOCR_FILE), 'r', encoding='utf-8')
    #     parser = bs4.BeautifulSoup(hocr_file, 'lxml')
    #     lines = parser.findAll('span', {'class' : 'ocr_line'})
    #     structure = []
    #     for line in lines :
    #         line_text = line.text.replace('\n', ' ').strip()
    #         title = line['title']
    #         x,y,w,h = map(int, title[5:title.find(';')].split())
    #         structure.append({'x1' : x, 'y1' : y, 'x2' : w, 'y2' : h, 'text' : line_text})
    #     return structure

    #funkcia ktora najde polohu kazdeho slova ktore 
    def anonimize(self, file, newDir, img):
        self.dictCheck = {'RC' : False, 'PN' : False , 'IBAN' : False}
        newImg = img.copy()
        _words = pytesseract.image_to_data(newImg, lang='slk+eng', output_type=pytesseract.Output.DICT, config='--oem 3 --psm 6')
        for idx in range(len(_words['text'])):

            #kontrola ci nie je slovo prazdne (white space)
            if not _words['text'][idx].replace(' ', '') : continue

            x, y, w, h = _words['left'][idx] , _words['top'][idx], _words['width'][idx], _words['height'][idx]

            if bool(re.findall(PHONE_PATTENR1, _words['text'][idx])) or bool(re.findall(PHONE_PATTENR2, _words['text'][idx])) : 
                self.obdlznik.addRectangle(_words['text'][idx], x, y, w, h)
                self.dictCheck['PN'] = True
            elif bool(re.findall(IBAN_PATTERN, _words['text'][idx])) :
                self.obdlznik.addRectangle(_words['text'][idx], x, y, w, h)
                self.dictCheck['IBAN'] = True
            elif bool(re.findall(RC_PATTERN, _words['text'][idx])) :
                self.obdlznik.addRectangle(_words['text'][idx], x, y, w, h)
                self.dictCheck['RC'] = True

        # if (self.dictCheck['IBAN'] or self.dictCheck['PN'] or self.dictCheck['RC']) :
        self.obdlznik.setRectangle()
        # if not os.path.exists(self.pathToAnon) : 
        cv2.imwrite(self.pathToAnon, newImg)
        listOfFiles[file].append(newDir)

    def convert(self, file, newDir, img):
        base = os.path.splitext(file)[0]
        newImg = os.path.join(newDir, base + '_converted.jpg')
        if not os.path.exists(newImg) : cv2.imwrite(newImg, img)

    def getStringImage(self, file, _dirOut, imgURL):
        base, ext = os.path.splitext(file)        
        self.pathToAnon = os.path.join('\\OCR\\anonimizovane subory', file)

        self.obdlznik = RectanglePaint(file)
        img = cv2.imread(imgURL)

        listOfFiles[file] = [imgURL]

        newDir = os.path.join(_dirOut, base)

        print(f'NEW DIR {newDir}')
        if not os.path.exists(newDir) : os.mkdir(newDir)   

        if not os.path.exists(os.path.join(_dirOut, base+'.txt')):
            image = Image.open(imgURL)
            image = image.resize((1500, 1000), PIL.Image.NEAREST)
            text = pytesseract.image_to_string(image, lang = 'slk+eng', config = '-c preserve_interword_spaces=1 --psm 6').encode('cp1252', errors='ignore')
            newTxt = os.path.join(newDir, base+'.txt')
            f = open(newTxt, 'wb')
            f.write(text)
            f.close 
            text = text.decode('windows-1251')
        
        print('--------------------------------------------------------------------------------')
        self.anonimize(file, newDir, img)
        
        self.convert(file= file, newDir= newDir.replace('/', '\\'), img = img)
        fileList[base] = newDir

        return self.dictCheck['RC'] or self.dictCheck['IBAN'] or self.dictCheck['PN'] 
import pytesseract
import cv2
import re

from globs import *

src = "C:\\Users\\volodymyr.hezin\\Desktop\\Hlavny\\First\\First2\\aspigetpic.tiff"

pytesseract.pytesseract.tesseract_cmd = r'C:\\OCR\\AOMVSR\\tools\\Tesseract-OCR\\tesseract.exe'

def checkNumberPattern(_words, idx, img):
    if _words['text'][idx] == '+' or _words['text'][idx] == '+421':
        number = _words['text'][idx]
        spaces = 1
        for j in range(1,4):
            number += _words['text'][idx+j]
            spaces += 1
            if bool(re.findall(PHONE_PATTENR1, number)):
                    x, y, w, h = _words['left'][idx] , _words['top'][idx], _words['width'][idx] * (len(number)+spaces), _words['height'][idx]
                    img = cv2.rectangle(img, (x, y-3), (x+w, y+h+6), (0, 0, 0), -1)
                    break

def getTxtImage():
    img = cv2.imread(src)
    d = pytesseract.image_to_data(img, lang='slk', output_type=pytesseract.Output.DICT, config="-c preserve_interword_spaces=1 --psm 3")

    for i in range(len(d['text'])) :
        if re.findall(PHONE_PATTENR1, d['text'][i]) or re.fullmatch(RC_PATTERN, d['text'][i]) or re.fullmatch(IBAN_PATTERN, d['text'][i]):
            x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0,255,0), 2)
        checkNumberPattern(d, i, img)

    cv2.imshow('img',img)
    cv2.waitKey(0)

getTxtImage()
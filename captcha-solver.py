
import cv2
import pytesseract
from PIL import Image

image = cv2.imread('test.png')

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

gray = cv2.medianBlur(gray, 3)

filename = "{}.png".format("temp")
cv2.imwrite(filename, gray)
text = pytesseract.image_to_string(Image.open('temp.png'), config='--psm 6 -c tessedit_char_whitelist=0123456789+-= ')
print(text)

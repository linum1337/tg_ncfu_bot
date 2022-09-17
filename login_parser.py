import requests
import certifi
import config
import pytesseract
import cv2
from PIL import Image, ImageFilter, ImageEnhance
from PIL import ImageDraw, ImageOps

from bs4 import BeautifulSoup
import urllib3

http = urllib3.PoolManager(ca_certs=certifi.where())

url = config.CAPCHA_URL
response = http.request('GET', url)
soup = BeautifulSoup(response.data)
tag = soup.find('img')
img_url = 'https://ecampus.ncfu.ru' + tag['src']
print(img_url)
img_data = requests.get(img_url).content
with open('Captcha.jpeg', 'wb') as handler:
    handler.write(img_data)

filename = 'Captcha.jpeg'
image = cv2.imread(filename)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
gray = cv2.medianBlur(gray, 3)
#enchancer1 = ImageEnhance.Sharpness(gray)
#gray = enchancer1.enhance(0.01)
filename = "{}.png".format("temp")
cv2.imwrite(filename, gray)

text = pytesseract.image_to_string(Image.open('temp.png'), config='--psm 6 -c tessedit_char_whitelist=012345689+-= ')#.split('\n')
print(text)


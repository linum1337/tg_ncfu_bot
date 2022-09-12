import requests
import certifi
import config

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
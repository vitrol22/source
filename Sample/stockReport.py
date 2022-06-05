from urllib.request import urlopen
from urllib.request import HTTPError
from bs4 import BeautifulSoup as bs
import pymysql
import requests
import string
from time import time
import datetime
import pandas as pd
import urllib
from pathlib import Path

# 증권사 리포트를 report 폴더에 저장
url="https://finance.naver.com/research/company_list.naver"
print(url)
req=requests.get(url)
html=req.text
soup=bs(html,"lxml")

rContents=soup.select("#contentarea_left > div.box_type_m > table.type_1 > tr")
for rcontent in rContents:
    try:  
        rStock=rcontent.select_one("td:nth-child(1) > a").text
        rTitle=rcontent.select_one("td:nth-child(2) > a").text
        rCompany=rcontent.select_one("td:nth-child(3)").text   
        rDate=rcontent.select_one("td:nth-child(5)").text
        rDate=rDate.replace(".", "", 2).strip()
        rLink=rcontent.select_one("td.file > a")["href"]
        print(rLink) 
        
        #urllib.request.urlretrieve(rLink,f'./report/{rStock}_{rDate}.pdf')
        urllib.request.urlretrieve(rLink,f'C:/DataDisk/{rStock}_{rDate}.pdf')
    except AttributeError:
        continue

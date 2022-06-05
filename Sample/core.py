from bs4 import BeautifulSoup
import requests, lxml, os
import pymysql

import urllib

import urllib.request as req
import requests
import datetime
import time
import random
import black

#https://dev.to/dimitryzub/scrape-google-scholar-with-python-32oh

#headers = {
#    'User-agent':
#    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.#36 Edge/18.19582"
#}

'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'

header = {'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

proxies = {
  'http': os.getenv('HTTP_PROXY')
}

def gsSubjectSearch():
    for page in range(1, 900000):
        print(page, datetime.datetime.now())
        #time.sleep(random.randrange(53,104))
        #url=f'https://core.ac.uk/search?q=cigs%2Bsolar%2Bcell&page={page}'
        
        #header = {'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

        
        header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}


        url=f"https://core.ac.uk/search?q=cigs%2Bsolar%2Bcell&page={str(page+1)}"

        #response = requests.get(url)
        #header={'User-agent' : 'Mozila/2.0'}

        googleTrendsUrl = 'https://core.ac.uk/'
        response = requests.get(googleTrendsUrl)
        if response.status_code == 200:
            g_cookies = response.cookies.get_dict()

        response = requests.get(url, headers=header, cookies=g_cookies)
        html=response.text
        
        soup=BeautifulSoup(html,'html.parser') 
        #soup2=BeautifulSoup(html,'html5lib') 
        #soup3=BeautifulSoup(html,'lxml') 
        



        # Get the HTML
        conn = urllib.request.urlopen(url)
        html = conn.read()

        # Give BeautifulSoup the HTML:
        soup2 = BeautifulSoup(html, 'lxml')




        html = requests.get(url).content
        soup3 = BeautifulSoup(html, 'lxml')




        results=soup.select('.result-content') 

        '''
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')
        titles=soup.select('.news_wrap') 

        results=soup.select('.result-content') 
        '''

        for result in results:
            title=''
            title_link=''
            author=''
            jounal_link=''
            pdf_link=''

            try:
                title = result.select_one('.result-title-link').text
                title_link = result.select_one('.result-title-link a')['href']
                author = result.select_one('.author').text
                jounal_link=result.select_one('.result-label').text
                #abstract=result.select_one('.gs_rs').text
                pdf_link=result.select_one('.btn btn-primary a')['href']
                '''
                for ii in range(0,len(result.select_one('.gs_fl').text.split(' '))):
                    if result.select_one('.gs_fl').text.split(' ')[ii]=='by':
                        referenced_num=result.select_one('.gs_fl').text.split(' ')[ii+1]
                    elif result.select_one('.gs_fl').text.split(' ')[ii]=='all':
                        cluster_num=result.select_one('.gs_fl').text.split(' ')[ii+1]
                    else:
                        continue
                '''
                try:
                    interests = result.select_one('.gs_ai_one_int').text
                except:
                    interests = None       

                try:
                    conn=pymysql.connect(host='127.0.0.1',user='root',passwd='JRLEE',db='google_scholor')
                    cur = conn.cursor(pymysql.cursors.DictCursor)  
                    sql= "INSERT ignore INTO gs_results"
                    sql +=" (title, title_link, author, jounal_link, pdf_link)"
                    sql +=" values ("
                    sql += " '" + title + "'"
                    sql += ", '" + title_link + "'"
                    sql += ", '" + author + "'"
                    sql += ", '" + jounal_link + "'"
                    sql += ", '" + pdf_link + "');"

                    cur.execute(sql)
                    conn.commit()

                    #종료
                    cur.close()
                    conn.close()
                except:
                    continue
            except:
                continue

            print(page, title)
    return 

gsSubjectSearch()
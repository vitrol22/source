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


def get_soup(url):
    header = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    res = requests.get(url, headers=header)
    if res.status_code == 200:
        # print(res.text)
        return BeautifulSoup(res.text, "html.parser")
        # print(res.text)


def gsSubjectSearch():
    for page in range(1, 900000):
        print(page, datetime.datetime.now())
        url = f"https://core.ac.uk/search?q=cigs%2Bsolar%2Bcell&page={str(page+1)}"
        s = get_soup(url)

        #       body > app-root > main > app-search > div > div:nth-child(2) > div.col-md-9.px-0 > app-search-results > section > div.searchbar
        # \34 29738375 > div.result-content.media-body > p > a
        # \34 29738375 > div.result-content.media-body
        # \34 29738375
        # body > app - root
        body > app-root > main > app-search > div > div:nth-child(2) > div.col-md-9.px-0 > app-search-results > section > div.searchbar > div:nth-child(2) > div:nth-child(1)

        
        body > app - root > main
body > app-root > main > app-search > div

        results = s.select("#\34 29738375")
        for result in results:
            title = ""
            title_link = ""
            author = ""
            jounal_link = ""
            pdf_link = ""

            try:
                title = result.select_one(".result-title-link").text
                title_link = result.select_one(".result-title-link a")["href"]
                author = result.select_one(".author").text
                jounal_link = result.select_one(".result-label").text
                # abstract=result.select_one('.gs_rs').text
                pdf_link = result.select_one(".btn btn-primary a")["href"]
                """
                for ii in range(0,len(result.select_one('.gs_fl').text.split(' '))):
                    if result.select_one('.gs_fl').text.split(' ')[ii]=='by':
                        referenced_num=result.select_one('.gs_fl').text.split(' ')[ii+1]
                    elif result.select_one('.gs_fl').text.split(' ')[ii]=='all':
                        cluster_num=result.select_one('.gs_fl').text.split(' ')[ii+1]
                    else:
                        continue
                """
                try:
                    interests = result.select_one(".gs_ai_one_int").text
                except:
                    interests = None

                try:
                    conn = pymysql.connect(
                        host="127.0.0.1",
                        user="root",
                        passwd="JRLEE",
                        db="google_scholor",
                    )
                    cur = conn.cursor(pymysql.cursors.DictCursor)
                    sql = "INSERT ignore INTO gs_results"
                    sql += " (title, title_link, author, jounal_link, pdf_link)"
                    sql += " values ("
                    sql += " '" + title + "'"
                    sql += ", '" + title_link + "'"
                    sql += ", '" + author + "'"
                    sql += ", '" + jounal_link + "'"
                    sql += ", '" + pdf_link + "');"

                    cur.execute(sql)
                    conn.commit()

                    # 종료
                    cur.close()
                    conn.close()
                except:
                    continue
            except:
                continue

            print(page, title)
    return


header = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}
proxies = {"http": os.getenv("HTTP_PROXY")}

if __name__ == "__main__":
    subject = "cigs+solar+cell"
    conn = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="scholar")

    # print(s)
    # mainInfo(s)

    gsSubjectSearch()
    # cur = conn.cursor(pymysql.cursors.DictCursor)
    # cur.execute("use scholar")
    # conn.commit()
    # cur.close()

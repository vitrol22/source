from urllib.request import urlopen
from urllib.request import HTTPError
from bs4 import BeautifulSoup as bs
import pymysql
import requests
# from time 
import time
import datetime
import pandas as pd
from datetime import datetime


#현재 저장된 내용을 삭제
conn=pymysql.connect(host='127.0.0.1',user='root',passwd='JRLEE',db='sadvisor')
cur=conn.cursor()
cur.execute("use sadvisor")
cur.execute("delete from sadvisor.stockcodelist2;")
print(cur.fetchone())
conn.commit()
cur.close()
conn.close()

def replaceString(txt):
  dictionary = {',': '', '%': ''}
  transTable = txt.maketrans(dictionary)
  txt = txt.translate(transTable)
  txt=txt.replace("N/A", "0", 1).strip()
  return txt
  #print(txt)

marketType={
    "KOSPI":"0",
    "KOSDAQ":"1"
}
# time_check=time()

hsql=''
for market, code in marketType.items():
    #ksql=""
    for page in range(1,40):
        ksql=""
        code=str(code)
        page=str(page)
        # 첯번째 페이지만 코스피, 코스닥 코드를 넣고 나머지는 페이지를 넣는다.
        if page=='1' and code=='0':
            url=f"https://finance.naver.com/sise/field_submit.nhn?menu=market_sum&returnUrl=http://finance.naver.com/sise/sise_market_sum.nhn?sosok={code}&fieldIds=quant&fieldIds=ask_buy&fieldIds=amount&fieldIds=market_sum&fieldIds=operating_profit&fieldIds=per&fieldIds=open_val&fieldIds=ask_sell&fieldIds=prev_quant&fieldIds=property_total&fieldIds=operating_profit_increasing_rate&fieldIds=roe&fieldIds=high_val&fieldIds=buy_total&fieldIds=frgn_rate&fieldIds=debt_total&fieldIds=net_income&fieldIds=roa&fieldIds=low_val&fieldIds=sell_total&fieldIds=listed_stock_cnt&fieldIds=sales&fieldIds=eps&fieldIds=pbr&fieldIds=sales_increasing_rate&fieldIds=dividend&fieldIds=reserve_ratio"
        elif page=='1' and code=='1':
            url=f"https://finance.naver.com/sise/field_submit.nhn?menu=market_sum&returnUrl=http://finance.naver.com/sise/sise_market_sum.nhn?sosok={code}&fieldIds=quant&fieldIds=ask_buy&fieldIds=amount&fieldIds=market_sum&fieldIds=operating_profit&fieldIds=per&fieldIds=open_val&fieldIds=ask_sell&fieldIds=prev_quant&fieldIds=property_total&fieldIds=operating_profit_increasing_rate&fieldIds=roe&fieldIds=high_val&fieldIds=buy_total&fieldIds=frgn_rate&fieldIds=debt_total&fieldIds=net_income&fieldIds=roa&fieldIds=low_val&fieldIds=sell_total&fieldIds=listed_stock_cnt&fieldIds=sales&fieldIds=eps&fieldIds=pbr&fieldIds=sales_increasing_rate&fieldIds=dividend&fieldIds=reserve_ratio"
        else:
            url=f"https://finance.naver.com/sise/field_submit.naver?menu=market_sum&returnUrl=http%3A%2F%2Ffinance.naver.com%2Fsise%2Fsise_market_sum.nhn%3Fsosok%3D{code}%26page%3D{page}&fieldIds=quant&fieldIds=ask_buy&fieldIds=amount&fieldIds=market_sum&fieldIds=operating_profit&fieldIds=per&fieldIds=open_val&fieldIds=ask_sell&fieldIds=prev_quant&fieldIds=property_total&fieldIds=operating_profit_increasing_rate&fieldIds=roe&fieldIds=high_val&fieldIds=buy_total&fieldIds=frgn_rate&fieldIds=debt_total&fieldIds=net_income&fieldIds=roa&fieldIds=low_val&fieldIds=sell_total&fieldIds=listed_stock_cnt&fieldIds=sales&fieldIds=eps&fieldIds=pbr&fieldIds=sales_increasing_rate&fieldIds=dividend&fieldIds=reserve_ratio"            

        req=requests.get(url)
        time.sleep(1)
        html=req.text
        soup=bs(html,"lxml")

        # mysql 문의 header 가 없다면 생성하고 
        if hsql=='': 
            headers=soup.select("#contentarea > div.box_type_l > table.type_2 > thead > tr >th")
            headers=list(map(lambda x: x.text, headers))
            ii=0
            hsql="INSERT INTO StockCodeList2 ("
            while ii<len(headers)-1:
                if ii==1:
                    hsql += "종목코드, 종목명, "
                else:
                    hsql += headers[ii]+", "
                ii+=1

            hsql=hsql[:-2] + ") values "
            
            #print(headers)
            # print(hsql)

        stockContents=soup.select("#contentarea > div.box_type_l > table.type_2 > tbody >tr")
        sql=""
        for stockcontent in stockContents:
            ii=0
            try:
                while ii<=33:
                    if ii==0:
                        txt=stockcontent.select_one("td.no").text
                    elif ii==1:
                        #종목코드를 얻는 과정
                        txt=str(stockcontent.find('a', href=True)).replace('<a class="tltle" href="','https://finance.naver.com')[0:53]
                        txt=txt.replace("https://finance.naver.com/item/main.naver?code=","")
                    elif ii==30:
                        # ii += 1
                        txt=stockcontent.select_one("td:nth-child(%d)" % ii).text
                        # continue
                    else:
                        txt=stockcontent.select_one("td:nth-child(%d)" % ii).text
                        
                    txt=replaceString(txt) #얻어진 txt의 특수 문자 제거
                    sql += "'" + txt + "', "
                    ii+=1
                    # stockName=stockcontent.select_one("td:nth-child(11)").text
                
                ksql += "(" + sql[:-2] + "), "                
                sql=""

            except AttributeError:
                continue
            
        fsql=ksql[:-2]    
        ksql= hsql + fsql
        fsql=""
        # print(ksql)        

        #얻어진 정보를 저장하는 과정
        conn=pymysql.connect(host='127.0.0.1',user='root',passwd='JRLEE',db='sadvisor')
        cur=conn.cursor()
        cur.execute("use sadvisor")
        now = datetime.now()
        if len(ksql)>440:   #헤더의 정보가 440가 이므로 이보다 더 길면 유용한 정보가 포함되어 있으므로 저장
            cur.execute(ksql)
            conn.commit()
            ksql=""            
            print("현재시간 " + now.strftime("%Y%m%d, %H:%M:%S") + f"  {market} 시장에 대한 {page}페이지를 저장하였습니다.")
        else:
            print("현재시간 " + now.strftime("%Y%m%d, %H:%M:%S") + f"  {market} 시장에 대한 {page}페이지를 저장에 실패하였습니다.")            
            continue
        cur.close()
        conn.close()

        #date_time = datetime.now.strftime("%m/%d/%Y, %H:%M:%S")
        #now = datetime.now()
        #print("현재시간 " + now.strftime("%Y%m%d, %H:%M:%S") + f"  {market} 시장에 대한 {page}페이지를 저장하였습니다.")
#오늘 Naver 에서 시가총액 순위로 데이터를 가져오면 언제의 데이터인지 알 수 없다.
#Naver에서 저장된 삼성전자 데이터로부터 날자가져오기
#변수 savedRecentStockMarketOpeningDate 로 저장
url="https://fchart.stock.naver.com/sise.naver?symbol=005930&timeframe=day&count=1&requestType=0"
req=requests.get(url)
html=req.text
soup=bs(html,'html.parser') #"lxml")

# information
inf = soup.select('item')
columns = ['Date', 'Open' ,'High', 'Low', 'Close', 'Volume']
df_inf = pd.DataFrame([], columns = columns, index = range(len(inf)))

for i in range(len(inf)):
    df_inf.iloc[i] = str(inf[i]['data']).split('|')
    #print(df_inf.loc[1:1].values)
savedRecentStockMarketOpeningDate=int(df_inf.Date)
#print(int(df_inf.Date))

conn=pymysql.connect(host='127.0.0.1',user='root',passwd='JRLEE',db='sadvisor')
cur=conn.cursor()
cur.execute("use sadvisor")
now = datetime.now()
sql = "update StockCodeList2 set 기록시간= '" + str(now.strftime('%Y%m%d %H:%M:%S')) + "', 거래날자='" + str(savedRecentStockMarketOpeningDate) + "'"
cur.execute(sql)
conn.commit()

#CompanyList의 주요제품을 StockCodeList 의 주요제품으로 업데이트하는 과정       
SQL = "UPDATE StockCodeList2 T"
SQL = SQL + " INNER JOIN CompanyList S"
SQL = SQL + " ON T.종목명=S.회사명"
SQL = SQL + " Set T.주요제품 = S.주요제품;"

cur.execute(sql)
conn.commit()  

cur.close()
conn.close()


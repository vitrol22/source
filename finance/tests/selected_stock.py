import pandas as pd
import numpy as np
from pykrx import stock
import datetime
from pykrx.website import krx
from pykrx.website import naver
from pandas import DataFrame
import pymysql
from sqlalchemy import create_engine
import time
pymysql.install_as_MySQLdb()
import requests
from bs4 import BeautifulSoup
import talib as ta

def best_stock_to_db(calc_date):
    sql=f"SELECT DISTINCT 거래날자 FROM tA WHERE 거래날자<='{calc_date}' ORDER BY 거래날자 DESC;"
    dfDate = pd.read_sql_query(sql, connPy)

    dfSelected=[]
    # 볼린저밴드 상단
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+=" and ta.close>ta.up_band;"

    dfSelected = pd.read_sql_query(sql, connPy)

    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','1볼린저돌파')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '볼린저돌파 종목에 대한', '계산을 완료하였습니다.')

    #pd.merge(dfSelectedStock, dfSelected, left_on='종목코드', right_on='종목코드', how='outer')

    # 장기 눌림목   
    dfSelected=[] 
    sql="select DISTINCT ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+= " and tb.거래날자>'"+dfDate.거래날자[13]+"'"
    sql+= " and tb.거래날자<'"+dfDate.거래날자[4]+"'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and tb.MA5/tb.MA20>1.1"     # 14일전-5일전에 오일/이십일평균 이격도 1.1 이상
    sql+= " and ta.close/ta.MA20*100>99 and ta.close/ta.MA20*100<103"   # 오늘 현재가/이십일평균 이격도/99-103 이내
    sql+= " order by ta.close/ta.MA20 desc"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','2장기 눌림목')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '장기 눌림목 종목에 대한', '계산을 완료하였습니다.')


    # 지속상승
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+= " and ta.MA5/ta.MA20>1.15"
    sql+= " order by ta.MA5/ta.MA20 desc;"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','3지속상승')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '지속상승 종목에 대한', '계산을 완료하였습니다.')

    # Heikin Ash 방향전환
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+= " and tb.거래날자='" + dfDate.거래날자[1] + "'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and ta.HA_Close>ta.HA_Open"
    sql+= " and tb.HA_Close<tb.HA_Open"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','4Heikin Ash 방향전환')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], 'Heikin Ash 방향전환 종목에 대한', '계산을 완료하였습니다.')

    # 이십육십돌파
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+=" and tb.거래날자='" + dfDate.거래날자[1] + "'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and ta.MA20 > ta.MA60"
    sql+= " and tb.MA20 < tb.MA60"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','5이십육십돌파')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '이십육십돌파 종목에 대한', '계산을 완료하였습니다.')

    # 이십백이십돌파
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+=" and tb.거래날자='" + dfDate.거래날자[1] + "'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and ta.MA20 > ta.MA120"
    sql+= " and tb.MA20 < tb.MA120"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','6이십백이십돌파')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '이십백이십돌파 종목에 대한', '계산을 완료하였습니다.')

    # 이십이백사십돌파 
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+=" and tb.거래날자='" + dfDate.거래날자[1] + "'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and ta.MA20 > ta.MA240"
    sql+= " and tb.MA20 < tb.MA240"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','7이십이백사십돌파')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '이십이백사십돌파 종목에 대한', '계산을 완료하였습니다.')

    # 육십백이십돌파
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+=" and tb.거래날자='" + dfDate.거래날자[1] + "'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and ta.MA60 > ta.MA120"
    sql+= " and tb.MA60 < tb.MA120"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','8육십백이십돌파')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '육십백이십돌파 종목에 대한', '계산을 완료하였습니다.')

    # 오일거래세배
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+= " and ta.VMA5>ta.VMA10*1.5"
    sql+= " and ta.Close>ta.Open"
    sql+= " and ta.close>ta.mid_band"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','9오일거래량세배')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '오일거래량세배 종목에 대한', '계산을 완료하였습니다.')

    # 14일신고가
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+= " and ta.willr14 = 0"
    sql+= " and ta.AVGwillr120 < 0"
    sql+= " and ta.close>ta.mid_band"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','1014일신고가')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '14일신고가 종목에 대한', '계산을 완료하였습니다.')

    # 120일 신고가
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+=" and tb.거래날자='" + dfDate.거래날자[1] + "'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and ta.willr14=0"
    sql+= " and ta.willr120=0"
    sql+= " and ta.close>ta.mid_band"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','11120일 신고가')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '120일 신고가 종목에 대한', '계산을 완료하였습니다.')

    # 금일 StochasticPK와 StochasticPD 의 골드크로스
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+=" and tb.거래날자='" + dfDate.거래날자[1] + "'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and tb.slowd > tb.slowk"    
    sql+= " and ta.slowd < ta.slowk"
    sql+= " and ta.slowk> 60 and ta.slowk < 99"  # 30<StochasticPK <70
    #sql+= " order by ta.종목명"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','12Stochastic GC')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], 'Stochastic GC 종목에 대한', '계산을 완료하였습니다.')

    # 금일 MACD 골드크로스 종목표시 DMACD공중방향전환

    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+=" and tb.거래날자='" + dfDate.거래날자[1] + "'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and tb.macd < tb.macdSignal"    
    sql+= " and ta.macd > ta.macdSignal"
    sql+= " and ta.macd > tb.macd"
    sql+= " and ta.macd > 0"
    sql+= " order by ta.종목명"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','13MACD GC')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], 'MACD GC종목에 대한', '계산을 완료하였습니다.')

    # ta.close가 볼린저 상단에 위치하고 3일간 계속 Volume이 감소하면서 주가상승
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, ta tc, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+=" and tb.거래날자='" + dfDate.거래날자[1] + "'"
    sql+=" and tc.거래날자='" + dfDate.거래날자[2] + "'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and ta.종목코드=tc.종목코드"
    sql+= " and ta.Volume<tb.Volume and tb.Volume<tc.Volume"
    sql+= " and ta.close>tb.close and tb.close>tc.close"
    sql+= " and ta.close>ta.up_band;"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','143일간 눌림목')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '3일간 눌림목 종목에 대한', '계산을 완료하였습니다.')

    # Volume감소 대비 주가대비 유지
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, ta tb, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+=" and tb.거래날자='" + dfDate.거래날자[1] + "'"
    sql+= " and ta.종목코드=tb.종목코드"
    sql+= " and if(ta.VMA10=0,1,ta.VMA5/ta.VMA10) < 0.66" #10Volume대비 오Volume이 반으로 감소한 표현
    sql+= " and ((ifnull(tb.macd,0) < ifnull(tb.macdSignal,0) and ta.macd > ta.macdSignal)" # MACD > SSignal 방향전환
    sql+= " or (ta.macd>ifnull(tb.macd,0) and ta.macdSignal>ifnull(tb.macdSignal,0)))" # MACD 상승+SSignal 상승
    sql+= " and ta.close>ta.mid_band"
    sql+= " order by ta.VMA5/ta.VMA10*100"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','15주가대비거래량양호')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '주가대비거래량양호 종목에 대한', '계산을 완료하였습니다.')

    # 장기바닦
    sql="select ta.거래날자, ta.종목명, ta.종목코드"
    sql+=" from ta ta, daily da"
    sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
    sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
    sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
    sql+=" and ta.close>ta.psar"
    sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
    sql+=""
    sql+= " and ta.AVGwillr120<-88"
    sql+= " and ta.AVGwillr14>-30"
    #sql+= " order by da.등락률 DESC"

    dfSelected = pd.read_sql_query(sql, connPy)
    for idx in range(len(dfSelected)):
        sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
        sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','16장기바닦')"
    cur.execute(sql)
    connPy.commit()
    print(dfDate.거래날자[0], '장기바닦 종목에 대한', '계산을 완료하였습니다.')

if __name__ == "__main__":

    connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
    cur = connPy.cursor()
    cur.execute("use sstock")
    cur.fetchall()
    # 모든 거래날자를 거져와서 하루씩 계산
    # sql="SELECT DISTINCT 거래날자 FROM ta WHERE 거래날자>'20210101' ORDER BY 거래날자 ASC;"
    sql="SELECT DISTINCT ta.거래날자 FROM ta ta WHERE ta.거래날자>'20210101' and ta.거래날자 "
    sql+=" not in (select DISTINCT SaveDate from selected_stock WHERE SaveDate>'20210101');"

    dfDate = pd.read_sql_query(sql, connPy)

    MinTransactionPrice=5000
    MinMarketCapitalization=200000000000
    MinMarketTransation=100000000
    MinTransactionVolume=100000

    for df_Date in range(0,len(dfDate)):
        calc_date=dfDate.iloc[df_Date][0]
        best_stock_to_db(calc_date)


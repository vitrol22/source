import yfinance as yf
import talib as ta
import pandas as pd
import matplotlib.pyplot as plt
import pymysql
import mplfinance as mpf
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import pandas as pd
from pandas_datareader import data  
from datetime import datetime
from IPython.display import display
from pykrx import stock

def Ichimoku_Cloud(df): #일목균형표 계산
    d = df.sort_index(ascending=False) # my Live NSE India data is in Recent -> Oldest order

    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    period9_high = d['High'].rolling(window=9).max()
    period9_low = d['Low'].rolling(window=9).min()
    tenkan_sen = (period9_high + period9_low) / 2

    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    period26_high = d['High'].rolling(window=26).max()
    period26_low = d['Low'].rolling(window=26).min()
    kijun_sen = (period26_high + period26_low) / 2

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    period52_high = d['High'].rolling(window=52).max()
    period52_low = d['Low'].rolling(window=52).min()
    senkou_span_b = ((period52_high + period52_low) / 2).shift(26)

    # The most current closing price plotted 22 time periods behind (optional)
    chikou_span = d['Close'].shift(-22) # Given at Trading View.
    '''
    d['blue_line'] = tenkan_sen
    d['red_line'] = kijun_sen
    d['cloud_green_line_a'] = senkou_span_a
    d['cloud_red_line_b'] = senkou_span_b
    d['lagging_line'] = chikou_span
    '''
    df['전환선'] = tenkan_sen
    df['기준선'] = kijun_sen
    df['선행스팬1'] = senkou_span_a
    df['선행스팬2'] = senkou_span_b
    df['후행스팬'] = chikou_span

    return df #.sort_index(ascending=True)


def HA(df): # Heikin Ash 계산
    df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    df['HA_Open'] = (df['Open'].shift(1) + df['Open'].shift(1)) / 2
    df.iloc[0, df.columns.get_loc("HA_Open")] = (df.iloc[0]['Open'] + df.iloc[0]['Close'])/2
    df['HA_High'] = df[['High', 'Low', 'HA_Open', 'HA_Close']].max(axis=1)
    df['HA_Low'] = df[['High', 'Low', 'HA_Open', 'HA_Close']].min(axis=1)
    df = df.drop(['Open', 'High', 'Low', 'Close'], axis=1)  # remove old columns
    df = df.rename(columns={"HA_Open": "Open", "HA_High": "High", "HA_Low": "Low", "HA_Close": "Close", "Volume": "Volume"})
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]  # reorder columns
    return df

def TA_Calc(): 
    connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
    cur = connPy.cursor()
    cur.execute("use sstock")

    #240일 전의 날자를 확인 
    sql="select S.MarketOpenDate from (select MarketOpenDate from tradingdate order by MarketOpenDate desc limit 241) as S order by S.MarketOpenDate asc limit 1"
    cur.execute(sql) 
    before241ago = cur.fetchall()
    before241ago='20200101'
    sql="SELECT stock_code, Ta_calc_date FROM stock_code_list where basic_info_date<>ta_calc_date  or Ta_calc_date is null;"
    df_stock_code = pd.read_sql_query(sql, connPy)

    try:
        for ii in range(len(df_stock_code)):
            print(ii, "/", len(df_stock_code), df_stock_code.iloc[ii, 0], stock.get_market_ticker_name(df_stock_code.iloc[ii, 0]))
            if df_stock_code.iloc[ii, 0].isnumeric():   #종목코드가 숫자인지 검토

                #sql=f"select 거래날자, 종목코드, 시가 as Open, 고가 as High, 저가 as Low, 종가 as Close, 거래량 as Volume from daily where 거래날자>='"+before241ago[0][0]+" and 종목코드={str(df_stock_code.iloc[ii, 0])}" 
                sql=f"select 거래날자, 종목코드, 종목명, 시가 as Open, 고가 as High, 저가 as Low, 종가 as Close, 거래량 as Volume from daily where 거래날자>='"+before241ago[0][0]+"' and 종목코드='"+str(df_stock_code.iloc[ii, 0])+"'" 

                df = pd.read_sql_query(sql, connPy)
                # df.insert(7,'종목명', stock.get_market_ticker_name(df_stock_code.iloc[ii, 0]))
                df  = df .fillna(0)

                # power = yf.Ticker("POWERGRID.NS")
                # power = yf.Ticker('005380.KS')
                # df = power.history(start="2021-01-01", end='2022-02-04')
                # df.head()

                df['MA5'] = ta.SMA(df['Close'],5)       #종가이동평균
                df['MA10'] = ta.SMA(df['Close'],10)     #종가이동평균
                df['MA20'] = ta.SMA(df['Close'],20)     #종가이동평균
                df['MA60'] = ta.SMA(df['Close'],60)     #종가이동평균
                df['MA120'] = ta.SMA(df['Close'],120)   #종가이동평균
                df['MA240'] = ta.SMA(df['Close'],240)   #종가이동평균

                df['VMA5'] = ta.SMA(df['Volume'],5)         #거래량 이동평균
                df['VMA10'] = ta.SMA(df['Volume'],10)       #거래량 이동평균
                df['VMA20'] = ta.SMA(df['Volume'],20)       #거래량 이동평균
                df['VMA60'] = ta.SMA(df['Volume'],60)       #거래량 이동평균
                df['VMA120'] = ta.SMA(df['Volume'],120)     #거래량 이동평균
                df['VMA240'] = ta.SMA(df['Volume'],240)     #거래량 이동평균
                #Bollinger Band
                df['up_band'], df['mid_band'], df['low_band'] = ta.BBANDS(df['Close'], timeperiod =20) #Bollinger Band

                df['RSI'] = ta.RSI(df["Close"]) # RSI

                df['willr14'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=14) #Williams %R Price
                df['AVGwillr14'] = ta.SMA(df['willr14'], 5) #Williams %R Price Average

                df['willr120'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=120)   #Williams %R Volume
                df['AVGwillr120'] = ta.SMA(df['willr120'], 5)   #Williams %R Volume Average

                # Stochastic
                df['slowk'], df['slowd'] = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
                #  Stochastic Relative Strength Index
                df['STOCHRSI_fastk'], df['STOCHRSI_fastd'] = ta.STOCHRSI(df['Close'], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)

                # Parabolic SAR
                df['psar'] = ta.SAR(df['High'], df['Low'], acceleration=0, maximum=0)
                df['arronOSC'] = ta.AROONOSC(df['High'], df['Low'], timeperiod=14)

                #ADX
                df['adx'] = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)       # ADX - Average Directional Movement Index
                df['pdi'] = ta.PLUS_DI(df['High'], df['Low'], df['Close'], timeperiod=14)   #PLUS_DI - Plus Directional Indicator
                df['mdi'] = ta.MINUS_DI(df['High'], df['Low'], df['Close'], timeperiod=14)  #MINUS_DI - Minus Directional Indicator

                HA(df) # Heikin Ash 
                Ichimoku_Cloud(df)  #일목균형표

                df  = df .fillna(0)
                #df['종목명'] = df['종목코드'].map(lambda x: stock.get_market_ticker_name(x))
                

                for idx in range(len(df)):
                    # 저장된 적이 없는 신규코드인 경우  # 마지막으로 저장된 날자 이후의 날자라면 저장 
                    if (df_stock_code.iloc[ii, 1] is None) or df.iloc[idx,0]>=df_stock_code.iloc[ii, 1]: 
                        sql = "INSERT IGNORE INTO ta (거래날자, 종목코드, 종목명, Open, High, Low, Close, Volume,"
                        sql +=" MA5, MA10, MA20, MA60, MA120, MA240, VMA5, VMA10, VMA20, VMA60,	VMA120,	VMA240,"
                        sql +=" up_band, mid_band, low_band, RSI, willr14, AVGwillr14, willr120, AVGwillr120, slowk, slowd,"
                        sql +="  STOCHRSI_fastk, STOCHRSI_fastd, psar, arronOSC, adx, pdi, mdi,	HA_Close, HA_Open, HA_High,	HA_Low,"
                        sql +=" 전환선, 기준선, 선행스팬1, 선행스팬2, 후행스팬)"
                        sql +=" VALUES"
                        sql +=" (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

                        cur.execute(sql, tuple(df.values[idx]))
                        connPy.commit()
                    
                    elif df.iloc[idx,0]>=df_stock_code.iloc[ii, 1]:   # 마지막으로 저장된 날자 이후의 날자라면 저장 
                        sql = "INSERT IGNORE INTO ta (거래날자, 종목코드, 종목명, Open, High, Low, Close, Volume,"
                        sql +=" MA5, MA10, MA20, MA60, MA120, MA240, VMA5, VMA10, VMA20, VMA60,	VMA120,	VMA240,"
                        sql +=" up_band, mid_band, low_band, RSI, willr14, AVGwillr14, willr120, AVGwillr120, slowk, slowd,"
                        sql +="  STOCHRSI_fastk, STOCHRSI_fastd, psar, arronOSC, adx, pdi, mdi,	HA_Close, HA_Open, HA_High,	HA_Low,"
                        sql +=" 전환선, 기준선, 선행스팬1, 선행스팬2, 후행스팬)"
                        sql +=" VALUES"
                        sql +=" (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

                        cur.execute(sql, tuple(df.values[idx]))
                        connPy.commit()

                sql = "update stock_code_list set ta_calc_date='" + df.iloc[idx,0] + "' where stock_code='" + df.iloc[idx,1] +"'"
                cur.execute(sql)
                connPy.commit()
            else:
                pass
    except:
        pass

TA_Calc()

connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
cur = connPy.cursor()
cur.execute("use sstock")

sql = "SELECT ta.거래날자, ta.종목코드, ta.Open, ta.High, ta.Low, ta.Close, ta.Volume,"
sql += " ta.MA5, ta.MA10, ta.MA20, ta.MA60, ta.MA120, ta.MA240,"
sql += " ta.VMA5, ta.VMA10, ta.VMA20, ta.VMA60, ta.VMA120, ta.VMA240, ta.up_band, ta.mid_band, ta.low_band,"
sql += " ta.RSI, ta.willr14, ta.AVGwillr14, ta.willr120, ta.AVGwillr120, ta.slowk, ta.slowd, ta.STOCHRSI_fastk, ta.STOCHRSI_fastd,"
sql += " ta.psar, ta.arronOSC, ta.adx, ta.pdi, ta.mdi, ta.HA_Close, ta.HA_Open, ta.HA_High, ta.HA_Low"
sql += " FROM ta ta where ta.종목코드='005930' and ta.거래날자>'20210101'"


df = pd.read_sql_query(sql, connPy)

#최대값 찿는 방법
column = df["up_band"]
max_value_price = column.max()

column = df["Volume"]
max_value_volume = column.max()

df['pOpen'] = df['Open']/max_value_price*100
df['pHigh'] = df['High']/max_value_price*100
df['pLow'] = df['Low']/max_value_price*100
df['pClose'] = df['Close']/max_value_price*100

df['pMA5'] = df['MA5']/max_value_price*100
df['pMA10'] = df['MA10']/max_value_price*100
df['pMA20'] = df['MA20']/max_value_price*100
df['pMA60'] = df['MA60']/max_value_price*100
df['pMA120'] = df['MA120']/max_value_price*100
df['pMA240'] = df['MA240']/max_value_price*100

df['pup_band'] = df['MA60']/max_value_price*100
df['pmid_band'] = df['MA120']/max_value_price*100
df['plow_band'] = df['MA240']/max_value_price*100

df['pVMA5'] = df['VMA5']/max_value_volume*100   #5거래량이평
df['pVMA20'] = df['VMA20']/max_value_volume*100 #20거래량이평

df['pMA5-pMA20']=df['pMA5'] -df['pMA20'] + 50   #오일이평과 20일 이평의 간격
df['pMA5-pMA60']=df['pMA5'] -df['pMA60'] + 50   #오일이평과 60일 이평의 간격

# tickmark
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

t = np.arange(0.0, 100.0, 0.01)
s = np.sin(2 * np.pi * t) * np.exp(-t * 0.01)

fig, ax = plt.subplots()
ax.plot(t, s)

ax.xaxis.set_minor_locator(AutoMinorLocator())

ax.tick_params(which='both', width=2)
ax.tick_params(which='major', length=7)
ax.tick_params(which='minor', length=4, color='r')

plt.show()


# libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
 
# Data
#df=pd.DataFrame({'x_values': range(1,11), 'y1_values': np.random.randn(10), 'y2_values': np.random.randn(10)+range(1,11), 'y3_values': np.random.randn(10)+range(11,21) })
 
# multiple line plots
plt.plot( '거래날자', 'Open', data=df, marker='', markerfacecolor='blue', markersize=1, color='skyblue', linewidth=2)
plt.plot( '거래날자', 'High', data=df, marker='', markerfacecolor='blue', markersize=1, color='skyblue', linewidth=2)
plt.plot( '거래날자', 'Low', data=df, marker='', color='olive', linewidth=2)
plt.plot( '거래날자', 'Close', data=df, marker='', color='olive', linewidth=2, linestyle='solid')
plt.plot( '거래날자', 'up_band', data=df, marker='', color='red', linewidth=2, linestyle='solid')
plt.plot( '거래날자', 'low_band', data=df, marker='', color='blue', linewidth=2, linestyle='solid')

plt.grid(True, axis='y', color='red', alpha=0.5, linestyle='--')
# show legend
#plt.legend()

# show graph
plt.show()



import matplotlib.pyplot as plt
import numpy as np

plt.style.use('_mpl-gallery')

# make data
np.random.seed(1)
x = np.linspace(0, 8, 16)
y1 = 3 + 4*x/8 + np.random.uniform(0.0, 0.5, len(x))
y2 = 1 + 2*x/8 + np.random.uniform(0.0, 0.5, len(x))

# plot
fig, ax = plt.subplots()

ax.fill_between(x, y1, y2, alpha=.5, linewidth=0)
ax.plot(x, (y1 + y2)/2, linewidth=2)

ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
       ylim=(0, 8), yticks=np.arange(1, 8))

plt.show()

# select 종목코드, 종목명 from ta Where close>up_band and 거래날자> 20220204 and AVGwillr14>-50 and AVGwillr120<-20

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
import numpy as np

# tickmark
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
from matplotlib import style


connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
cur = connPy.cursor()
cur.execute("use sstock")

sql = "SELECT ta.거래날자, concat(substring(거래날자, 1, 4),'-',substring(거래날자, 5, 2),'-',substring(거래날자, 7, 2)) as Date, ta.종목코드, ta.종목명, ta.Open, ta.High, ta.Low, ta.Close, ta.Open-ta.Close as OC, ta.Volume,"
sql = "SELECT concat(substring(ta.거래날자, 1, 4),'-',substring(ta.거래날자, 5, 2),'-',substring(ta.거래날자, 7, 2)) as Date, ta.종목코드, ta.종목명, ta.Open, ta.High, ta.Low, ta.Close, ta.Open-ta.Close as OC, ta.Volume,"

sql += " ta.MA5, ta.MA10, ta.MA20, ta.MA60, ta.MA120, ta.MA240,"
sql += " ta.VMA5, ta.VMA10, ta.VMA20, ta.VMA60, ta.VMA120, ta.VMA240, ta.up_band, ta.mid_band, ta.low_band,"
sql += " ta.RSI, ta.willr14, ta.AVGwillr14, ta.willr120, ta.AVGwillr120, ta.slowk, ta.slowd, ta.STOCHRSI_fastk, ta.STOCHRSI_fastd,"
sql += " ta.psar, ta.arronOSC, ta.adx, ta.pdi, ta.mdi, ta.HA_Close, ta.HA_Open, ta.HA_High, ta.HA_Low"
sql += " FROM ta ta where ta.종목코드='318020' and ta.거래날자>'20210701'"

# '094820' 일진파워
# 318020 포인트모바일
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

df['pup_band'] = df['up_band']/max_value_price*100
df['pmid_band'] = df['mid_band']/max_value_price*100
df['plow_band'] = df['low_band']/max_value_price*100

df['pVMA5'] = df['VMA5']/max_value_volume*100   #5거래량이평
df['pVMA20'] = df['VMA20']/max_value_volume*100 #20거래량이평

df['pMA5-pMA20']=df['pMA5'] -df['pMA20'] + 20   #오일이평과 20일 이평의 간격
df['pMA5-pMA60']=df['pMA5'] -df['pMA60'] + 20   #오일이평과 60일 이평의 간격

'''
# libraries

 
# Data
#df=pd.DataFrame({'x_values': range(1,11), 'y1_values': np.random.randn(10), 'y2_values': np.random.randn(10)+range(1,11), 'y3_values': np.random.randn(10)+range(11,21) })
 
# multiple line plots
# plt.plot( '거래날자', 'pOpen', data=df, marker='', markerfacecolor='blue', markersize=1, color='skyblue', linewidth=2)
# plt.plot( '거래날자', 'pHigh', data=df, marker='', markerfacecolor='blue', markersize=1, color='skyblue', linewidth=2)
# plt.plot( '거래날자', 'pLow', data=df, marker='', color='olive', linewidth=2)
#plt.title(df('종목명'))
plt.figure(figsize=(20,10))
plt.subplot(2, 1, 1)
plt.plot( '거래날자', 'pClose', data=df, marker='o', color='crimson', linewidth=1, linestyle='solid')
#plt.plot( '거래날자', 'pup_band', data=df, marker='', color='firebrick', linewidth=1, linestyle='solid')
#plt.plot( '거래날자', 'pmid_band', data=df, marker='', color='pink', linewidth=1, linestyle='solid')
#plt.plot( '거래날자', 'plow_band', data=df, marker='', color='blue', linewidth=1, linestyle='solid')
de
plt.plot( '거래날자', 'pMA5', data=df, marker='', color='blue', linewidth=1, linestyle='solid')

plt.plot( '거래날자', 'pMA5-pMA20', data=df, marker='', color='red', linewidth=1, linestyle='solid')
plt.plot( '거래날자', 'pMA5-pMA60', data=df, marker='', color='blue', linewidth=1, linestyle='solid')

# plt.plot( '거래날자', 'pMA20', data=df, marker='', color='blue', linewidth=2, linestyle='solid')
plt.plot( '거래날자', 'pVMA5', data=df, marker='', color='blue', linewidth=1, linestyle='solid')
plt.plot( '거래날자', 'pVMA20', data=df, marker='', color='black', linewidth=1, linestyle='solid')

plt.fill_between(df.index, df['pup_band'], df['pmid_band'], where=df['pup_band'] >= df['pmid_band'], facecolor='red', alpha=0.1)
plt.fill_between(df.index, df['pmid_band'], df['plow_band'], where=df['pmid_band'] >= df['plow_band'], facecolor='blue', alpha=0.2)

plt.fill_between(df.index, df['pVMA5'], df['pVMA20'], where=df['pVMA5'] >= df['pVMA20'], facecolor='red', alpha=0.2)
plt.fill_between(df.index, df['pVMA5'], df['pVMA20'], where=df['pVMA5'] < df['pVMA20'], facecolor='green', alpha=0.2)
plt.grid(True, axis='y', color='red', alpha=0.5, linestyle='--')

# show legend
#plt.legend()

# show graph
#ax.xaxis.set_minor_locator(AutoMinorLocator())

#plt.figure(figsize=(20,5))
plt.legend(loc='upper left')
plt.subplot(2, 1, 2)
plt.legend(df.columns)
plt.plot( '거래날자', 'adx', data=df, marker='', color='black', linewidth=1, linestyle='solid')
plt.plot( '거래날자', 'pdi', data=df, marker='', color='red', linewidth=1, linestyle='solid')
plt.plot( '거래날자', 'mdi', data=df, marker='', color='blue', linewidth=1, linestyle='solid')

plt.legend(loc='upper left')
plt.ylim(0,100)
plt.grid(which="major", color='k', linestyle='-.', linewidth=0.5)
plt.show()
'''
# from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
import mplfinance as mpf



# df['Close'].plot()
# plt.grid(which="major", color='k', linestyle='-.', linewidth=0.5)



import mplfinance as mf

df['Low'].plot(grid = True)
df['High'].plot(secondary_y = ['High'])

#df[['Close','Open']].plot(grid = True)
#plt.plot(secondary_y = df[['High']], grid = True)

plt.show()

'''


'''
import yfinance as yf
import talib as ta
import pandas as pd
import matplotlib.pyplot as plt

def Ichimoku_Cloud(df):
        '''
        Get the values of Lines for Ichimoku Cloud
        args:
            df: Dataframe
        '''
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
        #d[['전환선','기준선','선행스팬1','선행스팬2','후행스팬']].plot(figsize=(12,12))
        #plt.show()
        return d.sort_index(ascending=True)


def HA(df):
    df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    df['HA_Open'] = (df['Open'].shift(1) + df['Open'].shift(1)) / 2
    df.iloc[0, df.columns.get_loc("HA_Open")] = (df.iloc[0]['Open'] + df.iloc[0]['Close'])/2
    df['HA_High'] = df[['High', 'Low', 'HA_Open', 'HA_Close']].max(axis=1)
    df['HA_Low'] = df[['High', 'Low', 'HA_Open', 'HA_Close']].min(axis=1)
    df = df.drop(['Open', 'High', 'Low', 'Close'], axis=1)  # remove old columns
    df = df.rename(columns={"HA_Open": "Open", "HA_High": "High", "HA_Low": "Low", "HA_Close": "Close", "Volume": "Volume"})
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]  # reorder columns
    return df

# power = yf.Ticker("POWERGRID.NS")
power = yf.Ticker('005380.KS')

df = power.history(start="2021-01-01", end='2022-02-04')
df.head()
Ichimoku_Cloud(df)

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




df['adx'] = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)       # ADX - Average Directional Movement Index
df['pdi'] = ta.PLUS_DI(df['High'], df['Low'], df['Close'], timeperiod=14)   #PLUS_DI - Plus Directional Indicator
df['mdi'] = ta.MINUS_DI(df['High'], df['Low'], df['Close'], timeperiod=14)  #MINUS_DI - Minus Directional Indicator



# df['Hhigh'], df['Hopen'], df['Hclose'], df['Hlow'] = 
HA(df) # ['High'], df['Open'], df['Close'], df['Low'])  #Heikin Ashi



#Ichimoku_Cloud(df)
print(df.head)
#df[['Close','MA5','MA20','MA60','MA120','VMA5','VMA20']].plot(figsize=(12,12))
df[['Close','MA5','MA20','MA60','MA120']].plot(figsize=(12,12))
plt.show()

#df['BBAND_UPPER'],df['BBAND_MIDDLE'],df['BBAND_LOWER'] = ta.BBANDS(df['close'],20,2)

# df['up_band'], df['mid_band'], df['low_band'] = ta.BBANDS(df['Close'], timeperiod =20)
# df[['Close','up_band','mid_band','low_band']].plot(figsize= (12,10))
# plt.show()


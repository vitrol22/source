import plotly.graph_objs as go
import plotly.offline
import pymysql
pymysql.install_as_MySQLdb()
import pandas as pd

import talib as ta

import sys

import pymysql
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton
from PyQt5.QtWidgets import *

import pymysql
from sqlalchemy import create_engine

pymysql.install_as_MySQLdb()
#import MySQLdb

import talib as ta
import plotly.express as px
colors = px.colors.qualitative.Plotly
from plotly.subplots import make_subplots

from PyQt5.QtGui import QFont
from PyQt5 import uic

from ast import Continue
from pykrx import stock
import datetime
from pykrx.website import krx
from pykrx.website import naver
from pandas import DataFrame
import requests
from bs4 import BeautifulSoup
import time
import numpy as np
#import mysql.connector

def make_df(df,종목코드):
    connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
    cur = connPy.cursor()
    cur.execute("use sstock")
    sql="select S.MarketOpenDate from (select MarketOpenDate from tradingdate order by MarketOpenDate desc limit 60) as S order by S.MarketOpenDate asc limit 1"
    cur.execute(sql) 
    before240ago = cur.fetchall()

    sql ="SELECT 거래날자, 종목코드, 종목명,"
    sql += " IF(ta.Close > ta.MA5, 5, 0)"
    sql += " + IF(ta.MA5 > ta.MA20, 5, 0)"
    sql += " + IF(ta.MA20 > ta.MA60, 5, 0)"
    sql += " + IF(ta.Close > ta.psar, 5, 0)"
    sql += " + IF(ta.macd > ta.macdSignal, 5, 0)"
    sql += " + IF(ta.slowk > ta.slowd, 5, 0)"
    sql += " + IF(ta.RSI > RSIMA5, 5, 0)"
    #sql += " + IF(ta.STOCHRSI_fastk > STOCHRSI_fastd, 5, 0)"
    sql += " + IF(ta.pdi > ta.mdi, 5, 0)"
    sql += " + IF(ta.HA_Close > ta.HA_Open, 5, 0)"
    sql += " + IF(ta.Close > ta.mid_band, 5, 0)"
    sql += " + IF(ta.Volume > ta.VMA5, 5, 0)"
    sql += " + IF(ta.VMA5 > ta.VMA10, 5, 0)"
    sql += " + IF(ta.VMA10 > ta.VMA20, 5, 0)"
    sql += " + IF(ta.willr120 > ta.AVGwillr120, 5, 0)"
    sql += " + IF(ta.willr14 > ta.AVGwillr14, 5, 0)"
    sql += " AS resultSUM,"


    #sql = "SELECT ta.거래날자, concat(substring(거래날자, 1, 4),'-',substring(거래날자, 5, 2),'-',substring(거래날자, 7, 2)) as Date, ta.종목코드, ta.종목명, ta.Open, ta.High, ta.Low, ta.Close, ta.Open-ta.Close as OC, ta.Volume,"
    sql += " ta.Open, ta.High, ta.Low, ta.Close, ta.Open-ta.Close as OC, ta.Volume,"
    sql += " ta.MA5, ta.MA10, ta.MA20, ta.MA60, ta.MA120, ta.MA240,"
    sql += " ta.VMA5, ta.VMA10, ta.VMA20, ta.VMA60, ta.VMA120, ta.VMA240, ta.up_band, ta.mid_band, ta.low_band,"
    sql += " ta.RSI, ta.willr14, ta.AVGwillr14, ta.willr120, ta.AVGwillr120, ta.slowk, ta.slowd, ta.STOCHRSI_fastk, ta.STOCHRSI_fastd,"
    sql += " ta.psar, ta.arronOSC, ta.adx, ta.pdi, ta.mdi, ta.HA_Close, ta.HA_Open, ta.HA_High, ta.HA_Low, ta.macd,ta.macdSignal"
    sql += " FROM ta"
    
    sql += " where ta.종목코드='"+종목코드+"'"

    sql += " and ta.거래날자>='"+before240ago[0][0]+"'"
    sql += " ORDER BY 거래날자 ASC"

    df = pd.read_sql_query(sql, connPy)
    if df.empty==False:
        #최대값 찿는 방법
        #column = df["up_band"]
        if df["up_band"].max()>df["High"].max():
            max_value_price = df["up_band"].max()
        else:
            max_value_price = df["High"].max()

        # column = df["Volume"]
        max_value_volume = df["Volume"].max()

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
        df.fillna(0)

        df['resultSUMMA10'] = ta.SMA(df['resultSUM'],10)

        df['ppsar'] = df['psar']/max_value_price*100
        df['pVMA5'] = df['VMA5']/max_value_volume*100   #5거래량이평
        df['pVMA20'] = df['VMA20']/max_value_volume*100 #20거래량이평

        df['pMA5-pMA20']=(df['MA5']-df['MA20'])/max_value_price*100 + 50   #오일이평과 20일 이평의 간격
        df['pMA5-pMA60']=(df['MA5']-df['MA60'])/max_value_price*100 + 50   #오일이평과 60일 이평의 간격
        ####################################################################################################################################


    return df

'''


specs=[[{"type": "scatter"}],[{"type": "scatter"}],[{"type": "scatter"}],[{"type": "scatter"}]]
specs=[
    [{'secondary_y':False}],
    [{'secondary_y':True}],
    [{'secondary_y':True}],
    [{'secondary_y':False}]
]
'''


def add_trace(fig,df,row,col):

    df_PSAR=df[['거래날자','Close','psar']] .copy()  #dataframe 을 분리
    df_PSAR.drop(df_PSAR.loc[df['Close']<df['psar']].index, inplace=True) # 음인 경우삭제

    for idx in range(2,len(df_PSAR),1):
        if df_PSAR.index[idx-1]-df_PSAR.index[idx-2]>1 and df_PSAR.index[idx]-df_PSAR.index[idx-1]>1:  
            df_PSAR.loc[df_PSAR.index[idx-1]-1]=[df_PSAR.iat[idx-1,0],df_PSAR.iat[idx-1,1], df_PSAR.iat[idx-1,2]]

    df_PSAR = df_PSAR.sort_index()  # sorting by index
    #df_PSAR.to_csv('C:/datadisk/test.csv', encoding='utf-8-sig')
    df_PSAR= df_PSAR.reset_index()
    df_PSAR.rename(columns = {'index':'oldindex'},inplace=True)


    for idx in range(2,len(df_PSAR),1):
        #if df_PSAR['거래날자'].index[idx-1]-df_PSAR['거래날자'].index[idx-2]==1 and df_PSAR['거래날자'].index[idx]-df_PSAR['거래날자'].index[idx-1]==1 :
        #    df_PSAR.loc[df_PSAR['거래날자'].index[idx-1],'Close']=None
        if df_PSAR.iat[idx-1,0]-df_PSAR.iat[idx-2,0]==1 and df_PSAR.iat[idx,0]-df_PSAR.iat[idx-1,0]==1 :        
            df_PSAR.iat[idx-1,3]=None

    df_PSAR  = df_PSAR.dropna(subset=['psar'])
    df_PSAR.loc[df_PSAR['거래날자'].index,'거래날자']=df_PSAR['거래날자'].index
    #df_PSAR.rename(columns = {'Posi_PSAR':'Posi_PSAR'},inplace=True)

    df_PSAR = df_PSAR.drop(columns=['거래날자','Close','psar'], axis=1).copy() #필요없는 컬럼삭제
    df_PSAR= df_PSAR.reset_index()

    shape_list = []  # 실적발표 기간을 나타내는 하이라이팅을 담당해 줄 dict 데이터를 리스트 변수에 담는다.
    '''
    ####################################################################################################################################
    # Stochastic 가 양인 경우 색상으로 표시
    df_stoch=df[['거래날자', 'slowk', 'slowd']]     #dataframe 을 분리
    #for idx in range(2,len(df_stoch),1):
    df_stoch.drop(df_stoch.loc[df_stoch['slowk']<df_stoch['slowd']].index, inplace=True) # 음인 경우삭제
    # 하루만 k>d 이고 바로k<0 인경우 하루를 더 넣어야 한다.
    for idx in range(2,len(df_stoch),1):
        if df_stoch.index[idx-1]-df_stoch.index[idx-2]>1 and df_stoch.index[idx]-df_stoch.index[idx-1]>1:  
            df_stoch.loc[df_stoch.index[idx-1]-1]=[df_stoch.iat[idx-1,0],df_stoch.iat[idx-1,1], df_stoch.iat[idx-1,2]] 
    
    df_stoch = df_stoch.sort_index()  # sorting by index
    df_stoch.to_csv('C:/datadisk/test.csv', encoding='utf-8-sig')
    df_stoch= df_stoch.reset_index()
    df_stoch.rename(columns = {'index':'oldindex'},inplace=True)

    for idx in range(2,len(df_stoch),1):
        if df_stoch.iat[idx-1,0]-df_stoch.iat[idx-2,0]==1 and df_stoch.iat[idx,0]-df_stoch.iat[idx-1,0]==1 :        
            df_stoch.iat[idx-1,3]=None

    df_stoch  = df_stoch.dropna(subset=['slowd'])
    df_stoch.loc[df_stoch['거래날자'].index,'거래날자']=df_stoch['거래날자'].index
    df_stoch.rename(columns = {'거래날자':'Posi_stoch'},inplace=True)

    df_stoch = df_stoch.drop(columns=['slowk','slowd','Posi_stoch'], axis=1) #필요없는 컬럼삭제
    df_stoch= df_stoch.reset_index()
    df_stoch.to_csv('C:/datadisk/testF.csv', encoding='utf-8-sig')
    ####################################################################################################################################
    '''
    ####################################################################################################################################
    # MACD 가 양인 경우 색상으로 표시
    df_macd=df[['거래날자', 'macd', 'macdSignal']].copy()     #dataframe 을 분리
    #for idx in range(2,len(df_macd),1):
    df_macd.drop(df_macd.loc[df_macd['macd']<df_macd['macdSignal']].index, inplace=True) # 음인 경우삭제
    # 하루만 k>d 이고 바로k<0 인경우 하루를 더 넣어야 한다.
    for idx in range(2,len(df_macd),1):
        if df_macd.index[idx-1]-df_macd.index[idx-2]>1 and df_macd.index[idx]-df_macd.index[idx-1]>1:  
            df_macd.loc[df_macd.index[idx-1]-1]=[df_macd.iat[idx-1,0],df_macd.iat[idx-1,1], df_macd.iat[idx-1,2]] 
    
    df_macd = df_macd.sort_index()  # sorting by index
    #df_macd.to_csv('C:/datadisk/macdINIT.csv', encoding='utf-8-sig')
    df_macd= df_macd.reset_index()
    df_macd.rename(columns = {'index':'oldindex'},inplace=True)

    for idx in range(2,len(df_macd),1):
        if df_macd.iat[idx-1,0]-df_macd.iat[idx-2,0]==1 and df_macd.iat[idx,0]-df_macd.iat[idx-1,0]==1 :        
            df_macd.iat[idx-1,3]=None

    df_macd  = df_macd.dropna(subset=['macdSignal']).copy()
    #df_macd.loc[df_macd['거래날자'].index,'거래날자']=df_macd['거래날자'].index
    #df_macd.rename(columns = {'거래날자':'Posi_macd'},inplace=True)

    df_macd = df_macd.drop(columns=['거래날자','macd','macdSignal'], axis=1) #필요없는 컬럼삭제
    df_macd= df_macd.reset_index()
    #df_macd.to_csv('C:/datadisk/MACD.csv', encoding='utf-8-sig')
    ####################################################################################################################################



    '''
    # 홀수면 마지막의 데이터로 한 줄을 더 추가 box를 그리고 안을 색으로 채운다
    if len(df_PSAR)%2 == 1:
        df_PSAR.loc[len(df_PSAR)]=[df_PSAR.iat[len(df_PSAR)-1,0],df_PSAR.iat[len(df_PSAR)-1,0]]
    for num in range(0,len(df_PSAR), 2):
        shape_list.append(dict(
                type="rect",
                xref="x", yref="paper",
                x0=str(df_PSAR.iat[num, 1]),y0=0.0,
                x1=str(df_PSAR.iat[num+1,1]),y1=1,
                fillcolor="LightSalmon",
                #fillcolor = 'rgba(168, 216, 234, 0.5)'
                #fillcolor="LightSeaGreen",
                opacity=0.3,
                layer="below",
                line_width=0,
            ))


    # 홀수면 마지막의 데이터로 한 줄을 더 추가 box를 그리고 안을 색으로 채운다
    if len(df_stoch)%2 == 1:
        df_stoch.loc[len(df_stoch)]=[df_stoch.iat[len(df_stoch)-1,1],df_stoch.iat[len(df_stoch)-1,1]]

    for num in range(0,len(df_stoch), 2):
        shape_list.append(dict(
                type="rect",
                xref="x", yref="paper", 
                x0=str(df_stoch.iat[num, 1]),y0=0.23,            
                x1=str(df_stoch.iat[num+1,1]),y1=0.95,            
                fillcolor="LightSalmon",
                #fillcolor = 'rgba(168, 216, 234, 0.5)'
                #fillcolor="LightSeaGreen",
                opacity=0.7,
                layer="below",
                line_width=0,

            ))
    '''

    # 홀수면 마지막의 데이터로 한 줄을 더 추가 box를 그리고 안을 색으로 채운다
    if len(df_macd)%2 == 1:
        df_macd.loc[len(df_macd)]=[df_macd.iat[len(df_macd)-1,1],df_macd.iat[len(df_macd)-1,1]]

    for num in range(0,len(df_macd), 2):
        shape_list.append(dict(
                type="rect",
                xref="x", yref="paper", 
                x0=str(df_macd.iat[num, 1]),y0=0.23,            
                x1=str(df_macd.iat[num+1,1]),y1=1,            
                fillcolor="LightSalmon",
                #fillcolor = 'rgba(168, 216, 234, 0.5)'
                #fillcolor="LightSeaGreen",
                opacity=0.3,
                layer="below",
                line_width=0,
            ))

    '''
    shape_list.append(dict(
                type="rect",
                #xref="x", yref="paper",
                # xref="paper", yref="y",
                #xref="x domain", yref="y domain",  
                xref="x", yref="paper",          
                x0="50",y0=0,            
                x1="51",y1=1,
                #fillcolor="LightSeaGreen",
                fillcolor="Red",
                opacity=0.3,
                layer="below",
                line_width=0))
    '''

    '''
    fig = make_subplots(
        rows=2, cols=1,
        #column_widths=[.6,.6,.6, 5],
        row_width=[.6,.6,.6, 5],
        shared_xaxes=True,
        vertical_spacing=0.01,
        specs=specs,
        print_grid=True,
        #column_width=[2],
        #subplot_titles="  시  험   ",
        #secondary_y=True,
        )
    '''
    fig.add_trace(go.Scatter(x=df.index,y=df.pup_band,opacity=0.9,line=dict(color='rgb(204, 0, 0)',width=1)),row=row,col=col)
    fig.add_trace(go.Scatter(x=df.index,y=df.pmid_band,mode="lines",fill="tonexty",fillcolor="rgba(200, 0, 0, 0.1)",line=dict(color="rgba(255, 0, 0, 0.1)"),),row=row,col=col)
    fig.add_trace(go.Scatter(x=df.index,y=df.pmid_band,line=dict(color=colors[0])),row=row,col=col)
    fig.add_trace(go.Scatter(x=df.index,y=df.plow_band,mode="lines",fill="tonexty",fillcolor="rgba(0, 0, 200, 0.1)",line=dict(color="rgba(0, 0, 255, 0.2)",width=1),),row=row,col=col)

    #fig.add_trace(go.Scatter(x=df.index,y=df.plow_band,line=dict(color='rgb(0, 0, 204)', width=3)))

    fig.add_trace(go.Candlestick(x=df.index,open=df.pOpen,high=df.pHigh,low=df.pLow,close=df.pClose,increasing_line_color='rgb(204, 0, 0)', decreasing_line_color='rgb(0, 0, 204)'),row=row,col=col)
    fig.add_trace(go.Scatter(x=df.index,y=df.resultSUM,line=dict(color='rgb(153, 0, 53)',width=1),name='resultSUM'),row=row,col=col)
    fig.add_trace(go.Scatter(x=df.index,y=df.resultSUMMA10,line=dict(color='rgb(153, 0, 53)',width=2),name='resultSUMMA10'),row=row,col=col)
    fig.add_hline(y=35,line=dict(color='rgb(153, 0, 53)',width=1))
    fig.add_hline(y=20,line=dict(color='rgb(153, 0, 53)',width=1))

    #fig.add_trace(go.Bar(x=df.index,y=df.Volume),secondary_y=True)
    fig.add_trace(go.Scatter(x=df.index,y=df.pMA5,line=dict(color='rgb(0, 204, 204)',width=1),name='MA5'),row=row,col=col) 
    fig.add_trace(go.Scatter(x=df.index,y=df.pMA20,line=dict(color='orange',width=1),name='MA20'),row=row,col=col)              
    fig.add_trace(go.Scatter(x=df.index,y=df.pMA60,line=dict(color='green',width=1),name='MA60'),row=row,col=col)
    fig.add_trace(go.Scatter(x=df.index,y=df.pMA120,line=dict(color='black',width=1),name='MA120'),row=row,col=col)
    #fig.add_trace(go.Scatter(x=df.index,y=df.ppsar,line=dict(color='black',width=3),name='ppsar'),row=row,col=col)


    fig.add_trace(go.Scatter(x=df.index,y=df.pVMA5,line=dict(color='rgb(0, 0, 204)',width=1),name='VMA5'),row=row,col=col)              
    fig.add_trace(go.Scatter(x=df.index,y=df.pVMA20,line=dict(color='rgb(0, 0, 204)',width=2),name='VMA20',    
        xperiodalignment="middle",hovertemplate="%{y}%{_xother}"),row=row,col=col,)
    fig.add_trace(go.Scatter(x=df.index,y=df['pMA5-pMA20'],line=dict(color='rgb(0, 204, 0)',width=2),name='pMA5pMA20'),row=row,col=col)              
    fig.add_hline(y=50,line=dict(color='rgb(0, 204, 0)',width=1))

    #fig.add_trace(go.Scatter(x=df.index,y=df['pMA5-pMA60'],line=dict(color='rgb(0, 204, 0)',width=2),name='pMA5-pMA60'),row=row,col=col)
    #fig.add_trace(go.Scatter(x=df.index,y=df['공매도잔고비중']+50,line=dict(color='rgb(0, 204, 204)',width=2),name='공매도잔고비중'), row=1, col=1)


    #fig.add_trace(go.Scatter(x=df.index,y=df['slowk'],line=dict(color="red",width=1),name='slowk'), row=2, col=1)
    #fig.add_trace(go.Scatter(x=df.index,y=df['slowd'],line=dict(color="blue",width=1),name='slowd'), row=2, col=1)
    #fig.update_yaxes(title_text='Sto', row=2, col=1)


    fig.update_yaxes(title_text='', row=row, col=col)
    fig.update_xaxes(rangeslider_visible=False)    
    #fig.for_each_xaxis(lambda axis: axis.title.update(font=dict(color = 'blue', size=5)))
    #fig.for_each_yaxis(lambda axis: axis.title.update(font=dict(color = 'blue', size=5)))

    #################################################################################################################################
    
def make_plot(fig):

    fig.update_layout(xaxis_rangeslider_visible=False)#,shapes=shape_list)
    if colC==1:
        fig['layout'].update(height=row*400, width=2000) #,title={'text': '<b>'+df.종목명[0]+'</b>', 'font': {'size': 20}})
    else:
        fig['layout'].update(height=row*400, width=1000) #,title={'text': '<b>'+df.종목명[0]+'</b>', 'font': {'size': 20}})
    fig.update(layout_showlegend=False)
    #fig.update_layout(title_text=df.종목명[0],title_x=0.5,title_y=0.87)

    #large_title_format = "<span style='font-size:15px; font-family:Tahoma'>"+df.종목명[0]
    #small_title_format = "<span style='font-size:10px; font-family:Tahoma'>색상이 진하면 사세요."

    fig.update_layout(
                    #title=large_title_format + "     " + small_title_format, height=400,
                    #margin=dict(t=130, b=0, l=70, r=40),
                    margin=dict(t=30, b=0, l=70, r=40),
                    xaxis_rangeslider_visible=False,
                    #hovermode="x unified", 
                    
                    xaxis_title=None, yaxis_title=None,
                    #plot_bgcolor='#333', paper_bgcolor='#333',
                    #title_font=dict(size=25, color='#8a8d93', family="Lato, sans-serif"),
                    font=dict(color='#8a8d93'),
                    legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5))

    #fig.update_xaxes(showspikes=True)
    #fig.update_yaxes(showspikes=True)

    fig.update_xaxes(showspikes=True,spikecolor="green",spikethickness=1,spikedash="dot",spikesnap="cursor",spikemode="across")
    fig.update_yaxes(showspikes=True,spikecolor="orange",spikethickness=1,spikedash="dot",spikesnap="cursor",spikemode="across")
    #fig.update_layout(spikedistance=10000, hoverdistance=100)

    #fig.update_xaxes(ticks="inside",col=1,nticks=12,tickangle=25, tickfont=dict(family='Rockwell', color='black',size=8))
    #fig.update_yaxes(ticks="inside",col=1,nticks=10,tickangle=0,tickfont=dict(family='Rockwell',color='black',size=8))
    fig.update_xaxes(ticks="inside",nticks=12,tickangle=25, tickfont=dict(family='Rockwell', color='black',size=8))
    fig.update_yaxes(ticks="inside",nticks=10,tickangle=0,tickfont=dict(family='Rockwell',color='black',size=8))

    #fig.update_yaxes(range=[0, 100])
    fig.update_layout(hoverlabel=dict(bgcolor="white",font_size=9,font_family="Rockwell"))
    fig.update_yaxes(ticklabelposition="inside top", title=None)
    fig.update_layout(xaxis_range=[0,240])
    fig.update_layout(yaxis_range=[0,100])
    fig.update_annotations(font_size=12)
    
import os, sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5 import QtWebEngineWidgets

class PlotlyViewer(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, fig, exec=True):
        # Create a QApplication instance or use the existing one if it exists
        self.app = QApplication.instance() if QApplication.instance() else QApplication(sys.argv)

        super().__init__()

        self.file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp.html"))
        plotly.offline.plot(fig, filename=self.file_path, auto_open=False)
        self.load(QUrl.fromLocalFile(self.file_path))
        self.setWindowTitle("Plotly Viewer")
        self.show()

        if exec:
            self.app.exec_()

    def closeEvent(self, event):
        os.remove(self.file_path)

if __name__ == "__main__":
    #선정된 오늘의 종목을 구한다.
#   for loop
#       총수를 기준으로 reo, column 수를 결정
#       sub 데이터를 가져오고 df 계산
#       sub add_plot
#   plot

    connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
    cur = connPy.cursor()
    cur.execute("use sstock")

    sql="SELECT SaveDate FROM selected_stock ORDER BY SaveDate DESC LIMIT 1"
    cur.execute(sql) 
    p_day = cur.fetchall()


    sql=f"SELECT DISTINCT SaveDate, 종목명, 종목코드, 선정이유 FROM selected_stock WHERE SaveDate={p_day[0][0]}"
    sql+=" and (선정이유='1오일거래량세배' or 선정이유='2볼린저돌파') order by 선정이유"# limit 8"

    sql="SELECT DISTINCT SaveDate, 종목명, 종목코드, 선정이유 FROM selected_stock WHERE SaveDate='20220218'"
    sql+=" and (선정이유='1오일거래량세배' or 선정이유='2볼린저돌파') order by 선정이유 limit 8"
    #sql=f"SELECT SaveDate, 종목명, 종목코드, 선정이유 FROM selected_stock WHERE SaveDate={p_day[0][0]}"
    
    selected_stock = pd.read_sql_query(sql, connPy)

    #selected_stock = pd.read_csv ('C:\DataDisk\Python\finance\tests\보유.csv')
    #selected_stock = pd.read_csv ('C:/DataDisk/Python/finance/tests/보유.csv', encoding='CP949')
    selected_stock = pd.read_excel('C:/DataDisk/Python/finance/tests/보유.xlsx', sheet_name='보유')


    #writer = pd.ExcelWriter('daum_real_time_keyword.xlsx')
    #df.to_excel('C:/DataDisk/Python/finance/tests/관심종목.xlsx', '보유', index=False)
    #writer.save()

    #dfPSAR=df[['거래날자','High','Low']].copy()    #dataframe 을 분리

    selected_stock =selected_stock[['종목명','선정이유']]
    sql="SELECT 종목코드, 종목명 FROM stock_code_list"
    stock_code = pd.read_sql_query(sql, connPy)
    selected_stock = pd.merge(selected_stock, stock_code)#, left_on='종목명', right_on='종목명', how='outer')
    
    #for idx in range(len(selected_stock)):
    #    len(str(selected_stock.종목코드[idx]))

        # '{0:06d}'.format(selected_stock.종목코드[idx]) #종목코드를 6개자리로 변경

        #selected_stock ['종목코드']=selected_stock ['종목코드'].map('{0:06d}'.format(selected_stock.종목코드[idx]))
    #    selected_stock['종목코드'].replace([selected_stock.종목코드[idx]], '{0:06d}'.format(selected_stock.종목코드[idx]))


    # selected_stock = cur.fetchall()
    #title_list=[]
#'<b>'+df.종목명[0]+'</b>'

    rowC, colC, legend = int(int(len(selected_stock)+1)/2),2,False#(len(selected_stock)+1)%2 + 1, False
    fig = make_subplots(rows=rowC, cols=colC, horizontal_spacing=0.03,vertical_spacing= 0.01,
                #subplot_titles=([f'<b>{prov}</b>' for prov in provinces]))
                    #subplot_titles="test")
                    #subplot_titles=selected_stock.column)
                    subplot_titles = [selected_stock.종목명[idx]+selected_stock.선정이유[idx] for idx in np.arange(len(selected_stock))]
                    ) #그래프 간 간격
                    #subplot_titles=([f'<b>{selected_stock.종목명[idx]}</b>' for idx in len(selected_stock)])
    #help(make_subplots)
    #make_subplots(rows=1, cols=1, shared_xaxes=False, shared_yaxes=False, start_cell='top-left', print_grid=False, horizontal_spacing=None, vertical_spacing=None, subplot_titles=None, column_widths=None, row_heights=None, specs=None, insets=None, column_titles=None, row_titles=None, x_title=None, y_title=None, figure=None, **kwargs)

    # psar가 양인 경우에 색상을 표시하기 위하여
    

    for row in range(1,rowC+1):
        for col in range(1,colC+1):
            if len(selected_stock)>((row-1)*2+col-1):
                df=[]
                df=make_df(df,str(selected_stock.종목코드[(row-1)*2+col-1])) # ]selected_stock[(row-1)*2+col-1][2]) 
                #CSV 의 데이터에 정수로 저장되는 종목코드의 앞에 6자리 종목으로 만들기 위하여 앞에'000' 을 넣는 과정
                #df=make_df(df,str('{0:06d}'.format(selected_stock.종목코드[(row-1)*2+col-1]))) # ]selected_stock[(row-1)*2+col-1][2]) 
                #'{0:06d}'.format(selected_stock.종목코드[(row-1)*2+col-1])

                if df.empty==False: 
                    add_trace(fig,df,row,col)
    make_plot(fig)
fig.show()
#win = PlotlyViewer(fig)
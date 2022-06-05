import os, sys
from queue import Empty
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtWebEngineWidgets

import plotly.graph_objs as go
import plotly.express as px
import plotly.offline
from plotly.offline import iplot, plot
from plotly.subplots import make_subplots
colors = px.colors.qualitative.Plotly
 
from bs4 import BeautifulSoup
import datetime
import pymysql
pymysql.install_as_MySQLdb()

from ast import Continue
import pandas as pd
from pandas import DataFrame
import numpy as np

from pykrx import stock
import datetime
from pykrx.website import krx
from pykrx.website import naver

from sqlalchemy import create_engine
import time

pymysql.install_as_MySQLdb()
import pymysql
import requests
from bs4 import BeautifulSoup

import talib as ta

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        QToolTip.setFont(QFont("SansSerif", 10))

        font = QFont()
        font.setFamily('HY동녘B')
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.setFont(font)
        #self.sb = self.statusBar()
        #self.statusBar().showMessage("작업중")
        self.statusBar().repaint()

        #self.btn_theme_stock.connect(self.theme_stock)
        

        #self.btn_theme_stock.clicked.connect(self.magic)

        self.btn_collect_data.setToolTip('필요한 주가정보를 수집하고 TA-Lib를 사용하여 기술적 지표를 계산합니다.'+'\n'+
                                         '매일 수집하여야 하지만 수집하지 못한 기간의 정보도 자동으로 수집합니다.')

        self.btn_theme_stock.setToolTip('테마종목의 정보를 수집하여 theme_stock 에 저장합니다.'+'\n'+
                                        '매일 가격등락을 모으지 않고 테마에 속한 종목의 정보를 수집하고 '+'\n'+
                                        'daily 정보에서 가격의 정보를 수집합니다. 매일 정보를 수집할 필요가 '+'\n'+
                                        '없고 1주일 또는 한달 정도에 한번 정도로 충분합니다.')

        self.cb_from_date.setToolTip('plot 하기 위한 기간을 설접합니다.')
        self.cb_selected_date.setToolTip('정보가 얻어진 날자를 설정합니다. 5일전에 얻어진 정보를 표시할 수 있습니다.')

        self.cb_best_stock.setToolTip('plot 할 정보를 선택합니다.')
        self.cb_compare_stock.setToolTip('plot 하여 서로 비교할 정보를 선택합니다.')
        
        self.statusBar().showMessage('Status Bar')
        self.statusBar().repaint()

        # 버튼 처리
        self.btn_collect_data.clicked.connect(self.Whole_Data_Collect)
        self.btn_theme_stock.clicked.connect(self.theme_stock)                            

        self.cb_best_stock.activated[str].connect(self.show_multi_plot)
        #self.cb_best_stock.currentTextChanged.connect(self.show_multi_plot)        

        self.cb_compare_stock.currentTextChanged.connect(self.def_cb_compare_stock)
        self.btn_plot_again.clicked.connect(self.X2Y2plot)
        #self.btn_counter.clicked.connect(self.stop_second)

    def initUI(self):

        self.setWindowTitle("예스 스탁")
        self.setGeometry(300, 300, 700, 500) 
 
        self.statusbar = self.statusBar() # 상태바 만들기
        self.statusBar().showMessage('예스 스탁이 준비되었습니다.')
        self.statusBar().repaint()

        url = "https://finance.naver.com/sise/"
        self.browser = QWebEngineView()
        self.browser.load(QUrl(url))

        self.createGridLayout()

        self.totalL = QVBoxLayout() 

        self.topL = QHBoxLayout()
        self.topL.addWidget(self.horizontalGroupBox)    # < --
        #self.setLayout(self.topL)                       # < --
        
        self.middleL = QHBoxLayout()
        self.middleL.addWidget(self.browser)               
        self.totalL.addLayout(self.topL,1)       
        self.totalL.addLayout(self.middleL,50)

        w = QWidget()
        w.setLayout(self.totalL)
        self.setCentralWidget(w)

        #self.syncComboBox()
        #self.cb_compare_stock.activated[str].connect(self.cb_compare_stock)
        
        #self.cbCommunes.currentIndexChanged.connect(self.selectionChange)


        self.show()

    def createGridLayout(self):
        self.btn_collect_data  = QPushButton("데이터 수집", self)
        self.btn_collect_data.setFont(QFont("'HY동녘B'",15)) #폰트,크기 조절
        self.btn_collect_data.setStyleSheet("color: rgb(255, 255, 255);"
                "background-color: rgb(0, 176, 30);"
                "border-style: dashed;"
                "border-width: 0px;"
                "border-color: #1E90FF")

        self.btn_theme_stock  = QPushButton("테마종목 수정", self)
        self.btn_theme_stock.setFont(QFont("'HY동녘B'",15)) #폰트,크기 조절
        self.btn_theme_stock.setStyleSheet("color: rgb(255, 255, 255);"
                "background-color: rgb(30, 76, 30);"
                "border-style: dashed;"
                "border-width: 0px;"
                "border-color: #1E90FF")

        #self.btn_theme_stock.currentTextChanged.connect(self.show_graph)
        #self.cb_from_date = QLabel("테마종목 수정", self)
        #plot 의 시작날자를 지정
        #여기에 plot을 보이기 위한 시작 날자를 DB 에서 가져와 표시
        self.lbl_from_date = QLabel("시작날자",self)
        self.lbl_from_date.setAlignment(Qt.AlignCenter) 

        #self.lbl_from_date.setText("Test set Text") #텍스트 변환 
        self.lbl_from_date.setFont(QFont("'HY동녘B'",12)) #폰트,크기 조절 
        #self.lbl_from_date.setStyleSheet("Color : green") #글자색 변환
        self.lbl_from_date.setStyleSheet("color: rgb(255, 255, 255);"
                "background-color: rgb(0, 76, 176);"
                "border-style: dashed;"
                "border-width: 0px;"
                "border-color: #1E90FF")
       #ui->labelName->setStyleSheet("color: #FF0000");

        cb_list_from_date = ["20", "60", "120", "240"]
        self.cb_from_date = QComboBox(self)
        self.cb_from_date.addItems(cb_list_from_date)
        self.cb_from_date.setFont(QFont("'HY동녘B'",15)) #폰트,크기 조절
        self.cb_from_date.setStyleSheet("color: rgb(255, 255, 255);"
                "background-color: rgb(0, 76, 176);"
                "border-style: dashed;"
                "border-width: 0px;"
                "border-color: #1E90FF")
        #self.cb_from_date = QComboBox(self)

        self.lbl_selected_date = QLabel("선정날자",self)  
        self.lbl_selected_date.setAlignment(Qt.AlignCenter)
        self.lbl_selected_date.setFont(QFont("'HY동녘B'",12)) #폰트,크기 조절
        self.lbl_selected_date.setStyleSheet("color: rgb(255, 255, 255);"
                "background-color: rgb(150, 0, 56);"
                "border-style: dashed;"
                "border-width: 0px;"
                "border-color: #1E90FF")

        cb_list_selected_date = ["오늘", "어제", "오늘~5일전", "5일전~10일전", "5일전", "10일전", "20일전"]
        self.cb_selected_date = QComboBox(self)
        self.cb_selected_date.addItems(cb_list_selected_date)
        self.cb_selected_date.setFont(QFont("'HY동녘B'",14)) #폰트,크기 조절
        self.cb_selected_date.setStyleSheet("color: rgb(255, 255, 255);"
                "background-color: rgb(150, 0, 56);"
                "border-style: dashed;"
                "border-width: 0px;"
                "border-color: #1E90FF")

        # 한개의 plot 을 stadlone window 에 보이기 선택
        # 선정이유
        # 1 오일거래 세배 눌림
        # 2 오일거래 세배 최초
        # 3 볼린저 상단 눌림
        # 4 볼린저 상단 최초
        # 5 장기 눌림목
        # 6 지속상승
        # 8 이십육십돌파
        # 9 이십백이십돌파
        # 10 이십이백사십돌파
        # 11 육십백이십돌파
        # 12 14일신고가
        # 13 120일 신고가
        # 14 Stochastic GC
        # 15 MACD GC
        # 16 3일간 눌림목
        # 17 주가대비거래량양호
        # 18 장기바닦

        cb_list_best_stock = ["","1 오일거래 세배 눌림", "3 볼린저 상단 눌림", "4 볼린저 상단 최초", "보유", "ETF", "관심종목"]

        self.cb_best_stock = QComboBox(self)
        self.cb_best_stock.addItems(cb_list_best_stock)
        self.cb_best_stock.setFont(QFont("'HY동녘B'",14)) #폰트,크기 조절
        self.cb_best_stock.setStyleSheet("color: rgb(255, 255, 255);"
                "background-color: rgb(50, 56, 56);"
                "border-style: dashed;"
                "border-width: 0px;"
                "border-color: #1E90FF")

         
        #self.cb_best_stock.currentTextChanged.connect(self.show_graph)

        # 비교할 기준을 선택
        #self.lbl_from_date = QLabel("기준날자",self)
        #self.cb_compare_stock = QComboBox(self)       
        cb_list_compare_stock = ["일간 고15 테마","", "기간 고15 테마", "기간 고30 테마", "기간 저15 테마",
            "기간 Best Stock","", "기간 고15 ETF", ""]
        
        self.cb_compare_stock = QComboBox(self)
        self.cb_compare_stock.addItems(cb_list_compare_stock)
        self.cb_compare_stock.setFont(QFont("'HY동녘B'",14)) #폰트,크기 조절
        self.cb_compare_stock.setStyleSheet("color: rgb(255, 255, 255);"
                "background-color: rgb(76, 0, 156);"
                "border-style: dashed;"
                "border-width: 0px;"
                "border-color: #1E90FF")
        #self.cb_compare_stock.currentIndexChanged.connect(self.cb_compare_stock)
        #self.cb_compare_stock.currentTextChanged.connect(self.def_cb_compare_stock)
        #self.btn_counter  = QPushButton("멈춤(초)", self)
        self.btn_plot_again  = QPushButton("2X2Yaxis", self)

        
        self.btn_search_button2  = QPushButton("예비 버튼", self)
        self.btn_search_button2.clicked.connect(self.show_graph)

        self.horizontalGroupBox = QGroupBox()
        self.layout = QGridLayout()

        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, 10)
        self.layout.setColumnStretch(2, 10)
        self.layout.setColumnStretch(3, 10)
        self.layout.setColumnStretch(4, 10)
        self.layout.setColumnStretch(5, 10)
        self.layout.setColumnStretch(6, 10)
        self.layout.setColumnStretch(7, 10)
        self.layout.setColumnStretch(8, 10)

        #self.layout.setRowStretch(0, 1)

        # AttributeError: 'Window' object has no attribute 'game_name'
        #self.layout.addWidget(self.game_name, 0, 0)
        self.layout.addWidget(self.btn_collect_data, 0, 0, 2, 1)
        self.layout.addWidget(self.btn_theme_stock, 0, 1, 2, 1)

        self.layout.addWidget(self.lbl_from_date, 0, 2, 2, 1) 
        self.layout.addWidget(self.cb_from_date, 0, 3, 2, 1) 
         
        self.layout.addWidget(self.lbl_selected_date, 0, 4, 2, 1) 
        self.layout.addWidget(self.cb_selected_date, 0, 5, 2, 1) 

        self.layout.addWidget(self.cb_best_stock, 0, 6, 2, 1)
        self.layout.addWidget(self.cb_compare_stock, 0, 7, 2, 1)

        self.layout.addWidget(self.btn_plot_again, 0, 8, 2, 1)
        self.layout.addWidget(self.btn_search_button2, 0, 9, 2, 1)

        self.horizontalGroupBox.setLayout(self.layout)          # +++ self.

    def X2Y2plot(self):
        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")

        sql=f"SELECT MarketOpenDate FROM tradingdate ORDER BY MarketOpenDate DESC LIMIT 20;"
        df_date = pd.read_sql_query(sql, connPy)
        # 선정된 날자를 선정
        if self.cb_best_stock.currentText() !="보유" or self.cb_best_stock.currentText()!="ETF" or self.cb_best_stock.currentText()!="관심종목":
            sql="SELECT SaveDate, 종목명, 종목코드, 선정이유 FROM selected_stock"
            sql+=f" WHERE 선정이유='{self.cb_best_stock.currentText()}'"
            sql+=f" AND SaveDate='{df_date.iloc[0][0]}'"
            plot_stock = pd.read_sql_query(sql, connPy)
            cur.fetchall()
#df.empty==False: 
            if plot_stock.empty == False:
                for ii in range(len(plot_stock)):
                    df=[]                
                    df=self.make_df(df,str(plot_stock.종목코드[ii])) 

                    fig=make_subplots(
                            specs=[[{"secondary_y": True}]])
                    print(fig.layout)    

                    fig.update_layout(xaxis2= {'anchor': 'y', 'overlaying': 'x', 'side': 'top'},
                                    yaxis_domain=[0, 0.94])

                    fig.add_trace(
                        go.Bar(x=df.index,
                            y=df.pVolume,
                            opacity=0.3,
                            width=1), secondary_y=False)

                    #fig.add_trace(
                    #    go.Bar(x=[1, 2, 3, 4],
                    #           y=[7, 4, 5, 6],
                    #           name="bar",
                    #          ), secondary_y=False)

                    fig.add_trace(go.Scatter(x=df.index,
                            y=df.pup_band,
                            opacity=0.9,
                            line=dict(color='rgb(204, 0, 0)',
                            width=1),
                            name='up_band'),
                        secondary_y=False)

                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.pup_band,opacity=0.9,line=dict(color='rgb(204, 0, 0)',width=1),name='up_band'))
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.pmid_band,mode="lines",fill="tonexty",fillcolor="rgba(200, 0, 0, 0.1)",line=dict(color="rgba(255, 0, 0, 0.1)")))
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.pmid_band,line=dict(color=colors[0])))
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.plow_band,mode="lines",fill="tonexty",fillcolor="rgba(0, 0, 200, 0.1)",line=dict(color="rgba(0, 0, 255, 0.2)",width=1),))

                    #fig.add_trace(go.Scatter(x=df.index,y=df.plow_band,line=dict(color='rgb(0, 0, 204)', width=3)))

                    fig.add_trace(go.Candlestick(
                        x=df.index,open=df.pOpen,high=df.pHigh,low=df.pLow,close=df.pClose,increasing_line_color='rgb(204, 0, 0)', decreasing_line_color='rgb(0, 0, 204)'))
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.resultSUM,line=dict(color='rgb(153, 0, 53)',width=1),name='resultSUM'))
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.resultSUMMA10,line=dict(color='rgb(153, 0, 53)',width=4),name='resultSUMMA10'))

                    fig.add_hline(
                        y=40,
                        line_dash='longdash',
                        line=dict(color='rgb(153, 0, 53)',width=1),
                        annotation_text='총점관심',
                        annotation_position="bottom right",
                        annotation_font_size=20,
                        annotation_font_color='rgb(153, 0, 53)')

                    fig.add_hline(
                        y=20,
                        line_dash='longdash',
                        line=dict(color='rgb(153, 0, 53)',width=1),
                        annotation_text='총점바닦',
                        annotation_position="bottom right",
                        annotation_font_size=20,
                        annotation_font_color='rgb(153, 0, 53)')

                    #fig.add_trace(go.Bar(x=df.index,y=df.Volume),secondary_y=True)
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.pMA5,line=dict(color='rgb(0, 204, 204)',width=1),name='MA5') ) 
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.pMA20,line=dict(color='orange',width=1),name='MA20'))              
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.pMA60,line=dict(color='green',width=1),name='MA60'))
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.pMA120,line=dict(color='black',width=1),name='MA120'))
                    #fig.add_trace(go.Scatter(x=df.index,y=df.ppsar,line=dict(color='black',width=3),name='ppsar'))

                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.pVMA5,line=dict(color='rgb(0, 0, 204)',width=1),name='VMA5'))              
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df.pVMA20,line=dict(color='rgb(0, 0, 204)',width=4),name='VMA20',    
                        xperiodalignment="middle",hovertemplate="%{y}%{_xother}"))
                    fig.add_trace(go.Scatter(
                        x=df.index,y=df['pMA5-pMA20'],line=dict(color='rgb(0, 204, 0)',width=4),name='pMA5pMA20'))              
                    fig.add_hline(
                        y=50,
                        line_dash='longdash',
                        line=dict(color='rgb(0, 204, 0)',width=2),
                        annotation_text='5일=20일 이평',
                        annotation_position="bottom right",
                        annotation_font_size=20,
                        annotation_font_color='rgb(0, 204, 0)')
                        
                    fig.data[1].update(xaxis='x2')
                    fig.update_layout(width=1900, height=850)
                    fig.update_layout(xaxis_rangeslider_visible=False)

                    #fig.update(layout_showlegend=False)
                    

                    #fig.update_layout(title='<b>성별 확진자 및 사망자 수</b>', font = layout_setting['font'], showlegend=True)

                    fig.update_layout(
                        title=df.종목명[0],
                        font=dict(size=22,color='#60606e',family='Franklin Gothic'),
                        #font = layout_setting['font'],
                        showlegend=False,
                        margin=dict(t=50, b=70, l=70, r=40),
                        xaxis_rangeslider_visible=False,            
                        xaxis_title=None, yaxis_title=None,
                        #font=dict(color='#8a8d93'),
                        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5))
                    
                    #fig.title('test title', fontsize=20)
                    #fig.show()
                    iplot(fig)

                    print(fig)

                    #self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
                    print(ii)
                    #time.sleep(3)
                    

                    #self.browser.reload()

    def stop_second(self, text):
        pass

    def show_graph(self):
        df = px.data.tips()
        fig = px.box(df, x="day", y="total_bill", color="smoker")
        fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

    def def_cb_compare_stock(self, text):
        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")
        cur.fetchall()

        limit_day_count=240
        #sql=f"SELECT MarketOpenDate FROM tradingdate ORDER BY MarketOpenDate LIMIT {limit_day_count} ORDER BY MarketOpenDate DESC"
        sql=f"SELECT MarketOpenDate FROM tradingdate ORDER BY MarketOpenDate DESC LIMIT {limit_day_count};"

        df_date = pd.read_sql_query(sql, connPy)
        # 선정된 날자를 선정
        if str(self.cb_selected_date.currentText())=='오늘':
            c_cb_selected_date = df_date.iloc[0][0]
        elif str(self.cb_selected_date.currentText())=='어제': 
            c_cb_selected_date = df_date.iloc[1][0]
        elif str(self.cb_selected_date.currentText())=='5일전': 
            c_cb_selected_date = df_date.iloc[4][0]
        elif str(self.cb_selected_date.currentText())=='10일전': 
            c_cb_selected_date = df_date.iloc[9][0]  
        elif str(self.cb_selected_date.currentText())=='20일전': 
            c_cb_selected_date = df_date.iloc[19][0]
        
        # plot 이 시작되는 날자를 선정
        if str(self.cb_from_date.currentText())=='20':
            c_cb_from_date = df_date.iloc[19][0]
        elif str(self.cb_from_date.currentText())=='60': 
            c_cb_from_date = df_date.iloc[59][0]
        elif str(self.cb_from_date.currentText())=='120': 
            c_cb_from_date = df_date.iloc[119][0]
        elif str(self.cb_from_date.currentText())=='240': 
            c_cb_from_date = df_date.iloc[239][0]  
    
        #"기간 고15 테마", "기간 고30 테마", "기간 저15 테마"
        # 1. 해당하는 테마 또는 ETF, 종목 15개를 선정하고
        # 2. 해당하는 테마 또는 ETF, 종목의 기간 중 전체종목을 df_compare_theme_all에 전체를 가져와서
        # 3. 1에서 얻어진 종목에 대하여 loop로서 필요한 종목만 선정하여 plot 을 위한 dataframe 을 만든다.
        # 4. 전체를 plot 
        plot_per_page=15
        if text=="일간 고15 테마":
            # 금일 최고의 테마를 선정
            sql="SELECT da.거래날자, ts.theme, AVG(da.등락률) AS 평균등락률"
            sql+=" FROM theme_stock ts, daily da"
            sql+=f" WHERE da.종목코드=ts.종목코드 AND da.거래날자='{c_cb_selected_date}'"
            sql+=" GROUP BY da.거래날자, ts.theme"
            sql+=f" ORDER BY 거래날자 DESC, 평균등락률 DESC LIMIT {plot_per_page};"

            df_compare_theme = pd.read_sql_query(sql, connPy)

        elif text=="기간 고15 테마":
            # 지정한 기간의 최고의 테마를 선정
            sql="SELECT S.거래날자, S.theme, S.평균등락률, sum(평균등락률) OVER(PARTITION BY S.theme ORDER BY S.거래날자) AS 합계등락률"
            sql+=" FROM (SELECT da.거래날자, ts.theme, AVG(da.등락률) AS 평균등락률"
            sql+=" FROM theme_stock ts, daily da"
            sql+=f" WHERE da.종목코드=ts.종목코드 AND da.거래날자>='{c_cb_selected_date}'"
            sql+=" GROUP BY da.거래날자, ts.theme"
            sql+=" ORDER BY 거래날자 DESC, 평균등락률 DESC) S"
            sql+=" GROUP BY S.거래날자, S.theme"
            sql+=f" ORDER BY 거래날자 DESC, 합계등락률 DESC LIMIT {plot_per_page};"

            df_compare_theme = pd.read_sql_query(sql, connPy)

        elif text=="기간 고30 테마":
            # 지정한 기간의 최고의 테마를 선정
            sql="SELECT S.거래날자, S.theme, S.평균등락률, sum(평균등락률) OVER(PARTITION BY S.theme ORDER BY S.거래날자) AS 합계등락률"
            sql+=" FROM (SELECT da.거래날자, ts.theme, AVG(da.등락률) AS 평균등락률"
            sql+=" FROM theme_stock ts, daily da"
            sql+=f" WHERE da.종목코드=ts.종목코드 AND da.거래날자>='{c_cb_selected_date}'"
            sql+=" GROUP BY da.거래날자, ts.theme"
            sql+=" ORDER BY 거래날자 DESC, 평균등락률 DESC) S"
            sql+=" GROUP BY S.거래날자, S.theme"
            sql+=f" ORDER BY S.거래날자 DESC, 합계등락률 DESC LIMIT {plot_per_page} offset {plot_per_page} ;"

            df_compare_theme = pd.read_sql_query(sql, connPy)

        elif text=="기간 저15 테마":
            # 지정한 기간의 최고의 테마를 선정
            sql="SELECT S.거래날자, S.theme, S.평균등락률, sum(평균등락률) OVER(PARTITION BY S.theme ORDER BY S.거래날자) AS 합계등락률"
            sql+=" FROM (SELECT da.거래날자, ts.theme, AVG(da.등락률) AS 평균등락률"
            sql+=" FROM theme_stock ts, daily da"
            sql+=f" WHERE da.종목코드=ts.종목코드 AND da.거래날자>='{c_cb_selected_date}'"
            sql+=" GROUP BY da.거래날자, ts.theme"
            sql+=" ORDER BY 거래날자 DESC, 평균등락률 DESC) S"
            sql+=" GROUP BY S.거래날자, S.theme"
            sql+=f" ORDER BY S.거래날자 DESC, 합계등락률 ASC LIMIT {plot_per_page};"

            df_compare_theme = pd.read_sql_query(sql, connPy)

        elif text=="기간 고15 ETF":
            # 지정한 기간의 최고의 테마를 선정
            sql="SELECT da.거래날자, da.종목명, da.등락률, sum(da.등락률) OVER(PARTITION BY da.종목코드 ORDER BY da.거래날자) AS 합계등락률"
            sql+=" FROM daily da, stock_code_list scl"
            sql+=" WHERE da.종목코드=scl.종목코드"
            sql+=" and scl.stockORetf='etf'"
            sql+=f" and da.거래날자>='{c_cb_selected_date}'"
            sql+=f" order by 거래날자 DESC, 합계등락률 DESC LIMIT {plot_per_page};"            

            df_compare_theme = pd.read_sql_query(sql, connPy)

        elif text=="기간 Best Stock":

            # Best Stock 은 선정된 이후 5일간의 데이터를 수집하므로 만약 현재로부터 5일 이내의 최고 상승율 종목의 데이터는 없으므로
            # 비교 날자를 조정할 필요가 있음
            sql="select DISTINCT savedate from sstock.selected_stock order by savedate DESC LIMIT 1 offset 5"
            df_compare_date = pd.read_sql_query(sql, connPy)
            #df_compare_date.iloc[0][0] = pd.read_sql_query(sql, connPy)

            if df_compare_date.iloc[0][0]<=c_cb_selected_date:
                c_cb_selected_date=df_compare_date.iloc[0][0]

            sql="SELECT distinct S.savedate as 거래날자, S.선정이유, S.상승율, avg(S.상승율) as 합계등락률"
            sql+=" FROM (SELECT savedate, 선정이유, 종목명, sum(D02Price+D03Price+D04Price+D05Price+D06Price) as 상승율"
            sql+=" FROM sstock.selected_stock"
            sql+=" GROUP BY savedate, 선정이유, 종목명"
            sql+=f" having 상승율  is not null AND SaveDate>='{c_cb_selected_date}') S"
            sql+=" GROUP BY S.savedate, S.선정이유"
            sql+=" having S.savedate = (select DISTINCT savedate from sstock.selected_stock order by savedate DESC LIMIT 1 offset 5)"
            sql+=" order by S.savedate DESC, 합계등락률 DESC;"

            df_compare_theme = pd.read_sql_query(sql, connPy)

        if text=="일간 고15 테마" or text=="기간 고15 테마" or text=="기간 고30 테마" or text=="기간 저15 테마":
            # 모든 테마의 데이터를 수집 
            sql="SELECT S.거래날자, S.theme, S.평균등락률, sum(평균등락률) OVER(PARTITION BY S.theme ORDER BY S.거래날자) AS 합계등락률"
            sql+=" FROM (SELECT da.거래날자, ts.theme, AVG(da.등락률) AS 평균등락률"
            sql+=" FROM theme_stock ts, daily da"
            sql+=f" WHERE da.종목코드=ts.종목코드 AND da.거래날자>='{c_cb_from_date}'"
            sql+=" GROUP BY da.거래날자, ts.theme"
            sql+=" ORDER BY 거래날자 DESC, 평균등락률 DESC) S"
            sql+=" GROUP BY S.거래날자, S.theme;"

            df_compare_theme_all = pd.read_sql_query(sql, connPy)
        elif text=="기간 고15 ETF":
#"기간 고15 ETF":
            sql="SELECT S.거래날자, S.종목명 as theme, S.등락률, 합계등락률"
            sql+=" FROM (SELECT da.거래날자, da.종목명, da.등락률, sum(da.등락률) OVER(PARTITION BY da.종목명 ORDER BY da.거래날자) AS 합계등락률"
            sql+=" FROM daily da, stock_code_list scl"
            sql+=f" WHERE da.거래날자>='{c_cb_from_date}'"
            sql+=" and scl.stockORetf='etf'"
            sql+=" and da.종목코드=scl.종목코드"
            sql+=" GROUP BY da.거래날자, da.종목명"
            sql+=" ORDER BY 거래날자 DESC, 합계등락률 DESC) S"
            sql+=""
            sql+=" GROUP BY S.거래날자, S.종목명 ORDER BY 거래날자 ASC;"

            df_compare_theme_all = pd.read_sql_query(sql, connPy)
        elif text=="기간 Best Stock":
            '''
            SELECT distinct S.savedate as 거래날자, S.선정이유 as theme, S.상승율, s.합계등락률
            FROM (SELECT savedate, 선정이유, 종목명, sum(D02Price+D03Price+D04Price+D05Price+D06Price) as 상승율, sum(sum(D02Price+D03Price+D04Price+D05Price+D06Price)) OVER (PARTITION BY 선정이유 ORDER BY savedate) AS 합계등락률 
            FROM sstock.selected_stock 
            GROUP BY savedate, 선정이유
            having 상승율  is not null AND SaveDate>='20220220') S 
            GROUP BY S.savedate, S.선정이유 
            order by S.savedate DESC, 합계등락률 DESC;
            '''

            sql="SELECT distinct S.savedate as 거래날자, S.선정이유 as theme, S.상승율, 합계등락률"
            sql+=" FROM (SELECT savedate, 선정이유, 종목명, sum(D02Price+D03Price+D04Price+D05Price+D06Price) as 상승율, sum(sum(D02Price+D03Price+D04Price+D05Price+D06Price)) OVER (PARTITION BY 선정이유 ORDER BY savedate) AS 합계등락률"
            sql+=" FROM sstock.selected_stock"
            sql+=" GROUP BY savedate, 선정이유"
            sql+=f" having 상승율  is not null AND SaveDate>='{c_cb_from_date}') S"
            sql+=" GROUP BY S.savedate, S.선정이유"
            sql+=" order by S.savedate ASC;"

            df_compare_theme_all = pd.read_sql_query(sql, connPy)

            #df_compare_theme_all=df_compare_theme.copy
        #df_compare_theme_all[df_compare_theme[idx]]

        #df_plot_data_temp=df_compare_theme_all[idx][1]

        # plot 하기 위한 데이터를 수집

        df_plot_data = pd.DataFrame()
        for idx in range(len(df_compare_theme)):
            # 지정한 기간의 최고의 테마의 데이터만을 선택하여 df 로 이동
            df_picked_theme = df_compare_theme_all[df_compare_theme_all['theme']==df_compare_theme.iloc[idx][1]]
            df_plot_data_temp=df_picked_theme[['거래날자', '합계등락률']].copy()
            df_plot_data_temp.rename(columns = {'합계등락률' : df_compare_theme.iloc[idx][1]}, inplace = True)

            if df_plot_data.empty:
                df_plot_data = df_plot_data_temp
            else:
                df_plot_data = pd.merge(df_plot_data, df_plot_data_temp, left_on='거래날자', right_on='거래날자', how='outer')
          

        #fig=px.line(x=df_plot_data.index, y = df_plot_data.columns)
        df_plot_data  = df_plot_data.fillna(0)
        #pd.options.plotting.backend = "plotly"
        #fig = df_plot_data.plot()
        #fig = px.box(df_plot_data, x="거래날자", y="total_bill", color="smoker")

        #fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
        #fig.update_traces(quartilemethod="linear") # or "inclusive", or "linear" by default
        
        #self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        #iplot(fig)

        df_plot_data.drop(['거래날자'],axis=1,inplace=True)
        df_plot_data.to_excel('C:/DataDisk/theme.xlsx')

        data = []
        for col in df_plot_data.columns:
            trace =  go.Scatter(
                x = df_plot_data.index,
                y = df_plot_data[col],
                name = col,
            )
            data.append(trace)

        layout = go.Layout(
            title='',#시총상위 7종목의 과거 20년간 순위 변화)',
            yaxis=dict(
                #autorange='reversed',
                title='기간상승률(%)',
            ),
            
            font=dict(color='#8a8d93',size=18),
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5),
            hoverlabel=dict(bgcolor="white",font_size=20,font_family="Rockwell")
        )
        

        fig = go.Figure(data=data, layout=layout)
        #fig.update_layout(hoverlabel=dict(bgcolor="white",font_size=20,font_family="Rockwell"))
        #fig.show()
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))









        '''

        fig = go.Figure()
        for i in range(3, len(df_plot_data.columns)):
            #col_name = 'S'+ str(i)
            #fig.add_trace(go.Scatter(x=df_plot_data['거래날자'], y=df_plot_data[col_name],
            #                    mode='lines', # 'lines' or 'markers'
            #                    name=col_name))
            fig.add_trace(go.Scatter(
                x=df_plot_data.index,y=df_plot_data.columns[i],
                                mode='lines', # 'lines' or 'markers'
                                name=df_plot_data.columns[i]))
        fig.show()
        #self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        
        fig = go.Figure(go.Scatter(
            #x=df_plot_data.index,y=df_plot_data.해운,opacity=0.9,line=dict(color='rgb(204, 0, 0)',width=1)))
            x=df_plot_data.index,y=df_plot_data.columns.values[1],opacity=0.9,line=dict(color='rgb(204, 0, 0)',width=1)))
        fig.add_trace(go.Scatter(
            x=df_plot_data.index,y=df_plot_data.농업,opacity=0.9,line=dict(color='rgb(204, 0, 0)',width=1)))
        #fig.show()
        #fig.imshow
        #iplot(fig)
        #fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        '''

    def get_soup(self, url):
        header = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        }
        res = requests.get(url, headers=header)
        if res.status_code == 200:
            return BeautifulSoup(res.text, "html.parser")
    
    def theme_stock(self):
        df = pd.DataFrame()
        
        #%%
        for pagenum in range(1,8):
        #for pagenum in range(1,2):  #테마 종목은 
            #url = "https://finance.naver.com/sise/theme.nhn?field=name&ordering=asc&page={pagenum}".format(pagenum=pagenum)
            url=f"https://finance.naver.com/sise/theme.naver?&page={pagenum}"

            s = self.get_soup(url)
            s.select(".tbody.tr")
            for main in range(len(s.select("#contentarea_left > table.type_1.theme > tr"))-5):
                #비료=s.select("td.col_type1")[2].text
                
                url_annex = s.select("#contentarea_left > table.type_1.theme > tr:nth-child("+str(main+5)+") > td.col_type1 > a")[0]
                url_annex = s.select("td.col_type1")[main]("a")[0]
                theme_group_code=str(url_annex).split("no=")[1].split('"')[0]
                theme = url_annex.text

                theme_url = 'https://finance.naver.com' +url_annex['href']
                theme_s = self.get_soup(theme_url)

                for detail in range(len(theme_s.select("table>tbody > tr"))-2):
                    stock_name=theme_s.select("table>tbody > tr .name_area")[detail].text
                    stock_name = stock_name.replace(" *", "").strip()

                    stock_detail= theme_s.select("#contentarea > div:nth-child(5) > table > tbody > tr:nth-child("+str(detail+1)+") > td:nth-child(2) > div > div > p")[0].text

                    print(pagenum,",", theme_group_code,",", theme,",", stock_name,",", stock_detail)
                    df = df.append({'page' : pagenum, 'theme_group_code' : theme_group_code, 'theme' : theme, 'stock' : stock_name, 'stock_detail' : stock_detail}, ignore_index =True)                

        df.fillna(0)     
        df.insert(1,'code_update_date', datetime.datetime.now().strftime("%Y%m%d")) #업데이트 날자 컬럼 추가

        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")

        sql="delete from theme_stock"
        cur.execute(sql) #현재의 table 삭제하고 새롭게 업데이트
        connPy.commit()    

        try:
            for idx in range(len(df)):
                sql = "INSERT IGNORE INTO theme_stock (pagenum, code_update_date, theme_group_code, theme, stock_name, stock_detail)"
                sql +=" VALUES"
                sql +="	(%s,%s,%s,%s,%s,%s)" 

                cur.execute(sql, tuple(df.values[idx]))
                connPy.commit()
        except:
            pass

    def show_multi_plot(self, text):
        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")

        sql="SELECT DISTINCT SaveDate FROM selected_stock ORDER BY SaveDate DESC"
        df_date =pd.read_sql_query(sql, connPy)

        if str(self.cb_selected_date.currentText())=='오늘':
            str_plot_period=f"SaveDate='{df_date.SaveDate[0]}'"
        elif str(self.cb_selected_date.currentText())=='어제': 
            str_plot_period=f"SaveDate='{df_date.SaveDate[1]}'"
        elif str(self.cb_selected_date.currentText())=="오늘~5일전": 
            str_plot_period=f"SaveDate<='{df_date.SaveDate[0]}' AND SaveDate>'{df_date.SaveDate[4]}'"
        elif str(self.cb_selected_date.currentText())=="5일전~10일전":
            str_plot_period=f"SaveDate<='{df_date.SaveDate[4]}' AND SaveDate>'{df_date.SaveDate[9]}'"

        elif str(self.cb_selected_date.currentText())=='5일전': 
            str_plot_period=f"SaveDate='{df_date.SaveDate[4]}'"
        elif str(self.cb_selected_date.currentText())=='10일전': 
            str_plot_period=f"SaveDate='{df_date.SaveDate[9]}'"
        elif str(self.cb_selected_date.currentText())=='20일전': 
            str_plot_period=f"SaveDate='{df_date.SaveDate[19]}'"

        if text=="1 오일거래 세배 눌림" or text=="3 볼린저 상단 눌림" or text=="4 볼린저 상단 최초":
            sql=f"SELECT DISTINCT SaveDate, 종목명, 종목코드, 선정이유 FROM selected_stock WHERE {str_plot_period}"
            sql+=f" and (선정이유='{text}') order by 선정이유"# limit 8"

            total_selected_stock = pd.read_sql_query(sql, connPy)
            #self.qlabel.setText(text+" plot 을 준비하고 있습니다.")
        #elif text=="3 볼린저 상단 눌림":
        #    sql=f"SELECT DISTINCT SaveDate, 종목명, 종목코드, 선정이유 FROM selected_stock WHERE SaveDate={p_day[0][0]}"
        #    sql+=" and (선정이유='{text}') order by 선정이유"

        #    total_selected_stock = pd.read_sql_query(sql, connPy)
            #self.qlabel.setText(text+" plot 을 준비하고 있습니다.")

        elif text=="보유":
            total_selected_stock = pd.read_excel('C:/DataDisk/Python/finance/tests/보유.xlsx', sheet_name=text)
            total_selected_stock =total_selected_stock[['SaveDate', '종목명','선정이유']]
            sql="SELECT 종목코드, 종목명 FROM stock_code_list"
            stock_code = pd.read_sql_query(sql, connPy)
            total_selected_stock = pd.merge(total_selected_stock, stock_code)
        
        # 한페이지에 그래프를 많이 그리면 시간이 오래걸리므로 browser 당 6개로 제한하고 browser 수를 늘린다. 
        #if len(total_selected_stock)>6:
        browser_num=int(int(len(total_selected_stock)-1)/6)+1
        print("총종목수:",len(total_selected_stock), " plot page:",browser_num)
        self.statusBar().showMessage("총종목수:"+str(len(total_selected_stock))+ " plot page:"+str(browser_num))
        self.statusBar().repaint()
        #self.qlabel.setText("총종목수:"+str(len(total_selected_stock))+"   plot page:"+str(browser_num))

        for idx_browser_num in range(browser_num):
            selected_stock=total_selected_stock.iloc[(idx_browser_num)*6:(idx_browser_num+1)*6,:]
            selected_stock= selected_stock.reset_index(drop=True,inplace=False)
            #print(selected_stock)
            #for idx in range(len(selected_stock)):
            rowC, colC, legend = int(int(len(selected_stock)+1)/2),2,False#(len(selected_stock)+1)%2 + 1, False
            fig = make_subplots(rows=rowC, cols=colC, horizontal_spacing=0.03,vertical_spacing= 0.03,
                #subplot_titles=([f'<b>{prov}</b>' for prov in provinces]))
                #subplot_titles="test")
                #subplot_titles=selected_stock.column)
                subplot_titles = [selected_stock.종목명[idx]+', '+str(selected_stock.SaveDate[idx])+', '+selected_stock.선정이유[idx] for idx in np.arange(len(selected_stock))]
                ) #그래프 간 간격        

            for row in range(1,rowC+1):
                for col in range(1,colC+1):
                    if len(selected_stock)>((row-1)*2+col-1):
                        df=[]
                        df=self.make_df(df,str(selected_stock.종목코드[(row-1)*2+col-1])) 
                        #CSV 의 데이터에 정수로 저장되는 종목코드의 앞에 6자리 종목으로 만들기 위하여 앞에'000' 을 넣는 과정
                        #df=make_df(df,str('{0:06d}'.format(selected_stock.종목코드[(row-1)*2+col-1]))) # ]selected_stock[(row-1)*2+col-1][2]) 
                        #'{0:06d}'.format(selected_stock.종목코드[(row-1)*2+col-1])

                        if df.empty==False: 
                            self.sub_add_trace(fig,df,row,col)
            self.make_plot(fig,colC,rowC)
            #iplot(fig)
            fig.show()

    def make_df(self,df,종목코드):
        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")
        xaxis_count=60
        sql=f"select S.MarketOpenDate from (select MarketOpenDate from tradingdate order by MarketOpenDate desc limit {xaxis_count}) as S order by S.MarketOpenDate asc limit 1"
        cur.execute(sql) 
        plot_start_date = cur.fetchall()

        sql ="SELECT 거래날자, 종목코드, 종목명,"
        sql += " IF(ta.Close > ta.MA5, 5, 0)"
        sql += " + IF(ta.VWAP > ta.MA5, 5, 0)"
        sql += ""
        
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
        sql += ""
        sql += " ta.Open, ta.High, ta.Low, ta.Close, ta.Open-ta.Close as OC, ta.Volume,"
        sql += " ta.MA5, ta.MA10, ta.MA20, ta.MA60, ta.MA120, ta.MA240,"
        sql += " ta.VMA5, ta.VMA10, ta.VMA20, ta.VMA60, ta.VMA120, ta.VMA240, ta.up_band, ta.mid_band, ta.low_band,"
        sql += " ta.RSI, ta.willr14, ta.AVGwillr14, ta.willr120, ta.AVGwillr120, ta.slowk, ta.slowd, ta.STOCHRSI_fastk, ta.STOCHRSI_fastd,"
        sql += " ta.psar, ta.arronOSC, ta.adx, ta.pdi, ta.mdi, ta.HA_Close, ta.HA_Open, ta.HA_High, ta.HA_Low, ta.macd,ta.macdSignal, ta.VWAP"
        sql += " FROM ta"        
        sql += " where ta.종목코드='"+종목코드+"'"
        sql += " and ta.거래날자>='"+plot_start_date[0][0]+"'"
        sql += " ORDER BY 거래날자 ASC"

        df = pd.read_sql_query(sql, connPy)
        if df.empty==False:
            # 최대가격 검색
            if df["up_band"].max()>df["High"].max():
                max_value_price = df["up_band"].max()
            else:
                max_value_price = df["High"].max()
            # 최대거래량 검색
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
            df['pVWAP'] = df['VWAP']/max_value_price*100
            df.fillna(0)

            df['resultSUMMA10'] = ta.SMA(df['resultSUM'],10)

            df['ppsar'] = df['psar']/max_value_price*100
            df['pVolume'] = df['Volume']/max_value_volume*100   #5거래량이평
            df['pVMA5'] = df['VMA5']/max_value_volume*100   #5거래량이평
            df['pVMA20'] = df['VMA20']/max_value_volume*100 #20거래량이평

            df['pMA5-pMA20']=(df['MA5']-df['MA20'])/max_value_price*100 + 50   #오일이평과 20일 이평의 간격
            df['pMA5-pMA60']=(df['MA5']-df['MA60'])/max_value_price*100 + 50   #오일이평과 60일 이평의 간격
            ####################################################################################################################################


        return df

    def sub_add_trace(self,fig,df,row,col):

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
        fig.add_trace(go.Bar(
                x=df.index,
                y=df.pVolume,
                opacity=0.2,
                width=1,
                marker=dict(color='rgb(222,0,0)')
                ),row=row,col=col)

        fig.add_trace(go.Scatter(
            x=df.index,y=df.pup_band,opacity=0.9,line=dict(color='rgb(204, 0, 0)',width=1))
            ,row=row,col=col)
        fig.add_trace(go.Scatter(
            x=df.index,y=df.pmid_band,mode="lines",fill="tonexty",fillcolor="rgba(200, 0, 0, 0.1)",line=dict(color="rgba(255, 0, 0, 0.1)"),)
            ,row=row,col=col)
        fig.add_trace(go.Scatter(
            x=df.index,y=df.pmid_band,line=dict(color=colors[0]))
            ,row=row,col=col)
        fig.add_trace(go.Scatter(
            x=df.index,y=df.plow_band,mode="lines",fill="tonexty",fillcolor="rgba(0, 0, 200, 0.1)",line=dict(color="rgba(0, 0, 255, 0.2)",width=1),)
            ,row=row,col=col)

        #fig.add_trace(go.Scatter(x=df.index,y=df.plow_band,line=dict(color='rgb(0, 0, 204)', width=3)))

        fig.add_trace(go.Candlestick(
            x=df.index,open=df.pOpen,high=df.pHigh,low=df.pLow,close=df.pClose,increasing_line_color='rgb(204, 0, 0)', decreasing_line_color='rgb(0, 0, 204)')
            ,row=row,col=col)
        fig.add_trace(go.Scatter(
            x=df.index,y=df.resultSUM,line=dict(color='rgb(153, 0, 53)',width=1),name='resultSUM')
            ,row=row,col=col)
        fig.add_trace(go.Scatter(
            x=df.index,y=df.resultSUMMA10,line=dict(color='rgb(153, 0, 53)',width=4),name='resultSUMMA10')
            ,row=row,col=col)

        #fig.add_hline(
        #    y=40,line=dict(color='rgb(153, 0, 53)',width=1))
        #fig.add_hline(
        #    y=20,line=dict(color='rgb(153, 0, 53)',width=1))



        fig.add_hline(
            y=40,
            line_dash='longdash',
            line=dict(color='rgb(153, 0, 53)',width=1),
            annotation_text='총점관심',
            annotation_position="bottom right",
            annotation_font_size=20,
            annotation_font_color='rgb(153, 0, 53)')

        fig.add_hline(
            y=20,
            line_dash='longdash',
            line=dict(color='rgb(153, 0, 53)',width=1),
            annotation_text='총점바닦',
            annotation_position="bottom right",
            annotation_font_size=20,
            annotation_font_color='rgb(153, 0, 53)')



        '''
        fig.add_trace(go.Scatter(
            x=df.index,y=df.pup_band,opacity=0.9,line=dict(color='rgb(204, 0, 0)',width=1))
            ,row=row,col=col)
        fig.add_trace(go.Scatter(
            x=df.index,y=df.pmid_band,mode="lines",fill="tonexty",fillcolor="rgba(200, 0, 0, 0.1)",line=dict(color="rgba(255, 0, 0, 0.1)"),)
            ,row=row,col=col)
        '''

        #fig.add_trace(go.Bar(x=df.index,y=df.Volume),secondary_y=True)
        fig.add_trace(go.Scatter(
            x=df.index,y=df.pMA5,line=dict(color='rgb(0, 204, 204)',width=2),name='MA5')
            ,row=row,col=col) 
        fig.add_trace(go.Scatter(
            x=df.index,y=df.pVWAP,mode="lines",fill="tonexty",fillcolor="rgba(255, 0, 0, 0.5)",line=dict(color="rgba(255, 0, 0, 0.1)"),)
            ,row=row,col=col)

        fig.add_trace(go.Scatter(
            x=df.index,y=df.pVWAP,line=dict(color='rgb(255, 0, 53)',width=2),name='VWAP')
            ,row=row,col=col)

        fig.add_trace(go.Scatter(
            x=df.index,y=df.pMA20,line=dict(color='orange',width=1),name='MA20')
            ,row=row,col=col)              
        fig.add_trace(go.Scatter(
            x=df.index,y=df.pMA60,line=dict(color='green',width=1),name='MA60')
            ,row=row,col=col)
        fig.add_trace(go.Scatter(
            x=df.index,y=df.pMA120,line=dict(color='black',width=1),name='MA120')
            ,row=row,col=col)
        fig.add_trace(go.Scatter(
            x=df.index,y=df['pMA5-pMA20'],line=dict(color='rgb(0, 204, 0)',width=4),name='pMA5pMA20'),row=row,col=col)   

        fig.add_hline(
            y=50,
            line_dash='longdash',
            line=dict(color='rgb(0, 204, 0)',width=2),
            annotation_text='5일=20일 이평',
            annotation_position="bottom right",
            annotation_font_size=20,
            annotation_font_color='rgb(0, 204, 0)')

        #fig.add_hline(
        #    y=50,line=dict(color='rgb(0, 204, 0)',width=1))

        #fig.add_trace(go.Scatter(x=df.index,y=df['pMA5-pMA60'],line=dict(color='rgb(0, 204, 0)',width=2),name='pMA5-pMA60'),row=row,col=col)
        #fig.add_trace(go.Scatter(x=df.index,y=df['공매도잔고비중']+50,line=dict(color='rgb(0, 204, 204)',width=2),name='공매도잔고비중'), row=1, col=1)


        #fig.add_trace(go.Scatter(x=df.index,y=df['slowk'],line=dict(color="red",width=1),name='slowk'), row=2, col=1)
        #fig.add_trace(go.Scatter(x=df.index,y=df['slowd'],line=dict(color="blue",width=1),name='slowd'), row=2, col=1)
        #fig.update_yaxes(title_text='Sto', row=2, col=1)


        fig.update_yaxes(title_text='', row=row, col=col)
        fig.update_xaxes(rangeslider_visible=False)    
        #################################################################################################################################
    
    def make_plot(self,fig,colC,rowC):

        #fig.update_layout(xaxis_rangeslider_visible=False)#,shapes=shape_list)
        if colC==1:
            fig['layout'].update(height=rowC*300*2, width=2000*2) #,title={'text': '<b>'+df.종목명[0]+'</b>', 'font': {'size': 20}})
        else:
            fig['layout'].update(height=rowC*300*2, width=1000*2) #,title={'text': '<b>'+df.종목명[0]+'</b>', 'font': {'size': 20}})
        fig.update(layout_showlegend=False)
        #fig.update_layout(title_text=df.종목명[0],title_x=0.5,title_y=0.87)

        #large_title_format = "<span style='font-size:15px; font-family:Tahoma'>"+df.종목명[0]
        #small_title_format = "<span style='font-size:10px; font-family:Tahoma'>색상이 진하면 사세요."

        fig.update_layout(
            #title=large_title_format + "     " + small_title_format, height=400,
            #margin=dict(t=130, b=0, l=70, r=40),
            margin=dict(t=30, b=0, l=70, r=40),
            xaxis_rangeslider_visible=False,    
            
            xaxis_title=None, yaxis_title=None,
            #plot_bgcolor='#333', paper_bgcolor='#333',
            #title_font=dict(size=25, color='#8a8d93', family="Lato, sans-serif"),
            font=dict(color='#8a8d93'),
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5))

        fig.update_xaxes(showspikes=True,spikecolor="green",spikethickness=5,spikedash="dot",spikesnap="cursor",spikemode="across")
        fig.update_yaxes(showspikes=True,spikecolor="orange",spikethickness=5,spikedash="dot",spikesnap="cursor",spikemode="across")

        #fig.update_xaxes(ticks="inside",nticks=12,tickangle=25, tickfont=dict(family='Rockwell', color='black',size=8))
        #fig.update_yaxes(ticks="inside",nticks=10,tickangle=0,tickfont=dict(family='Rockwell',color='black',size=8))

        fig.update_layout(hoverlabel=dict(bgcolor="white",font_size=24,font_family="Rockwell"))
        fig.update_yaxes(ticklabelposition="inside top", title=None)
        xaxis_count=60
        fig.update_layout(xaxis_range=[0,xaxis_count])
        fig.update_layout(yaxis_range=[0,100])
        fig.update_annotations(font_size=24)
    
    def Stock_Price_After_Selected(self): #
        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")
        cur.fetchall()

        #sql="SELECT DISTINCT td.MarketOpenDate FROM tradingdate td WHERE td.MarketOpenDate>'20210101'"
        #sql+=" and td.MarketOpenDate not in (select DISTINCT SaveDate from selected_stock WHERE SaveDate>'20210101');"

        sql="SELECT DISTINCT td.MarketOpenDate"
        sql+=" FROM tradingdate td, selected_stock ss"
        sql+=" WHERE td.MarketOpenDate>'20210101'"
        sql+=" and td.MarketOpenDate = ss.SaveDate"
        sql+=" and ss.D06Price is Null"
        sql+=" order by td.MarketOpenDate ASC"

        dfDate = pd.read_sql_query(sql, connPy)
        cur.fetchall()
        for df_Date in range(0,len(dfDate)-5):

            calc_date=dfDate.iloc[df_Date][0]
            sql=f"SELECT S.marketopendate from (SELECT marketopendate FROM tradingdate WHERE MarketOpenDate>='{calc_date}' ORDER BY marketopendate ASC LIMIT 6) as S ORDER BY marketopendate ASC"
            df_Calc_Date = pd.read_sql_query(sql, connPy)

            calc_date1=df_Calc_Date.marketopendate[0]
            calc_date2=df_Calc_Date.marketopendate[1]
            calc_date3=df_Calc_Date.marketopendate[2]
            calc_date4=df_Calc_Date.marketopendate[3]
            calc_date5=df_Calc_Date.marketopendate[4]
            calc_date6=df_Calc_Date.marketopendate[5]
            sql=f"SELECT ss.SaveDate, ss.종목코드 FROM selected_stock ss WHERE SaveDate='{calc_date}'"
            df_selected_stock = pd.read_sql_query(sql, connPy)
            for idx in range(len(df_selected_stock)):
                sql="UPDATE selected_stock T,"
                #sql+=" SET T.D01Price=S.D01Price, T.D02Price=S.D02Price, T.D03Price=S.D03Price, T.D04Price=S.D04Price, T.D05Price=S.D05Price, T.D06Price=S.D06Price"
                sql+=" (SELECT ss.SaveDate, ss.종목코드,"
                sql+=" da1.등락률 as D01Price, da2.등락률 as D02Price, da3.등락률 as D03Price, da4.등락률 as D04Price, da5.등락률 as D05Price, da6.등락률 as D06Price"
                sql+=" FROM selected_stock ss, daily da1, daily da2, daily da3, daily da4, daily da5, daily da6"
                sql+=f" WHERE ss.SaveDate='{calc_date1}'"
                sql+=f" and da1.거래날자='{calc_date1}'"
                sql+=f" and da2.거래날자='{calc_date2}'"
                sql+=f" and da3.거래날자='{calc_date3}'"
                sql+=f" and da4.거래날자='{calc_date4}'"
                sql+=f" and da5.거래날자='{calc_date5}'"
                sql+=f" and da6.거래날자='{calc_date6}'"
                sql+=""
                sql+=" and da1.종목코드=ss.종목코드"                 
                sql+=f" and da1.종목코드='{df_selected_stock.종목코드[idx]}'" 
                sql+=" and da1.종목코드=da2.종목코드"
                sql+=" and da1.종목코드=da3.종목코드"
                sql+=" and da1.종목코드=da4.종목코드"
                sql+=" and da1.종목코드=da5.종목코드"
                sql+=" and da1.종목코드=da6.종목코드) AS S"
                sql+=" SET T.D01Price=S.D01Price, T.D02Price=S.D02Price, T.D03Price=S.D03Price, T.D04Price=S.D04Price, T.D05Price=S.D05Price, T.D06Price=S.D06Price"
                
                sql+=" WHERE T.SaveDate=S.SaveDate and T.종목코드=S.종목코드"
                cur.execute(sql)
                connPy.commit()
            print(calc_date1,"날자에 선정된 최고의 종목에 대한 이후 주가변화를 저장하였습니다.")

        #sql="UPDATE selected_stock T"
        #sql+=" (SELECT da.종목코드, da.거래날자, da.등락률 FROM daily da, selected_stock ss"
        #sql+=" WHERE ss.D01Price is Null"
        #sql+=" AND da.종목코드=ss.종목코드"
        #sql+=" AND da.거래날자=ss.SaveDate) S"
        #sql+=" SET T.D01Price=S.등락률"
        #sql+=" WHERE T.SaveDate=S.거래날자 and T.종목코드=S.종목코드"
        
        #cur.execute(sql)

        print("최고의 종목에 대한 이후 주가변화를 모두 저장하였습니다.")
        self.statusBar().showMessage("최고의 종목에 대한 이후 주가변화를 모두 저장하였습니다.")
        self.statusBar().repaint()
    '''
    def Select_Best_Stock(self):
        # Selected_Stock 을 선정하기 위하여 모든 거래날자를 거져와서 하루씩 계산
        # sql="SELECT DISTINCT 거래날자 FROM ta WHERE 거래날자>'20210101' ORDER BY 거래날자 ASC;"
        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")
        cur.fetchall()

        sql="SELECT DISTINCT ta.거래날자 FROM ta ta WHERE ta.거래날자>'20210101' and ta.거래날자 "
        #sql+=" not in (select DISTINCT SaveDate from selected_stock WHERE SaveDate>'20210101');"
        dfDate = pd.read_sql_query(sql, connPy)

        for df_Date in range(0,len(dfDate)):
            calc_date=dfDate.iloc[df_Date][0]
            self.best_stock_to_db(calc_date)
        print("가장 좋은 종목을 선정완료하였습니다.")
        self.statusBar().showMessage("가장 좋은 종목을 선정완료하였습니다.")
        self.statusBar().repaint()
    '''
    def get_soup(self, url):
        header = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        }
        res = requests.get(url, headers=header)
        if res.status_code == 200:
            # print(res.text)
            return BeautifulSoup(res.text, "html.parser")

    def stock_market_open_date(self):   #주식장이 열리는 날이면 tradingdate 에 날자를 기록
        url = "https://fchart.stock.naver.com/sise.nhn?symbol=005930&timeframe=day&count=500&requestType=0"   
        sHTML = self.get_soup(url)
        sHTML=str(sHTML)

        try:
            fString='<item data="'
            sHTML=sHTML[sHTML.find(fString)+len(fString):] # header 를 잘라내고 

            df = pd.DataFrame(columns=['dayORweek', 'MarketOpenDate'])
            while sHTML.find(fString)>-1:
                hHTML=sHTML[:sHTML.find(fString)] # 한개의 줄의 정보에서 날자를 추출
                strDate=hHTML.split("|",1)

                dfT = pd.DataFrame({'dayORweek':['day'],'MarketOpenDate':[strDate[0]]})
                df=pd.concat([df, dfT], ignore_index=True)
                sHTML=sHTML[sHTML.find(fString)+len(fString):] # 나머지 정보를 순환
            # 문자가 없어도 마지막날 한개가 남아 있다
            hHTML=sHTML[:sHTML.find(fString)] # 한개의 줄의 정보에서 날자를 추출
            strDate=hHTML.split("|",1)

            dfT = pd.DataFrame({'dayORweek':['day'],'MarketOpenDate':[strDate[0]]})
            df=pd.concat([df, dfT], ignore_index=True)
        except:
            print("네이버 주식에서 개장일을 가져오는데 실패하였습니다.")
            #self.statusBar().showMessage("네이버 주식에서 개장일을 가져오는데 실패하였습니다.")
            self.statusBar().repaint()

        # user = 'root'
        # hostname="localhost"
        # db = 'sstock' # In previous posts similar to "schema"
        # pwd="JRLEE"

        try:
            connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
            cur = connPy.cursor()
            cur.execute("use sstock")

            for ii in range(len(df)):        
                sql="INSERT IGNORE INTO tradingdate (dayORweek, MarketOpenDate) VALUES ('day', '" + df.loc[ii, "MarketOpenDate"] + "');"
                cur.execute(sql)
                connPy.commit()

            '''
            
            engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=db, user=user, pw=pwd))
            conn=engine.connect()
            # Convert dataframe to sql table                                   
            df.to_sql('temp', engine, if_exists = 'replace', index=False)



            conn.close()

            connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
            cur = connPy.cursor()
            cur.execute("use sstock")

            # sql="DELETE FROM tradingdate"
            # cur.execute(sql)
            connPy.commit()

            sql = "SELECT dayORweek, MarketOpenDate FROM temp order by MarketOpenDate ASC"
            tempTradingDate = pd.read_sql_query(sql, connPy)
            tempTradingDate = tempTradingDate.reset_index()
            tempTradingDate.fetchall
            for ii in range(len(tempTradingDate)):
                # dDate=pdTradingDate.loc[ii, "MarketOpenDate"]
                # basic_info_mission=pdTradingDate.loc[ii, "basic_info"]
                # shorting_info_mission=pdTradingDate.loc[ii, "shorting_info"]
                # sql="SELECT count(MarketOpenDate)
            
                sql="INSERT IGNORE INTO tradingdate (dayORweek, MarketOpenDate) VALUES ('day', '" + tempTradingDate.loc[ii, "MarketOpenDate"] + "');"
                cur.execute(sql)
                connPy.commit()
            '''
        except:
            pass

    def Data_Collector(self, dDate, basic_info_mission):
        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")
        cur.fetchall()
        
        if not basic_info_mission == 'Collected':
            try:
                stock_list = pd.DataFrame({'종목코드':stock.get_market_ticker_list(market="ALL")})
                stock_list['종목명'] = stock_list['종목코드'].map(lambda x: stock.get_market_ticker_name(x))
                #stock_list = stock_list.reset_index()

                market_ohlcv=stock.get_market_ohlcv_by_ticker(dDate, market="ALL")
                #df = stock.get_market_ohlcv("20200831", market="KOSPI")

                # market_ohlcv = market_ohlcv.reset_index()
                stock_list = pd.merge(stock_list, market_ohlcv, left_on='종목코드', right_on='티커', how='outer')

                # stock_list.to_csv('C:/datadisk/test.csv', encoding='utf-8-sig')
                exhaustion_rates_of_foreign=stock.get_exhaustion_rates_of_foreign_investment(dDate, 'ALL')
                # exhaustion_rates_of_foreign = exhaustion_rates_of_foreign.reset_index()
                stock_list = pd.merge(stock_list, exhaustion_rates_of_foreign, left_on='종목코드', right_on='티커', how='outer')

                # 밑으로 더하기
                market_net_purchases_Total=stock.get_market_net_purchases_of_equities_by_ticker(dDate, dDate, "ALL", "외국인")
                market_net_purchases_Total=market_net_purchases_Total.drop(["종목명", "매도거래량", "매수거래량", '매도거래대금', '매수거래대금'], axis=1)
                market_net_purchases_Total.rename(columns={'순매수거래량':'외국인순매수거래량', '순매수거래대금':'외국인순매수거래대금'}, inplace=True)


                # market_net_purchases_foreign = market_net_purchases_foreign.reset_index()
                #stock_list = pd.merge(stock_list, market_net_purchases_foreign, left_on='종목코드', right_on='티커', how='outer')

                market_net_purchases=stock.get_market_net_purchases_of_equities_by_ticker(dDate, dDate, "ALL", "기관합계")
                market_net_purchases=market_net_purchases.drop(["종목명", "매도거래량", "매수거래량", '매도거래대금', '매수거래대금'], axis=1)
                market_net_purchases.rename(columns={'순매수거래량':'기관순매수거래량', '순매수거래대금':'기관순매수거래대금'}, inplace=True)

                # market_net_purchases_Total=pd.concat([market_net_purchases_Total, market_net_purchases])

                # market_net_purchases_foreign = market_net_purchases_foreign.reset_index()
                market_net_purchases_Total = pd.merge(market_net_purchases_Total, market_net_purchases, left_on='티커', right_on='티커', how='outer')

                market_net_purchases=stock.get_market_net_purchases_of_equities_by_ticker(dDate, dDate, "ALL", "개인")
                market_net_purchases=market_net_purchases.drop(["종목명", "매도거래량", "매수거래량", '매도거래대금', '매수거래대금'], axis=1)
                market_net_purchases.rename(columns={'순매수거래량':'개인순매수거래량', '순매수거래대금':'개인순매수거래대금'}, inplace=True)
                # market_net_purchases_foreign = market_net_purchases_foreign.reset_index()
                market_net_purchases_Total = pd.merge(market_net_purchases_Total, market_net_purchases, left_on='티커', right_on='티커', how='outer')
                # market_net_purchases_Total=pd.concat([market_net_purchases_Total, market_net_purchases])

                stock_list = pd.merge(stock_list, market_net_purchases_Total, left_on='종목코드', right_on='티커', how='outer')

                shorting_value_KOSPI=stock.get_shorting_value_by_ticker(dDate, 'KOSPI')
                shorting_value_KOSDAQ=stock.get_shorting_value_by_ticker(dDate, 'KOSDAQ')
                shorting_value_total=pd.concat([shorting_value_KOSPI, shorting_value_KOSDAQ])
                
                shorting_value_total=shorting_value_total.drop(["매수"], axis=1)
                shorting_value_total.rename(columns={'비중':'공매도비중'}, inplace=True)
                
                stock_list = pd.merge(stock_list, shorting_value_total, left_on='종목코드', right_on='티커', how='outer')

                market_fundamental=pd.DataFrame(stock.get_market_fundamental_by_ticker(date=dDate, market="ALL"))  
                market_fundamental.rename(columns={'DIV':'DDIV'}, inplace=True)

                stock_list = pd.merge(stock_list, market_fundamental, left_on='종목코드', right_on='티커', how='outer')
                
                df_total = stock.get_market_cap(dDate, 'ALL')
                df_total = df_total.drop(["종가", "거래량", '거래대금', '상장주식수'], axis=1)
                stock_list = pd.merge(stock_list, df_total, left_on='종목코드', right_on='티커', how='outer')

                stock_list  = stock_list.dropna(subset=['종목명'])    #종목명이 없으면 삭제
                stock_list  = stock_list .fillna(0)   # NaN항목을 "0" 으로 변환

                stock_list.insert(0,'거래날자', dDate)
                stock_list.insert(0,'기록시간', datetime.datetime.now().strftime("%Y%m%d %H%M%S"))

                # stock_list.to_csv('C:/datadisk/test.csv', encoding='utf-8-sig')
            except:
                pass        

            try:
                for idx in range(len(stock_list)):
                    sql = "INSERT IGNORE INTO daily (기록시간,거래날자,종목코드,종목명,시가,고가,저가,종가,거래량,거래대금,"
                    sql +=" 등락률,상장주식수,보유수량,지분율,한도수량,한도소진률,외국인순매수거래량,외국인순매수거래대금,"
                    sql +=" 기관순매수거래량,기관순매수거래대금,개인순매수거래량,개인순매수거래대금,공매도,공매도비중,BPS,PER,"	
                    sql +=" PBR,EPS,DDIV,DPS,시가총액)"
                    sql +=" VALUES"
                    sql +="	(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" 

                    cur.execute(sql, tuple(stock_list.values[idx]))
                    connPy.commit()

                    sql="update stock_code_list set basic_info_date= '" + dDate + "' where 종목코드='" + str(stock_list['종목코드'][idx]) + "'"
                    cur.execute(sql)
                    connPy.commit()

                #print(dDate, '기본정보 저장성공')
            except:
                print(dDate, '기본정보 저장실패')
                #self.statusBar().showMessage(dDate, '기본정보 저장실패')
                pass

            try:    # ETF
                ##########################################################
                # ETF
                ##########################################################

                etf_list = pd.DataFrame({'종목코드':stock.get_etf_ticker_list()})
                etf_list['종목명'] = etf_list['종목코드'].map(lambda x: stock.get_etf_ticker_name(x))

                etf_list_copy = etf_list.copy()
                etf_list_copy = etf_list_copy.reset_index()

                etf_list_copy = etf_list.copy()
                etf_list_copy.insert(0,'거래날자', dDate)
                etf_list_copy.insert(0,'기록시간', datetime.datetime.now().strftime("%Y%m%d %H%M%S"))
                etf_list_copy.rename(columns={'티커':'종목코드'}, inplace=True)
                
                dfETF = stock.get_etf_ohlcv_by_ticker(dDate)
                dfETF = dfETF.reset_index()
                dfETF.rename(columns={'티커':'종목코드'}, inplace=True)
                dfETF=dfETF.drop(["NAV", "기초지수"], axis=1)

                df = stock.get_etf_price_change_by_ticker(dDate, dDate)
                df = df.drop(["시가", "종가", "변동폭", '거래량', '거래대금'], axis=1)
                df = df.reset_index()
                df.rename(columns={'티커':'종목코드'}, inplace=True)
                # df.to_csv('C:/datadisk/df.csv', encoding='utf-8-sig')
                # df = df.drop(["시가", "종가", "변동폭", "거래량", "거래대금"], axis=1)

                result = pd.merge(etf_list_copy, dfETF, left_on='종목코드', right_on='종목코드', how='outer')
                resultS= pd.merge(result, df, left_on='종목코드', right_on='종목코드', how='outer')       
                resultS  = resultS.dropna(subset=['종목명'])    #종목명이 없으면 삭제

                resultS  = resultS .fillna(0)   # NaN항목을 "0" 으로 변환

                for kk in range(len(resultS)):
                    sql = "INSERT IGNORE INTO daily (기록시간, 거래날자, 종목코드, 종목명, 시가, 고가, 저가, 종가, 거래량, 거래대금, 등락률)"
                    sql+=" VALUES ("
                    sql+= "'"+ datetime.datetime.now().strftime('%Y%m%d %H%M%S') + "', "
                    sql+= str(dDate) + ", "
                    sql+= str(resultS.loc[kk, "종목코드"]) + ", "
                    sql+= "'" + str(resultS.loc[kk, "종목명"]) + "', "
                    
                    sql+= str(resultS.loc[kk, "시가"]) + ", "
                    sql+= str(resultS.loc[kk, "고가"]) + ", "
                    sql+= str(resultS.loc[kk, "저가"]) + ", "
                    sql+= str(resultS.loc[kk, "종가"]) + ", "
                    sql+= str(resultS.loc[kk, "거래량"]) + ", "
                    sql+= str(resultS.loc[kk, "거래대금"]) + ", "
                    sql+= str(resultS.loc[kk, "등락률"]) + ""
                    sql+=")"

                    cur.execute(sql)
                    connPy.commit()
                    
                    sql="update stock_code_list set basic_info_date= '" + dDate + "' where 종목코드='" + str(resultS.loc[kk, "종목코드"]) + "'"
                    cur.execute(sql)
                    connPy.commit()

                sql="update tradingdate set basic_info= 'Collected' where MarketOpenDate='" + dDate + "'"
                cur.execute(sql)
                connPy.commit()
                print("ETF", dDate, '2/2 ETF 저장성공','하루의 결과를 완료', datetime.datetime.now().strftime("%H:%M:%S"))
                #self.statusBar().showMessage("ETF", dDate, '2/2 ETF 저장성공','하루의 결과를 완료', datetime.datetime.now().strftime("%H:%M:%S"))
            except:
                print('ETF 저장실패', dDate)
                #self.statusBar().showMessage('ETF 저장실패', dDate)
                pass
            print("Basic_Info", dDate, '하루의 결과를 완료', datetime.datetime.now().strftime("%H:%M:%S"))
            #self.statusBar().showMessage("Basic_Info", dDate, '하루의 결과를 완료', datetime.datetime.now().strftime("%H:%M:%S"))
        else: # 이미 기본정보가 저장되었다면 stock_code_list 의 basic_info_date 에 오늘의 날자를 기록
            pass
            '''
            stock_list = pd.DataFrame({'종목코드':stock.get_market_ticker_list(market="ALL")})
            for idx in range(len(stock_list)):
                sql="update stock_code_list set basic_info_date= '" + dDate + "' where 종목코드='" + str(stock_list['종목코드']) + "'"
                cur.execute(sql)
                connPy.commit()
            etf_list = pd.DataFrame({'종목코드':stock.get_etf_ticker_list(dDate)})
            for idx in range(len(etf_list)):
                sql="update stock_code_list set basic_info_date= '" + dDate + "' where 종목코드='" + str(etf_list['종목코드']) + "'"
                cur.execute(sql)
                connPy.commit()
            '''
    
    def shorting_update(self):#(fromdate, todate, 종목코드, 종목명):

        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")
        cur.fetchall()
        ########################################################################################################################
            # 공매도는 3일전까지만 조회가능하므로 3일전 거래일을 조회
        sql = "SELECT S.marketopendate from (SELECT marketopendate FROM tradingdate ORDER BY marketopendate DESC LIMIT 3) as S ORDER BY marketopendate ASC"

        cur.execute(sql)
        rows = cur.fetchall()
        #print(rows) 
        todate = rows[0][0] # "20220124"

        sql="SELECT 종목코드, 종목명, shorting_date FROM stock_code_list where stockORetf='stock'"
        shorting_update_stock_code = pd.read_sql_query(sql, connPy)
        shorting_update_stock_code  = shorting_update_stock_code.fillna(0)

        for idx in range(len(shorting_update_stock_code)):
            if int(todate) > int(shorting_update_stock_code.loc[idx, "shorting_date"]) or int(shorting_update_stock_code.loc[idx, "shorting_date"])==0:
                if int(shorting_update_stock_code.loc[idx, "shorting_date"])==0:
                    fromdate = "20200101"
                else:
                    fromdate = shorting_update_stock_code.loc[idx, "shorting_date"]# "20200101"


                # shorting_update(fromdate, todate, 종목코드, 종목명)
                # print(idx+1,"/",len(shorting_update_stock_code), 종목명)
        #cur.close()
        #connPy.close()
        ##########################################################################################################################

                sqlH="UPDATE daily SET 공매도잔고 = %s, 공매도금액 = %s, 공매도잔고비중 = %s WHERE 종목코드 = %s and 거래날자 = %s"
                # sql=[['0','0','0.0','000020','20200103'], ['0','0','0.0','000020','20200103']]
                # cur.executemany(sqlH, sql)
                sql_value=[]

                try:      
                    # 가끔 Access Denied
                    dfshort = stock.get_shorting_balance_by_date(fromdate, todate, shorting_update_stock_code.loc[idx, "종목코드"])
                    time.sleep(0.1)
                    if dfshort.empty==False:                         
                        sqlH="UPDATE daily SET 공매도잔고 = %s, 공매도금액 = %s, 공매도잔고비중 = %s WHERE 종목코드 = %s and 거래날자 = %s"
                        sql_inner=[]
                        for kk in range(len(dfshort)):
                            sql_inner.append(str(dfshort.iloc[kk, 0]))
                            sql_inner.append(str(dfshort.iloc[kk, 2]))
                            sql_inner.append(str(dfshort.iloc[kk, 4]))
                            sql_inner.append(str(shorting_update_stock_code.loc[idx, "종목코드"]))
                            sql_inner.append(dfshort.index[kk].strftime("%Y%m%d"))
                            
                            sql_value.append(sql_inner)
                            
                            del sql_inner
                            sql_inner=[]
                        cur.executemany(sqlH, sql_value)
                        connPy.commit()
                    else:
                        #print(shorting_update_stock_code.loc[idx, "종목명"], '에 공매도 정보가 없습니다. 상장 전이죠?')
                        print(str(str(idx+1)+"/"+str(len(shorting_update_stock_code))),shorting_update_stock_code.loc[idx, "종목명"], '에 공매도를 저장하지 못했어요?')
                            
                        #self.statusBar().showMessage(shorting_update_stock_code.loc[idx, "종목명"], '에 공매도 정보가 없습니다. 상장 전이죠?')
                        pass
                    
                    try:
                        if dfshort.empty==False:    #공매도 데이터가 있는 경우만 날자를 기록
                            print(str(str(idx+1)+"/"+str(len(shorting_update_stock_code))), dfshort.index[kk].strftime("%Y%m%d"), shorting_update_stock_code.loc[idx, '종목명'],'공매도 저장성공')
                            #sself.statusBar().showMessage(str(str(idx+1)+"/"+str(len(shorting_update_stock_code))), dfshort.index[kk].strftime("%Y%m%d"), shorting_update_stock_code.loc[idx, '종목명'],'공매도 저장성공')
                            sql = "update stock_code_list set shorting_date='" + dfshort.index[kk].strftime("%Y%m%d") + "' where 종목코드='" + shorting_update_stock_code.loc[idx, '종목코드'] +"'"
                            cur.execute(sql)
                            connPy.commit()
                    except:
                        pass
                except:
                    #print(shorting_update_stock_code.loc[idx, "종목명"],'공매도 저장실패') #, dfshort.index[kk].strftime("%Y%m%d"), 종목명)
                    print(str(str(idx+1)+"/"+str(len(shorting_update_stock_code))),shorting_update_stock_code.loc[idx, "종목명"], '에 공매도 정보가 없습니다. 아마도 상장 전이죠?')
                        
                    #self.statusBar().showMessage(shorting_update_stock_code.loc[idx, "종목명"],'공매도 저장실패')
                            
                    #shorting_update_stock_code
                    pass
            종목코드=shorting_update_stock_code.loc[idx, "종목코드"]
            종목명=shorting_update_stock_code.loc[idx, "종목명"]
            #print_string=str(str(idx+1)+"/"+str(len(shorting_update_stock_code)))
    #####################################################################################################
    def Ichimoku_Cloud(self, df): #일목균형표 계산
        #global d
        global df_Ichimoku_Cloud
        df_Ichimoku_Cloud = df.sort_index(ascending=True)#False) # my Live NSE India data is in Recent -> Oldest order

        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
        period9_high = df_Ichimoku_Cloud['High'].rolling(window=9).max()
        period9_low = df_Ichimoku_Cloud['Low'].rolling(window=9).min()
        tenkan_sen = (period9_high + period9_low) / 2

        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        period26_high = df_Ichimoku_Cloud['High'].rolling(window=26).max()
        period26_low = df_Ichimoku_Cloud['Low'].rolling(window=26).min()
        kijun_sen = (period26_high + period26_low) / 2

        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        period52_high = df_Ichimoku_Cloud['High'].rolling(window=52).max()
        period52_low = df_Ichimoku_Cloud['Low'].rolling(window=52).min()
        senkou_span_b = ((period52_high + period52_low) / 2).shift(26)

        # The most current closing price plotted 22 time periods behind (optional)
        chikou_span = df_Ichimoku_Cloud['Close'].shift(-22) # Given at Trading View.
        
        df_Ichimoku_Cloud['전환선'] = tenkan_sen
        df_Ichimoku_Cloud['기준선'] = kijun_sen
        df_Ichimoku_Cloud['선행스팬1'] = senkou_span_a
        df_Ichimoku_Cloud['선행스팬2'] = senkou_span_b
        df_Ichimoku_Cloud['후행스팬'] = chikou_span    

        # 현재의 후행스팬은 존재하지 않는다.
        df_Ichimoku_Cloud=df_Ichimoku_Cloud[['거래날자','전환선','기준선','선행스팬1','선행스팬2','후행스팬']]
        

        return df_Ichimoku_Cloud #.sort_index(ascending=True)
    
    def sub_VWAP(self, df, sum_day_count): #Volume Weighted Average Price Calculation
        global df_VWAP

        #df_VWAP = df.sort_index(ascending=True)

        '''
        sum_day_count=2
        data = [['1',1,1,1,1],
            ['2',1,1,1,1],
            ['3',1,1,1,1],
            ['4',10,1,1,10],
            ['6',10,1,1,10],
            ['7',20,1,1,20],
            ['8',20,1,1,20],
            ['9',20,1,1,20]
            ]

        df = pd.DataFrame(data, columns=['거래날자', 'High', 'Low', 'Close', 'Volume'])
        '''
        df_VWAP=df[['거래날자', 'High', 'Low', 'Close', 'Volume']].copy()
        df_VWAP['Rep_Price']=(df_VWAP['High']+df_VWAP['Low']+df_VWAP['Close'])/3
        df_VWAP['Rep_Price_C_Volume']=df_VWAP['Rep_Price']*df_VWAP['Volume']
        df_VWAP['VWAP']=1
        
        df_VWAP['sum_P_CV']=1
        df_VWAP['sum_vol']=1

        for ii in range(len(df_VWAP)):
            if ii<sum_day_count+1: # 몇일 평균인지 그리고 그보다 작으면 
                if sum(df_VWAP['Volume'][0:ii+1]) > 0:#거래량이 0보다 크면
                    #df_VWAP['sum_P_CV'][ii]=sum(df_VWAP['Rep_Price_C_Volume'][ii-sum_day_count+1:ii+1])
                    #df_VWAP['sum_vol'][ii]=sum(df_VWAP['Volume'][ii-sum_day_count+1:ii+1])

                    df_VWAP['VWAP'][ii]=sum(df_VWAP['Rep_Price_C_Volume'][0:ii+1])/sum(df_VWAP['Volume'][0:ii+1])
            else:#if i>=m_lim and i < len(A) - m_lim:
                if sum(df_VWAP['Volume'][ii-sum_day_count+1:ii+1])>0:
                    #df_VWAP['sum_P_CV'][ii]=sum(df_VWAP['Rep_Price_C_Volume'][ii-sum_day_count+1:ii+1])
                    #df_VWAP['sum_vol'][ii]=sum(df_VWAP['Volume'][ii-sum_day_count+1:ii+1])

                    df_VWAP['VWAP'][ii]=sum(df_VWAP['Rep_Price_C_Volume'][ii-sum_day_count+1:ii+1])/sum(df_VWAP['Volume'][ii-sum_day_count+1:ii+1])
        #df_VWAP.to_excel('C:/DataDisk/df_VWAP.xlsx')
        df_VWAP=df_VWAP[['거래날자', 'VWAP']].copy()
        return df_VWAP.sort_index(ascending=True)

    def sub_HA(self, df): # Heikin Ash 계산
        df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
        df['HA_Open'] = (df['Open'].shift(1) + df['Open'].shift(1)) / 2
        df.iloc[0, df.columns.get_loc("HA_Open")] = (df.iloc[0]['Open'] + df.iloc[0]['Close'])/2
        df['HA_High'] = df[['High', 'Low', 'HA_Open', 'HA_Close']].max(axis=1)
        df['HA_Low'] = df[['High', 'Low', 'HA_Open', 'HA_Close']].min(axis=1)
        df = df.drop(['Open', 'High', 'Low', 'Close'], axis=1)  # remove old columns
        df = df.rename(columns={"HA_Open": "Open", "HA_High": "High", "HA_Low": "Low", "HA_Close": "Close", "Volume": "Volume"})
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]  # reorder columns

        return df

    def sub_TA_Calc(self): # TA-LIB 계산
        # update stock_code_list set ta_calc_date='20220214';
        # delete from ta where 거래날자>='20220214';

        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")

        #240일 전의 날자를 확인 
        sql="select S.MarketOpenDate from (select MarketOpenDate from tradingdate order by MarketOpenDate desc limit 250) as S order by S.MarketOpenDate asc limit 1"
        #cur.execute(sql) 
        #before250ago = cur.fetchall()

        before250ago ='20200101'
        #before250ago ='20220201'

        sql="SELECT 종목코드, Ta_calc_date FROM stock_code_list where basic_info_date<>ta_calc_date or Ta_calc_date is null;"
        df_stock_code = pd.read_sql_query(sql, connPy)
        #df_stock_code=df_stock_code(df_stock_code,str('{0:06d}'.format(df_stock_code[(row-1)*2+col-1]))) # ]selected_stock[(row-1)*2+col-1][2]) 
                    
        cur.fetchall()

        # df_stock_code.to_csv('C:/datadisk/test.csv', encoding='utf-8-sig')

        print("TA 를 계산하기 위하여 데이터를 가져오고 있어요 시간이 필요합니다.")
        self.statusBar().showMessage("TA 를 계산하기 위하여 데이터를 가져오고 있어요 시간이 필요합니다.")
        self.statusBar().repaint()
        #sql=f"select 거래날자, 종목코드, 종목명, 시가 as Open, 고가 as High, 저가 as Low, 종가 as Close, 거래량 as Volume from daily where 거래날자>='"+before250ago[0][0]+"' ORDER BY 종목코드 ASC, 거래날자 ASC" 
        
        sql="select 거래날자, 종목코드, 종목명, 시가 as Open, 고가 as High, 저가 as Low, 종가 as Close, 거래량 as Volume"
        sql+=" from daily"
        sql+=f" where 거래날자>='"+before250ago[0][0]+"'"
        sql+=" and 종목코드 in (SELECT 종목코드 FROM stock_code_list where basic_info_date<>ta_calc_date or Ta_calc_date is null)"
        sql+=" ORDER BY 종목코드 ASC, 거래날자 ASC"

        df_all = pd.read_sql_query(sql, connPy)
        print("데이터를 가져왔습니다. 오래 기다렸죠. TA를 계산합니다.")
        self.statusBar().showMessage("TA 를 계산하기 위하여 데이터를 가져왔습니다. 오래 기다렸죠. TA를 계산합니다.")
        self.statusBar().repaint()
        try:
            for jj in range(len(df_stock_code)):
                #print(str(df_stock_code.loc[jj, '종목코드']) +'종목에 대하여 TA 계산을 시작합니다.')
                #self.statusBar().showMessage(str(df_stock_code.loc[jj, '종목코드']) +'종목에 대하여 TA 계산을 시작합니다.')
                start = time.time()
                df=[]
                #df[df['country'] == '한국']
                if df_stock_code.loc[jj, '종목코드']=='069500':
                    Continue
                
                try:
                    df=df_all[df_all['종목코드']==str(df_stock_code.loc[jj, '종목코드'])]
                except:
                    #상장폐지되는 종목을 지운다
                    #종목코드리스트에 종목은 있지만 daily 에 데이터가 없는 경우 삭제
                    sql="DELETE FROM stock_code_list WHERE 종목코드='"+str(df_stock_code.loc[jj, '종목코드'])+"'"
                    cur.execute(sql)
                    sql="DELETE FROM daily WHERE 종목코드='"+str(df_stock_code.loc[jj, '종목코드'])+"'"
                    cur.execute(sql)
                df = df.sort_index(ascending=True)
                #print("TA 계산", ii, "/", len(df_stock_code), df_stock_code.loc[ii, '종목코드']) # , stock.get_market_ticker_name(df_stock_code.iloc[ii, 0]))
                #sql=f"select 거래날자, 종목코드, 종목명, 시가 as Open, 고가 as High, 저가 as Low, 종가 as Close, 거래량 as Volume from daily where 거래날자>='"+before250ago[0][0]+"' and 종목코드='"+str(df_stock_code.iloc[ii, 0])+"' ORDER BY 거래날자 " 

                if df.empty==False:   # 정보가 daily 에 있다면

                    #sql=f"select 거래날자, 종목코드, 시가 as Open, 고가 as High, 저가 as Low, 종가 as Close, 거래량 as Volume from daily where 거래날자>='"+before241ago[0][0]+" and 종목코드={str(df_stock_code.iloc[ii, 0])}" 
                    # df.insert(7,'종목명', stock.get_market_ticker_name(df_stock_code.iloc[ii, 0]))
                    df  = df.fillna(0)

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

                    df.fillna(0)
                    try:
                        df['RSIMA5'] = ta.SMA(df["RSI"],5) # RSI 5일평균
                    except:
                        df['RSIMA5'] =0
                    df['willr14'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=14) #Williams %R Price
                    df  = df .fillna(0)
                    df['AVGwillr14'] = ta.SMA(df['willr14'], 5) #Williams %R Price Average

                    df['willr120'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=120)   #Williams %R Volume
                    df  = df .fillna(0)
                    df['AVGwillr120'] = ta.SMA(df['willr120'], 5)   #Williams %R Volume Average

                    # Stochastic
                    df['slowk'], df['slowd'] = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
                    #  Stochastic Relative Strength Index
                    df['STOCHRSI_fastk'], df['STOCHRSI_fastd'] = ta.STOCHRSI(df['Close'], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)

                    # Parabolic SAR

                    dfPSAR=df[['거래날자','High','Low']].copy()    #dataframe 을 분리
                    dfPSAR.fillna(0)
                    #print(df.iat[1,2])

                    dfPSAR['psar'] = ta.SAR(high=dfPSAR.High, low=dfPSAR.Low, acceleration=0.02, maximum=0.20)
                    #dfPSAR.fillna(0)

                    #pd.merge(df, dfPSAR, left_on='거래날자', right_on='거래날자')#.drop(columns='High',columns='Low')
                    df=pd.merge(df, dfPSAR)
                    #df.to_csv('C:/datadisk/test.csv', encoding='utf-8-sig')
                    df['arronOSC'] = ta.AROONOSC(df['High'], df['Low'], timeperiod=14)

                    #ADX
                    df['adx'] = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)       # ADX - Average Directional Movement Index
                    df['pdi'] = ta.PLUS_DI(df['High'], df['Low'], df['Close'], timeperiod=14)   #PLUS_DI - Plus Directional Indicator
                    df['mdi'] = ta.MINUS_DI(df['High'], df['Low'], df['Close'], timeperiod=14)  #MINUS_DI - Minus Directional Indicator
                    #dft=[]
                    #df  = df.fillna(0)
                    df['macd'], df['macdSignal'],df['macdHist'] = ta.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

                    self.sub_HA(df) # Heikin Ash 
                    df=df.fillna(0)
                    
                    self.Ichimoku_Cloud(df)  #일목균형표
                    df = pd.merge(df, df_Ichimoku_Cloud, how='left', on='거래날자')

                    #일목균형표에서 계산된 data frame d 를 결합
                    df.fillna(0)    

                    self.sub_VWAP(df, 5) #Volume Weighted Average Price, 계산하는 기간을 설정
                    df = pd.merge(df, df_VWAP, how='left', on='거래날자')
                    # >= 이 올바른 표현                    
                    df = df[df['거래날자'] >= df_stock_code.loc[jj, 'Ta_calc_date']]
                    df  = df.fillna(0)
                    df.to_csv('C:/datadisk/test.csv', encoding='utf-8-sig')
                    #df=df.replace('0.0e0', 0)
                    for idx in range(len(df)):

                        sql = "INSERT IGNORE INTO ta (거래날자, 종목코드, 종목명, Open, High, Low, Close, Volume,"
                        sql +=" MA5, MA10, MA20, MA60, MA120, MA240, VMA5, VMA10, VMA20, VMA60, VMA120,VMA240,"
                        sql +=" up_band, mid_band, low_band, RSI, RSIMA5, willr14, AVGwillr14, willr120, AVGwillr120, slowk, slowd,"
                        sql +="  STOCHRSI_fastk, STOCHRSI_fastd, psar, arronOSC, adx, pdi, mdi, macd,macdSignal, macdHist, HA_Close, HA_Open, HA_High, HA_Low,"
                        sql +=" 전환선, 기준선, 선행스팬1, 선행스팬2, 후행스팬, VWAP)"
                        sql +=" VALUES"
                        sql +=" (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
 
                        try:
                            cur.execute(sql, tuple(df.values[idx]))
                            #connPy.commit()
                            
                            sql = "update stock_code_list set ta_calc_date='" + df.iloc[idx,0] + "' where 종목코드='" + df.iloc[idx, 1] +"'"
                            cur.execute(sql)
                            #connPy.commit()                          

                        except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
                            print('예외가 발생했습니다.', e)
                            Continue
                    connPy.commit()
                    print(str(jj)+'/'+str(len(df_stock_code))," 저장했어요, 저장시간", time.time()-start)
                    self.statusBar().showMessage(str(jj)+'/'+str(len(df_stock_code))+" 저장했어요, 저장시간 :"+ str(time.time()-start))
                    self.statusBar().repaint()

                    #self.statusBar().showMessage(jj+'/'+len(df_stock_code)," 저장했어요, 저장시간", time.time()-start)
                else:
                    print("종목코드 "+df_stock_code.loc[jj, '종목코드']+" 정보가 없어 보조지표를 계산할 수 없습니다. 왜 daily 에 정보가 없는지 확인해야 합니다. 추후 확인필요")
                    #self.statusBar().showMessage("종목코드 "+df_stock_code.loc[jj, '종목코드']+" 정보가 없어 보조지표를 계산할 수 없습니다.")
                    pass
        except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
            print('예외가 발생했습니다.', e)


    #####################################################################################################
    def best_stock_to_db(self,calc_date):
        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")
        cur.fetchall()

        MinTransactionPrice=5000
        MinMarketCapitalization=200000000000
        MinMarketTransation=100000000
        MinTransactionVolume=100000

        sql=f"SELECT DISTINCT 거래날자 FROM tA WHERE 거래날자<='{calc_date}' ORDER BY 거래날자 DESC;"
        dfDate = pd.read_sql_query(sql, connPy)

        # 오일거래세배 눌림
        dfSelected=[]
        sql="select ta.거래날자, ta.종목명, ta.종목코드"
        sql+=" from ta ta, ta tb, ta tc, daily da"
        sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
        sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
        sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
        sql+=" and ta.close>ta.psar"
        sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
        sql+=""
        sql+= " and tb.거래날자='"+dfDate.거래날자[1]+"'"
        sql+= " and tc.거래날자='"+dfDate.거래날자[2]+"'"
        sql+= " and ta.종목코드=tb.종목코드"
        sql+= " and ta.종목코드=tc.종목코드"
        sql+= " and tb.VMA5>tb.VMA10*1.5"
        sql+= " and tc.VMA5<tc.VMA10*1.5" 
        sql+= " and tb.Volume>ta.Volume"               
        sql+= " and ta.close>ta.mid_band"

        dfSelected = pd.read_sql_query(sql, connPy)
        for idx in range(len(dfSelected)):
            sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','1 오일거래 세배 눌림')"
            cur.execute(sql)
            connPy.commit()
        print(dfDate.거래날자[0], '오일거래량세배 눌림 종목에 대한', '계산을 완료하였습니다.')
        # 오일거래세배 최초
        dfSelected=[]
        sql="select ta.거래날자, ta.종목명, ta.종목코드"
        sql+=" from ta ta, ta tb, ta tc, daily da"
        sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
        sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
        sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
        sql+=" and ta.close>ta.psar"
        sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
        sql+=""
        sql+= " and tb.거래날자='"+dfDate.거래날자[1]+"'"
        sql+= " and tc.거래날자='"+dfDate.거래날자[2]+"'"
        sql+= " and ta.종목코드=tb.종목코드"
        sql+= " and ta.종목코드=tc.종목코드"
        sql+= " and ta.VMA5>ta.VMA10*1.5"
        sql+= " and tb.VMA5<tb.VMA10*1.5"              
        sql+= " and ta.close>ta.mid_band"

        dfSelected = pd.read_sql_query(sql, connPy)
        for idx in range(len(dfSelected)):
            sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','2 오일거래 세배 최초')"
            cur.execute(sql)
            connPy.commit()
        print(dfDate.거래날자[0], '오일거래량세배 최초 종목에 대한', '계산을 완료하였습니다.')

        dfSelected=[]
        # 오늘 볼린저밴드 상단 눌림
        sql="select ta.거래날자, ta.종목명, ta.종목코드"
        sql+=" from ta ta, ta tb, ta tc, daily da"
        sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
        sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
        sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
        sql+=" and ta.close>ta.psar"
        sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
        sql+=""
        sql+= " and tb.거래날자='"+dfDate.거래날자[1]+"'"
        sql+= " and tc.거래날자='"+dfDate.거래날자[2]+"'"
        sql+= " and ta.종목코드=tb.종목코드"
        sql+= " and ta.종목코드=tc.종목코드"

        sql+= " and tb.close>tb.up_band"
        sql+= " and tc.close<tc.up_band"
        sql+= " and tb.Volume>ta.Volume"               
        sql+= " and ta.close>ta.mid_band;"

        print(sql)

        dfSelected = pd.read_sql_query(sql, connPy)

        for idx in range(len(dfSelected)):
            sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','3 볼린저 상단 눌림')"
            cur.execute(sql)
            connPy.commit()
        print(dfDate.거래날자[0], '볼린저돌파 종목에 대한', '계산을 완료하였습니다.')

        dfSelected=[]
        # 오늘 볼린저밴드 상단 최초
        sql="select ta.거래날자, ta.종목명, ta.종목코드"
        sql+=" from ta ta, ta tb, ta tc, daily da"
        sql+=" Where da.거래대금>"+str(MinMarketTransation)+" and da.시가총액>"+str(MinMarketCapitalization)+""    #거래대금 1억원 이상, #시가총액 2000억 이상 
        sql+=" and ta.VMA5>"+str(MinTransactionVolume)+" and da.종가>"+str(MinTransactionPrice)+""  #Volume 5만주이상 #종가 5000원 이상
        sql+=" and da.거래날자=ta.거래날자 and ta.종목코드=da.종목코드"
        sql+=" and ta.close>ta.psar"
        sql+=" and ta.거래날자='" + dfDate.거래날자[0] + "'"
        sql+=""
        sql+= " and tb.거래날자='"+dfDate.거래날자[1]+"'"
        sql+= " and tc.거래날자='"+dfDate.거래날자[2]+"'"
        sql+= " and ta.종목코드=tb.종목코드"
        sql+= " and ta.종목코드=tc.종목코드"

        sql+= " and ta.close>ta.up_band"
        sql+= " and tb.close<tb.up_band"            
        sql+= " and ta.close>ta.mid_band;"

        print(sql)

        dfSelected = pd.read_sql_query(sql, connPy)

        for idx in range(len(dfSelected)):
            sql="INSERT IGNORE INTO selected_stock (SaveDate, 종목명, 종목코드, 선정이유) values ("
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','4 볼린저 상단 최초')"
            cur.execute(sql)
            connPy.commit()
        print(dfDate.거래날자[0], '볼린저돌파 종목에 대한', '계산을 완료하였습니다.')


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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','5 장기 눌림목')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','6 지속상승')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','7 5Heikin Ash 방향전환')"
            #cur.execute(sql)
            #connPy.commit()
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','8 이십육십돌파')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','9 이십백이십돌파')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','10 이십이백사십돌파')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','11 육십백이십돌파')"
            cur.execute(sql)
            connPy.commit()
        print(dfDate.거래날자[0], '육십백이십돌파 종목에 대한', '계산을 완료하였습니다.')



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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','12 14일신고가')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','13 120일 신고가')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','14 Stochastic GC')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','15 MACD GC')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','16 3일간 눌림목')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','17 주가대비거래량양호')"
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
            sql+="'"+dfSelected.iloc[idx,0]+"','"+dfSelected.iloc[idx,1]+"','"+dfSelected.iloc[idx,2]+"','18 장기바닦')"
            cur.execute(sql)
            connPy.commit()
        print(dfDate.거래날자[0], '장기바닦 종목에 대한', '계산을 완료하였습니다.')


        # SELECT 종목명, count(종목명)
        # FROM selected_stock 
        # WHERE SaveDate>'20220201' and (선정이유='1오일거래량세배' or 선정이유='2볼린저돌파') GROUP BY 종목코드 HAVING count(종목명) >1
        # 2번이상 선정된 종목을 Excel 에 기록하는 프로그램 작성필요
        #   
    def Whole_Data_Collect(self):

    #if __name__ == '__main__': 

        connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
        cur = connPy.cursor()
        cur.execute("use sstock")
        cur.fetchall()
        #sub_TA_Calc()
        self.statusBar().showMessage("전체데이터 수집을 시작합니다.")
        self.statusBar().repaint()

        self.stock_market_open_date() #장이 열리는 날인지 확인하고 날자를 tradingdate 에 기록
    # 주식코드 정리
        stock_list = pd.DataFrame({'종목코드':stock.get_market_ticker_list(market="ALL")})
        stock_list['종목명'] = stock_list['종목코드'].map(lambda x: stock.get_market_ticker_name(x))
        # stock_list['종목명'] = stock_list['종목명']+stock_list['code_update_date']
        
        stock_list.insert(2,'code_update_date', datetime.datetime.now().strftime("%Y%m%d"))
        stock_list.insert(3,'stockORetf', 'stock')

        for idx in range(len(stock_list)):
            sql = "INSERT INTO stock_code_list (종목코드,종목명,code_update_date,stockORetf)"
            sql += " VALUES ("
            sql += "'"+str(stock_list.loc[idx,'종목코드'])+"','"+str(stock_list.loc[idx,'종목명'])+"','"+str(stock_list.iloc[idx,2])+"','"+str(stock_list.iloc[idx, 3])+"'"
            sql += ") ON DUPLICATE KEY"
            sql += " UPDATE code_update_date='" + str(stock_list.iloc[idx, 2])+"',stockORetf='"+str(stock_list.iloc[idx,3])+"'"

            cur.execute(sql)#, tuple(stock_list.values[idx]))
            connPy.commit()

        # ETF는 종목정리
        etf_list = pd.DataFrame({'종목코드':stock.get_etf_ticker_list()})
        etf_list['종목명'] = etf_list['종목코드'].map(lambda x: stock.get_etf_ticker_name(x))
        etf_list.insert(2,'code_update_date', datetime.datetime.now().strftime("%Y%m%d"))
        etf_list.insert(3,'stockORetf', 'etf')

        for idx in range(len(etf_list)):
            sql = "INSERT INTO stock_code_list (종목코드, 종목명, code_update_date, stockORetf)"
            sql += " VALUES ("
            sql += "'"+str(etf_list.iloc[idx,0])+"','"+str(etf_list.iloc[idx,1])+"','"+str(etf_list.iloc[idx,2])+"','"+str(etf_list.iloc[idx,3])+"'"
            sql += ") ON DUPLICATE KEY"
            sql += " UPDATE code_update_date='"+str(etf_list.iloc[idx,2])+"',stockORetf='"+str(etf_list.iloc[idx,3])+"'"

            cur.execute(sql)#, tuple(stock_list.values[idx]))
            connPy.commit()

        # tradingdate 테이블에 새로운 날자가 넣어지면 basic_info 는 null 
        # null 의 날자가 있으면 기본 정보를 모은다
        sql = "SELECT MarketOpenDate, basic_info FROM tradingdate"
        sql+= " WHERE dayORweek='day' and basic_info is null order by MarketOpenDate ASC;"

        pdTradingDate = pd.read_sql_query(sql, connPy) #장이 열리는 날을 가져온다

        for ii in range(len(pdTradingDate)):
            dDate=pdTradingDate.loc[ii, "MarketOpenDate"]
            basic_info_mission=pdTradingDate.loc[ii, "basic_info"]
            if dDate>datetime.datetime.now().strftime("%Y%m%d") or (dDate==datetime.datetime.now().strftime("%Y%m%d") and datetime.datetime.now().strftime("%H:%M:%S")>'18:00:00'):
                self.Data_Collector(dDate, basic_info_mission)
                #self.shorting_update()
                connPy.commit()
                #cur.close()
                #connPy.close()
        self.statusBar().showMessage("공매도 정보 수집을 시작합니다.")
        self.statusBar().repaint()

        self.shorting_update()

        #종목코드가 5자리이면 6개로 변경
        sql="select 종목코드 from daily where length(종목코드)=5"
        df = pd.read_sql_query(sql, connPy)

        for idx in range(len(df)):
            sql=f"update daily set 종목코드=concat('0','{df.종목코드[idx]}') where 종목코드='{df.종목코드[idx]}';"
            cur.execute(sql)
            connPy.commit()

        self.sub_TA_Calc()

        # Selected_Stock 을 선정
        # 모든 거래날자를 거져와서 하루씩 계산
        # sql="SELECT DISTINCT 거래날자 FROM ta WHERE 거래날자>'20210101' ORDER BY 거래날자 ASC;"
        sql="SELECT DISTINCT ta.거래날자 FROM ta ta WHERE ta.거래날자>'20210101' and ta.거래날자 "
        sql+=" not in (select DISTINCT SaveDate from selected_stock WHERE SaveDate>'20210101');"
        dfDate = pd.read_sql_query(sql, connPy)

        for df_Date in range(0,len(dfDate)):
            calc_date=dfDate.iloc[df_Date][0]
            self.best_stock_to_db(calc_date)

        # selected_stock 에 대하여 선정된 날자 이후의 주가변화를 기록
        #self.Select_Best_Stock()
        self.Stock_Price_After_Selected()

        print("모든 계산을 완료했어요")
        self.statusBar().showMessage("모든 계산을 완료했어요")
        self.statusBar().repaint()
        
            #connPy.commit()



    #df.to_excel('C:/DataDisk/theme.xlsx')     
    #df1 = df.groupby(['stock'])['theme'].apply(lambda x: ','.join(x)).reset_index() 


    #@pyqtSlot()
    #def on_click(self):
    #    self.game.setText(self.game_line_edit.text())

if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())


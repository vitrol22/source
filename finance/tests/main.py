from PyQt5.QtCore import pyqtSlot
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

import plotly.express as px
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from pyparsing import Empty

sys.path.append('C:\\Users\\user\\Anaconda3\\libs')
import requests
from io import BytesIO
import pandas as pd
 
from bs4 import BeautifulSoup
import datetime
import pymysql
pymysql.install_as_MySQLdb()
from plotly.offline import iplot, plot
import plotly.graph_objs as go

#class Window(QWidget):
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
        # 버튼 처리
        self.btn_theme_stock.clicked.connect(self.theme_stock)                            
        self.cb_compare_stock.currentTextChanged.connect(self.def_cb_compare_stock)

    def initUI(self):

        self.setWindowTitle("예스 스탁")
        self.setGeometry(300, 300, 700, 500) 
 
        self.statusbar = self.statusBar() # 상태바 만들기
        self.statusBar().showMessage('예스 스탁이 준비되었습니다.')

        url = "https://finance.naver.com/sise/sise_market_sum.naver"
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

        cb_list_selected_date = ["오늘", "어제", "5일전", "10일전", "20일전"]
        self.cb_selected_date = QComboBox(self)
        self.cb_selected_date.addItems(cb_list_selected_date)
        self.cb_selected_date.setFont(QFont("'HY동녘B'",14)) #폰트,크기 조절
        self.cb_selected_date.setStyleSheet("color: rgb(255, 255, 255);"
                "background-color: rgb(150, 0, 56);"
                "border-style: dashed;"
                "border-width: 0px;"
                "border-color: #1E90FF")

        # 한개의 plot 을 stadlone window 에 보이기 선택
        cb_list_best_stock = ["보유", "1오일거래량세배", "2볼린저돌파", "ETF", "관심종목"]
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

        self.btn_plot_again  = QPushButton("다시 보이기", self)
        self.btn_plot_again.clicked.connect(self.show_graph)

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
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5)
        )
        

        fig = go.Figure(data=data, layout=layout)
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

    #df.to_excel('C:/DataDisk/theme.xlsx')     
    #df1 = df.groupby(['stock'])['theme'].apply(lambda x: ','.join(x)).reset_index() 


    #@pyqtSlot()
    #def on_click(self):
    #    self.game.setText(self.game_line_edit.text())

if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())


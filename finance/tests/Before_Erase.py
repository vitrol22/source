    '''
        stock_list = pd.DataFrame({'종목코드':stock.get_market_ticker_list(market="ALL")})
        stock_list['종목명'] = stock_list['종목코드'].map(lambda x: stock.get_market_ticker_name(x))

        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host='localhost', db='sstock', user='root', pw='JRLEE'))
        stock_list_copy = stock_list.copy()
        stock_list_copy = stock_list_copy.reset_index()

        try:
            #############################################################################

            # stock_list = pd.DataFrame({'종목코드':stock.get_market_ticker_list(market="ALL")})
            # df.columns
            # stock_list['종목명'] = stock_list['종목코드'].map(lambda x: stock.get_market_ticker_name(x))
            # stock.get_market_ohlcv_by_ticker("20210122")
            # stock.get_market_net_purchases_of_equities_by_ticker("20210122", "20210122", "ALL", "외국인합계")
            # stock.get_market_net_purchases_of_equities_by_ticker("20210122", "20210122", "ALL", "기관합계")
            # stock.get_market_net_purchases_of_equities_by_ticker("20210122", "20210122", "ALL", "개인")
            # stock.get_shorting_value_by_ticker("20210122", 'KOSPI')
            # stock.get_shorting_value_by_ticker("20210122", 'KOSDAQ')
            # pd.DataFrame(stock.get_market_fundamental_by_ticker(date="20210122", market="ALL"))
            # stock.get_exhaustion_rates_of_foreign_investment("20210122")
            # df_shorting_KOSPI = stock.get_shorting_value_by_ticker("20210122" "KOSPI")
            # df_shorting_KOSDAQ =stock.get_shorting_value_by_ticker("20210122", "KOSDAQ")

            #dDate=pdTradingDate.loc[ii, "MarketOpenDate"]
            stock_list_copy = stock_list.copy()
            stock_list_copy.insert(0,'거래날자', dDate)
            stock_list_copy.insert(0,'기록시간', datetime.datetime.now().strftime("%Y%m%d %H%M%S"))
            # 기본적인 분석'
            stock_fud = pd.DataFrame(stock.get_market_fundamental_by_ticker(date=dDate, market="ALL"))
            stock_fud = stock_fud.reset_index()
            stock_fud.rename(columns={'티커':'종목코드'}, inplace=True)

            stock_fud.rename(columns={'BPS':'BPSS'}, inplace=True)
            stock_fud.rename(columns={'PER':'PERR'}, inplace=True)
            stock_fud.rename(columns={'PBR':'PBRR'}, inplace=True)
            stock_fud.rename(columns={'EPS':'EPSS'}, inplace=True)
            
            stock_fud.rename(columns={'DIV':'DDIVV'}, inplace=True)
            stock_fud.rename(columns={'DPS':'DPSS'}, inplace=True)
            
            # 가격정보
            stock_price = stock.get_market_ohlcv_by_ticker(date=dDate, market="ALL")
            stock_price = stock_price.reset_index()
            stock_price.rename(columns={'티커':'종목코드'}, inplace=True)
            
            foreign_investment=stock.get_exhaustion_rates_of_foreign_investment(dDate)
            foreign_investment = foreign_investment.reset_index()
            foreign_investment.rename(columns={'티커':'종목코드'}, inplace=True)
            foreign_investment=foreign_investment.drop(["상장주식수", "보유수량", "한도수량", "한도소진률"], axis=1)

            df_total = stock.get_market_cap(dDate)
            df_total = df_total.reset_index()
            df_total.rename(columns={'티커':'종목코드'}, inplace=True)

            df_total=df_total.drop(["종가", "거래량", '거래대금'], axis=1)
            df_total = df_total[['시가총액', '상장주식수', '종목코드']]

            df_shorting_KOSPI = stock.get_shorting_value_by_ticker(dDate, "KOSPI")
            df_shorting_KOSPI = df_shorting_KOSPI.reset_index()
            df_shorting_KOSDAQ =stock.get_shorting_value_by_ticker(dDate, "KOSDAQ")
            df_shorting_KOSDAQ =df_shorting_KOSDAQ.reset_index()
            df_shorting = pd.concat([df_shorting_KOSPI,df_shorting_KOSDAQ], ignore_index=True)            
            df_shorting.rename(columns={'티커':'종목코드'}, inplace=True)
            df_shorting=df_shorting.drop(["매수"], axis=1)

            result = pd.merge(stock_list_copy, stock_price, left_on='종목코드', right_on='종목코드', how='outer')
            resultS = pd.merge(result, stock_fud, left_on='종목코드', right_on='종목코드', how='outer')
            resultS = pd.merge(resultS, foreign_investment, left_on='종목코드', right_on='종목코드', how='outer')
            resultS = pd.merge(resultS, df_total, left_on='종목코드', right_on='종목코드', how='outer') 
            resultS = pd.merge(resultS, df_shorting, left_on='종목코드', right_on='종목코드', how='outer')
            
            
            resultS  = resultS.dropna(subset=['종목명'])    #종목명이 없으면 삭제
            resultS  = resultS .fillna(0)   # NaN항목을 "0" 으로 변환
            #resultS = resultS.reset_index()
            #conn=engine.connect()                                  
            #resultS.to_sql('temp', engine, if_exists = 'replace', index=False)

    
            try:
                for idx in range(len(resultS)):
                    sql = "INSERT IGNORE INTO daily (기록시간, 거래날자, 종목코드, 종목명, 시가, 고가, 저가, 종가, 거래량, 거래대금, 등락률, BPSS, PERR, PBRR, EPSS, DDIVV, DPSS, 외국인지분율, 시가총액, 상장주식수, 공매도금액, 공매비중) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" 

                    cur.execute(sql, tuple(resultS.values[idx]))
                    connPy.commit()

                print(dDate, '1/2 기본정보 저장성공', '공매도 정보 진행')
            except:
                print(dDate, '기본정보 저장실패')
                pass

            try:
                ##########################################################
                # ETF
                ##########################################################

                etf_list = pd.DataFrame({'종목코드':stock.get_etf_ticker_list(dDate)})
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
                df = df.reset_index()
                df.rename(columns={'티커':'종목코드'}, inplace=True)
                df = df.drop(["시가", "종가", "변동폭", "거래량", "거래대금"], axis=1)

                result = pd.merge(etf_list_copy, dfETF, left_on='종목코드', right_on='종목코드', how='outer')
                resultS= pd.merge(result, df, left_on='종목코드', right_on='종목코드', how='outer')       
                # resultS  = result.dropna(subset=['종목명'])    #종목명이 없으면 삭제
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

                # for kk in range(len(etf_list_copy)):                
                #     df = stock.get_etf_portfolio_deposit_file(etf_list_copy.loc[kk, "종목코드"])
                #    print(df.head())
                sql="update tradingdate set basic_info= 'Collected' where MarketOpenDate='" + dDate + "'"
                cur.execute(sql)
                connPy.commit()
                print(dDate, '2/2 ETF 저장성공','하루의 결과를 완료', datetime.datetime.now().strftime("%H:%M:%S"))
                
            except:
                print('ETF 저장실패', dDate)
                pass

        except:
            print(dDate, '데이터 저장에 실패하였습니다.')
            print('지정한 일자의 정보를 완전하게 저장하였습니다.')
            #############################
    elif not shorting_info_mission =='Collected':
        try:      
            #공매도
            stock_list = pd.DataFrame({'종목코드':stock.get_market_ticker_list(market="ALL")})
            stock_list['종목명'] = stock_list['종목코드'].map(lambda x: stock.get_market_ticker_name(x))

            engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host='localhost', db='sstock', user='root', pw='JRLEE'))
            stock_list_copy = stock_list.copy()
            stock_list_copy = stock_list_copy.reset_index()

            for kk in range(len(stock_list_copy)):
                stockcode=stock_list_copy.loc[kk, "종목코드"]
                #time.sleep(0.1)
                dfshort = stock.get_shorting_balance_by_date(dDate, dDate, stockcode)
                if dfshort.empty==False:   
                    dfshort = dfshort.reset_index()
                    dfshort = dfshort[['공매도잔고', '비중']]        
                    # 투자주체별(기관, 개인, 외국인) 순매수량
                    df = stock.get_market_trading_value_by_investor(dDate, dDate, stockcode)

                    # 공매도량 + 기관순매수량 저장
                    sql="update daily set"
                    sql += " 공매도잔고=" + str(dfshort.loc[0, "공매도잔고"])
                    sql += ", 공매도비중=" + str(dfshort.loc[0, "비중"])
                    sql += ", 기관순매수=" + str(df.loc['기관합계', '순매수'])    #가져오기 tock.get_market_trading_value_by_investor(dDate, dDate, stockcode)
                    sql += ", 개인순매수=" + str(df.loc['개인', '순매수'])    #가져오기 tock.get_market_trading_value_by_investor(dDate, dDate, stockcode)
                    sql += ", 외국인순매수=" + str(df.loc['외국인', '순매수'])    #가져오기 tock.get_market_trading_value_by_investor(dDate, dDate, stockcode)
                    
                    sql += " where 종목코드='" + str(stockcode) + "'"
                    sql += " and 거래날자=" + str(dDate) + ""
                    
                    cur.execute(sql)
                    connPy.commit()
                else:
                    print(kk, dDate, stockcode, stock_list_copy.loc[kk, "종목명"], '에 공매도 정보가 없습니다. 상장 전이죠?')
                    pass
            print(dDate, '1/1 공매도 저장성공','ETF 진행 중')
            sql="update tradingdate set shorting_info= 'Collected' where MarketOpenDate='" + dDate + "'"
            cur.execute(sql)
            connPy.commit()

        except:
            print('공매도 저장실패', dDate, stockcode)
            pass
    '''
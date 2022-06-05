def save_excel(df):
    df.to_excel('E:/pycharmproject/untitled/stock/Africa.xlsx',sheet_name="sheet1",index=False)
 
def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    code = code.strip()
    print(code)
    #url = 'http://finance.naver.com/item/sise.nhn?code={code}'.format(code=code)
    url_day = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    print("요청 URL = {}".format(url_day))
    return url_day
    # 아프리카의 데이터 url 그리고 일자별 데이터 가져옴
 
 
def africa(code_df):
    item_name='아프리카TV'
    #url_day = get_url(item_name, code_df) # 데이터를 담을 df라는 DataFrame 정의
    df , df_url= pd.DataFrame(),pd.DataFrame()
    #print(df)
 
    # 웹 페이지에서 크롤링을 통해 20페이지까지의 데이터를 저장
    # for page in range(1, 21):
    #     pg_url = '{url}&page={page}'.format(url=url_day, page=page)
    #     df_url = df_url.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)
    #     #print(pg_url,df_url,end=" ")
 
    # 결측값이 있는 행을 제거, 이게 없으면 0번째 컬럼에 Nan 으로 데이터가 없는게 뜸
    #df_url = df_url.dropna()

    # 한글로 된 컬럼명을 영어로 바꿔줌
    #df_url = df_url.rename(columns={'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high',
    #                            '저가': 'low', '거래량': 'volume'})
    # 데이터의 타입을 int형으로 바꿔줌
    #print(df_url.columns)
    #df_url = df_url.fillna(0)
    #df_url[['close', 'diff', 'open', 'high', 'low', 'volume']] \
    #    = df_url[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)
    # 컬럼명 'date'의 타입을 date로 바꿔줌
    #df_url['date'] = pd.to_datetime(df['date'])
    # 일자(date)를 기준으로 오름차순 정렬
    #df_url = df_url.sort_values(by=['date'], ascending=True)
 
    df_url = pd.read_excel("E:/pycharmproject/untitled/stock/Africa.xlsx",sheet_name="sheet1")
 
    # 상위 5개 데이터 확인하기 
    print(df_url.head())
    save_excel(df_url)
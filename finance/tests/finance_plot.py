import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import re
import pymysql
import plotly.figure_factory as ff


connPy = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="sstock")
cur = connPy.cursor()
cur.execute("use sstock")


sql = "SELECT 시기, 년분기, 매출액, 영업이익, 당기순이익, 영업이익률, 순이익률, ROE, 부채비율, 당좌비율, 유보율, EPS, PER, BPS, pbr, 주당배당금, 시가배당률, 배당성향"
sql+= " FROM sstock.naver_finance where 종목명='삼성전자' order by 년분기, 시기;"
df = pd.read_sql_query(sql, connPy)
#df = df.drop(df.index[0])

#df=df.set_index('시기', drop=True)
dfT=df.T
dfT=dfT.reset_index(0, drop=False)

# df1 = df.reset_index(0, drop=True).T
# idx = pd.MultiIndex.from_tuples(
#     zip(range(len(df1)), df1.index.tolist())
# )
# df1 = df1.set_index(idx)


# fig =  ff.create_table(df)
# #dfT.set_index("0", append=True)
# fig.show()

fig = go.Figure(data=[go.Table(
    header=dict(values=list(dfT.columns),
                fill_color='paleturquoise',
                align='center'),
    cells=dict(
        values=[dfT[k].tolist() for k in dfT.columns[0:]],
        fill_color='lavender',
        align='right'))
])
# data=[go.Table(header=dict(values=['X_Score', 'Y_Score'], align='left', fill=dict(color='yellow'), 
# font=dict(color='red',size=16), height=50, line=dict(color='red', width=4), prefix='!', suffix='=') ,
#                  cells=dict(values=[[10, 9, 8, 9], [5, 5, 7, 9]]))]
fig.show()





df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/Mining-BTC-180.csv")
for i, row in enumerate(df["Date"]):
    p = re.compile(" 00:00:00")
    datetime = p.split(df["Date"][i])[0]
    df.iloc[i, 1] = datetime

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    specs=[[{"type": "table"}],
           #[{"type": "scatter"}],
           [{"type": "scatter"}]]
)

fig.add_trace(
    go.Table(
        header=dict(
            values=["Date", "Number<br>Transactions", "Output<br>Volume (BTC)",
                    "Market<br>Price", "Hash<br>Rate", "Cost per<br>trans-USD",
                    "Mining<br>Revenue-USD", "Trasaction<br>fees-BTC"],
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[df[k].tolist() for k in df.columns[1:]],
            align = "left")
    ),
    row=1, col=1
)

# fig.add_trace(
#     go.Scatter(
#         x=df["Date"],
#         y=df["Mining-revenue-USD"],
#         mode="lines",
#         name="mining revenue"
#     ),
#     row=3, col=1
# )

fig.add_trace(
    go.Scatter(
        x=df["Date"],
        y=df["Hash-rate"],
        mode="lines",
        name="hash-rate-TH/s"
    ),
    row=2, col=1
)


fig.update_layout(
    height=800,
    showlegend=False,
    title_text="Bitcoin mining stats for 180 days",
)

fig.show()
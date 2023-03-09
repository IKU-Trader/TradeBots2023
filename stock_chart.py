# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 22:03:46 2023

@author: dcela
"""

import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas_datareader as web
from datetime import datetime

app = dash.Dash()


import os
import datetime as dt
import pandas_datareader.data as web
 
#銘柄コード入力(7177はGMO-APです。)
ticker_symbol="7177"
ticker_symbol_dr=ticker_symbol + ".JP"
 
#2022-01-01以降の株価取得
start='2022-01-01'
end = dt.date.today()
 
#データ取得
df = web.DataReader(ticker_symbol_dr, data_source='stooq', start=start,end=end)

# ローソク足チャートのデータを作成する
candlestick = go.Candlestick(x=df.index,
                             open=df['Open'],
                             high=df['High'],
                             low=df['Low'],
                             close=df['Close'],
                             name=ticker_symbol)

# レイアウトを作成する
layout = go.Layout(title=ticker_symbol + ' 株価チャート',
                   xaxis=dict(title='日付'),
                   yaxis=dict(title='価格'))

# チャートを表示する
app.layout = html.Div(children=[
    html.H1(children='株価チャート'),
    dcc.Graph(id='stock-graph',
              figure={'data': [candlestick],
                      'layout': layout})
])

if __name__ == '__main__':
    app.run_server(debug=True)

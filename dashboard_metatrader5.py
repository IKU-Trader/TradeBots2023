# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 20:41:14 2023

@author: IKU-Trader
"""

import sys
sys.path.append('./libs')
sys.path.append('./libs/PyMT5')

import numpy as np
import pandas as pd
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.figure_factory import create_candlestick

from PyMT5 import PyMT5
from TimeUtils import TimeUtils
from const import const

INTERVAL_MSEC = 1000
TICKERS = ['DOWUSD', 'NASUSD', 'JPXJPY', 'XAUUSD', 'WTIUSD', 'USDJPY','EURJPY', 'GBPJPY', 'AUDJPY']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']

server = PyMT5(TimeUtils.TIMEZONE_TOKYO)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

symbol_dropdown = html.Div([
    html.P('Symbol:'),
    dcc.Dropdown(
        id='symbol-dropdown',
        options=[{'label': symbol, 'value': symbol} for symbol in TICKERS],
        value='DOWUSD'
    )
])

timeframe_dropdown = html.Div([
    html.P('Timeframe:'),
    dcc.Dropdown(
        id='timeframe-dropdown',
        options=[{'label': timeframe, 'value': timeframe} for timeframe in TIMEFRAMES],
        value='M1'
    )
])

num_bars_input = html.Div([
    html.P('Number of Candles'),
    dbc.Input(id='num-bar-input', type='number', value='100')
])

# creates the layout of the App
app.layout = html.Div([
    html.H1('Real Time Charts'),
    dbc.Row([
        dbc.Col(symbol_dropdown),
        dbc.Col(timeframe_dropdown),
        dbc.Col(num_bars_input)
    ]),
    html.Hr(),
    dcc.Interval(id='update', interval=INTERVAL_MSEC),
    html.Div(id='chart_output')

], style={'margin-left': '5%', 'margin-right': '5%', 'margin-top': '20px'})


@app.callback(
    Output('chart_output', 'children'),
    Input('update', 'n_intervals'),
    State('symbol-dropdown', 'value'), State('timeframe-dropdown', 'value'), State('num-bar-input', 'value')
)
def update_ohlc_chart(interval, symbol, timeframe, num_bars):
    num_bars = int(num_bars)
    #print(symbol, timeframe, num_bars)
    dic = server.download(symbol, timeframe, num_bars)
    return createChart(symbol, timeframe, dic)
  
def createChart(symbol, timeframe, dic):
    fig = create_candlestick(dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE])
    time = dic[const.TIME]
    #print(symbol, timeframe, dic)
    xtick0 = (5 - time[0].weekday()) % 5
    tfrom = time[0].strftime('%Y-%m-%d %H:%M')
    tto = time[-1].strftime('%Y-%m-%d %H:%M')
    if timeframe == 'D1' or timeframe == 'H1':
        form = '%m-%d'
    else:
        form = '%d/%H:%M'
    fig['layout'].update({
                            'title': symbol + '　' +  tfrom + '  ->  ' + tto,
                            'xaxis':{
                                        'title': '日付',
                                        'showgrid': True,
                                        'ticktext': [x.strftime(form) for x in time][xtick0::5],
                                        'tickvals': np.arange(xtick0, len(time), 5)
                                    },
                            'yaxis':{
                                        'title': '価格'
                                }
       })
    #print(fig)
    return dcc.Graph(id='stock-graph', figure=fig)
      
def createChart2(dic):
    fig = go.Figure(data=go.Candlestick(x=dic[const.TIME],
                    open=dic[const.OPEN],
                    high=dic[const.HIGH],
                    low=dic[const.LOW],
                    close=dic[const.CLOSE]))
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_layout(yaxis={'side': 'right'})
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

if __name__ == '__main__':
    app.run_server(debug=True, port=3333)


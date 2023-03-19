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
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.figure_factory import create_candlestick

from PyMT5 import PyMT5
from TimeUtils import TimeUtils
from const import const

INTERVAL_MSEC = 200
TICKERS = ['DOWUSD', 'NASUSD', 'JPXJPY', 'XAUUSD', 'WTIUSD', 'USDJPY','EURJPY', 'GBPJPY', 'AUDJPY']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']
BARSIZE = ['50', '100', '150', '200', '300', '400', '500']

account_info = None
server = PyMT5(TimeUtils.TIMEZONE_TOKYO)
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# ----
setting_bar = dbc.Row([
                        html.H5('Settings',
                        style={'margin-top': '2px', 'margin-left': '24px'})
                        ],
                        style={"height": "3vh"},
                        className='bg-primary text-white')

ticker_dropdown = dcc.Dropdown(id='symbol_dropdown',
                             multi=False,
                             value=TICKERS[0],
                             options=[{'label': x, 'value': x} for x in TICKERS],
                             style={'width': '140px'})

ticker = html.Div([ html.P('Ticker Symbol',
                           style={'margin-top': '8px', 'margin-bottom': '4px'}, 
                           className='font-weight-bold'),
                   ticker_dropdown])
 
timeframe_dropdown = dcc.Dropdown(id='timeframe_dropdown', 
                                  multi=False, 
                                  value=TIMEFRAMES[1], 
                                  options=[{'label': x, 'value': x} for x in TIMEFRAMES],
                                  style={'width': '120px'})                
timeframe =  html.Div([
                                html.P('Time Frame',
                                       style={'margin-top': '16px', 'margin-bottom': '4px'},
                                       className='font-weight-bold'),
                                timeframe_dropdown])

barsize_dropdown = dcc.Dropdown(id='barsize_dropdown', 
                                multi=False, 
                                value=BARSIZE[2],
                                options=[{'label': x, 'value': x} for x in BARSIZE],
                                style={'width': '120px'})

barsize = html.Div([    html.P('Display Bar Size',
                               style={'margin-top': '16px', 'margin-bottom': '4px'},
                               className='font-weight-bold'),
                        barsize_dropdown])


position_button = html.Div( html.Button(id='draw_button', n_clicks=0, children='Position Update',
                            style={'margin-top': '16px'},
                            className='btn btn-primary'))

sidebar =  html.Div([
                        setting_bar,
                        html.Div([ticker,
                                 timeframe,
                                 barsize,
                                 html.Hr(),
                                 position_button],
                        style={'height': '50vh', 'margin': '8px'})
                    ])
    
contents = html.Div([    
                        dbc.Row([
                                    html.H5('MetaTrader5', style={'margin-top': '2px', 'margin-left': '24px'})
                                ],
                                style={"height": "3vh"}, className='bg-primary text-white'),
                        dbc.Row([
                                    html.Div(id='chart_output'),
                                    html.P('Account',
                                           style={'margin-top': '12px', 'margin-bottom': '12px'}, 
                                           className='font-weight-bold'),
                                    html.Div([],
                                             id='account_info',
                                             style={'height': '5vh', 'width': '120vh', 'margin': '10px'}),
                                    html.Div(id='table_container')
                                ]),
                        dcc.Interval(
                                        id='timer',
                                        interval=INTERVAL_MSEC,
                                        n_intervals=0)
                    ])

app.layout = dbc.Container([
                            dbc.Row(
                                    [
                                        dbc.Col(sidebar, width=2, className='bg-light'),
                                        dbc.Col(contents, width=9)
                                    ],
                                    style={"height": "80vh"}),
                            ],
                            fluid=True)
@app.callback(
    [Output('chart_output', 'children'),
    Output('account_info', 'children')],
    Input('timer', 'n_intervals'),
    State('symbol_dropdown', 'value'), State('timeframe_dropdown', 'value'), State('barsize_dropdown', 'value')
)
def updateChart(interval, symbol, timeframe, num_bars):
    #print(interval)
    num_bars = int(num_bars)
    #print(symbol, timeframe, num_bars)
    dic = server.download(symbol, timeframe, num_bars)
    chart = createChart(symbol, timeframe, dic)
    if (interval % 10) == 0 or (account_info is None):
        account = accountTable()
    return (chart, account)
  
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
                                        'title': '',
                                        'showgrid': True,
                                        'ticktext': [x.strftime(form) for x in time][xtick0::5],
                                        'tickvals': np.arange(xtick0, len(time), 5)
                                    },
                            'yaxis':{
                                        'title': ''
                                    }
       })
    #print(fig)
    return dcc.Graph(id='stock-graph', figure=fig)


def accountTable():
    df = server.accountInfo()
    return createTable(df)
    


def createTable(df):
    table = dash_table.DataTable(
            # セルサイズの設定
            style_cell={
                'textAliign':'center',  # テキストを中央寄せ
                'maxWidth':'60px',      # 最大横幅
                'minWidth':'60px',      # 最小横幅
                'whiteSpace':'normal'   # 文字を折り返して表示
            },
            fixed_rows={'headers':True},        # 縦スクロール時にヘッダーを固定
            style_table={'minWidth':'90%'},    # テーブル全幅表示
            columns=[{'name':col, 'id':col} for col in df.columns],
            data=df.to_dict('records')
        )
    return table


if __name__ == '__main__':
    app.run_server(debug=True, port=3333)


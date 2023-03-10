# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 10:23:54 2023

@author: dcela
"""

import sys 
sys.path.append('../libs')
import numpy as np
from datetime import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
from plotly.tools import FigureFactory as ff
#import pandas_datareader as web
from YahooFinanceApi import YahooFinanceApi

from TimeUtils import TimeUtils
from const import const

TICKERS = ['AAPL', 'AMZN', 'META']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'H8', 'D1']
BARSIZE = ['25', '50', '100', '150', '200', '300', '400']

def createApp():
    app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
    timeframes = list(YahooFinanceApi.TIMEFRAMES.keys())
    sidebar = html.Div(
    [
        dbc.Row(
            [
                html.H5('Settings',
                        style={'margin-top': '12px', 'margin-left': '24px'})
            ],
            style={"height": "5vh"}, className='bg-primary text-white'
        ),
        dbc.Row(
            [
                html.Div([
                    html.P('Ticker Symbol',
                           style={'margin-top': '8px', 'margin-bottom': '4px'},
                           className='font-weight-bold'),
                            dcc.Dropdown(id='symbol', multi=False, value=TICKERS[0], options=[{'label': x, 'value': x} for x in TICKERS], style={'width': '220px'}
                    ),
                    html.P('Time Frame',
                           style={'margin-top': '16px', 'margin-bottom': '4px'},
                           className='font-weight-bold'),
                            dcc.Dropdown(id='timeframe', multi=False, value=timeframes[0], options=[{'label': x, 'value': x} for x in timeframes], style={'width': '120px'}
                    ),
                    html.P('Display Bar Size',
                           style={'margin-top': '16px', 'margin-bottom': '4px'},
                           className='font-weight-bold'),
                            dcc.Dropdown(id='barsize', multi=False, value=BARSIZE[1], options=[{'label': x, 'value': x} for x in BARSIZE], style={'width': '120px'}
                    ),
                    html.Button(id='apply', n_clicks=0, children='apply',
                                style={'margin-top': '16px'},
                                className='btn btn-primary'),
                    html.Hr()
                ])
            ],
            style={'height': '50vh', 'margin': '8px'}
            )
        ])

    content = html.Div(
    [    
        dbc.Row(
            [
                html.H5('Stock Chart', style={'margin-top': '12px', 'margin-left': '24px'})
            ],
            style={"height": "5vh"}, className='bg-primary text-white'
            ),
        dbc.Row(
            [
                html.Div(id='output_chart'),
            ],
            style={"height": "60vh"}, className='bg-white'
        ),
        dbc.Row(
            [
                html.P('Positions')
            ],
            style={"height": "20vh"}, className='bg-primary text-white'
            )
        ]
    )

    app.layout = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(sidebar, width=3, className='bg-light'),
                    dbc.Col(content, width=9)
                ],
                style={"height": "100vh"}
            ),
        ],
    fluid=True)
    return app

app = createApp()
@app.callback([Output(component_id='apply', component_property='n_clicks'),
               Output(component_id='output_chart', component_property='children')],
              [Input(component_id='apply', component_property='n_clicks'),
               Input(component_id='symbol', component_property='value'),
               Input(component_id='timeframe', component_property='value'),
               Input(component_id='output_chart', component_property='children')])
def update_value(apply, symbol, timeframe, graph):
    print('res... ', apply, symbol, timeframe)
    if apply == 0 or symbol.strip() == '':
        return (apply, graph)
    start = datetime(2022, 7, 1)  
    end = datetime.now() 
    #df0 = web.DataReader(symbol, data_source='stooq', start=start,end=end)
    #df = df0.sort_index()
    df = YahooFinanceApi.download(symbol, timeframe, TimeUtils.TIMEZONE_TOKYO)
    #print(df.iloc[:5, :])
    fig = ff.create_candlestick(df[const.OPEN], df[const.HIGH], df[const.LOW], df[const.CLOSE])
    #tbegin = df.index[0]
    #tend = df.index[-1]
    #print(tbegin, tend)
    xtick0 = (5 - df.index[0].weekday()) % 5
    
    tfrom = df.index[0].strftime('%y-%m-%d')
    tto = df.index[-1].strftime('%y-%m-%d')
    if timeframe == 'D1' or timeframe == 'H1':
        form = '%m-%d'
    else:
        form = '%H:%M'
    fig['layout'].update({
                            'title': symbol + '　' +  tfrom + ' - ' + tto,
                            'xaxis':{
                                        'title': '日付',
                                        'showgrid': True,
                                        'ticktext': [x.strftime(form) for x in df.index][xtick0::5],
                                        'tickvals': np.arange(xtick0, len(df), 5)
                                    },
                            'yaxis':{
                                        'title': '価格'
                                }
       })
    return (0, dcc.Graph(id='stock-graph', figure=fig))

'''
def update_value2(symbol): 
    if symbol.strip() == '':
        return None
    start = datetime(2022, 10, 1)  
    end = datetime.now() 
    df = web.DataReader(symbol, data_source='stooq', start=start,end=end)
    candlestick = go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=symbol)    
    layout = go.Layout(title=symbol + ' 株価チャート', xaxis={'title':'日付'}, yaxis={'title':'価格'})
    return dcc.Graph(id='stock-graph', figure={'data': [candlestick], 'layout': layout})
'''

if __name__ == "__main__":
    app.run_server(debug=True, port=1234)
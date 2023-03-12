# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 10:23:54 2023

@author: dcela
"""

import sys 
sys.path.append('../libs')
import numpy as np
import pandas as pd
from datetime import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

import plotly
import plotly.graph_objs as go
#from plotly.tools import FigureFactory as ff
from plotly.figure_factory import create_candlestick
#import pandas_datareader as web
from YahooFinanceApi import YahooFinanceApi

from TimeUtils import TimeUtils
from const import const

TICKERS = ['AAPL', 'AMZN', 'META']
TIMEFRAMES = list(YahooFinanceApi.TIMEFRAMES.keys())
BARSIZE = ['50', '100', '150', '200', '300', '400']


class Globals:
    def __init__(self, ticker: str, timeframe: str, barsize: str):
        self.ticker = ticker 
        self.timeframe = timeframe
        self.barsize = barsize
        self.df = pd.DataFrame()
        
g = Globals(TICKERS[0], TIMEFRAMES[0], BARSIZE[3])        

def createApp():
    app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
    sidebar = html.Div(
    [
        dbc.Row(
            [
                html.H5('Settings',
                        style={'margin-top': '2px', 'margin-left': '24px'})
            ],
            style={"height": "3vh"}, className='bg-primary text-white'
        ),
        dbc.Row(
            [
                html.Div([
                    html.P('Ticker Symbol',
                           style={'margin-top': '8px', 'margin-bottom': '4px'},
                           className='font-weight-bold'),
                            dcc.Dropdown(id='symbol', multi=False, value=g.ticker, options=[{'label': x, 'value': x} for x in TICKERS], style={'width': '220px'}
                    ),
                    html.P('Time Frame',
                           style={'margin-top': '16px', 'margin-bottom': '4px'},
                           className='font-weight-bold'),
                            dcc.Dropdown(id='timeframe', multi=False, value=g.timeframe, options=[{'label': x, 'value': x} for x in TIMEFRAMES], style={'width': '120px'}
                    ),
                    html.P('Display Bar Size',
                           style={'margin-top': '16px', 'margin-bottom': '4px'},
                           className='font-weight-bold'),
                            dcc.Dropdown(id='barsize', multi=False, value=g.barsize, options=[{'label': x, 'value': x} for x in BARSIZE], style={'width': '120px'}
                    ),
                    html.Div(
                        html.Button(id='draw_button', n_clicks=0, children='drarw',
                                    style={'margin-top': '16px'},
                                    className='btn btn-primary'),
                    ),
                    html.Div(
                        html.Button(id='set_button', n_clicks=0, children='table',
                                    style={'margin-top': '16px'},
                                    className='btn btn-primary')
                    ),
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
                html.H5('Yahoo Finance', style={'margin-top': '2px', 'margin-left': '24px'})
            ],
            style={"height": "3vh"}, className='bg-primary text-white'
            ),
        dbc.Row(
            [
                html.Div(id='output_chart'),
            ],
            style={"height": "40vh"}, className='bg-white'
        ),
        dbc.Row(
            [
                html.Div(id='table_container')
            ],
            #style={"height": "20vh"}, className='bg-primary text-white'
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

@app.callback(Output(component_id='symbol', component_property='value'),
               [Input(component_id='symbol', component_property='value'),
               Input(component_id='timeframe', component_property='value'),
               Input(component_id='barsize', component_property='value')])
def update_property(symbol, timeframe, barsize):
    #print('*1', symbol, timeframe, barsize)
    g.ticker = symbol
    g.timeframe = timeframe
    g.barsize = barsize
    return symbol
             
@app.callback([Output(component_id='draw_button', component_property='n_clicks'),
               Output(component_id='output_chart', component_property='children')],
              [Input(component_id='draw_button', component_property='n_clicks'),
               Input(component_id='output_chart', component_property='children')])
def update_graph(n_clicks, graph):
    #print('*2', n_clicks)
    if n_clicks == 0:
        return (n_clicks, graph)
    df = YahooFinanceApi.download(g.ticker, g.timeframe, TimeUtils.TIMEZONE_TOKYO)
    n = int(g.barsize)
    if len(df) > n:
        df = df.iloc[-n:, :]
    print('Data size: ', len(df))
    #fig = ff.create_candlestick(df[const.OPEN], df[const.HIGH], df[const.LOW], df[const.CLOSE])
    fig = create_candlestick(df[const.OPEN], df[const.HIGH], df[const.LOW], df[const.CLOSE])
    xtick0 = (5 - df.index[0].weekday()) % 5
    tfrom = df.index[0].strftime('%Y-%m-%d')
    tto = df.index[-1].strftime('%Y-%m-%d')
    if g.timeframe == 'D1' or g.timeframe == 'H1':
        form = '%m-%d'
    else:
        form = '%d/%H:%M'
    fig['layout'].update({
                            'title': g.ticker + '　' +  tfrom + ' - ' + tto,
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
@app.callback([Output(component_id='set_button', component_property='n_clicks'),
              Output(component_id='table_container', component_property='children')],
              [Input(component_id='set_button', component_property='n_clicks'),
              Input(component_id='table_container', component_property='children')])
def update_table(n_clicks, table):
    print(n_clicks, table)
    if n_clicks == 0:
        return (n_clicks, table)
    g.df = pd.read_csv('https://git.io/Juf1t')
    #print(g.df)
    output_table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in g.df.columns],
        data=g.df.to_dict('records'),
        page_size = 10
    )
    return (0, output_table)
'''
  
@app.callback([Output(component_id='set_button', component_property='n_clicks'),
              Output(component_id='table_container', component_property='children')],
              [Input(component_id='set_button', component_property='n_clicks'),
              Input(component_id='table_container', component_property='children')])
def update_table(n_clicks, fig):
    headerColor = 'grey'
    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'
    print(n_clicks, fig)
    if n_clicks == 0:
        return (n_clicks, fig)
    g.df = pd.read_csv('https://git.io/Juf1t')
    out_fig = go.Figure(
            data=[
                    go.Table(
                    header=dict(
                        values=g.df.columns,
                        line_color='darkslategray',
                        fill_color=headerColor,
                        align=['center'],
                        font=dict(color='white', size=11),
                        height=20
                    ),
                    cells=dict(
                        values=g.df.values.T,
                        line_color='darkslategray',
                        fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*5],
                        align=['center'],
                        font = dict(color = 'darkslategray', size = 10)
                    )
              )
            ]
          )           
    return (0, dcc.Graph(id='position_table', figure=out_fig))

if __name__ == "__main__":
    app.run_server(debug=True, port=1234)
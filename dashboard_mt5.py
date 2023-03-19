# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 10:23:54 2023

@author: dcela
"""

import sys 
sys.path.append('./libs')
sys.path.append('./libs/PyMT5')
import numpy as np
import pandas as pd
from datetime import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

import plotly
import plotly.graph_objs as go
from plotly.figure_factory import create_candlestick

import MetaTrader5 as mt5

from PyMT5 import PyMT5
from TimeUtils import TimeUtils
from const import const

TICKERS = ['DOWUSD', 'NASUSD', 'JPXJPY', 'XAUUSD', 'WTIUSD', 'USDJPY','EURJPY', 'GBPJPY', 'AUDJPY']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']
BARSIZE = ['50', '100', '150', '200', '300', '400']

INTERVAL_MSEC = 10000

class Globals:
    def __init__(self, ticker: str, timeframe: str, barsize: str):
        self.ticker = ticker 
        self.timeframe = timeframe
        self.barsize = barsize
        self.df = pd.DataFrame()
        #self.api = PyMT5(TimeUtils.TIMEZONE_TOKYO)
        
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
            ),
        dcc.Interval(
            id='timer_interval',
            interval=INTERVAL_MSEC, # in milliseconds
            n_intervals=0
        )]
        
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
    print('*1', symbol, timeframe, barsize)
    g.ticker = symbol
    g.timeframe = timeframe
    g.barsize = barsize
    return symbol
             
@app.callback(Output(component_id='output_chart', component_property='children'),
              Input(component_id='timer_interval', component_property='n_intervals'))
def update_graph(n_intervals):
    print('*timer', n_intervals, g.ticker, g.timeframe, g.barsize)
    if len(g.ticker) == 0:
        return None
    print('*??')
    #dic = g.api.download(g.symbol, g.timeframe, int(g.barsize))
    d = mt5.copy_rates_from_pos(g.symbol, g.timeframe , 0, int(g.barsize)) 
    print(d)
    dic = {}
    fig = create_candlestick(dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE])
    time = dic[const.TIME]
    print('Data ', len(time))
    xtick0 = (5 - time[0].weekday()) % 5
    tfrom = time[0].strftime('%Y-%m-%d %H:%M')
    tto = time[-1].strftime('%Y-%m-%d %H:%M')
    if g.timeframe == 'D1' or g.timeframe == 'H1':
        form = '%m-%d'
    else:
        form = '%d/%H:%M'
    fig['layout'].update({
                            'title': g.ticker + '　' +  tfrom + '  ->  ' + tto,
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
    mt5.initialize()
    app.run_server(debug=True, port=1234)
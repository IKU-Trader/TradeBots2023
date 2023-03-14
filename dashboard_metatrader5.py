# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 20:41:14 2023

@author: IKU-Trader
"""

import sys
sys.path.append('./libs')
sys.path.append('./libs/PyMT5')
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from PyMT5 import PyMT5
from TimeUtils import TimeUtils
from const import const

TICKERS = ['DOWUSD', 'NASUSD', 'JPXJPY', 'XAUUSD', 'WTIUSD', 'USDJPY','EURJPY', 'GBPJPY', 'AUDJPY']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']

server = PyMT5(TimeUtils.TIMEZONE_TOKYO)
# creates the Dash App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



symbol_dropdown = html.Div([
    html.P('Symbol:'),
    dcc.Dropdown(
        id='symbol-dropdown',
        options=[{'label': symbol, 'value': symbol} for symbol in TICKERS],
        value='EURUSD'
    )
])

timeframe_dropdown = html.Div([
    html.P('Timeframe:'),
    dcc.Dropdown(
        id='timeframe-dropdown',
        options=[{'label': timeframe, 'value': timeframe} for timeframe in TIMEFRAMES],
        value='D1'
    )
])

num_bars_input = html.Div([
    html.P('Number of Candles'),
    dbc.Input(id='num-bar-input', type='number', value='20')
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

    dcc.Interval(id='update', interval=200),

    html.Div(id='page-content')

], style={'margin-left': '5%', 'margin-right': '5%', 'margin-top': '20px'})


@app.callback(
    Output('page-content', 'children'),
    Input('update', 'n_intervals'),
    State('symbol-dropdown', 'value'), State('timeframe-dropdown', 'value'), State('num-bar-input', 'value')
)
def update_ohlc_chart(interval, symbol, timeframe, num_bars):
    num_bars = int(num_bars)
    print(symbol, timeframe, num_bars)
    dic = server.download(symbol, timeframe, num_bars)
    #bars = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    #df = pd.DataFrame(bars)
    #df['time'] = pd.to_datetime(df['time'], unit='s')

    fig = go.Figure(data=go.Candlestick(x=dic[const.TIME],
                    open=dic[const.OPEN],
                    high=dic[const.HIGH],
                    low=dic[const.LOW],
                    close=dic[const.CLOSE]))

    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_layout(yaxis={'side': 'right'})
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    return [
        html.H2(id='chart-details', children=f'{symbol} - {timeframe}'),
        dcc.Graph(figure=fig, config={'displayModeBar': False})
        ]


if __name__ == '__main__':
    # starts the server
    app.run_server(debug=True, port=3333)


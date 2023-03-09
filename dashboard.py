# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 19:23:12 2023

@author: IKU-Trader
"""

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from libs.const import const
from libs.TimeUtils import TimeUtils
from libs.PyMT5.PyMT5 import PyMT5
from libs.TA.STA import TechnicalAnalysis as ta
from libs.DataBuffer import DataBuffer


TICKERS = ['DOWUSD', 'S&PUSD', 'JPXJPY', 'XAUUSD', 'XAGUSD', 'WTIUSD', 'USDJPY', 'GBPJPY', 'AUDUSD']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'H8', 'D1']
BARSIZE = ['25', '50', '100', '150', '200', '300', '400']



def createChart():
    fig = go.Figure(data=[go.Scatter(
                                        x=[1, 2, 3, 4],
                                        y=[10, 11, 12, 13],
                                        mode='markers',
                                        marker_size=[40, 60, 80, 100])
                            ]
        )
    return fig    
    
def createApp():
    app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
    chart = createChart()

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
                            dcc.Dropdown(id='timeframe', multi=False, value=TIMEFRAMES[0], options=[{'label': x, 'value': x} for x in TIMEFRAMES], style={'width': '120px'}
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
        ),
        dbc.Row(
            [
                html.P('Order')
            ],
            style={"height": "60vh"}, className='bg-dark text-white'
        )]
    )

    content = html.Div(
    [    
        dbc.Row(
            [
                html.H5('Xxxxx',
                        style={'margin-top': '12px', 'margin-left': '24px'})
            ],
            style={"height": "5vh"}, className='bg-primary text-white'
            ),
        dbc.Row(
            [
                dcc.Graph(id='chart', figure=chart)
            ]
        ),
        dbc.Row(
            [
                html.P('Position')
            ],
            style={"height": "30vh"}, className='bg-light'
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

if __name__ == "__main__":
    app = createApp()
    app.run_server(debug=True, port=1234)
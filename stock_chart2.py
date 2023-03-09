# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 22:43:54 2023

@author: dcela
"""

import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas_datareader as web
from datetime import datetime
from dash.dependencies import Input, Output

def createApp():
    app = dash.Dash()
    app.title='Stock Visualiztion'
    app.layout = html.Div(children=[
        html.H1('Stock Visualiztion Dashboard'),
        html.H4('Please enter the stock name'),
        dcc.Input(id='input_symbol', value='', type='text'),
        html.Div(id= 'output_chart')
        ])
    return app
 
app = createApp()

@app.callback(Output(component_id='output_chart', component_property='children'),
              [Input(component_id='input_symbol', component_property='value')])
def update_value(symbol): 
    if symbol.strip() == '':
        return None
    start = datetime(2022, 10, 1)  
    end = datetime.now() 
    df = web.DataReader(symbol, data_source='stooq', start=start,end=end)
    candlestick = go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=symbol)    
    layout = go.Layout(title=symbol + ' 株価チャート', xaxis={'title':'日付'}, yaxis={'title':'価格'})
    return dcc.Graph(id='stock-graph', figure={'data': [candlestick], 'layout': layout})

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
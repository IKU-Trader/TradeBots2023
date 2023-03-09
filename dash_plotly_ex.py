# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 15:12:55 2023

@author: dcela
"""

import dash
from dash.dependencies import Output, Input
from dash import dcc
from dash import html
import plotly
import random
import plotly.graph_objs as go
from collections import deque

import numpy as np
import pandas as pd
import psutil

from datetime import datetime

#設定
#Tipping dataの読み込み
#https://vincentarelbundock.github.io/Rdatasets/doc/reshape2/tips.html
#来店カウント用に'count'カラムを追加
data = plotly.data.tips()
data = plotly.data.tips()
data['count'] = 1

#曜日別の来店カウントの基礎データ
#可視化対象のデータに依存して出現曜日が異なることを避けるために用意
bar_base_data =  pd.Series([0])
bar_base_data = bar_base_data.repeat(7)
bar_base_data.set_axis(
    ['Mon','Tue','Wed','Thur','Fri','Sat','Sun'],
    axis=0,
    inplace=True
)
bar_base_data.index.name = 'day'
bar_base_data.rename('count',inplace=True)

#Bar ChartやPie Chartで使用するcolor定義
color_dict = {
    'sex':{
        'Female':'LightCoral',
        'Male':'LightBlue'
    },
    'smoker':{
        'Yes':'Navy',
        'No':'Orange'
    }
    
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=external_stylesheets)

# Create server variable with Flask server object for use with gunicorn
server = app.server

app.layout = html.Div([
    #Title
    html.H1([
        'Tips Data Explorer'
    ]),
    #Radio Button
    dcc.RadioItems(
        id='time_selector',
        options=[
            {'label':'Lunch', 'value':'Lunch'},
            {'label':'Dinner', 'value':'Dinner'}
        ],
        value='Dinner',
        labelStyle={'display':'inline-block'} #Radio Buttonを横並びにする
    ),
    #Pie Chart
    #グラフを横並びにするため、グラフをDivで囲み、inline-blockにする
    html.Div(
        style={'width':'40%', 'display':'inline-block'},
        children=[
            dcc.Graph(
                id='sex_pie_chart',
                #figure=draw_visiter_count_pie_chart(data, 'sex', ['Female','Male'])
            )
        ]
    ),
    #Bar Chart
    html.Div(
        style={'width':'60%', 'display':'inline-block'},
        children=[
            dcc.Graph(
                id='smoker_bar_chart',
                #figure=draw_visiter_count_bar_chart(data, 'smoker', ['Yes','No'])
            )
        ]
    )
])



def draw_visiter_count_bar_chart(data, group_name, group_labels):
    """曜日別の来店合計を示すBar Chartを表示するFigureを作成。

    Args:
      data: 元データ(plotly.data.tipsを想定)
      group_name: グラフの系列対象のカラム名('sex'か'smoker'を想定)
      group_labels: 系列名のリスト

    Returns:
      Bar Chartを表示するFigureオブジェクト.
    """
    data = data.groupby(by=[group_name, 'day']).sum().loc[:,'count']
    
    #系列ごとにBar Chartを作る
    figures = []
    for label in group_labels:
        #グラフ形状をFixするための処理
        _data = (bar_base_data + data[label]).fillna(0)
        _data = _data.reindex(index=bar_base_data.index)
        
        figures.append(
            go.Bar(
                name=label, 
                x=_data.index, 
                y=_data,
                marker_color=color_dict[group_name][label])
        )
    fig = go.Figure(data=figures)
    #Stacked Bar Chartで表示する
    fig.update_layout(
        title={'text':'Week Day Visiter:' + group_name},
        barmode='stack'
    )
    return fig

def draw_visiter_count_pie_chart(data, group_name, group_labels):
    """来店合計を示すPie Chartを表示するFigureを作成。

    Args:
      data: 元データ(plotly.data.tipsを想定)
      group_name: グラフの系列対象のカラム名('sex'か'smoker'を想定)
      group_labels: 系列名のリスト

    Returns:
      Pie Chartを表示するFigureオブジェクト.
    """
    data = data.groupby(by=group_name).sum().loc[:,'count']
    fig = go.Figure(
        data=[
            go.Pie(
                labels=data.index,
                values=data,
                marker_colors=
                    [color_dict[group_name][i] for i in data.index]
            )
        ]
    )
    fig.update_traces(textinfo='value')
    fig.update_layout(title={'text':'Total Visiter：' + group_name})

    return fig


#Radio Buttonの値を変更した時のcallback
@app.callback(
    Output('sex_pie_chart', 'figure'),
    Output('smoker_bar_chart', 'figure'),
    Input('time_selector', 'value'))
def update_figures(input_value):
    #input_value = "Lunch" or "Dinner"
    _data = data.query('time=="{}"'.format(input_value))
    return \
        draw_visiter_count_pie_chart(_data, 'sex', ['Female','Male']),\
        draw_visiter_count_bar_chart(_data, 'smoker', ['Yes','No'])
#Server起動
app.run_server(port=1233)

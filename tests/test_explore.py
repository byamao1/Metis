#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/13 13:31
# @Author  : Baiyu
# @File    : test_explore.py
import datetime
import time
from io import BytesIO

import pandas as pd
import numpy as np
import pywebio
from adtk.data import validate_series
from adtk.detector import QuantileAD, InterQuartileRangeAD, ThresholdAD, GeneralizedESDTestAD, PersistAD, LevelShiftAD, \
    VolatilityShiftAD, SeasonalAD, AutoregressionAD
from adtk.visualization import plot
from pywebio.input import file_upload
from pywebio.output import popup, put_html, use_scope, put_row

import plotly.express as px

from app.service.explore.data_explore import _check_data, _detect_show


def show_lines():
    csv_object = file_upload("Select a csv:", accept=".csv")

    bio = BytesIO()
    bio.write(csv_object['content'])
    bio.seek(0)
    df = pd.read_csv(bio, parse_dates=['time'], infer_datetime_format=True,)

    # 获取整分钟的数据点
    df = df[df.apply(lambda x: x['time'].second == 0, axis=1)]


    # Filter by time
    # s_date = pd.to_datetime('2021/9/20 00:00:00', format='%Y/%m/%d %H:%M:%S')
    # e_date = pd.to_datetime('2021/9/21 00:00:00', format='%Y/%m/%d %H:%M:%S')
    # df = df[(s_date <= df['time']) & (df['time'] < e_date)]
    # df.to_csv("单日.csv", encoding='utf-8', index=False)

    fig = px.line(df, x='time', y=df.columns[:13], width=1500, height=800)
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    put_html(html)


def anomaly_detect():
    # data = {
    #     "time": [
    #         '2017-1-2 10:59:59.999999999',
    #         '2017-1-2 11:59:59.999999999',
    #         '2017-1-2 12:59:59.999999999',
    #         '2017-1-2 13:59:59.999999999',
    #         '2017-1-2 14:59:59.999999999',
    #         '2017-1-2 15:59:59.999999999',
    #         '2017-1-2 16:59:59.999999999',
    #     ],
    #     "data": [1, 2, 3, 9, -5, 2, 30]
    # }
    # df = pd.DataFrame(data)
    # time_index = pd.DatetimeIndex([
    #     '2017-1-2 10:59:59.999999999',
    #     '2017-1-2 11:59:59.999999999',
    #     '2017-1-2 12:59:59.999999999',
    #     '2017-1-2 13:59:59.999999999',
    #     '2017-1-2 14:59:59.999999999',
    #     '2017-1-2 15:59:59.999999999',
    #     '2017-1-2 16:59:59.999999999',
    # ])
    # s = pd.Series([1, 2, 3, 9, -5, 2, 30], index=time_index)

    # put_row([
    #     put_input('input'),
    #     put_select('select', options=['A', 'B', 'C'])
    # ])
    #
    csv_object = file_upload("Select a csv:", accept=".csv")

    bio = BytesIO()
    bio.write(csv_object['content'])
    bio.seek(0)
    df = pd.read_csv(bio, parse_dates=['time'], infer_datetime_format=True,)
    # 获取整分钟的数据点
    df = df[df.apply(lambda x: x['time'].second == 0, axis=1)]
    df = _check_data(df)

    # detect_show(df, ThresholdAD(high=30, low=15), 'ThresholdAD')
    _detect_show(df, QuantileAD(high=0.99, low=0.01), 'QuantileAD')
    _detect_show(df, InterQuartileRangeAD(c=1.5), 'InterQuartileRangeAD')
    _detect_show(df, GeneralizedESDTestAD(alpha=0.3), 'GeneralizedESDTestAD')
    _detect_show(df, PersistAD(c=3.0, side='positive'), 'PersistAD')
    _detect_show(df, LevelShiftAD(c=6.0, side='both', window=5), 'LevelShiftAD')
    _detect_show(df, VolatilityShiftAD(c=6.0, side='positive', window=30), 'VolatilityShiftAD')
    _detect_show(df, SeasonalAD(c=3.0, side="both"), 'SeasonalAD')
    _detect_show(df, AutoregressionAD(n_steps=7 * 2, step_size=24, c=3.0), 'AutoregressionAD')


if __name__ == '__main__':
    # 显示为2个功能。这里把访问端口改为 80
    pywebio.start_server([show_lines, anomaly_detect], port=80)

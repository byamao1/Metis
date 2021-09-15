#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/14 10:39
# @Author  : Baiyu
# @File    : data_explore.py
import traceback
from io import BytesIO

import pandas as pd
import numpy as np
from adtk.data import validate_series
from adtk.detector import QuantileAD, InterQuartileRangeAD, ThresholdAD, GeneralizedESDTestAD, PersistAD, LevelShiftAD, \
    VolatilityShiftAD, SeasonalAD, AutoregressionAD
from pywebio.input import file_upload
from pywebio.output import put_html

import plotly.express as px


def explore():
    csv_object = file_upload("Select a csv:", accept=".csv")

    bio = BytesIO()
    bio.write(csv_object['content'])
    bio.seek(0)
    df = pd.read_csv(bio)
    df = _check_data(df)

    # detect_show(df, ThresholdAD(high=30, low=15), 'ThresholdAD')
    _detect_show(df, QuantileAD(high=0.99, low=0.01), 'QuantileAD')
    _detect_show(df, InterQuartileRangeAD(c=1.5), 'InterQuartileRangeAD')
    _detect_show(df, GeneralizedESDTestAD(alpha=0.3), 'GeneralizedESDTestAD')
    _detect_show(df, PersistAD(c=3.0, side='positive'), 'PersistAD')
    _detect_show(df, LevelShiftAD(c=6.0, side='both', window=5), 'LevelShiftAD')
    _detect_show(df, VolatilityShiftAD(c=6.0, side='positive', window=30), 'VolatilityShiftAD')
    _detect_show(df, SeasonalAD(c=3.0, side="both"), 'SeasonalAD')
    _detect_show(df, AutoregressionAD(n_steps=7*2, step_size=24, c=3.0), 'AutoregressionAD')


def _check_data(df):
    if 'time' not in df.columns:
        # 没有时间列
        df['time'] = pd.date_range(start='1/1/1900', periods=len(df))
    return df


def _detect_show(df, detector, title):
    try:
        s = pd.Series(df['data'].values, index=pd.DatetimeIndex(df['time'].values))
        s = validate_series(s)
        if 'fit_detect' in dir(detector):
            anomalies = detector.fit_detect(s)
        else:
            anomalies = detector.detect(s)

        if anomalies.dtype == np.float:
            fig = px.scatter(df, x="time", y="data", color=anomalies, title=title,
                             color_continuous_scale=['rgba(0,0,255,0.2)', 'red'])
        else:
            fig = px.scatter(df, x="time", y="data", color=anomalies, title=title,
                             color_discrete_map={True: 'red', False: 'rgba(0,0,255,0.2)'})

        html = fig.to_html(include_plotlyjs="require", full_html=False)
        put_html(html)
    except Exception as e:
        traceback.print_exc()

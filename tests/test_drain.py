#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/27 14:20
# @Author  : Baiyu
# @File    : test_drain.py
from io import BytesIO

import pandas as pd
import numpy as np
import pywebio
import plotly.graph_objects as go
from pywebio.input import file_upload, input, NUMBER, FLOAT
from pywebio.output import popup, put_html, use_scope, put_row, put_table

from app.log_detector.Drain import Drain
from app.utils.list_util import conditions_in_dst

WHITE_LIST = [
    "/mes",
    "/openapi",
    "/h5",
    "/report",
    "/config",
    "/robots",
]

def detect_log():
    file_object = file_upload("Select a log file:", )

    bio = BytesIO()
    bio.write(file_object['content'])
    bio.seek(0)
    # Detect
    log_format = r'<IP> - - \[<Time>\] <Content>'

    # Regular expression list for optional preprocessing (default: [])
    regex = [
        r'blk_(|-)[0-9]+',  # block id
        r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)',  # IP
        r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$',  # Numbers
    ]
    st = 0.6  # Similarity threshold
    depth = 4  # Depth of all leaf nodes

    parser = Drain.LogParser(log_format, depth=depth, st=st, rex=regex)
    parser.parse(bio)
    df_event = parser.df_event
    df_log = parser.df_log

    # Filter anomaly logs
    quantile_num = input("模板最多出现次数的分位数", type=FLOAT, value='0.35')
    min_occur = int(df_event['Occurrences'].quantile(quantile_num))
    df_anomaly_event = df_event[(df_event['Occurrences'] <= min_occur) &
                                (~df_event.apply(lambda x: conditions_in_dst(WHITE_LIST, x['EventTemplate']), axis=1))]
    anomaly_event_ids = df_anomaly_event['EventId'].to_list()
    df_anomaly_log = df_log[df_log['EventId'].isin(anomaly_event_ids) &
                            (~df_log.apply(lambda x: conditions_in_dst(WHITE_LIST, x['Content']), axis=1))]

    # Show
    _show_df(df_anomaly_event, title=f"模板数 <= {min_occur} 且不在白名单内", width=1300, height=800)
    df_anomaly_event.to_csv("df_anomaly_event.csv", index=False,)
    df_anomaly_log.to_csv("df_anomaly_log.csv", index=False,)
    _show_df(df_anomaly_log, title="异常日志记录")


def _show_df(df, title, width=1500, height=1300):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    line_color='darkslategray',
                    fill_color='grey',
                    align='left',
                    font=dict(color='white', size=12)),
        cells=dict(values=[df[f'{col}'] for col in df.columns],
                   line_color='darkslategray',
                   # fill_color='lightgrey',
                   align='left',
                   font=dict(color='darkslategray', size=11)))
    ])
    fig.update_layout(title_text=title, width=width, height=height, )
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    put_html(html)


if __name__ == '__main__':
    # 显示为2个功能。这里把访问端口改为 80
    pywebio.start_server([detect_log], port=80)
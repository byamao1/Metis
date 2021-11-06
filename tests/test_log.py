#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/15 14:55
# @Author  : Baiyu
# @File    : test_log.py

import pandas as pd
import pywebio
import plotly.express as px
from pywebio.output import put_html
from sklearn.feature_extraction.text import HashingVectorizer


def show_log():
    df_src = pd.read_csv("日志.csv", keep_default_na=False)
    corpus = df_src['sql_template'].to_list()
    # corpus = [
    #     r'SELECT * FROM xxl_job_lock WHERE lock_name=$? FOR UPDATE',
    #     r'SELECT * FROM config_info_beta WHERE id=$?',
    #     r'SELECT FROM config_info WHERE data_id=$?',
    #     r'Is this the first document?',
    # ]
    vectorizer = HashingVectorizer(n_features=3)
    X = vectorizer.fit_transform(corpus)
    print(X.shape)
    df = pd.concat([pd.DataFrame(X.toarray()), df_src], axis=1)


    # fig = px.line(df, width=1500, height=800)
    fig = px.scatter_3d(df, x=0, y=1, z=2, color='user', hover_data=['sql_template'], width=1500, height=800)

    html = fig.to_html(include_plotlyjs="require", full_html=False)
    put_html(html)


if __name__ == '__main__':
    # 显示为2个功能。这里把访问端口改为 80
    pywebio.start_server([show_log], port=80)

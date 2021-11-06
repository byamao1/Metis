#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/9 10:53
# @Author  : Baiyu
# @File    : list_util.py


def conditions_in_dst(conditions, dst) -> bool:
    """
    检测条件列表中是否有元素在dst中出现
    :param conditions:
    :param dst: list或字符串类型
    :return:
    """
    for condition in conditions:
        if condition in dst:
            return True
    return False


def conditions_dst_start(conditions, dst: str) -> bool:
    """
    检测条件列表中是否有元素在dst字符串的前面出现
    :param conditions:
    :param dst: 字符串类型
    :return:
    """
    for condition in conditions:
        if dst.startswith(condition):
            return True
    return False

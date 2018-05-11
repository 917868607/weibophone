#!/usr/bin/env python
# encoding: utf-8

"""
@version: ??
@author: thsheep
@file: public.py
@time: 2018/4/29 23:59
@site:
"""
# 　　　┏┓　　　┏┓
# 　　┏┛┻━━━┛┻┓
# 　　┃　　　　　　　 ┃
# 　　┃　　　━　　　 ┃
# 　　┃　┳┛　┗┳　┃
# 　　┃　　　　　　　 ┃
# 　　┃　　　┻　　　 ┃
# 　　┃　　　　　　　 ┃
# 　　┗━┓　　　┏━┛Codes are far away from bugs with the animal protecting
# 　　　　┃　　　┃    神兽保佑,代码无bug
# 　　　　┃　　　┃
# 　　　　┃　　　┗━━━┓
# 　　　　┃　　　　　 ┣┓
# 　　　　┃　　　　 ┏┛
# 　　　　┗┓┓┏━┳┓┏┛
# 　　　　　┃┫┫　┃┫┫
# 　　　　　┗┻┛　┗┻┛

import re
import json
from json.decoder import JSONDecodeError


class ReSearchError(Exception):pass


def get_uid(url):
    """从URL中获取uid
    :param url:
    :return:
    """
    uid = re.search(r'uid=\d+', url)
    if uid:
        uid = uid.group()
        uid = uid[4:]
        return uid
    raise ReSearchError


def get_count(response, tag, category):
    """获取各种统计数
    :param response:
    :param tag:
    :param category:
    :return:
    """
    count = response.xpath(f"substring-after(substring-before"
                           f"(.//{tag}[contains(text(),'{category}[')]/text(), ']'), '[')").extract_first(0)
    if count:
        return count
    return 0


def load_json(string):
    '''将Json转换为字典
    :param string:字符串
    :return:字典
    '''
    try:
        res = json.loads(string)
    except JSONDecodeError:
        return {}
    return res
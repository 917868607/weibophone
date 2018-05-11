# -*- coding: utf-8 -*-
# @Time    : 2017/7/27 10:22
# @Author  : thsheep
# @Site    : 用作微博时间格式转换；例如 ：3小时之前 3天之前
# @File    : time_conversion.py
# @Software: PyCharm

import re
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
import threading
Lock = threading.Lock()


def re_findall(pattern, string, flags=0):
    """
    :param pattern: 正则表达式
    :param string: 需要匹配的字符串
    :param flags:
    :return: 与结果相匹配的字符串
    """
    string = re.findall(pattern, string, flags)
    return ''.join(string) or ''


clean_objects = []


def clean_class(_class):
    clean_objects.append(_class)
    return clean_objects


class Handler(metaclass=ABCMeta):
    '''时间转换基类'''

    def __init__(self,):
        self.successor = None

    def set_successor(self, successor):
        """设置继任者
        :param successor: 继任者
        :return:
        """
        self.d = datetime.now()
        self.successor = successor

    @abstractmethod
    def handler(self, data): return


@clean_class
class MinutesBefore(Handler):
    """分钟之前"""

    def handler(self, data):
        value = re_findall(r'\s*(\d+)\s?分钟\s*', data)
        if value:
            d1 = self.d + timedelta(minutes=-int(value))
            return d1.strftime('%Y-%m-%d %H:%M:%S')
        return self.successor.handler(data) if self.successor else data


@clean_class
class HoursBefore(Handler):
    """小时之前"""

    def handler(self, data):
        value = re_findall(r'\s*(\d+)\s?小时\s*', data)
        if value:
            d1 = self.d + timedelta(hours=-int(value))
            return d1.strftime('%Y-%m-%d %H:%M:%S')
        return self.successor.handler(data) if self.successor else data


@clean_class
class MonthsBefore(Handler):
    """月份前"""

    def handler(self, data):
        value = re_findall(r'\s*(\d{1,2}\s?月\d{1,2}\s?日\s+\d{2}:\d{2})\s*', data)
        if value:
            d1 = datetime.strptime(value, '%m月%d日 %H:%M')
            return str(self.d.year) + '-' + d1.strftime('%m-%d %H:%M:%S')
        return self.successor.handler(data) if self.successor else data


@clean_class
class YearsBefore(Handler):
    """年之前"""

    def handler(self, data):
        value = re_findall(r'\s*(\d{4}-\d{1,2}-\d{1,2}\s+\d{2}:\d{2}:\d{2})\s*', data)
        if value:
            return value
        return self.successor.handler(data) if self.successor else data


@clean_class
class TodayBefore(Handler):
    """今天"""

    def handler(self, data):
        value = re_findall(r'\s*今天\s?\s*(\d{2}:\d{2})\s*', data)
        if value:
            d2 = self.d.strftime('%Y-%m-%d')
            return d2 + ' ' + value + ':00'
        return self.successor.handler(data) if self.successor else data


@clean_class
class Yesterday(Handler):
    '''昨天'''

    def handler(self, data):
        value = re_findall(r'昨天\s*(\d{2}:\d{2})\s*', data)
        if value:
            d1 = datetime.now() + timedelta(days=-1)
            return d1.strftime('%Y-%m-%d') + ' ' + value + ':00'
        return self.successor.handler(data) if self.successor else data


@clean_class
class YesterdayBefore(Handler):
    '''前天'''

    def handler(self, data):
        value = re_findall(r'前天\s*(\d{2}:\d{2})\s*', data)
        if value:
            d1 = datetime.now() + timedelta(days=-2)
            return d1.strftime('%Y-%m-%d') + ' ' + value + ':00'
        return self.successor.handler(data) if self.successor else data


@clean_class
class SeveralDays(Handler):
    '''几天前'''

    def handler(self, data):
        value = re_findall(r'\s*(\d+)\s?天前', data)
        if value:
            d1 = datetime.now() + timedelta(days=-int(value))
            return d1.strftime('%Y-%m-%d') + ' 00:00:00'
        return self.successor.handler(data) if self.successor else data


class TimeConversion(object):
    """单例模式
        防止每次重复创建实例化、节约系统资源
    """
    # 定义静态变量实例
    __instance = None

    def __init__(self, *args, **kwargs):
        pass

    def __new__(cls, *args, **kwargs):
        """判断需要实例化对象是否存在 存在则直接返回 不存在则新建
        :param args:
        :param kwargs:
        :return: 清洗职责链的实例化对象
        """
        if not cls.__instance:
            try:
                Lock.acquire()
                if not cls.__instance:
                    cls.__instance = super(TimeConversion, cls).__new__(cls, *args, **kwargs)
                    # 拿到第一个清洗class
                    objects = [key() for key in clean_objects]
                    time_cleaner = objects[0]
                    tmp_cleaner = None
                    for obj in objects[1:]:
                        time_cleaner.set_successor(obj) if not tmp_cleaner else tmp_cleaner.set_successor(obj)
                        tmp_cleaner = obj
                    setattr(cls.__instance, 'time_cleaner', time_cleaner)
            finally:
                Lock.release()
        return cls.__instance

    def handler(self, data):
        return self.time_cleaner.handler(data)


def time_conversion_main(data):
    TC = TimeConversion()
    return TC.handler(data)


if __name__ == '__main__':

    print(time_conversion_main('13分钟前'))
#!/usr/bin/env python
# encoding: utf-8

"""
@version: ??
@author: thsheep
@file: extensions.py
@time: 2018/1/26 13:34
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
import redis
from scrapy import signals
from scrapy.exceptions import NotConfigured


class ExtensionThatAccessStats(object):

    def __init__(self, redis_url):
        self.redis_url = redis_url
        self.redis_conn = None

    @classmethod
    def from_crawler(cls, crawler):
        try:
            redis_url = crawler.settings.getdict('RABBIT_MQ_CONFIG')
        except Exception as e:
            raise NotConfigured
        o = cls(redis_url)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        spider.redis_conn = self.redis_conn
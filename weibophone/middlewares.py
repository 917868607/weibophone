# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import re
import base64
import random
import logging

import requests
from requests.exceptions import Timeout

from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

from weibophone.common.public import load_json

logger = logging.getLogger(__name__)


class RandomUserAgent(object):
    """随机选择一个请求头"""

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        '''设置headers和切换请求头
        :param request: 请求体
        :param spider: spider对象
        :return: None
        '''
        request.headers.setdefault('User-Agent', random.choice(self.agents))


class CookieMiddleware(RetryMiddleware):

    def __init__(self,
                 crawler,
                 get_cookie_url,
                 delete_cookie_url,
                 settings):

        self.delete_cookie_url = delete_cookie_url
        self.get_cookie_url = get_cookie_url
        self.crawler = crawler

        super(CookieMiddleware, self).__init__(settings)

    def process_request(self, request, spider):
        if re.search("weibo\.(com|cn)", request.url):
            try:
                response = requests.get(self.get_cookie_url)
                if response.status_code == 200:
                    cookie = load_json(response.text)
                    cookies = load_json(cookie.get('value'))
                    request.cookies = cookies
                    request.meta['key'] = cookie.get('key')
                elif response.text is None:
                    print("{}没有可用的Cookie, 请检查Cookie池".format(spider.name))
            except Timeout:
                print("请求超时请检查Cookie池API是否正常工作")

    # def process_response(self, request, response, spider):
    #     if "weibo" in request.url:
    #         if response.status in (300, 301, 302, 303, 404):
    #             key = request.meta.get('key')
    #             requests.get(self.delete_cookie_url.format(key))
    #             reason = response_status_message(response.status)
    #             logger.error("出现302正在重试, 删除Cookie：", key)
    #             return self._retry(request, reason, spider) or response  # 重试
    #     return response

    @classmethod
    def from_crawler(cls, crawler):  # 读取Setting配置
        settings = crawler.settings
        return cls(
            crawler,
            get_cookie_url=settings.get('GET_COOKIE_URL'),
            delete_cookie_url=settings.get("DELETE_COOKIE_URL"),
            settings=settings,
        )


class ProxyMiddleware(object):
    '''随机选择代理'''

    def __init__(self, proxy_server, proxy_user, proxy_pass):
        self.proxy_server = proxy_server
        self.proxy_auth = "Basic " + base64.urlsafe_b64encode(bytes((proxy_user +
                                                                     ":" + proxy_pass), "ascii")).decode("utf8")

    def process_request(self, request, spider):
        # 使用Splash渲染的页面不可以设置代理否则会出现503
        request.meta["proxy"] = self.proxy_server
        request.headers["Proxy-Authorization"] = self.proxy_auth

    @classmethod
    def from_crawler(cls, crawler):  # 读取Setting配置
        settings = crawler.settings
        return cls(
            proxy_server=settings.get('PROXY_SERVER'),
            proxy_user=settings.get("PROXY_USER"),
            proxy_pass=settings.get("PROXY_PASS")
        )


class WeibophoneSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WeibophoneDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

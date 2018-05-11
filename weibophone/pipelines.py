# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import six
import logging
import pymysql
from twisted.enterprise import adbapi
from scrapy.exceptions import CloseSpider
from weibophone.items import MBlogItem, CommitInfoItem, UserInfoItem

logger = logging.getLogger(__name__)


class CheckItemPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, MBlogItem):
            uid = item.get('uid')
            if not uid:
                raise CloseSpider("没有UID参数")
        return item


class WeibophonePipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def form_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            # cursorclass=pymysql.connect,
            charset='utf8mb4',
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        return cls(dbpool=dbpool)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.form_settings(crawler.settings)

    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

    def _do_upsert(self, conn, item, spider):
        if isinstance(item, MBlogItem):
            table_name = "mblog"
            sql = self._generate_sql(table_name, item)
            conn.execute(sql)
            logger.warning(f"{table_name} item已存储到数据")
            return item
        if isinstance(item, UserInfoItem):
            table_name = "user"
            sql = self._generate_sql(table_name, item)
            conn.execute(sql)
            logger.warning(f"{table_name} item已存储到数据")
            return item
        if isinstance(item, CommitInfoItem):
            table_name = "commit"
            sql = self._generate_sql(table_name, item)
            conn.execute(sql)
            logger.warning(f"{table_name} item已存储到数据")
            return item

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logger.error(item)
        logger.error(failure)

    def _generate_sql(self, table_name, item):
        col_str = ''
        row_str = ''
        for key in item.keys():
            col_str = col_str + " " + key + ","
            if not isinstance(item[key], str):
                row_str = "{}'{}',".format(row_str,
                                           item[key])
            else:
                item[key].replace("'", "\\'")
                row_str = "{}'{}',".format(row_str,
                                           item[key])
            sql = "insert INTO {} ({}) VALUES ({}) ON DUPLICATE KEY UPDATE ".format(table_name, col_str[1:-1],
                                                                                    row_str[:-1])
        for (key, value) in six.iteritems(item):
            sql += "{} = '{}', ".format(key, value if not isinstance(value, str) else value.replace("'", "\\'"))
        sql = sql[:-2]
        return sql

    # def execute(self, txn, sql):
    #     result = txn.execute(sql)
    #     return result
    #
    # def dbpool_execute(self, sql):
    #     return self.dbpool.runInteraction(self.execute, sql)
    #
    # def printresult(self, age):
    #
    #     pass

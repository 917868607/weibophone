# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class UserInfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    uid = Field()
    name = Field()
    gender = Field()
    location = Field()
    created_at = Field()
    friends_count = Field()
    followers_count = Field()
    statuses_count = Field()
    friends = Field()
    table = Field()


class MBlogItem(scrapy.Item):
    """
    博文内容
    """
    status_id = Field()   # 博文ID
    uid = Field()   # 用户ID
    created_at = Field()  # 发布时间
    mblogid = Field()   # 博文地址ID
    text = Field()  # 博文内容
    reposts_count = Field()     # 转发数
    comments_count = Field()    # 评论数
    attitudes_count = Field()   # 点赞数
    table = Field()


class CommitInfoItem(scrapy.Item):
    status_id = Field()
    text = Field()
    like_counts = Field()
    table = Field()


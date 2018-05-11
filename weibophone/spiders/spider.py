#!/usr/bin/env python
# encoding: utf-8

"""
@version: ??
@author: thsheep
@file: spider.py
@time: 2018/4/27 16:27
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
import json
import re
import time
import redis
import logging
from copy import deepcopy

from scrapy.spiders import Spider, CrawlSpider
from scrapy import Request
from scrapy.cmdline import execute
from scrapy.utils.project import get_project_settings

from scrapy_redis.spiders import RedisSpider

from weibophone.items import UserInfoItem, MBlogItem, CommitInfoItem

logger = logging.getLogger()

project = get_project_settings()

UserInfoDict = {
    "uid": 'id',
    "name": "name",
    "gender": "gender",
    "location": "location",
    "friends_count": "friends_count",
    "followers_count": "followers_count",
    "statuses_count": "statuses_count"
}

MBlogDict = {
    "status_id": 'id',
    "mblogid": 'mblogid',
    "text": "text",
    "reposts_count": "reposts_count",
    "comments_count": "comments_count",
    "attitudes_count": "attitudes_count"
}


MBlogURL = "https://api.weibo.cn/2/profile/statuses?" \
        "gsid=_&" \
        "i=ef6235c&c=iphone&networktype=wifi&v_p=60&lang=zh_CN&sflag=1&ua=iPhone8,1__weibo__8.4.2__iphone__os11.3&" \
        "sourcetype=page&count=20&page={page}&containerid=107603{uid}&s=2dd94aa5&from="


FriendsUrl = "https://api.weibo.cn/2/cardlist?" \
             "gsid=" \
             "from=&c=iphone&networktype=wifi&ua=iPhone8,1__weibo__8.4.2__iphone__os11.3&" \
             "aid=&feed_mypage_card_remould_enable=1&count=20" \
             "&lfid=107603{uid}&page={page}&containerid=231051_-_followers_-_1713926427&s=2dd94aa5"

CommitURL = "https://api.weibo.cn/2/comments/build_comments?" \
            "gsid=&" \
            "wm=3333_2001&i=ef6235c&from=&c=iphone&s=2dd94aa5&ua=iPhone8,1__weibo__8.4.2__iphone__os11.3&" \
            "aid=&count=20&_status_id={commit}&page=0&" \
            "lfid=1076031713926427&id={commit}&is_show_bulletin=2"


class WBSpider(RedisSpider):

    name = "weibo"

    def __init__(self, **kwargs):

        super().__init__(self.name, **kwargs)
        self.redis_conn = redis.from_url(project.get('REDIS_URL'), encoding='utf-8')

    def start_requests(self):
        yield Request(FriendsUrl.format(page='1', uid="1713926427"),
                      callback=self.parse, meta={'page': 1,
                                                 'uid': "1713926427"},
                      dont_filter=True)
        # yield Request(MBlogURL.format(page='1', uid="1713926427"),
        #               callback=self.m_blog,  meta={'page': 1,
        #                                            'uid': "1713926427"},
        #               dont_filter=True)

    def parse(self, response):
        """解析用户信息
        :param response:
        :return:
        """
        friends = [] if not response.meta.get('friends', False) else response.meta.get('friends')
        page = re.search(r'page=(\d+)', response.url).group()
        page = page.split('=')[-1]
        page = int(page)
        uid = re.search(r'107603\d+', response.url).group()
        uid = uid[6:]
        cards = json.loads(response.text)
        cards = cards.get('cards', False)
        if page == 1:
            # 关注第一页需要单独处理
            cards = cards[-1]
            card_groups = cards.get('card_group')
            for card_group in card_groups:
                user = card_group.get('user')
                friends.append(user.get('id'))
            else:
                page += 1
                yield Request(FriendsUrl.format(page=page, uid=uid),
                              callback=self.parse, meta={'page': page,
                                                         'uid': uid,
                                                         'friends': friends})
        elif cards:
            for card in cards:
                for card_group in card.get('card_group'):
                    user = card_group.get('user')
                    friends.append(user.get('id'))
            else:
                page += 1
                yield Request(FriendsUrl.format(page=page, uid=uid),
                              callback=self.parse, meta={'page': page,
                                                         'uid': uid,
                                                         'friends': friends},
                              priority=1)
        else:
            p = self.redis_conn.pipeline()
            for i in friends:
                p.lpush('weibo:start_urls', FriendsUrl.format(page='1', uid=i))
            else:
                p.execute()
            yield Request(MBlogURL.format(page='1', uid=uid),
                          callback=self.get_info,
                          meta={'friends': friends})

    def m_blog(self, response):
        """获取博文内容
        :param response:
        :return:
        """
        logger.warning("获取博文内容")
        mblog_item = MBlogItem()
        page = response.meta['page']
        uid = response.meta['uid']
        cards = json.loads(response.text).get('cards', False)
        if cards:
            for card in cards:
                mblog = card.get('mblog', False)
                if mblog:
                    _id = mblog.get('id')
                    created_at = mblog.get('created_at')
                    created_at = time.strptime(created_at, "%a %b %d %H:%M:%S +0800 %Y")
                    created_at = time.strftime("%Y-%m-%d %H:%M:%S", created_at)
                    for k, v in MBlogDict.items():
                        mblog_item[k] = mblog.get(v)
                    else:
                        mblog_item['table'] = "mblog"
                        mblog_item['created_at'] = created_at
                        mblog_item['status_id'] = _id
                        mblog_item['uid'] = uid
                        yield mblog_item
                        yield Request(CommitURL.format(commit=_id),
                                      callback=self.commit_info,
                                      meta={'id': _id},
                                      priority=-1)
            else:
                page += 1
                yield Request(MBlogURL.format(page=page, uid=uid),
                              callback=self.m_blog, meta={'page': page,
                                                          'uid': uid},
                              priority=1)

    def get_info(self, response):
        """获取用户信息
        :param response:
        :return:
        """
        logger.warning("获取用户详细信息")
        friends = response.meta.get('friends')
        user_info_item = UserInfoItem()
        user_info_item['table'] = 'user'
        cards = json.loads(response.text).get('cards', False)
        if cards:
            card = cards[2]
            mblog = card.get("mblog")
            user = mblog.get("user")
            created_at = user.get('created_at')
            created_at = time.strptime(created_at, "%a %b %d %H:%M:%S +0800 %Y")
            created_at = time.strftime("%Y-%m-%d %H:%M:%S", created_at)
            for k, v in UserInfoDict.items():
                user_info_item[k] = user.get(v)
            else:
                user_info_item['created_at'] = created_at
                user_info_item['friends'] = deepcopy(friends)
                yield user_info_item

        # uid = self.redis_conn.spop('weibo')
        # yield Request(FriendsUrl.format(page='1', uid=uid),
        #               callback=self.parse, meta={'page': 1,
        #                                          'uid': uid},
        #               priority=-1)
        # #     yield Request(MBlogURL.format(page='1', uid=uid),
        # #                   callback=self.m_blog, meta={'page': 1,
        # #                                               'uid': uid})

    def commit_info(self, response):
        """处理博文回复信息
        :param response:
        :return:
        """
        logger.warning("获取博文回复")
        commit_info_item = CommitInfoItem()
        _id = response.meta.get('id')
        root_comments = json.loads(response.text).get('root_comments', False)
        if root_comments:
            root_comments = root_comments[:10]
            for root_comment in root_comments:
                commit_info_item['text'] = root_comment.get('text')
                commit_info_item['like_counts'] = root_comment.get('like_counts')
                commit_info_item['status_id'] = _id
                commit_info_item['table'] = 'commit'
                yield commit_info_item


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'weibo'])
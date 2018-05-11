import json
import re
import time
import redis
import logging
from copy import deepcopy

from scrapy import Request
from scrapy.cmdline import execute
from scrapy.utils.project import get_project_settings

from scrapy_redis.spiders import RedisSpider

from urllib.parse import urljoin

from weibophone.items import UserInfoItem, MBlogItem, CommitInfoItem
from weibophone.common.public import get_uid, get_count
from weibophone.common.timeconversion import time_conversion_main

logger = logging.getLogger()

project = get_project_settings()

M_BLOG_TIME = 1514736000.0


class WeiBoCN(RedisSpider):

    name = 'weibocn'

    def __init__(self, **kwargs):

        super().__init__(self.name, **kwargs)
        self.redis_conn = redis.from_url(project.get('REDIS_URL'), encoding='utf-8')

    def start_requests(self):
        yield Request("https://weibo.cn/1713926427/follow",
                      callback=self.parse, dont_filter=True)

    def parse(self, response):
        """解析用户关注
        :param response:
        :return:
        """
        friends = [] if not response.meta.get('friends', False) else response.meta.get('friends')
        friends_urls = response.xpath(".//a[text()='关注他']/@href | .//a[text()='关注她']/@href").extract()
        next_url = response.xpath(".//a[text()='下页']/@href").extract_first(False)
        for friend_url in friends_urls:
            follow_uid = get_uid(friend_url)
            friends.append(follow_uid)
        if next_url:
            url = urljoin(response.url, next_url)
            yield Request(url, callback=self.parse, meta={'friends': friends}, priority=-2)

        else:
            #   此处注释用于向Redis添加起始URL
            p = self.redis_conn.pipeline()
            for follow_uid in friends:
                new_start_url = f"https://weibo.cn/{follow_uid}/follow"
                p.lpush('weibocn:start_urls', new_start_url)
            else:
                p.execute()
            index_url = response.url.replace("/follow", '')
            yield Request(index_url, callback=self.user_index, meta={'friends': friends})

    def user_index(self, response):
        """解析用户主页资料
        :param response:
        :return:
        """
        friends = [] if not response.meta.get('friends', False) else response.meta.get('friends')
        #   发布微博综述
        statuses_count = get_count(response, 'span', '微博')
        # statuses_count = response.xpath("substring-after(substring-before(.//span[contains(text(),"
        #                                 " '微博[')]/text(), ']'), '[')")
        #   关注了多少人
        friends_count = get_count(response, 'a', '关注')
        # friends_count = response.xpath("substring-after(substring-before(.//a[contains(text(), "
        #                                "'关注[')]/text(), ']'), '[')")
        #   被多少人关注（有多少粉丝）
        followers_count = get_count(response, 'a', '粉丝')
        # followers_count = response.xpath("substring-after(substring-before(.//a[contains(text(), "
        #                                  "'粉丝[')]/text(), ']'), '[')")
        info_url = re.sub('\?.*', '/info', response.url)
        yield Request(info_url,
                      callback=self.user_info,
                      meta={
                          "friends": friends,
                          "statuses_count": statuses_count,
                          "friends_count":  friends_count,
                          "followers_count":  followers_count
                      })

    def user_info(self, response):
        """解析用户详情页资料
        :param response:
        :return:
        """
        user_info_item = UserInfoItem()
        # user_info_item['table'] = 'user'
        info_text = ';'.join(response.xpath("./*//div[@class='c']//text()").extract())
        name = re.findall(r'昵称[：:]?(.*?);', info_text)
        gender = re.findall(r'性别[：:]?(.*?);', info_text)
        location = re.findall(r'地区[：:]?(.*?);', info_text)
        uid = re.findall(r'/(\d+)/', response.url)
        uid = ''.join(uid)
        user_info_item['uid'] = uid
        user_info_item['name'] = ''.join(name)
        user_info_item['gender'] = ''.join(gender)
        user_info_item['location'] = ''.join(location)
        user_info_item['friends'] = json.dumps(response.meta.get('friends'))
        user_info_item['statuses_count'] = response.meta.get('statuses_count')
        user_info_item['friends_count'] = response.meta.get('friends_count')
        user_info_item['followers_count'] = response.meta.get('followers_count')
        yield user_info_item
        m_blog_url = response.url.replace("/info", '')
        yield Request(m_blog_url,
                      callback=self.m_blog_index,
                      meta={'uid': uid})

    def m_blog_index(self, response):
        """解析博文信息
        :param response:
        :return:
        """
        #   获取用户主页的博文URL
        uid = response.meta.get('uid')
        m_blog_urls = response.xpath(".//a[contains(text(), '评论[')]/@href").extract()
        #   下一页地址
        at = response.xpath(".//a[contains(text(),'评论[')]/following-sibling::span/text()").extract_first(0)
        at = at.strip()
        at = time_conversion_main(at)
        at = time.mktime(time.strptime(at, '%Y-%m-%d %H:%M:%S'))
        next_url = response.xpath(".//a[text()='下页']/@href").extract_first(False)
        for m_blog_url in m_blog_urls:
            yield Request(m_blog_url,
                          callback=self.m_blog_info,
                          meta={'uid': uid},
                          priority=1)
        if next_url and at > M_BLOG_TIME:
            new_next_url = urljoin(response.url, next_url)
            yield Request(new_next_url,
                          callback=self.m_blog_index,
                          meta={'uid': uid},
                          priority=1)

    def m_blog_info(self, response):
        mblog_item = MBlogItem()
        uid = response.meta.get('uid')
        status_id = re.findall(r'https?://weibo.cn/comment/(.*?)\?', response.url)
        status_id = ''.join(status_id)
        if status_id:
            # mblog_item['table'] = "mblog"
            mblog_item['status_id'] = status_id
            mblog_item['uid'] = uid
            created_at = response.xpath("./*//div[@id='M_' and @class='c']/div/span[@class='ct']/text()"
                                      ).extract_first()
            created_at = created_at.strip()     # 时间两头有烂七八糟的空格 需要去除掉才能进行时间转换
            created_at = time_conversion_main(created_at)
            mblog_item['created_at'] = created_at
            mblog_item['text'] = ''.join(response.xpath("./*//div[@id='M_' and @class='c']/div/span[@class='ctt']/descendant::text()"
                                 ).extract())
            mblog_item['reposts_count'] = get_count(response, 'a', '转发')
            mblog_item['comments_count'] = get_count(response, 'span', '评论')
            mblog_item['attitudes_count'] = get_count(response, 'a', '赞')
            mblog_item['mblogid'] = response.url
            yield mblog_item
            #   获取博文回复
            yield Request(f"https://weibo.cn/comment/hot/{status_id}?rl=1",
                          callback=self.commit_info,
                          meta={'status_id': status_id},
                          priority=-2)

    def commit_info(self, response):
        """获取博文前几名回复 默认八页 需要更多的回复，添加翻页递归回调自身
        :param response:
        :return:
        """
        status_id = re.findall(r'https?://weibo.cn/comment/hot/(.*?)\?', response.url)
        if status_id:
            divs = response.xpath("./*//div[@id and @class='c' and not(@id='M_')]")
            if divs:
                for div in divs:
                    commit_info_item = CommitInfoItem()
                    commit_info_item['status_id'] = ''.join(status_id)
                    commit_info_item['text'] = ''.join(div.xpath("span[@class='ctt']/descendant::text()").extract())
                    like_counts = div.xpath("span/a[contains(text(),'赞[')]/text()").extract_first('')
                    if like_counts:
                        commit_info_item['like_counts'] = ''.join(re.findall(r'\[(\d+)\]', like_counts))
                    else:
                        commit_info_item['like_counts'] = 0
                    # commit_info_item['table'] = 'commit'
                    yield commit_info_item




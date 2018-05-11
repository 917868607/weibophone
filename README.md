# 一个分布式的weibo.cn爬虫

## 请务必注意此爬虫会顺着用户关注的人进行采集 源源不断追踪（向 weibocn:start_urls 中添加起始URL）

## 请务必检查redis中 weibocn:start_urls 中的起始URL数量。
## 达到合适的用户数量后注释掉 weibocn.py 中的以下内容重新启动爬虫（将不再添加起始URL）：

```Python
#   此处用于向Redis添加起始URL
p = self.redis_conn.pipeline()
for follow_uid in friends:
    new_start_url = f"https://weibo.cn/{follow_uid}/follow"
    p.lpush('weibocn:start_urls', new_start_url)
else:
    p.execute()

```

**需要更改settings.py中以下配置**

```Python
MYSQL_HOST = 'XXXXXXXXXX'
MYSQL_DBNAME = 'weibo'         #数据库名字
MYSQL_USER = 'XXXXX'             #数据库账号
MYSQL_PASSWD = 'XXXXXXXXXX'         #数据库密码
MYSQL_PORT = 3306               #数据库端口


SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER_PERSIST = True
REDIS_URL = 'redis://user:XXXXX@XXXXXXXXXX:6379'

# Cookie池地址
GET_COOKIE_URL = "http://XXXXXXXXXX:8080/weibo/random"
DELETE_COOKIE_URL = "http://XXXXX:8080/weibo/delete/{}"

# 代理配置
PROXY_SERVER = "http://http-dyn.abuyun.com:9020"
PROXY_USER = "XXXX"
PROXY_PASS = "XXXXX"
```

**Note1： 如果需要代理则取消掉以下中间件注释**

```Python

DOWNLOADER_MIDDLEWARES = {
   'weibophone.middlewares.RandomUserAgent': 90,
   'weibophone.middlewares.CookieMiddleware': 543,
   'weibophone.middlewares.ProxyMiddleware': 100,
   # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
}
```

**Note2: Pipeline中Twisted adbapi 入MySQL库没有做断线重连机制**

**Note3：Cookie借助于Cookie池项目**

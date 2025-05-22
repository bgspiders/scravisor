#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name :   crawl_requests
   Project   :   scravisor
   Author    :   bgspider
   date      :   2025/5/22
-------------------------------------------------
"""
from ..items import CrawlResponseItem
from scrapy_queue.spiders import RedisSpider
from utils.tools import *
from ..settings import REDIS_REQ_KEY


class CrawlHtml(RedisSpider):
    name = 'crawl_requests'
    custom_settings = {
        'REDIS_START_URLS_AS_ZSET': True,
    }

    def __init__(self, *args, **kwargs):
        super(CrawlHtml, self).__init__(*args, **kwargs)
        self.redis_key = REDIS_REQ_KEY
        self.push_list = []
    def parse(self, response):
        item=CrawlResponseItem()
        item['RESPONSE']=response
        yield item
#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name :   run_debug
   Project   :   scravisor
   Author    :   bgspider
   date      :   2025/5/22
-------------------------------------------------
"""
from scrapy.cmdline import execute
execute('scrapy crawl crawl_requests'.split())
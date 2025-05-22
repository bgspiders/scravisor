#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name :   redis_db
   Project   :   scravisor
   Author    :   bgspider
   date      :   2025/5/22
-------------------------------------------------
"""

import redis
from config import DATABASE_CONFIG
redis_server = redis.StrictRedis(
    host=DATABASE_CONFIG['redis']['host'],
    port=DATABASE_CONFIG['redis']['port'],
    password=DATABASE_CONFIG['redis']['password'],
    db=DATABASE_CONFIG['redis']['db'],
    decode_responses=True
)

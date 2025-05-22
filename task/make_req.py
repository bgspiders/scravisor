#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name :   make_req
   Project   :   scravisor
   Author    :   bgspider
   date      :   2025/5/22
-------------------------------------------------
"""
import re

from utils.tools import *
def create_req_start(config):
    info=config.get('start_req')
    if info:
        req_list=[]
        loop=info.get('max_loop')
        headers = info.get('headers') if info.get('headers') else random_ua()
        for page_number in range(loop):
            urls=[x for x in info.get('url').split('\n') if x.strip()]
            for _url in urls:
                req={}
                req['headers']=headers
                req['method'] = info.get('method','GET')
                if info.get('method')=='POST':
                    pass
                else:
                    if '$page_number' in _url:
                        _pageno=re.findall('\$(page_number[+,-]\d+)\$', _url)[0]
                        req['url']=_url.replace(f'${_pageno}$', str(eval(_pageno)))
                    req_list.append(req)
        return req_list
    else:
        raise ValueError('没有初始化请求')

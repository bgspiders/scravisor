#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：scravisor
@File    ：scravisor_download_handler.py
@IDE     ：PyCharm 
@INFO     ： 
@Author  ：BGSPIDER
@Date    ：21/05/2025 上午9:42
'''
import asyncio
from time import time
from urllib.parse import urldefrag

from curl_cffi import const
from curl_cffi import curl
from curl_cffi.requests import AsyncSession
from scrapy.http import Response
from scrapy.spiders import Spider
from twisted.internet.defer import Deferred
from twisted.internet.error import TimeoutError

from utils.tools import *


def as_deferred(f):
    return Deferred.fromFuture(asyncio.ensure_future(f))


class FingerprintDownloadHandler:

    def __init__(self, user, password, server, proxy_port):
        self.user = user
        self.password = password
        self.server = server
        self.proxy_port = proxy_port
        if self.user:
            proxy_meta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
                "host": self.server,
                "port": self.proxy_port,
                "user": self.user,
                "pass": self.password,
            }
            self.proxies = {
                "http": proxy_meta,
                "https": proxy_meta,
            }
        else:
            self.proxies={}

    async def _download_request(self, request):
        async with AsyncSession() as s:
            timeout = (3,30)
            impersonate = ''
            req_url=request.url
            render_flag=request.meta.get('render_flag')
            proxy_type = request.meta.get('proxy_type')
            headers=request.meta.get('headers')
            if request.meta.get('is_ssl'):
                impersonate = request.meta.get("impersonate") or 'chrome123'
            if request.meta.get('impersonate'):
                if request.meta.get('impersonate')=='1':
                    impersonate = 'chrome123'
                elif request.meta.get('impersonate')=='2':
                    #后期浏览器请求
                    pass
                else:
                    impersonate =None

            if proxy_type:
                if proxy_type=='dynamic':
                    proxy = None
                elif proxy_type=='private':
                    proxy = None
                elif proxy_type=='none':
                    proxy = {}
                else:
                    proxy={}
            else:
                proxy=self.proxies
            if 'User-Agent'  not in headers:
                headers['User-Agent'] = random_ua()
            if 'Content-Type' in request.headers:
                if 'json' in request.headers.get('Content-Type').decode():
                    request.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
            try:
                if '__type' in request.meta:
                    if request.meta['__type'] == 'json':
                        response = await s.request(
                            request.method,
                            req_url,
                            verify=False,
                            allow_redirects=True,
                            json=request.meta['data'],
                            cookies=request.cookies,
                            headers=headers,
                            proxies=proxy, impersonate=impersonate,
                            timeout=timeout
                        )
                    else:
                        response = await s.request(
                            request.method,
                            req_url,
                            verify=False,
                            allow_redirects=True,

                            data=request.meta['data'],
                            cookies=request.cookies,

                            headers=headers,
                            proxies=proxy, impersonate=impersonate,
                            timeout=timeout)
                else:
                    response = await s.request(
                        request.method,
                        req_url,
                        # data=request.body,
                        allow_redirects=True,

                        verify=False,
                        params=request.meta.get('data'),
                        cookies=request.cookies,
                        headers=headers,
                        proxies=proxy, impersonate=impersonate,
                        timeout=timeout)
            except curl.CurlError as e:
                if 'BoringSSL:' in str(e):
                    request.meta['impersonate'] = '1'
                    raise e
                if e.code == const.CurlECode.OPERATION_TIMEDOUT:
                    url = urldefrag(request.url)[0]
                    raise TimeoutError(
                        f"Getting {url} took longer than {timeout} seconds."
                    ) from e
                raise e
            if request.meta.get('impersonate')=='2':
                response = HtmlResponse(url=request.url, encoding='utf-8',
                                        body=response.json()['content'].encode('utf-8'),
                                        status=200)
                return response
            else:
                response.headers['cookies'] = json.dumps(dict(response.cookies), ensure_ascii=False)
                if request.meta.get('charset'):
                    encoding = request.meta['charset']
                else:
                    encoding = apparent_encoding(response)
                response = HtmlResponse(
                    response.url,
                    encoding=encoding,
                    status=response.status_code,
                    headers=response.headers,
                    body=response.content,
                )
                # response = self.cbeck_html_encoding(response)
                return response

    def download_request(self, request: scrapy.Request,
                         spider: Spider) -> Deferred:
        del spider
        start_time = time.time()
        d = as_deferred(self._download_request(request))
        d.addCallback(self._cb_latency, request, start_time)

        return d

    @staticmethod
    def _cb_latency(response: Response, request: scrapy.Request,
                    start_time: float) -> Response:
        request.meta["download_latency"] = time.time() - start_time
        return response

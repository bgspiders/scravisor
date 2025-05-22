#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name :   tools
   Project   :   scravisor
   Author    :   bgspider
   date      :   2025/5/22
-------------------------------------------------
"""
import traceback
from urllib.parse import urlunparse
import urllib3
# 禁用所有警告
urllib3.disable_warnings()
# 或者禁用特定类型的警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from crawl.settings import *
import re,regex
import copy, socket, hashlib
import logging
from lxml import etree
from urllib.parse import urlparse
import datetime, time, json
import scrapy
from scrapy.http import HtmlResponse
from urllib.parse import unquote
from bs4 import BeautifulSoup, Comment
import html
from utils.user_agent import *
import pickle
from curl_cffi import requests as requests_pro
import requests
from RestrictedPython import safe_builtins, Guards
import chardet, urllib


def get_now_time():
    return datetime.datetime.now().strftime("%Y-%m-%d")


class TimeCheckError(Exception):

    def __init__(self, *args):
        super(TimeCheckError, self).__init__(*args)


def parse_re_list(rule: str, response: list):
    """
    高效解析正则表达式匹配结果

    参数:
        rule (str): 正则表达式规则
        response (list): 需要匹配的字符串列表

    返回:
        list: 匹配到的结果列表
    """
    # 预编译正则表达式，避免重复编译
    try:
        _re = regex.compile(rule.strip())
        return [
            match.group()
            for s in response
            for match in _re.finditer(s, timeout=3)
        ]
    except Exception as e:
        if 'regex timed out' in str(e):
            raise TimeCheckError(f'正则表达式匹配超时，表达式为{rule}')
        else:
            traceback.format_exc()
            return []


def bs_brokenhearted(broken_html):
    """
    使用html5lib修复损坏的HTML

    参数:
        broken_html (str): 损坏的HTML字符串

    返回:
        str: 修复后的HTML字符串
    """
    soup = BeautifulSoup(broken_html, 'html5lib')
    return str(soup)


def html_to_str(htmls: str):
    """
    提取HTML中的纯文本内容

    参数:
        htmls (str): HTML字符串

    返回:
        str: 提取后的纯文本
    """
    _tree = etree.HTML(str(htmls))
    _str = ''.join(_tree.xpath('//text()'))
    return _str


def get_domain(url: str):
    """
    获取URL的域名

    参数:
        url (str): URL地址

    返回:
        str: 域名
    """
    result = urlparse(url)
    return result.netloc


def try_json(data):
    """
    尝试将数据转换为JSON对象

    参数:
        data (str): 需要转换的数据

    返回:
        dict: 转换后的字典，失败返回空字典
    """
    try:
        return json.loads(data)
    except Exception as e:
        return {}


def check_time(string, time_format="%Y-%m-%d %H:%M:%S"):
    """
    验证并格式化时间字符串

    参数:
        string (str): 时间字符串或时间戳
        time_format (str): 输出时间格式

    返回:
        str: 格式化后的时间字符串

    异常:
        TimeCheckError: 时间格式不正确或超出合理范围
    """
    if not string:
        return ''
    if string == '':
        raise TimeCheckError(f"时间格式化失败 {str(string)}")
    string = string.replace('\r', '').replace('\n', '').replace('\t', '')
    if string.strip() in ('ABC', 'abc'):
        string = str(datetime.datetime.now())
    if isinstance(string, (int, float)):
        string = str(int(string))
    if not isinstance(string, str):
        raise TimeCheckError(f"时间格式化失败 {str(string)}")
    
    if string.isdigit():
        if len(string) == 13:
            return time.strftime(time_format, time.localtime(int(string) / 1000))
        elif len(string) == 10:
            return time.strftime(time_format, time.localtime(int(string)))
        else:
            raise TimeCheckError(f"时间格式化失败,错误时间格式为：{str(string)}")
    
    string = string.strip()
    if len(string.split('-')[0]) == 2:
        string = '20' + string
    
    _str = re.findall('\d{4}-\d{2}-\d{2}', string)
    if _str:
        string = _str[0]
    _str = re.findall('\d{4}/\d{2}/\d{2}', string)
    if _str:
        string = _str[0]
    
    if '年' in string and '月' in string and '日' in string:
        string = string.split("日")[0]
        t_format = time_format
        if not ("年" in time_format or '月' in time_format or '日' in time_format):
            t_format = "%Y年%m月%d"
        try:
            d = datetime.datetime.strptime(string, t_format)
        except Exception as e:
            raise TimeCheckError(f"时间格式化失败，错误时间格式为： {string}")
    
    elif '年' in string and '月' in string:
        string = string.split(" ")[0]
        t_format = time_format
        if not ("年" in time_format or '月' in time_format):
            t_format = "%Y年%m月%d"
        try:
            d = datetime.datetime.strptime(string, t_format)
        except Exception as e:
            raise TimeCheckError(f"时间格式化失败，错误时间格式为： {string}")
    
    else:
        raise TimeCheckError(f"时间格式化失败，错误时间格式为： {string}")
    
    n_year_later = datetime.datetime.now().replace(year=datetime.datetime.now().year + 1)
    if d.tzinfo:
        d = d.replace(tzinfo=None)
    if d > n_year_later:
        raise TimeCheckError(f"格式化后时间大于一年后时间 {str(d)}")
    return d.strftime(time_format)


def get_response_type(response):
    """
    判断返回体是不是Json
    """
    try:
        _ = response.json()
        return 'json'
    except Exception as e:
        return 'text'


import xml.etree.ElementTree as ET


def json_to_xml(json_data):
    root = ET.Element("root")#根节点
    def _to_xml(parent, data,old_key=None):
        if isinstance(data, dict):  # 字典处理
            for key, value in data.items():
                element = ET.SubElement(parent, key)
                _to_xml(element, value,old_key=key)
        elif isinstance(data, list):
            # 列表处理
            for item in data:
                if old_key:
                    _to_xml(parent, item)
                else:
                    array_element = ET.SubElement(parent, 'array')
                    _to_xml(array_element, item)
        else:
            parent.text = str(data)
    _to_xml(root, json_data)
    return ET.ElementTree(root)




def calculate_md5(data, chunk_size=4096):
    """
    优化版单参数MD5计算，针对大文本或字节数据
    :param data: 需要计算的单个参数（字符串或字节）
    :param chunk_size: 分块大小（处理大字符串时使用，默认4KB）
    :return: MD5哈希值的十六进制字符串
    """
    h = hashlib.md5()
    if isinstance(data, bytes):
        # 直接处理字节数据
        h.update(data)
    else:
        # 处理字符串数据
        s = str(data)
        for i in range(0, len(s), chunk_size):
            h.update(s[i:i + chunk_size].encode('utf-8'))
    return h.hexdigest()


def apparent_encoding(response):
    """The apparent encoding, provided by the charset_normalizer or chardet libraries."""
    if chardet is not None:
        return chardet.detect(response.content)["encoding"]
    else:
        # If no character detection library is available, we'll fall back
        # to a standard Python utf-8 str.
        return response.encoding



def requests_bg(url: str = '', method='get', headers: dict = None, data: dict = None, try_number: int = 3,
                json: json = None, params: dict = None, proxy_type=None, cookies: dict = None, impersonate=None,
                render_finish_flag=None):
    """
    请求封装
    :param url:请求url
    :param data:请求的data
    :param try_number:请求重试次数
    :return:
    """
    if not headers:
        headers = random_ua()
    for i in range(try_number):
        try:
            if url:
                if proxy_type == 'dynamic':
                    proxy = None
                elif proxy_type == 'private':
                    proxy = None
                elif proxy_type == 'none':
                    proxy = {}
                else:
                    proxy = {}
                if impersonate == '1':
                    impersonate = 'chrome123'
                else:
                    impersonate = None
                print(proxy)
                if method == 'POST':
                    if data:
                        res = requests_pro.post(url=url, headers=headers, data=data, verify=False, proxies=proxy,
                                                impersonate=impersonate)
                        if res.status_code == 200:
                            return res
                    elif json:
                        res = requests_pro.post(url=url, headers=headers, json=json, verify=False, proxies=proxy,
                                                impersonate=impersonate)
                        if res.status_code == 200:
                            return res
                    else:
                        res = requests_pro.post(url=url, headers=headers, data={}, verify=False, proxies=proxy,
                                                impersonate=impersonate)
                        if res.status_code == 200:
                            return res
                else:
                    if params:
                        res = requests_pro.get(url=url, headers=headers, params=params, verify=False, proxies=proxy,
                                               impersonate=impersonate)
                        if res.status_code == 200:
                            return res
                    else:
                        res = requests_pro.get(url=url, headers=headers, verify=False, proxies=proxy,
                                               impersonate=impersonate)
                        if res.status_code == 200:
                            return res
            else:
                raise ValueError('url不存在')
        except Exception as e:
            if 'OPENSSL_internal' in str(e):
                if try_number > 2:
                    impersonate = '1'
                    continue
                raise ValueError('请配置渲染方式为动态渲染')


def build_response(req_data):
    """生成scrapy response对象，测试使用"""
    url = req_data.get('url')
    if not url:
        return {'mag': "没有请求url"}
    headers = req_data.get('headers')
    data = req_data.get('data')
    try_number = req_data.get('try_number', 3)
    json = req_data.get('json')
    params = req_data.get('params')
    is_proxy = req_data.get('is_proxy')
    res = requests_bg(url=url, headers=headers, data=data, try_number=try_number, json=json, params=params)
    content_url = req_data.get('url')
    if res.status_code == 200:
        request = scrapy.Request(url=content_url)
        response = HtmlResponse(url=request.url, body=res.content, request=request, status=200)
        return response


def loads(s):
    return pickle.loads(s)

def dumps(obj):
    return pickle.dumps(obj, protocol=-1)



import ast


def check_input(code):
    # 检查是否包含恶意代码
    malicious_patterns = ['os.', 'sys.', 'import', 'eval', 'exec']
    for pattern in malicious_patterns:
        if pattern in code:
            raise ValueError('恶意代码检测')
    # 检查语法是否正确
    try:
        ast.parse(code)
    except Exception as e:
        raise ValueError(f'语法错误')
    return code



def convert_entities(match):
    entity = match.group()
    if entity == '&lt;':
        return '<'
    elif entity == '&gt;':
        return '>'
    elif entity == '&amp;':
        return '&'
    elif entity == '&quot;':
        return '"'
    elif entity == '&apos;':
        return "'"
    else:
        return entity


def clean_attr(html_content, rule):
    root = etree.HTML(html_content)
    rule = rule.replace(' ', '').strip()
    # 遍历所有元素，删除 style 和 class 属性
    for element in root.iter():
        for _r in rule.split(','):
            if _r:
                element.attrib.pop(_r, None)
    # 将修改后的 XML 对象转换为字符串
    clean_html = etree.tostring(root, pretty_print=True, encoding='unicode')
    return clean_html


def remove_ele(content, xpath):
    try:
        tree = etree.HTML(content)
        for b in tree.xpath(xpath):
            b.getparent().remove(b)
        content = etree.tostring(tree, encoding="utf-8", pretty_print=True,
                                 method="html").decode('utf-8')
        return content
    except Exception as e:
        raise ValueError(str(e))


def clean_html_pro(htmls):
    soup = BeautifulSoup(htmls, 'html.parser')
    style_list = ['style', 'class', 'width', 'valign', 'height', 'script']
    for _s in style_list:
        for style in soup.find_all('style'):
            style.decompose()
    # 去除所有注释
    for comment in soup.findAll(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    # 去除所有空白字符和空白行
    for tag in soup.findAll():
        if tag.string:
            tag.string = tag.string.strip()
    # 去除HTML实体编码
    soup = BeautifulSoup(re.sub(r'&\w+?;', convert_entities, str(soup)), 'html.parser')
    # 保留 src 和 href 属性，去除其他属性
    for tag in soup.find_all():
        attrs_to_keep = ['src', 'href']
        tag.attrs = {k: v for k, v in tag.attrs.items() if k in attrs_to_keep}
    return (
        str(soup).replace('\r', '').replace('\\r', '').replace('\\n', '').replace('\\t', '').replace('\n', '').replace(
            '\t', '').
        replace(' ', '').replace(' ', '').replace(' ', ''))


def eval_code(code):
    if not code:
        return {}
    restricted_code = check_input(code)
    bgspider_____ = ''
    restricted_code = 'bgspider_____=' + restricted_code
    # print(restricted_code)
    restricted_globals = {
        '__builtins__': safe_builtins,
        'bgspider_____': bgspider_____,
    }
    executing_context = Guards.safe_globals.copy()
    executing_context.update(restricted_globals)
    a = {}
    exec(restricted_code, executing_context, a)
    return a['bgspider_____']

if __name__ == "__main__":
    pass
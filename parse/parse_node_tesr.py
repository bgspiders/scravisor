#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name :   parse_node
   Project   :   scravisor
   Author    :   bgspider
   date      :   2025/5/22
-------------------------------------------------
"""
from task.make_req import create_req_start
from parse.content_replace import *
from db.redis_db import redis_server
class ConfigParser:
    def __init__(self):
        """
        初始化解析器

        参数:
            config (dict): test_config.py 中定义的提取规则字典
            html_content (str): 待解析的 HTML 内容
        """
        pass

    def _apply_xpath(self, xpath_expr):
        """
        执行 XPath 提取

        参数:
            xpath_expr (str): XPath 表达式

        返回:
            list: 提取到的结果列表
        """
        return self.tree.xpath(xpath_expr) if xpath_expr else []

    def _apply_regex(self, text, regex_pattern):
        """
        执行正则表达式匹配

        参数:
            text (str): 需要匹配的文本
            regex_pattern (str): 正则表达式

        返回:
            str or None: 匹配结果
        """
        if not regex_pattern:
            return text
        match = re.search(regex_pattern, text)
        return match.group(0) if match else None

    def _apply_replaces(self, text, replaces):
        """
        对提取结果应用替换操作

        参数:
            text (str): 原始文本
            replaces (list): 替换规则列表

        返回:
            str: 替换后的文本
        """
        for replace in replaces:
            if replace['searchFlag'] == 0:
                text = text.replace(replace['searchValue'], replace['replaceValue'])
            else:
                text = re.sub(replace['searchValue'], replace['replaceValue'], text)
        return text

    def _clean_text(self, text, ab_strip):
        """
        清理文本（去空格等）

        参数:
            text (str): 原始文本
            ab_strip (int): 是否去除空白字符（1 表示是）

        返回:
            str: 清理后的文本
        """
        if ab_strip == 1 and isinstance(text, str):
            return text.strip()
        return text

    def parse_list_items(self):
        """
        解析列表项（如 url, title, publish_time 等字段）

        返回:
            list: 解析后的字段对象列表
        """
        list_rule = self.config.get('rule_tree', {}).get('list', {})
        xpath = list_rule.get('xpath')
        items = self._apply_xpath(xpath)

        results = []
        for item_tree in items:
            item_result = {}
            for field in list_rule.get('rule', []):
                name = field.get('name')
                xpath_expr = field.get('xpath')
                regex_expr = field.get('re')
                replaces = field.get('replaces', [])
                ab_strip = field.get('ab_strip', 0)

                # 提取原始值
                raw_value = ''.join(item_tree.xpath(xpath_expr)) if xpath_expr else ''

                # 应用正则表达式
                matched_value = self._apply_regex(raw_value, regex_expr)

                # 清理文本
                cleaned_value = self._clean_text(matched_value, ab_strip)

                # 替换内容
                replaced_value = self._apply_replaces(cleaned_value, replaces) if cleaned_value else None

                item_result[name] = replaced_value
            results.append(item_result)
        return results

    def parse_detail_fields(self):
        """
        解析详情页字段（如 content）

        返回:
            dict: 解析后的字段对象
        """
        detail_rules = self.config.get('rule_tree', {}).get('detail', [])
        result = {}

        for field in detail_rules:
            name = field.get('name')
            xpath_expr = field.get('xpath')
            regex_expr = field.get('re')
            replaces = field.get('replaces', [])
            ab_strip = field.get('ab_strip', 0)

            # 提取原始值
            raw_value = ''.join(self.tree.xpath(xpath_expr)) if xpath_expr else ''

            # 应用正则表达式
            matched_value = self._apply_regex(raw_value, regex_expr)

            # 清理文本
            cleaned_value = self._clean_text(matched_value, ab_strip)

            # 替换内容
            replaced_value = self._apply_replaces(cleaned_value, replaces) if cleaned_value else None

            result[name] = replaced_value
        return result
    def make_response(self,task_info):
        content=task_info['body']
        headers=task_info['headers']
        status=task_info['status']
        url=task_info['url']
        charset=task_info['encoding']
        response_plus=HtmlResponse(url=url,headers=headers,encoding=charset, body=content.encode('utf-8'),
                     status=status)
        return  response_plus
    def run(self,task_info):
        resp=self.make_response(task_info)
        print(resp)
        # self.config = config
        # self.html_content = html_content
        # self.tree = etree.HTML(html_content)
def get_all_keys():
    global all_keys
    cursor = 0
    pattern = 'response:*'
    count = 100  # 每次迭代返回的 key 数量
    while True:
        if len(all_keys)<50:
            cursor, keys = redis_server.scan(cursor=cursor, match=pattern, count=count)
            all_keys.extend(keys)
            if cursor == 0:
                time.sleep(10)
if __name__ == '__main__':
    ####并发消费#######
    import threading
    _json = {
    "start_req": {
        'url':'https://lssggzy.lishui.gov.cn/jsearchfront/interfaces/search.do?_cus_lq_bidsectionname=&_cus_pq_title=&begin=&end=&_cus_lq_dljg=&_cus_lq_jyjf=&_cus_eq_author=&sortType=2&websiteid=331101000003826&tpl=1621&p=$page_number+1$&pg=30&cateid=681&_cus_lq_regioncode=',
        'headers':{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"},
        'max_loop':50,
        'loop_auto':0,
    },
    "rule_tree": {
        "list": {
        "value": "/",
        "succeed":0,
        "type": "xpath",
        "rule": [
            {
                "name":"url",
                "xpath": "//url",
                "type": "xpath",
                're':'',
                'ab_strip':1,
                'plain':1,
                'remove_style':0,
                "replaces": [
                    {
                        "searchFlag": 0,
                        "replaceValue": "aaa",
                        "replaceFlag": 1,
                        "searchValue": "sss"
                    }
                ],
            },
            {
                "name": "title",
                "xpath": "//bidsectioncode",
                "type": "xpath",
                're': '',
                'ab_strip': 1,
                'plain': 1,
                'remove_style': 0,
                "replaces": [
                    {
                        "searchFlag": 0,
                        "replaceValue": "aaa",
                        "replaceFlag": 1,
                        "searchValue": "sss"
                    }
                ],
            },
            {
                "name": "publish_time",
                "xpath": "//createdate",
                "type": "xpath",
                're': '',
                'ab_strip': 1,
                'plain': 1,
                'remove_style': 0,
                "replaces": [
                    {
                        "searchFlag": 0,
                        "replaceValue": "aaa",
                        "replaceFlag": 1,
                        "searchValue": "sss"
                    }
                ],
            }
        ]
    },
        "detail": [
            {
                "name": "content",
                "xpath": "//div[@class='article-conter']",
                "type": "xpath",
                're': '',
                'ab_strip': 1,
                'plain': 1,
                'remove_style': 0,
                "replaces": [
                    {
                        "searchFlag": 0,
                        "replaceValue": "aaa",
                        "replaceFlag": 1,
                        "searchValue": "sss"
                    }
                ],
            },
        ]
    }

}
    reqq=create_req_start(_json)[0]
    print(reqq)
    resp=requests_bg(reqq['url'],headers=reqq['headers'])
    task_info={
        "body": resp.text,
        "headers": resp.headers,
        "status": resp.status_code,
        "url": reqq['url'],
        "config":_json,
        "encoding": apparent_encoding(resp),
    }
    crawl=ConfigParser()
    crawl.run(task_info)
    # def worker():
    #     crawler = ConfigParser()
    #     crawler.run()
    # THREAD_COUNT = 4
    # all_keys=[]
    # threads = []
    # t = threading.Thread(target=get_all_keys)
    # t.daemon = True
    # t.start()
    # threads.append(t)
    # for _ in range(THREAD_COUNT):
    #     t = threading.Thread(target=worker)
    #     t.daemon = True
    #     t.start()
    #     threads.append(t)
    #
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("Stopping all threads...")

# -*- coding: UTF-8 -*-
'''
@Project ：spider_v9 
@File    ：test_rule.py
@IDE     ：PyCharm 
@INFO     ： 
@Author  ：BGSPIDER
@Date    ：5/9/2024 下午3:56 
'''
from typing import List, Dict

from utils.tools import *


def safe_html_unescape(s):
    # 替换标准 HTML 实体（如 &amp;、&lt;、&gt; 等）
    s = re.sub(r"&([a-zA-Z0-9#]+);", lambda m: html.unescape(f"&{m.group(1)};"), s)
    return s
class DetailAction:
    """
    处理解析规则，对应v9的，正则，替换等规则
    """

    def __init__(self):

        json_object = None

    def execute(self, json_object, body: str, response, requests_info, base_dict, rules_keys):
        """
        context为规则对象，body为已经第一次处理完毕数据
        """
        if isinstance(body, int):
            data_value = str(body)
        elif '_Element' in str(type(body)) and '_ElementUnicodeResult' not in str(type(body)):
            data_value = etree.tostring(body, encoding='unicode', method='html').replace('\xa0', '&nbsp;')
        else:
            data_value = body
        data_value = unquote(data_value)  # 先解码 URL 编码
        data_value = safe_html_unescape(data_value)
        # self.rules_keys = rules_keys
        # response = response
        # base_dict = base_dict
        data_value=self.process_reg(data_value, json_object)
        # 正则提取
        data_value=self.process_substr(data_value, json_object)
        # 正输入租测试
        before_value = json_object.get("beforeValue")
        if before_value and data_value:
            # 内容前加字符串
            data_value = before_value + data_value
        after_value = json_object.get("afterValue")
        if after_value and data_value:
            # 内容后加字符串
            data_value += after_value
        # 过滤全部属性
        data_value=self.process_filter_tags(data_value, json_object)
        data_value=self.process_filter_atts(data_value, json_object)
        data_value=self.process_filter_all_att(data_value, json_object)
        if json_object.get("sbcFlag"):
            # 3全角转半角
            data_value = self.sbc2dbc(data_value)
        if json_object.get("plainFlag"):
        # 转为纯文本
            data_value = PlainExtractor().process(data_value)
        # if json_object.get("stripFlag"):
            # 去除前后空格
        data_value = data_value.strip()
        if json_object.get("unicodeFlag"):
            # unicode处理
            data_value = self.unescape_java(data_value)
        # 替换规则
        data_value=self.process_replace(data_value, json_object)
        requests_info=base_dict['rule_data']['first_rules']['requestInfoes']
        if json_object.get('delEles','').strip():
            # 删除元素
            data_value=remove_ele(data_value,json_object['delEles'].strip())
        if json_object.get('delAttrs','').strip():
            # 删除样式
            data_value=clean_attr(data_value,json_object['delAttrs'])
        if json_object.get('removeStyle'):
            # 补全url,使用requests_info,参数
            data_value=clean_html_pro(data_value)
        if json_object['fieldName'] == 'SOURCE_URL':
            # 补全url,使用requests_info,参数
            data_value = PlainExtractor().process(data_value)
            data_value=self.full_url(data_value,base_dict,response,requests_info)
        if json_object['fieldName'] == 'TITLE' or json_object['fieldName'] == 'PUBLISH_DATE':
            # 补全url,使用requests_info,参数
            if data_value=='':
                if json_object['fieldName'] == 'TITLE':
                    raise ValueError('标题最终结果是空')
                if json_object['fieldName'] == 'PUBLISH_DATE':
                    raise ValueError('发布时间最终结果是空')
            data_value = PlainExtractor().process(data_value)
        return data_value

    def full_url(self,data_value,base_dict,response, requestInfoes):
        data_value = data_value.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '').replace('amp;', '')
        start_url = data_value
        if base_dict['rule_data']['first_rules']['detailUrl']:
            if len(base_dict['rule_data']['first_rules']['detailUrl'].strip()) > 1:
                start_url = base_dict['rule_data']['first_rules']['detailUrl']
        req = {
            'source_url': data_value,
            'url': start_url
        }
        headers = {}
        if requestInfoes:
            req_data = {}
            for infos in requestInfoes:
                if infos['requestType'] == 'HEADER':
                    headers[infos['name']] = infos['value'].strip()
                    req['headers'] = headers
                if infos['requestType'] == 'DETAIL_PARAM':
                    data = infos['value']
                    if 'rest' in infos['name']:
                        if data:
                            req['type'], req['data'] = format_str_to_dict(data)
                        else:
                            req['type'], req['data'] = format_str_to_dict(data_value)
                    elif infos['requestValueType'] == 'DIRECT':
                        req_data[infos['name']] = infos['value']
                    elif infos['requestValueType'] == 'INPUT':
                        # _detailParamName=base_dict['rule_data']['first_rules'].get('detailParamName','')
                        req_data[infos['name']] = data_value
                        req['type'] = 'data'
                    else:
                        req['type'] = 'data'
                        req_data[infos['name']] = data
                if base_dict['rule_data']['first_rules']['detailPost'] == 1:
                    req['method'] = 'POST'
                    if not req_data:
                        req['type'], req['data'] = format_str_to_dict(data_value)
                else:
                    req['method'] = 'GET'
                    if '\\' in data_value:
                        data_value = data_value.replace('\\', '')
                    req['url'] = response.urljoin(data_value)
                    req['source_url'] = req['url']
            if req_data:
                req['data'] = req_data
        else:
            if base_dict['rule_data']['first_rules']['detailPost'] == 1:
                req['method'] = 'POST'
                req['type'], req['data'] = format_str_to_dict(data_value)
            else:
                req['method'] = 'GET'
                req['url'] = response.urljoin(data_value)
                req['source_url'] = req['url']
                if '\\' in data_value:
                    data_value = data_value.replace('\\', '')
            req['headers'] = headers
        if 'http' not in req['url']:
            if '\\' in data_value:
                data_value = data_value.replace('\\', '')
            req['url'] = response.urljoin(data_value)
        if 'method' not in req:
            req['method'] = 'GET'
            req['source_url']=req['url']
        data_value = req
        data_value['md5']=calculate_md5(data_value['source_url'])
        return data_value


    # def urljoin(self,baseurl,url):
    #     """
    #     只拼接主url
    #     """
    #     base='https://www.baidu.com/aaaa/'
    #     url='/111/111'
    #     new_url='https://www.baidu.com/111/111'

    def process_substr(self,data_value,json_object):
        if 'response' in str(type(data_value)):
            # 为scrapy对象
            return
        _find = ''
        start_index = 0
        start_str = json_object.get("startStr")
        containStart = json_object.get("containStart", '')
        if start_str:
            start_index = data_value.find(start_str)
            if start_index != -1:
                if containStart == 1:
                    start_index = start_index
                else:
                    start_index += len(start_str)
            else:
                start_index = 0
        end_str = json_object.get("endStr")
        end_index = -1
        containEnd = json_object.get("containEnd")
        if end_str:
            if start_index == -1:
                end_index = data_value.find(end_str)
            else:
                end_index = data_value.find(end_str, start_index)
            if containEnd == 1:
                end_index += len(end_str)
        if end_index == -1:
            data_value = data_value[start_index:]
        else:
            data_value = data_value[start_index:end_index]
        return data_value

    def process_reg(self,data_value,json_object):
        reg_value = json_object.get("regValue2")
        reg_value2_result = json_object.get("regValue2Result")
        if reg_value:
            matcher = re.compile(reg_value, re.IGNORECASE | re.DOTALL)
            match = matcher.search(data_value)
            if not match:
                data_value = ""
            elif reg_value2_result:
                data_value = reg_value2_result
                for i in range(match.re.groups + 1):
                    data_value = data_value.replace("${_" + str(i) + "}", match.group(i))
            else:
                data_value = match.group(0)
        return data_value

    def process_filter_tags(self,data_value,json_object):
        filter_tags = json_object.get("filterTags")
        if filter_tags:
            tags = filter_tags.split(',')
            for tag in tags:
                if tag.lower() == 'b':
                    data_value = re.sub(r"<[/]?b>", "", data_value, flags=re.IGNORECASE)
                else:
                    data_value = re.sub(r"<[/]?" + re.escape(tag) + r".*?[/]?>", "", data_value, flags=re.IGNORECASE)
        return data_value
    def process_filter_atts(self,data_value,json_object):
        filter_atts = json_object.get("filterAtts")
        if filter_atts:
            atts = filter_atts.split(',')
            for att in atts:
                data_value = re.sub(r"\s*" + re.escape(att) + r"\s*=\s*[\"'].+?[\"']", "", data_value,
                                   flags=re.IGNORECASE)
        return data_value

    def process_filter_all_att(self,data_value,json_object):
        if json_object.get("filterFlag"):
            buffer = []
            matcher = re.compile(r"<[a-z]+\s+(.*?)\s*/?>", flags=re.IGNORECASE | re.DOTALL)
            last_end = 0
            for match in matcher.finditer(data_value):
                buffer.append(data_value[last_end:match.start()])
                buffer.append(match.group().replace(match.group(1), ""))
                last_end = match.end()
            buffer.append(data_value[last_end:])
            data_value = "".join(buffer)
        return data_value

    def process_replace(self,data_value,json_object):
        replaces = json_object.get("replaces", [])
        for i in range(len(replaces)):
            replace_json_object = replaces[i]
            search_value = replace_json_object.get("searchValue")
            if search_value=='\\r':
                search_value='\r'
            elif search_value=='\\n':
                search_value='\n'
            elif search_value=='\\t':
                search_value='\t'
            replace_value = replace_json_object.get("replaceValue")
            if '$' in replace_value:
                search_list = re.findall(search_value, data_value, re.S)
                if search_list:
                    if isinstance(search_list[0], tuple):
                        search_list = search_list[0]
                    _replace = re.findall('(\$\d+)', replace_value)
                    for _ in _replace:
                        replace_value = replace_value.replace(_, search_list[int(_.replace('$', '')) - 1])
            if replace_value == "[EMPTY]":
                replace_value = ""
            search_flag = replace_json_object.get("searchFlag")
            replace_flag = replace_json_object.get("replaceFlag")
            if search_flag:
                if replace_flag:
                    data_value = re.sub(search_value, replace_value, data_value, flags=re.IGNORECASE | re.DOTALL)
                else:
                    data_value = re.sub(search_value, replace_value, data_value, count=1, flags=re.IGNORECASE | re.DOTALL)
            elif replace_flag:
                data_value = data_value.replace(search_value, replace_value)
            else:
                data_value = data_value.replace(search_value, replace_value, 1)
        return data_value

    @staticmethod
    def sbc2dbc(text):
        return text.translate(str.maketrans({
            '！': '!', '＠': '@', '＃': '#', '＄': '$', '％': '%', '＆': '&', '＊': '*', '（': '(',
            '）': ')', '－': '-', '＝': '=', '＋': '+', '＜': '<', '＞': '>', '｛': '{', '｝': '}',
            '［': '[', '］': ']', '｜': '|', '＼': '\\', '＾': '^', '～': '~', '∶': ':', '；': ';',
            '＂': '"', '｀': '`', '＜': '<', '＞': '>', '＿': '_', '～': '~', '？': '?', '！': '!',
            '＠': '@', '＃': '#', '＄': '$', '％': '%', '＆': '&', '＊': '*', '（': '(',
            '）': ')', '－': '-', '＝': '=', '＋': '+', '＜': '<', '＞': '>', '｛': '{', '｝': '}',
            '［': '[', '］': ']', '｜': '|', '＼': '\\', '＾': '^', '～': '~', '∶': ':', '；': ';',
            '＂': '"', '｀': '`'
        }))

    @staticmethod
    def unescape_java(text):
        if re.search(r'\\u[0-9a-fA-F]{4}', text):
            text = text.encode('utf-8').decode('unicode_escape')
        return text

class NodeVariable:
    def __init__(self, value):
        self.value = value


class PlainExtractor:
    def process(self, text):
        html = ''.join(etree.HTML(text).xpath('.//text()'))
        return html.strip()


class IJsonObject:
    def __init__(self, data: Dict):
        self.data = data

    def get(self, key):
        return self.data.get(key, "")

    def get(self, key):
        return bool(self.data.get(key, False))

    def get(self, key):
        return self.data.get(key, [])


class IJsonArray:
    def __init__(self, data: List):
        self.data = data

    def size(self):
        return len(self.data)

    def get_json_object(self, index):
        return IJsonObject(self.data[index])


if __name__ == "__main__":
    demo = DetailAction()
    rule = {'containEnd': 0, 'endStr': '', 'fieldName': 'SOURCE_URL', 'beforeValue': 'http://www.fsigc.com:6116',
            'containStart': 0, 'unicodeFlag': 0, 'afterValue': '',
            'xpath': '//*[@id="form1"]/div[6]/div/div[2]/div[1]/div/div[1]/div[1]/a/@href', 'startStr': '',
            'visitFlag': 0, 'regValue2Result': '', 'id': 2135236, 'filterTags': '', 'plainFlag': 0,
            'spiderValueType': 'XPATH', 'attFlag': 0, 'pageReg': None, 'stripFlag': 0, 'filterFlag': 0, 'replaces': [],
            'startToBorder': 0, 'regValue2': '', 'endToBorder': 0, 'filterAtts': '', 'attPatterns': [], 'regValue': '',
            'spiderPosType': 'LIST', 'sbcFlag': 0, 'constantValue': ''}
    text = ''
    print(demo.execute(rule, text))

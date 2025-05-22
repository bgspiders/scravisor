config = {
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

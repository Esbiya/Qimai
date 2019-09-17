# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import requests
import json
import logging
import execjs
import time
import random
from urllib.parse import urlencode, quote
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest


class GenerateAnalysisJSMiddleware:
    """
    动态生成 analysis 加密参数, 重新构造请求 url
    """
    def __init__(self, analysis_js, api_configuration):
        self.js_text = analysis_js
        self.ctx = execjs.compile(self.js_text)
        self.api_configuration = api_configuration

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            analysis_js=crawler.settings.get('ANALYSIS_JS'),
            api_configuration=crawler.settings.get('API_CONFIGURATION')
        )

    @staticmethod
    def process_params(params):
        """
        对请求参数值进行排序, 构造加密字符串
        :param params:
        :return:
        """
        xparams = []
        for value in params.values():
            xparams.append(value)
        p_str = ''
        # 对参数列表进行排序
        xparams.sort()
        for p in xparams:
            p_str += p
        return p_str

    @staticmethod
    def _get_synct():
        """
        请求首页获取 synct： 这个参数的意思是首次访问时间戳
        :return:
        """
        while True:
            resp = requests.get('https://www.qimai.cn/rank')
            cookies = resp.cookies.get_dict()
            synct = cookies.get('synct')
            if synct:
                return cookies.get('synct')
            time.sleep(random.random())

    def _get_analysis(self, p_str, url):
        synct = self._get_synct()
        return self.ctx.call('getAnalysis', p_str, url, synct)

    def process_request(self, request, spider):
        """
        构造请求 url 并替换原始 api
        :param request:
        :param spider:
        :return:
        """
        meta = request.meta
        api_type = meta['api_type']
        operating_system = meta['operating_system']
        page = meta.get('page', 0)
        keyword = meta.get('keyword', '')
        device = meta.get('device', 'iphone')
        version = meta.get('version', 'ios12')
        app_id = meta.get('app_id', 0)
        api_config = self.api_configuration.get(api_type)
        params = api_config['params'][operating_system]
        if 'page' in params.keys():
            params.update({
                'page': str(page)
            })
        if 'search' in params.keys():
            params.update({
                'search': keyword
            })
        if 'date' in params.keys():
            params.update({
                'date': str(time.strftime("%Y-%m-%d", time.localtime(int(time.time()))))
            })
        if 'device' in params.keys():
            params.update({
                'device': device
            })
        if 'version' in params.keys():
            params.update({
                'version': version
            })
        p_str = self.process_params(params)
        analysis = self._get_analysis(p_str, api_config['api'][operating_system])
        params.update({
            'analysis': analysis
        })
        new_url = api_config['api'][operating_system] + '?' + urlencode(params)
        request._set_url(new_url)
        if app_id:
            request.headers['Referer'] = api_config['referer'][operating_system].format(app_id)
        else:
            request.headers['Referer'] = api_config['referer'][operating_system].format(quote(keyword))


class SetRefererMiddleware:

    def process_request(self, request, spider):
        referer = request.meta['referer']
        request.headers.update({'Referer': referer})


class RandomUserAgentMiddleware:

    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
            "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3013.3 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36 BIDUBrowser/8.8',
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)


class RandomCookiesMiddleware:

    def __init__(self, cookies_pool_url):
        self.logger = logging.getLogger(__name__)
        self.cookies_pool_url = cookies_pool_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            cookies_pool_url=crawler.settings.get('COOKIES_POOL_URL')
        )

    def get_random_cookies(self):
        while True:
            try:
                r = requests.get(self.cookies_pool_url)
                cookies = json.loads(r.text)
                return cookies
            except Exception as e:
                print('获取 Cookies 失败: ', e.args)

    def process_request(self, request, spider):
        if request.meta.get('retry_times'):
            cookies = self.get_random_cookies()
            if cookies:
                # 打印使用 cookies 信息, 将 debug 改成 info 即可
                self.logger.debug('使用 cookies: \n' + json.dumps(cookies))
                request.cookies = cookies


class RandomProxyMiddleware:

    def __init__(self, proxy_pool_url):
        self.proxy_pool_url = proxy_pool_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_pool_url=crawler.settings.get('PROXY_POOL_URL')
        )

    def get_random_proxy(self):
        while True:
            try:
                resp = requests.get(self.proxy_pool_url)
                proxy = resp.content.decode('utf-8')
                proxies = 'https://{}'.format(proxy)
                return proxies
            except Exception as e:
                pass

    def process_request(self, request, spider):
        proxy = self.get_random_proxy()
        if proxy:
            request.meta['proxy'] = proxy


class MyRetryMiddleware(RetryMiddleware):

    @staticmethod
    def check_response_bad(response):
        try:
            result = json.loads(response.body)
            if result['code'] != 10000:
                reason = 'Json code is Invalid! '
                return reason
            return False
        except json.decoder.JSONDecodeError:
            if response.status != 200:
                reason = 'Response.status is Invalid! '
                return reason
            reason = 'Json decode error! '
            return reason

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response

        reason = self.check_response_bad(response)
        if reason:
            retry_times = request.meta.get('retry_times', 0) + 1
            if retry_times >= self.max_retry_times:
                spider.logger.warning('已到达最大重试次数，放弃！{}'.format(request.url))
                raise IgnoreRequest
            spider.logger.warning('{}, Retry！{}'.format(reason, request.url))
            return self._retry(request, reason, spider)
        else:
            return response

# -*- coding: utf-8 -*-

import json
import time
import requests
import random
import execjs
from datetime import datetime
from scrapy_redis.spiders import RedisSpider
from scrapy import Request
from urllib.parse import urlencode, quote
from .. import md5
from ..items import IphoneBaseInfoItem, AndroidBaseInfoItem
from ..items import IphoneVersionUpdateRecordItem, IphoneVersionInfoItem, IphoneCommentScoreItem
from ..items import IphoneCommentItem, AndroidCommentScoreItem, AndroidPlatformShelvesItem
from ..items import AndroidDownloadTotalCountItem, AndroidPlatformDownloadCountItem
from ..items import IphoneRankInfoItem, AndroidRankInfoItem


class QimaiAppSpider(RedisSpider):
    name = 'counter_qimai'
    today = datetime.today()

    custom_settings = {
        'LOG_LEVEL': 'INFO',
        # 日志路径
        # 'LOG_FILE': 'log/{}_{}_{}_{}.log'.format(today.year, today.month, today.day, name),
        # 并发设为15
        'CONCURRENT_REQUESTS': 10,
        # TTL DUPEFILTER 调度器
        'SCHEDULER': 'scrapy_redis.scheduler.Scheduler',
        # TTL DUPEFILTER
        'DUPEFILTER_CLASS': 'scrapy_redis.dupefilter.RFPDupeFilter',
        # REDIS连接
        'REDIS_URL': 'redis://:*************/1',
        # 代理池地址
        'PROXY_POOL_URL': 'http://***********/random/',
        # Cookie 池地址
        'COOKIES_POOL_URL': 'http://*************/qimai/random',
        # 不清空数据
        'SCHEDULER_PERSIST': True,
        # 下载中间件
        'DOWNLOADER_MIDDLEWARES': {
            'crawl_qimai.middlewares.MyRetryMiddleware': 557,
            'crawl_qimai.middlewares.RandomUserAgentMiddleware': 558,
            'crawl_qimai.middlewares.SetRefererMiddleware': 559,
            'crawl_qimai.middlewares.RandomProxyMiddleware': 560,
            'crawl_qimai.middlewares.RandomCookiesMiddleware': 561
        },
        # 数据管道
        'ITEM_PIPELINES': {
            'crawl_qimai.pipelines.DefaultValueItemPipeline': 301,
            'crawl_qimai.pipelines.ContentCleanItemPipeline': 302,
            'crawl_qimai.pipelines.ContentCheckItemPipeline': 303,
            'crawl_qimai.pipelines.MongoPipeline': 305,
        },
        # mongo管道会进行处理的item的名称列表
        'MONGO_PIPELINE_ITEM_CLASS_LIST': [
            'IphoneBaseInfoItem', 'AndroidBaseInfoItem',
            'IphoneVersionUpdateRecordItem', 'IphoneVersionInfoItem',
            'IphoneCommentScoreItem', 'AndroidDownloadTotalCountItem',
            'AndroidPlatformDownloadCountItem', 'IphoneCommentItem',
            'AndroidCommentScoreItem', 'AndroidPlatformShelvesItem',
            'IphoneRankInfoItem', 'AndroidRankInfoItem'
        ],
        # 定时关闭爬虫 45分钟
        'CLOSESPIDER_TIMEOUT': 30 * 60,
    }

    operating_system_set = {'iphone', 'android'}

    @staticmethod
    def process_params(params):
        """
        对请求参数值进行排序, 构造加密字符串
        :param params:
        :return:
        """
        xparams = []
        for value in params.values():
            if not isinstance(value, str):
                value = str(value)
            xparams.append(value)
        p_str = ''
        # 对参数列表进行排序
        xparams.sort()
        for p in xparams:
            p_str += p
        return p_str

    @staticmethod
    def get_headers(referer):
        return {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://www.qimai.cn',
            'Referer': referer,
        }

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
        js_text = self.settings.get('ANALYSIS_JS')
        ctx = execjs.compile(js_text)
        return ctx.call('getAnalysis', p_str, url, synct)

    def make_requests_from_url(self, url):
        task = json.loads(url)
        etid = task['etid']
        name = task['name']
        shortname = task['shortname']
        keyword = shortname if shortname else name

        api_configuration = self.settings.get('API_CONFIGURATION')
        for operating_system in self.operating_system_set:
            if operating_system == 'android':
                # 安卓入口
                api = api_configuration['search']['api'][operating_system]
                params = api_configuration['search']['params'][operating_system]
                referer = api_configuration['search']['referer'][operating_system].format(quote(keyword))
                params.update({'search': keyword})
                p_str = self.process_params(params)
                analysis = self._get_analysis(p_str, api)
                search_params = params.copy()
                search_params.update({
                    'analysis': analysis
                })
                meta = {
                    'etid': etid, 'name': name, 'shortname': shortname,
                    'keyword': keyword, 'page': 1,
                    'operating_system': operating_system, 'referer': referer
                }
                xurl = api + '?' + urlencode(search_params)
                return Request(url=xurl,
                               meta=meta,
                               callback=self.parse,
                               priority=10)
            elif operating_system == 'iphone':
                # 苹果入口
                for device in {'iphone', 'ipad'}:
                    for ios in {'ios11', 'ios12'}:
                        api = api_configuration['search']['api'][operating_system]
                        params = api_configuration['search']['params'][operating_system]
                        referer = api_configuration['search']['referer'][operating_system]
                        params.update({
                            'date': time.strftime("%Y-%m-%d", time.localtime(int(time.time()))),
                            'device': device,
                            'search': keyword,
                            'version': ios
                        })
                        p_str = self.process_params(params)
                        analysis = self._get_analysis(p_str, api)
                        search_params = params.copy()
                        search_params.update({
                            'analysis': analysis
                        })
                        meta = {
                            'etid': etid, 'name': name, 'shortname': shortname,
                            'keyword': keyword, 'page': 1,
                            'operating_system': operating_system, 'referer': referer
                        }
                        xurl = api + '?' + urlencode(search_params)
                        return Request(url=xurl,
                                       meta=meta,
                                       callback=self.parse,
                                       priority=10)

    def parse(self, response):
        meta = response.meta
        operating_system = meta['operating_system']
        etid = meta['etid']
        fullname = meta['name']
        keyword = meta['keyword']

        result = json.loads(response.body)
        if result['code'] == 10000:

            api_configuration = self.settings.get('API_CONFIGURATION')

            app_list = result['appList']
            max_page = result.get('maxPage', 0)
            num = 0
            for app in app_list:
                app_info = app.get('appInfo', 0)
                # 有插播广告...
                if not app_info:
                    continue
                # 比较开发商全称及 App 名称是否符合
                if fullname not in app_info['publisher'] and keyword not in app_info['appName']:
                    num += 1
                    continue

                # App 在七麦的 id
                app_id = app_info['appId']
                # App 名称
                app_name = app_info['appName']
                # 开发者
                developer = app_info['publisher']
                # 图标
                icon_url = app_info['icon']
                # 图标: 二进制数据
                if icon_url and icon_url != '':
                    icon = requests.get(icon_url).content
                else:
                    icon = b''
                # 类型
                type = app['genre']

                if operating_system == 'android':
                    # 评论数
                    comment_count = app_info['comment_count']
                    if comment_count == '':
                        comment_count = 0
                    # 评分
                    comment_score = app_info['comment_score']
                    if comment_score == '':
                        comment_score = 0

                    item = AndroidBaseInfoItem()
                    item['comment_count'] = comment_count
                    item['comment_score'] = comment_score
                else:
                    # app 别名
                    subname = app_info['subName']
                    # 所属国家
                    country = app_info['country']
                    # 副标题
                    subtitle = app_info['subtitle']
                    # 类型排名
                    ranking = app['ranking']
                    rank_info = {
                        'all': {
                            'genre': ranking['genre_all'],
                            'rank': ranking['rank_all']
                        },
                        'class': {
                            'genre': ranking['genre_class'],
                            'ranking': ranking['rank_class']
                        }
                    }
                    # 是否上线
                    is_online = int(app['is_online'])

                    item = IphoneBaseInfoItem()
                    item['subname'] = subname
                    item['country'] = country
                    item['subtitle'] = subtitle
                    item['rank_info'] = rank_info
                    item['is_online'] = is_online

                item['operating_system'] = operating_system
                item['etid'] = etid
                item['app_id'] = app_id
                item['app_name'] = app_name
                item['developer'] = developer
                item['icon_url'] = icon_url
                item['icon'] = icon
                item['type'] = type

                callback_map = {
                    'base_info': self.parse_base_info,
                    'ios_version': self.parse_version,
                    'ios_comment_score': self.parse_comment_rate,
                    'comment': self.parse_comment,
                    'android_shelves': self.parse_shelves,
                    'android_download': self.parse_download,
                    'realtime_rank': self.parse_rank,
                    'same_developer': self.parse_same
                }
                for api_type in api_configuration.keys():
                    # 安卓各平台的排名信息入口放在 self.parse_base_info 里
                    if api_type == 'realtime_rank' and operating_system == 'android' or api_type == 'search':
                        continue
                    api = api_configuration[api_type]['api'].get(operating_system, 0)
                    if not api:
                        continue
                    params = api_configuration[api_type]['params'][operating_system]
                    referer = api_configuration[api_type]['referer'][operating_system].format(app_id)
                    params.update({'appid': app_id})
                    p_str = self.process_params(params)
                    analysis = self._get_analysis(p_str, api)
                    xparams = params.copy()
                    xparams.update({'analysis': analysis})
                    meta.update({
                        'app_id': app_id,
                        'app_name': app_name,
                        'item': item,
                        'referer': referer
                    })
                    xurl = api + '?' + urlencode(xparams)
                    yield Request(url=xurl,
                                  meta=meta,
                                  callback=callback_map[api_type],
                                  priority=20)
                # 找到查询企业的 App, 停止遍历
                break

            # 如果遍历查询的 App 数量已达到该列表总 App 数量, 说明有下一页, 继续查询下一页
            page = meta['page']
            if num >= len(app_list):
                page += 1
                if page <= max_page:
                    api = api_configuration['search']['api'][operating_system]
                    params = api_configuration['search']['params'][operating_system]
                    referer = api_configuration['search']['referer'][operating_system].format(quote(keyword))
                    params.update({'page': str(page)})
                    p_str = self.process_params(params)
                    analysis = self._get_analysis(p_str, api)
                    search_params = params.copy()
                    search_params.update({
                        'analysis': analysis
                    })
                    meta.update({
                        'page': page,
                        'referer': referer
                    })
                    xurl = api + '?' + urlencode(search_params)
                    yield Request(url=xurl,
                                  meta=meta,
                                  callback=self.parse,
                                  priority=10)
        else:
            print('search error: {}: {}'.format(keyword, result['msg']))
            yield response.request

    def parse_base_info(self, response):
        meta = response.meta
        operating_system = meta['operating_system']
        item = meta['item']

        result = json.loads(response.body)
        if result['code'] == 10000:
            app_info = result['appInfo']
            if operating_system == 'iphone':
                for xinfo in app_info:
                    name = xinfo['name']
                    if name == '发布日期':
                        item['publish_time'] = xinfo['value']
                    elif name == '更新日期':
                        item['update_time'] = xinfo['value']
                    elif name == 'Bundle ID':
                        item['bundle_id'] = xinfo['value']
                    elif name == '版本':
                        item['version'] = xinfo['value']
                    elif name == '大小':
                        item['size'] = xinfo['value']
                    elif name == '是否支持 Watch':
                        if xinfo['value'] == '支持':
                            item['is_support_watch'] = 1
                        else:
                            item['is_support_watch'] = 0
                    elif name == '家人共享':
                        if xinfo['value'] == '可使用':
                            item['family_share'] = 1
                        else:
                            item['family_share'] = 0
                    elif name == '支持网站':
                        item['support_website'] = xinfo['value']
                    elif name == '开发者网站':
                        item['developer_website'] = xinfo['value']
                    elif name == '兼容性':
                        item['compatibility'] = xinfo['value']
                    elif name == '支持语言':
                        item['language'] = xinfo['value']
                    elif name == '发行国家/地区':
                        item['publish_area'] = xinfo['value']
                    elif name == '内容评级':
                        item['qimai_content_rating'] = xinfo['value']

                # 简介
                item['description'] = result['description']
                # 截图
                screenshots = {}
                xscreenshots = result['screenshot']
                for xscreenshot in xscreenshots:
                    name = xscreenshot['name']
                    imgs = xscreenshot['value']
                    for img_url in imgs:
                        if img_url and img_url != '':
                            img = requests.get(img_url).content
                        else:
                            img = b''
                        screenshots.setdefault(name, []).append({
                            'img_url': img_url,
                            'img': img
                        })
                item['screenshots'] = screenshots
                item['addtime'] = int(time.time())
                # md5去重
                encrypt_str = item['app_id'] + item['version'] + item['publish_time']
                item['hash_text'] = md5.encrypt(encrypt_str)
                yield item

            elif operating_system == 'android':
                # 简介
                description = app_info['app_brief']
                # 大小
                size = app_info['app_size']
                # 版本
                version = app_info['app_version']
                # 发布日期
                publish_time = app_info['app_version_time']
                # 别名
                subname = app_info['sub_name']
                # Bundle ID
                bundle_id = app_info['app_bundleid']
                # 是否上线
                is_online = app_info['is_online']
                # 截图
                screenshots = {}
                xscreenshots = app_info['app_screenshot']
                for xscreenshot in xscreenshots:
                    img_url = xscreenshot
                    if img_url and img_url != '':
                        img = requests.get(img_url).content
                    else:
                        img = b''
                    screenshots.setdefault('android', []).append({
                        'img_url': img_url,
                        'img': img
                    })
                # 应用平台列表
                platform_list = [x['name'] for x in result['marketList']]
                item['platform_list'] = platform_list
                # md5去重
                encrypt_str = item['app_id'] + version + publish_time
                item['hash_text'] = md5.encrypt(encrypt_str)
                item['addtime'] = int(time.time())
                item['description'] = description
                item['size'] = size
                item['version'] = version
                item['publish_time'] = publish_time
                item['subname'] = subname
                item['bundle_id'] = bundle_id
                item['is_online'] = is_online
                item['screenshots'] = screenshots

                yield item

                platform_id_list = [x['marketId'] for x in result['marketList']]
                api_configuration = self.settings.get('API_CONFIGURATION')
                for index, platform_id in enumerate(platform_id_list):
                    platform = platform_list[index]
                    api = api_configuration['realtime_rank']['api'][operating_system]
                    params = api_configuration['realtime_rank']['params'][operating_system]
                    referer = api_configuration['realtime_rank']['referer'][operating_system].format(item['app_id'])
                    rank_params = params.copy()
                    rank_params.update({'market': platform_id, 'appid': item['app_id']})
                    p_str = self.process_params(rank_params)
                    anaysis = self._get_analysis(p_str, api)
                    rank_params.update({'analysis': anaysis})
                    meta.update({
                        'platform': platform,
                        'referer': referer
                    })
                    xurl = api + '?' + urlencode(rank_params)
                    yield Request(url=xurl,
                                  meta=meta,
                                  callback=self.parse_rank,
                                  priority=20)
        else:
            print('crawl base_info error: {}: {}'.format(meta['keyword'], result['msg']))
            yield response.request

    def parse_version(self, response):
        meta = response.meta
        etid = meta['etid']
        app_id = meta['app_id']
        app_name = meta['app_name']
        operating_system = meta['operating_system']

        result = json.loads(response.body)
        if result['code'] == 10000:
            # 全球最早版本上线日期
            first_publish_time = result['stat']['first']
            # 近一年版本更新次数
            recent_update_num = int(result['stat']['recentNum'])
            # 距离上次更新时间
            last_update_interval = result['stat'].get('last', 0)
            # md5去重
            encrypt_str = app_id + first_publish_time
            hash_text = md5.encrypt(encrypt_str)

            version_update_item = IphoneVersionUpdateRecordItem()
            version_update_item['operating_system'] = operating_system
            version_update_item['app_id'] = app_id
            version_update_item['app_name'] = app_name
            version_update_item['etid'] = etid
            version_update_item['first_publish_time'] = first_publish_time
            version_update_item['recent_update_num'] = recent_update_num
            version_update_item['last_update_interval'] = last_update_interval
            version_update_item['addtime'] = int(time.time())
            version_update_item['hash_text'] = hash_text
            yield version_update_item

            # 版本
            versions = result['version']
            for xversion in versions:
                # 版本名称
                app_name = xversion['app_name']
                # 版本编号
                version = xversion['version']
                # 副标题
                subtitle = xversion['subtitle']
                # 简介
                description = xversion['description']
                # 是否首次发布的版本
                is_first = xversion['first']
                # 图标
                icon_url = xversion['icon']
                # 图标: 二进制数据
                if icon_url and icon_url != '':
                    icon = requests.get(icon_url).content
                else:
                    icon = b''
                # 是否有旧版本
                is_pre_version = xversion['is_pre_version']
                # 上一个版本的发布时间
                pre_publish_timme = xversion['pre_release_time']
                # 上一个版本编号
                pre_version = xversion['pre_version']
                # 发布时间
                publish_time = xversion['release_time']
                # 发布说明
                publish_note = xversion['release_note']
                # 截图
                screenshots = {}
                xscreenshots = xversion['screenshot']
                for xscreenshot in xscreenshots:
                    name = xscreenshot['name']
                    imgs = xscreenshot['value']
                    for img_url in imgs:
                        if img_url and img_url != '':
                            img = requests.get(img_url).content
                        else:
                            img = b''
                        screenshots.setdefault(name, []).append({
                            'img_url': img_url,
                            'img': img
                        })
                # md5去重
                encrypt_str = app_id + version + publish_time
                hash_text = md5.encrypt(encrypt_str)

                version_item = IphoneVersionInfoItem()
                version_item['operating_system'] = operating_system
                version_item['app_id'] = app_id
                version_item['app_name'] = app_name
                version_item['subtitle'] = subtitle
                version_item['version'] = version
                version_item['description'] = description
                version_item['icon_url'] = icon_url
                version_item['icon'] = icon
                version_item['is_first'] = is_first
                version_item['is_pre_version'] = is_pre_version
                version_item['pre_publish_time'] = pre_publish_timme
                version_item['pre_version'] = pre_version
                version_item['publish_time'] = publish_time
                version_item['publish_note'] = publish_note
                version_item['screenshots'] = screenshots
                version_item['etid'] = etid
                version_item['addtime'] = int(time.time())
                version_item['hash_text'] = hash_text
                yield version_item
        else:
            print('crawl version error: {}: {}'.format(meta['keyword'], result['msg']))
            yield response.request

    def parse_comment_rate(self, response):
        meta = response.meta
        etid = meta['etid']
        app_id = meta['app_id']
        app_name = meta['app_name']
        operating_system = meta['operating_system']

        result = json.loads(response.body)
        if result['code'] == 10000:
            rate_info = result['rateInfo']
            # 所有版本评分
            all = rate_info['all']
            # App Store 当前显示评分
            current = rate_info['current']
            # md5去重
            encrypt_str = app_id + str(all['total'])
            hash_text = md5.encrypt(encrypt_str)

            item = IphoneCommentScoreItem()
            item['app_id'] = app_id
            item['app_name'] = app_name
            item['operating_system'] = operating_system
            item['all'] = all
            item['current'] = current
            item['etid'] = etid
            item['addtime'] = int(time.time())
            item['hash_text'] = hash_text
            yield item
        else:
            print('crawl comment_rate error: {}: {}'.format(meta['keyword'], result['msg']))
            yield response.request

    def parse_comment(self, response):
        meta = response.meta
        etid = meta['etid']
        app_id = meta['app_id']
        app_name = meta['app_name']
        operating_system = meta['operating_system']

        result = json.loads(response.body)
        if result['code'] == 10000:
            if operating_system == 'iphone':
                # 评论数
                comment_count = result['appCommentCount']
                # 评论
                comments = result['appComments']
                # 最大页码
                max_page = result['maxPage']
                for comment in comments:
                    # 用户名
                    username = comment['comment']['name']
                    # 标题
                    title = comment['comment']['title']
                    # 内容
                    content = comment['comment']['body']
                    # 发布时间
                    release_time = comment['date']
                    # 赞同数
                    voteup = comment['comment']['voteup']
                    # 不赞同数
                    votedown = comment['comment']['votedown']
                    # 评价星级
                    rating = comment['rating']
                    # md5去重
                    encrypt_str = app_id + comment['id'] + release_time
                    hash_text = md5.encrypt(encrypt_str)

                    item = IphoneCommentItem()
                    item['app_id'] = app_id
                    item['app_name'] = app_name
                    item['comment_count'] = comment_count
                    item['username'] = username
                    item['title'] = title
                    item['content'] = content
                    item['release_time'] = release_time
                    item['voteup'] = voteup
                    item['votedown'] = votedown
                    item['rating'] = rating
                    item['etid'] = etid
                    item['addtime'] = int(time.time())
                    item['hash_text'] = hash_text
                    yield item

                # 剩余页
                if meta['page'] == 1:
                    api_configuration = self.settings.get('API_CONFIGURATION')
                    for page in range(2, max_page):
                        api = api_configuration['comment']['api'][operating_system]
                        params = api_configuration['comment']['params'][operating_system]
                        referer = api_configuration['comment']['referer'][operating_system].format(app_id)
                        params.update({
                            'appid': app_id,
                            'page': str(page)
                        })
                        p_str = self.process_params(params)
                        analysis = self._get_analysis(p_str, api)
                        comment_params = params.copy()
                        comment_params.update({
                            'analysis': analysis
                        })
                        meta.update({
                            'page': page,
                            'referer': referer
                        })
                        xurl = api + '?' + urlencode(comment_params)
                        yield Request(url=xurl,
                                      meta=meta,
                                      callback=self.parse_comment,
                                      priority=20)

            elif operating_system == 'android':
                comments = result['appComments']
                for comment in comments:
                    # 应用平台
                    platform = comment['app_market']
                    # 评分
                    comment_score = comment['app_comment_score']
                    # 评论数
                    comment_count = comment['app_comment_count']
                    # 发布时间
                    publish_time = comment['app_version_time']
                    # md5去重
                    encrypt_str = app_id + platform + publish_time
                    hash_text = md5.encrypt(encrypt_str)

                    item = AndroidCommentScoreItem()
                    item['operating_system'] = operating_system
                    item['app_id'] = app_id
                    item['app_name'] = app_name
                    item['platform'] = platform
                    item['comment_score'] = comment_score
                    item['comment_count'] = comment_count
                    item['publish_time'] = publish_time
                    item['etid'] = etid
                    item['addtime'] = int(time.time())
                    item['hash_text'] = hash_text
                    yield item
        else:
            print('crawl comment error: {}: {}'.format(meta['keyword'], result['msg']))
            yield response.request

    def parse_shelves(self, response):
        meta = response.meta
        etid = meta['etid']
        app_id = meta['app_id']
        app_name = meta['app_name']
        operating_system = meta['operating_system']

        result = json.loads(response.body)
        if result['code'] == 10000:
            shelves = result['appShelves']
            for shelve in shelves:
                # 上架状态
                status = shelve['status']
                # 图标
                icon_url = shelve['app_icon']
                # 图标: 二进制数据
                if icon_url and icon_url != '':
                    icon = requests.get(icon_url).content
                else:
                    icon = b''
                # 应用平台
                platform = shelve['app_market']
                # 版本
                version = shelve['app_version']
                # 下载地址
                download_url = shelve['app_url']
                # md5去重
                encrypt_str = app_id + platform + version + download_url
                hash_text = md5.encrypt(encrypt_str)

                item = AndroidPlatformShelvesItem()
                item['operating_system'] = operating_system
                item['app_id'] = app_id
                item['app_name'] = app_name
                item['status'] = status
                item['icon_url'] = icon_url
                item['icon'] = icon
                item['platform'] = platform
                item['version'] = version
                item['download_url'] = download_url
                item['etid'] = etid
                item['addtime'] = int(time.time())
                item['hash_text'] = hash_text
                yield item
        else:
            print('crawl shelves error: {}: {}'.format(meta['keyword'], result['msg']))
            yield response.request

    def parse_download(self, response):
        meta = response.meta
        etid = meta['etid']
        app_id = meta['app_id']
        app_name = meta['app_name']
        operating_system = meta['operating_system']

        result = json.loads(response.body)
        if result['code'] == 10000:
            # 总下载量
            total_count = result['total']
            # 近一个月下载量
            recent_count = result['rTotal']
            # md5去重
            encrypt_str = app_id + str(recent_count)
            hash_text = md5.encrypt(encrypt_str)

            total_item = AndroidDownloadTotalCountItem()
            total_item['operating_system'] = operating_system
            total_item['app_id'] = app_id
            total_item['app_name'] = app_name
            total_item['total_count'] = total_count
            total_item['recent_count'] = recent_count
            total_item['etid'] = etid
            total_item['addtime'] = int(time.time())
            total_item['hash_text'] = hash_text
            yield total_item

            # 各平台
            downList = result['downList']
            for down in downList:
                # 平台名称
                platform = down['market_name']
                # 近一个月下载量
                p_recent_count = down['rDownload']
                # 总下载量
                p_total_count = down['totalDownload']
                # md5去重
                xencrypt_str = app_id + platform + str(p_recent_count)
                xhash_text = md5.encrypt(xencrypt_str)

                platform_item = AndroidPlatformDownloadCountItem()
                platform_item['operating_system'] = operating_system
                platform_item['app_id'] = app_id
                platform_item['app_name'] = app_name
                platform_item['platform'] = platform
                platform_item['total_count'] = p_total_count
                platform_item['recent_count'] = p_recent_count
                platform_item['etid'] = etid
                platform_item['addtime'] = int(time.time())
                platform_item['hash_text'] = xhash_text
                yield platform_item
        else:
            print('crawl download error: {}: {}'.format(meta['keyword'], result['msg']))
            yield response.request

    def parse_rank(self, response):
        meta = response.meta
        etid = meta['etid']
        app_id = meta['app_id']
        app_name = meta['app_name']
        operating_system = meta['operating_system']

        result = json.loads(response.body)
        if result['code'] == 10000:
            if operating_system == 'iphone':
                realTimeRank = result['realTimeRank']
                categories = realTimeRank[0][1:]
                datas = realTimeRank[1:]
                for data in datas:
                    # 平台: iphone 或 ipad 或 iphone watch
                    platform = data[0].replace('实时排名', '').strip()
                    ranks = data[1:]
                    for index, category in enumerate(categories):
                        # 当前排名
                        ranking = ranks[index]['ranking']
                        # 距上次更新时间
                        update_time_interval = ranks[index]['time']
                        # md5去重
                        encrypt_str = app_id + platform + category
                        hash_text = md5.encrypt(encrypt_str)

                        item = IphoneRankInfoItem()
                        item['operating_system'] = operating_system
                        item['app_id'] = app_id
                        item['app_name'] = app_name
                        item['etid'] = etid
                        item['addtime'] = int(time.time())
                        item['platform'] = platform
                        item['category'] = category
                        item['ranking'] = ranking
                        item['update_time_interval'] = update_time_interval
                        item['hash_text'] = hash_text
                        yield item

            elif operating_system == 'android':
                platform = meta['platform']
                ranks = result['list']
                if ranks:
                    for rank in ranks:
                        # 排行榜
                        category = rank['category']
                        # 当前排名
                        ranking = int(rank['ranking'])
                        # 近七日最高排名
                        max_rank = int(rank['max'])
                        # 排行变化
                        if '上升' in rank['change']:
                            change = int(rank['change'].replace('上升', '').strip())
                        elif '下降' in rank['change']:
                            change = - int(rank['change'].replace('下降', '').strip())
                        else:
                            change = 0
                        # md5去重
                        encrypt_str = app_id + platform + category
                        hash_text = md5.encrypt(encrypt_str)

                        item = AndroidRankInfoItem()
                        item['operating_system'] = operating_system
                        item['app_id'] = app_id
                        item['app_name'] = app_name
                        item['etid'] = etid
                        item['addtime'] = int(time.time())
                        item['platform'] = platform
                        item['category'] = category
                        item['ranking'] = ranking
                        item['max_rank'] = max_rank
                        item['change'] = change
                        item['hash_text'] = hash_text
                        yield item
        else:
            print('crawl rank error: {}: {}'.format(meta['keyword'], result['msg']))
            yield response.request

    def parse_same(self, response):
        meta = response.meta
        operating_system = meta['operating_system']
        etid = meta['etid']

        result = json.loads(response.body)
        if result['code'] == 10000:
            api_configuration = self.settings.get('API_CONFIGURATION')

            app_list = result['samePubApps'] if result['samePubApps'] else []
            for app in app_list:
                if operating_system == 'iphone':
                    app_info = app.get('appInfo', 0)
                    # 有插播广告...
                    if not app_info:
                        continue

                    item = IphoneBaseInfoItem()
                    # App 在七麦的 id
                    app_id = app_info['appId']
                    # App 名称
                    app_name = app_info['appName']
                    # 开发者
                    developer = app_info['publisher']
                    # 图标
                    icon_url = app_info['icon']
                    # 图标: 二进制数据
                    if icon_url and icon_url != '':
                        icon = requests.get(icon_url).content
                    else:
                        icon = b''
                    # 所属国家
                    item['country'] = app_info['country']
                    # 是否上线
                    if app['status'] == '在线':
                        item['is_online'] = 1
                    else:
                        item['is_online'] = 0
                else:
                    item = AndroidBaseInfoItem()
                    # App 在七麦的 id
                    app_id = app['appId']
                    # App 名称
                    app_name = app['appName']
                    # 开发者
                    developer = app['publisher']
                    # 图标
                    icon_url = app['icon']
                    item['icon_url'] = icon_url
                    # 图标: 二进制数据
                    if icon_url and icon_url != '':
                        icon = requests.get(icon_url).content
                    else:
                        icon = b''
                item['operating_system'] = operating_system
                item['etid'] = etid
                item['app_id'] = app_id
                item['app_name'] = app_name
                item['developer'] = developer
                item['icon_url'] = icon_url
                item['icon'] = icon

                callback_map = {
                    'base_info': self.parse_base_info,
                    'ios_version': self.parse_version,
                    'ios_comment_score': self.parse_comment_rate,
                    'comment': self.parse_comment,
                    'android_shelves': self.parse_shelves,
                    'android_download': self.parse_download,
                    'realtime_rank': self.parse_rank,
                }
                for api_type in api_configuration.keys():
                    # 安卓各平台的排名信息入口放在 self.parse_base_info 里
                    if api_type == 'realtime_rank' and operating_system == 'android' or api_type == 'search' or api_type == 'same_developer':
                        continue
                    api = api_configuration[api_type]['api'].get(operating_system, 0)
                    if not api:
                        continue
                    params = api_configuration[api_type]['params'][operating_system]
                    referer = api_configuration[api_type]['referer'][operating_system].format(app_id)
                    params.update({'appid': app_id})
                    p_str = self.process_params(params)
                    analysis = self._get_analysis(p_str, api)
                    xparams = params.copy()
                    xparams.update({'analysis': analysis})
                    meta.update({
                        'app_id': app_id,
                        'app_name': app_name,
                        'item': item,
                        'referer': referer
                    })
                    xurl = api + '?' + urlencode(xparams)
                    yield Request(url=xurl,
                                  meta=meta,
                                  callback=callback_map[api_type],
                                  priority=20)
        else:
            print('crawl same_developer error: {}: {}'.format(meta['keyword'], result['msg']))
            yield response.request

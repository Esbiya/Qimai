# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import time
import pymongo
import re
from scrapy.exceptions import DropItem
from .items import IphoneBaseInfoItem, AndroidBaseInfoItem
from .items import IphoneVersionUpdateRecordItem, IphoneVersionInfoItem, IphoneCommentScoreItem
from .items import IphoneCommentItem, AndroidCommentScoreItem, AndroidPlatformShelvesItem
from .items import AndroidDownloadTotalCountItem, AndroidPlatformDownloadCountItem
from .items import IphoneRankInfoItem, AndroidRankInfoItem


class DefaultValueItemPipeline:
    """
    为item设置默认值的管道
    """

    def process_item(self, item, spider):

        # **设置通用属性默认值**
        int_set = {
            'addtime', 'update_time', 'pre_publish_time', 'is_first',
            'publish_time', 'etid', 'voteup', 'votedown', 'recent_update_num',
            'release_time', 'score', 'recent_update_num', 'comment_count',
            'first_publish_time', 'last_update_interval', 'is_online',
            'is_pre_version', 'pre_publish_time', 'comment_score', 'comment_count',
            'rating', 'recent_count', 'total_count', 'status'
        }
        bytes_set = {'img', 'icon'}
        for key, value in item.items():
            if value is None:
                if key in int_set:
                    item[key] = 0
                elif key in bytes_set:
                    item[key] = b''
                else:
                    item[key] = ''
        return item


class ContentCleanItemPipeline:
    """
    对item中的内容进行清洗的管道
    """

    @staticmethod
    def clean_brackets(text):
        """
        处理文本中的括号，由全角转化为半角
        :param text:
        :return:
        """
        text = text.replace('）', ')').replace('（', '(').replace('【', '[').replace('】', ']')
        return text

    @staticmethod
    def _replace_invalid_symbol(text):
        text = text.replace(u'\xa0', u'').replace(u'\ufeff', u'').replace(u'\uf070', u'PI')
        text = text.replace(u'\u2022', u'.').replace(u'\u2028', u'').replace(u'\xbb', u' ')
        text = text.replace(u'\u200b', u' ').replace(u'\u0b67', u' ').replace(u'\xae', u' ')
        text = text.replace(u'\uff64', u'.').replace(u'\u2795', u' ').replace(u'\u265e', u' ')
        text = text.replace(u'\u25c9', u' ').replace(u'\u0e1a', u' ').replace(u'\u0300', u' ')
        text = text.replace(u'\xd8', u' ').replace(u'\u2f08', u'人').replace(u'\ufa41', u'敏')
        return text

    @staticmethod
    def data_to_timestamp(date):
        """
        日期转时间戳
        :param date:
        :return:
        """
        if re.match(r'(\d+)年(\d+)月(\d+)日', date):
            date = '-'.join(list(re.match(r'(\d+)年(\d+)月(\d+)日', date).groups()))
        if re.match(r'\d+-\d+-\d+ \d+:\d+:\d+', date):
            if date != '0000-00-00 00:00:00':
                return int(time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S")))
            return 0
        elif re.match(r'\d+-\d+-\d+', date) and ':' not in date:
            # 日期转时间戳只能转 1970-01-01 之后的日期, 如果出现转换失败, 则日期取 0: 意为 UnKnow
            try:
                return int(time.mktime(time.strptime(date, "%Y-%m-%d")))
            except OverflowError or ValueError:
                return 0
        else:
            return 0

    @staticmethod
    def clean_int(text):
        """
        清洗数字文本: 转化 str 为 int
        :param text:
        :return:
        """
        if isinstance(text, int):
            return text
        try:
            if ',' in text:
                text = text.replace(',', '')
            return int(text)
        except ValueError:
            print(text)
            return 0

    @staticmethod
    def clean_interval(interval):
        """
        清洗时间间隔
        :return:
        """
        timestamp = int(time.time())
        if '天' in interval:
            day = int(re.search(r'(\d+)天', interval).group(1))
            timestamp -= day * 86400
        if '小时' in interval:
            hour = int(re.search(r'(\d+)小时', interval).group(1))
            timestamp -= hour * 3600
        if '分钟' in interval:
            minute = int(re.search(r'(\d+)分钟', interval).group(1))
            timestamp -= minute * 60
        if '秒' in interval:
            second = int(re.search(r'(\d+)秒', interval).group(1))
            timestamp -= second
        return timestamp

    def replace_invalid_symbol(self, item):
        for key, value in item.items():
            if isinstance(value, str):
                text = self._replace_invalid_symbol(value)
                item[key] = text.encode(encoding='gbk', errors='ignore').decode(encoding='gbk', errors='ignore')
                item[key] = self.clean_brackets(text)

    def process_item(self, item, spider):
        time_set = {
            'update_time', 'pre_publish_time', 'publish_time',
            'release_time', 'first_publish_time'
        }
        int_set = {
            'is_first', 'etid', 'voteup', 'votedown', 'recent_update_num',
            'score', 'recent_update_num', 'comment_count',
            'is_online', 'is_pre_version', 'comment_count',
            'rating', 'recent_count', 'total_count', 'status'
        }
        for key, value in item.items():
            if key in time_set:
                item[key] = self.data_to_timestamp(value)
            elif 'interval' in key:
                item[key] = self.clean_interval(value)
            elif key in int_set:
                item[key] = self.clean_int(value)
        self.replace_invalid_symbol(item)
        return item


class ContentCheckItemPipeline:
    """
    对item中内容进行错误检查的管道，
    这里会将异常的item删除
    """

    @staticmethod
    def process_item(item, spider):
        if isinstance(item, IphoneBaseInfoItem):
            try:
                assert item['etid'] != 0
                assert item['app_name'] != ''
                assert item['description'] != ''
                assert type(item['icon']) == bytes
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, AndroidBaseInfoItem):
            try:
                assert item['etid'] != 0
                assert item['app_name'] != ''
                assert item['description'] != ''
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, IphoneVersionUpdateRecordItem):
            try:
                assert item['app_name'] != ''
                assert type(item['first_publish_time']) == int
                assert type(item['last_update_interval']) == int
                assert type(item['recent_update_num']) == int
                assert item['etid'] != 0
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, IphoneVersionInfoItem):
            try:
                assert item['app_name'] != ''
                assert item['description'] != ''
                assert item['etid'] != 0
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, IphoneCommentScoreItem):
            try:
                assert item['app_name'] != ''
                assert item['etid'] != 0
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, IphoneCommentItem):
            try:
                assert item['app_name'] != ''
                assert item['username'] != ''
                assert item['content'] != ''
                assert item['etid'] != 0
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, AndroidCommentScoreItem):
            try:
                assert item['app_name'] != ''
                assert item['platform'] != ''
                assert item['etid'] != 0
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, AndroidPlatformShelvesItem):
            try:
                assert item['platform'] != ''
                assert item['app_name'] != ''
                assert item['icon_url'] != ''
                assert item['etid'] != 0
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, AndroidDownloadTotalCountItem):
            try:
                assert item['app_name'] != ''
                assert item['etid'] != 0
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, AndroidPlatformDownloadCountItem):
            try:
                assert item['app_name'] != ''
                assert item['platform'] != ''
                assert item['etid'] != 0
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, IphoneRankInfoItem):
            try:
                assert item['app_name'] != ''
                assert item['platform'] != ''
                assert item['category'] != ''
                assert item['etid'] != 0
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item
        elif isinstance(item, AndroidRankInfoItem):
            try:
                assert item['app_name'] != ''
                assert item['platform'] != ''
                assert item['category'] != ''
                assert item['etid'] != 0
            except AssertionError:
                raise DropItem('数据异常，放弃！')
            return item


class MongoPipeline(object):

    def __init__(self, db_host, db_port, db_user, db_password, item_class_list):
        self.site = 'qimai'
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.item_class_list = item_class_list
        self.client = None
        self.db = None
        self.db_name = 'crawl_datastore_{}'.format(self.site)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_host=crawler.settings.get('MONGO_DB_HOST'),
            db_port=crawler.settings.get('MONGO_DB_PORT'),
            db_user=crawler.settings.get('MONGO_DB_USER'),
            db_password=crawler.settings.get('MONGO_DB_PASSWORD'),
            item_class_list=crawler.settings.get('MONGO_PIPELINE_ITEM_CLASS_LIST')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.db_host, port=self.db_port)
        db = self.client.admin
        db.authenticate(name=self.db_user, password=self.db_password, mechanism='SCRAM-SHA-1')
        self.db = self.client[self.db_name]
        for item_class in self.item_class_list:
            self.db[eval(item_class).collection].create_index([('hash_text', 1)])

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[item.collection].update({'hash_text': item.get('hash_text')}, {'$set': item}, True)

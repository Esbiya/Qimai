# -*- coding: utf-8 -*-
# @Time    : 2019/8/29 9:16
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : log_formatter.py
# @Software: PyCharm


import logging
from scrapy import logformatter


class PoliteFormatter(logformatter.LogFormatter):
    """
    改写 scrapy 日志, 使 DropItem 不打印丢弃的 item
    """
    def dropped(self, item, exception, response, spider):
        return {
            'level': logging.DEBUG,  # 不想打印 DropItem 把日志等级调成 DEBUG 即可, 因为爬虫的日志等级为 INFO, 低于这个等级不会打印
            'msg': logformatter.DROPPEDMSG,
            # DropItem 打印内容
            'args': {
                'exception': exception,
                'item': item   # 可以改成想要打印的内容
            }
        }

# 七麦APP数据爬虫

项目说明
---------

* 该项目使用 scrapy 框架编写
* 七麦数据接口使用js参数加密( analysis ), 破解 js 在 settings.py中 
* 考虑到数据量的问题, 使用代理池加 cookies 池一起采集, 请修改 counter_qimai.py 中的代理池和 cookie 池地址
* 基于 RedisSpider 实现分布式爬虫, 方便任务队列管理和去重, 请修改 counter_qimai.py 中的 redis 数据库地址
* 实现为 item 字段设置默认值、item 字段清洗、item 错误检查等管道
* 数据存入 MongoDB 数据库, 请修改 settings.py 中的 MongoDB 数据库地址

运行
---------
终端运行: scrapy crawl counter_qimai

公告
--------

该项目仅供学习参考, 请勿用作非法用途! 如若涉及侵权, 请联系2995438815@qq.com/18829040039@163.com, 收到必删除! 
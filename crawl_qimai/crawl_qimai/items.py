# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IphoneBaseInfoItem(scrapy.Item):
    collection = 'iphone_base_info'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    subname = scrapy.Field()
    subtitle = scrapy.Field()
    icon = scrapy.Field()
    icon_url = scrapy.Field()
    country = scrapy.Field()
    type = scrapy.Field()
    rank_info = scrapy.Field()
    developer = scrapy.Field()
    publish_time = scrapy.Field()
    update_time = scrapy.Field()
    description = scrapy.Field()
    bundle_id = scrapy.Field()
    version = scrapy.Field()
    size = scrapy.Field()
    is_online = scrapy.Field()
    is_support_watch = scrapy.Field()
    family_share = scrapy.Field()
    support_website = scrapy.Field()
    developer_website = scrapy.Field()
    compatibility = scrapy.Field()
    language = scrapy.Field()
    publish_area = scrapy.Field()
    screenshots = scrapy.Field()
    qimai_content_rating = scrapy.Field()
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class AndroidBaseInfoItem(scrapy.Item):
    collection = 'android_base_info'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    subname = scrapy.Field()
    description = scrapy.Field()
    type = scrapy.Field()
    version = scrapy.Field()
    size = scrapy.Field()
    icon = scrapy.Field()
    icon_url = scrapy.Field()
    bundle_id = scrapy.Field()
    developer = scrapy.Field()
    publish_time = scrapy.Field()
    is_online = scrapy.Field()
    comment_count = scrapy.Field()
    comment_score = scrapy.Field()
    platform_list = scrapy.Field()
    screenshots = scrapy.Field()
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class IphoneVersionUpdateRecordItem(scrapy.Item):
    collection = 'iphone_version_update_info'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    first_publish_time = scrapy.Field()
    recent_update_num = scrapy.Field()
    last_update_interval = scrapy.Field()
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class IphoneVersionInfoItem(scrapy.Item):
    collection = 'iphone_version_info'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    subtitle = scrapy.Field()
    version = scrapy.Field()
    description = scrapy.Field()
    icon_url = scrapy.Field()
    icon = scrapy.Field()
    is_first = scrapy.Field()
    is_pre_version = scrapy.Field()
    pre_publish_time = scrapy.Field()
    pre_version = scrapy.Field()
    publish_time = scrapy.Field()
    publish_note = scrapy.Field()
    screenshots = scrapy.Field()  # 截图
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class IphoneCommentScoreItem(scrapy.Item):
    """
    iphone 端版本评分
    """
    collection = 'iphone_comment_score'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    all = scrapy.Field()  # 所有版本评分
    current = scrapy.Field()  # App Store 当前显示评分
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class IphoneCommentItem(scrapy.Item):
    """
    iphone 端用户评论
    """
    collection = 'iphone_comments'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    comment_count = scrapy.Field()
    username = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    release_time = scrapy.Field()
    voteup = scrapy.Field()
    votedown = scrapy.Field()
    rating = scrapy.Field()
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class AndroidCommentScoreItem(scrapy.Item):
    """
    安卓端各平台用户评分
    """
    collection = 'android_comment_score'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    platform = scrapy.Field()
    publish_time = scrapy.Field()
    comment_score = scrapy.Field()
    comment_count = scrapy.Field()
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class AndroidPlatformShelvesItem(scrapy.Item):
    """
    安卓端各平台上架状态
    """
    collection = 'android_shelves_info'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    status = scrapy.Field()
    icon = scrapy.Field()
    platform = scrapy.Field()
    icon_url = scrapy.Field()
    version = scrapy.Field()
    download_url = scrapy.Field()
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class AndroidDownloadTotalCountItem(scrapy.Item):
    """
    安卓全平台下载量
    """
    collection = 'android_all_download_count'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    recent_count = scrapy.Field()
    total_count = scrapy.Field()
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class AndroidPlatformDownloadCountItem(scrapy.Item):
    """
    安卓各平台下载量
    """
    collection = 'android_platform_download_count'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    platform = scrapy.Field()
    recent_count = scrapy.Field()
    total_count = scrapy.Field()
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class IphoneRankInfoItem(scrapy.Item):
    collection = 'iphone_rank_info'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    platform = scrapy.Field()
    category = scrapy.Field()
    ranking = scrapy.Field()
    update_time_interval = scrapy.Field()
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()


class AndroidRankInfoItem(scrapy.Item):
    collection = 'android_rank_info'

    operating_system = scrapy.Field()
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    platform = scrapy.Field()
    category = scrapy.Field()
    ranking = scrapy.Field()
    max_rank = scrapy.Field()
    change = scrapy.Field()
    etid = scrapy.Field()
    addtime = scrapy.Field()
    hash_text = scrapy.Field()

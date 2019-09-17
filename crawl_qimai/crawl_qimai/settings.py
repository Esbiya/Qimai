# -*- coding: utf-8 -*-

# Scrapy settings for crawl_qimai project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'crawl_qimai'

SPIDER_MODULES = ['crawl_qimai.spiders']
NEWSPIDER_MODULE = 'crawl_qimai.spiders'

import os

LOG_LEVEL = 'INFO'

if not os.path.exists('log'):
    os.mkdir('log')

LOG_FORMATTER = 'crawl_qimai.log_formatter.PoliteFormatter'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

DOWNLOAD_TIMEOUT = 50

RETRY_ENABLED = True
RETRY_TIMES = 3

# REDIRECT_ENABLED = False

# 线上mongo数据库连接
MONGO_DB_HOST = '*******'  # 主机
MONGO_DB_PORT = 27017  # 端口
MONGO_DB_USER = '***'  # 用户名
MONGO_DB_PASSWORD = '********'  # 密码

# mongo管道会进行处理的item的名称列表
MONGO_PIPELINE_ITEM_CLASS_LIST = []

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://www.qimai.cn',
    'Referer': 'https://www.qimai.cn/search/android/search/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'lezhi_jobs_spider.middlewares.LezhiJobsSpiderSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'lezhi_jobs_spider.middlewares.LezhiJobsSpiderDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#     'lezhi_jobs_spider.common_pipelines.mysql_pipeline.MysqlPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# API 接口参数配置模板
API_CONFIGURATION = {
    # 搜索入口
    'search': {
        'api': {
            'android': 'https://api.qimai.cn/search/android',
            'iphone': 'https://api.qimai.cn/search/index'
        },
        'referer': {
            'android': 'https://www.qimai.cn/search/android/search/{}',
            'iphone': 'https://www.qimai.cn/search/index/country/cn/search/{}'
        },
        'params': {
            'android': {
                'market': '0',  # 0: 全平台
                'page': '1',
                'search': ''  # 关键词
            },
            'iphone': {
                'date': '',  # 查询日期
                'device': '',  # 设备
                'country': 'cn',  # 地区(默认中国)
                'search': '',  # 关键词
                'version': '',  # ios 系统版本, ios11, ios12
            }
        }
    },
    # 基本信息
    'base_info': {
        'api': {
            'iphone': 'https://api.qimai.cn/app/baseinfo',
            'android': 'https://api.qimai.cn/andapp/baseinfo'
        },
        'referer': {
            'android': 'https://www.qimai.cn/andapp/baseinfo/appid/{}',
            'iphone': 'https://www.qimai.cn/app/baseinfo/appid/{}/country/cn'
        },
        'params': {
            'android': {
                'appid': ''
            },
            'iphone': {
                'appid': '',
                'country': 'cn'
            }
        }
    },
    # ios 版本信息
    'ios_version': {
        'api': {
            'iphone': 'https://api.qimai.cn/app/version'
        },
        'referer': {
            'iphone': 'https://www.qimai.cn/app/version/appid/{}/country/cn'
        },
        'params': {
            'iphone': {
                'appid': '',
                'country': 'cn'
            }
        },
    },
    # ios 评分信息
    'ios_comment_score': {
        'api': {
            'iphone': 'https://api.qimai.cn/app/commentRate',
        },
        'referer': {
            'iphone': 'https://www.qimai.cn/app/comment/appid/{}/country/cn'
        },
        'params': {
            'iphone': {
                'appid': '',
                'country': 'cn'
            }
        }
    },
    # 评论
    'comment': {
        'api': {
            'iphone': 'https://api.qimai.cn/app/comment',
            'android': 'https://api.qimai.cn/andapp/comment'
        },
        'referer': {
            'android': 'https://www.qimai.cn/andapp/comment/appid/{}',
            'iphone': 'https://www.qimai.cn/app/comment/appid/{}/country/cn',
        },
        'params': {
            'android': {
                'appid': ''
            },
            'iphone': {
                'appid': '',
                'country': 'cn',
                'page': '1'
            }
        }
    },
    # android 上架状态
    'android_shelves': {
        'api': {
            'android': 'https://api.qimai.cn/andapp/shelves'
        },
        'referer': {
            'android': 'https://www.qimai.cn/andapp/shelves/appid/cn'
        },
        'params': {
            'android': {
                'appid': ''
            }
        }
    },
    # android 下载量 API
    'android_download': {
        'api': {
            'android': 'https://api.qimai.cn/andapp/downSources'
        },
        'referer': {
            'android': 'https://www.qimai.cn/andapp/downTotal/appid/cn'
        },
        'params': {
            'android': {
                'appid': ''
            }
        }
    },
    # 实时排名
    'realtime_rank': {
        'api': {
            'iphone': 'https://api.qimai.cn/app/rank',
            'android': 'https://api.qimai.cn/andapp/marketRank'
        },
        'referer': {
            'android': 'https://www.qimai.cn/andapp/rankinfo/appid/{}',
            'iphone': 'https://www.qimai.cn/app/rank/appid/{}/country/cn'
        },
        'params': {
            'android': {
                'appid': '',
                'market': ''
            },
            'iphone': {
                'appid': '',
                'country': 'cn',
            }
        }
    },
    # 同开发者应用 API
    'same_developer': {
        'api': {
            'iphone':'https://api.qimai.cn/app/samePubApp',
            'android': 'https://api.qimai.cn/andapp/samePubApp'
        },
        'referer': {
            'iphone': 'https://www.qimai.cn/app/rank/appid/{}/country/cn',
            'android': 'https://www.qimai.cn/andapp/samePubApp/appid/{}'
        },
        'params': {
            'iphone': {
                'appid': '',
                'country': 'cn'
            },
            'android': {
                'appid': ''
            }
        }
    }
}

ANALYSIS_JS = """
l = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "/"]

function n_(t) {
    var n;
    n = f(t.toString(), "binary");
    return u(n)
}
function a(t) {
    return l[t >> 18 & 63] + l[t >> 12 & 63] + l[t >> 6 & 63] + l[63 & t]
}
function s(t, e, n) {
    for (var r, i = [], o = e; o < n; o += 3)
        r = (t[o] << 16 & 16711680) + (t[o + 1] << 8 & 65280) + (255 & t[o + 2]),
            i.push(a(r));
    return i.join("")
}
function u(t) {
    for (var e, n = t.length, r = n % 3, i = "", o = [], a = 16383, u = 0, c = n - r; u < c; u += a)
        o.push(s(t, u, u + a > c ? c : u + a));
    return 1 === r ? (e = t[n - 1],
        i += l[e >> 2],
        i += l[e << 4 & 63],
        i += "==") : 2 === r && (e = (t[n - 2] << 8) + t[n - 1],
        i += l[e >> 10],
        i += l[e >> 4 & 63],
        i += l[e << 2 & 63],
        i += "="),
        o.push(i),
        o.join("")
}
function K(t, e, n, r) {
    for (var i = 0; i < r && !(i + n >= e.length || i >= t.length); ++i)
        e[i + n] = t[i];
    return i
}
function W(t) {
    for (var e = [], n = 0; n < t.length; ++n)
        e.push(255 & t.charCodeAt(n));
    return e
}
function t_(t, e, n, r) {
    return K(W(e), t, 0, r)
}
function f(e, n) {
    var r = e.length;
    t = new Uint8Array(r);
    var i = t_(t, e, n, r);
    return t
}
function v_(n) {
    return n_(encodeURIComponent(n)["replace"](/%([0-9A-F]{2})/g, function (a, n) {
        return String["fromCharCode"]("0x" + n)
    }))
}
function k_(a, n) {
    //n || (n = s()),
    a = a["split"]("");
    for (var t = a["length"], e = n["length"], r = "charCodeAt", i = 0; i < t; i++)
        //a[i] = m_(a[i][r](0) ^ n[(i + 10) % e][r](0));
        a[i] = String["fromCharCode"](a[i][r](0) ^ n[(i + 10) % e][r](0));
    return a["join"]("")
}
function getAnalysis (p_str, url, synct) {
    var g = new Date() - 1000 * synct;
    var e = new Date() - g - 1515125653845;
    var S = 1;
    m_0 = v_(p_str);
    m_1 = m_0 + "@#" + url.replace("https://api.qimai.cn", "");
    m_2 = m_1 + "@#" + e;
    m_3 = m_2 + "@#" + S;
    var b = "00000008d78d46a";
    return v_(k_(m_3, b))
}
"""

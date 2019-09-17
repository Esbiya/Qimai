# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 19:11
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : utils.py
# @Software: PyCharm

import hashlib


def encrypt(encrypt_str):
    md5 = hashlib.md5()
    md5.update(encrypt_str.encode())
    return md5.hexdigest()

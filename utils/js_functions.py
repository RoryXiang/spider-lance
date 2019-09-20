#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-09-20 10:11:33
# @Author  : RoryXiang (xiangshangping@lvwan.com)
# @Link    : ${link}
# @Version : $Id$

import execjs

with open("./js/cipher.js", "r", encoding="utf-8")as f:
    str_js = f.read()

func = execjs.compile(str_js)


def get_cipher():
    cipher = func.call("cipher")
    return cipher


def get_token():
    token = func.call("random", "24")
    return token

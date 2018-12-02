# -*- coding: utf-8 -*-

from requests import post
from booker.consts import urls


# verifying captcha
def verify_captcha_auto(captcha_img_path):
    url = urls['punch_captcha']
    files = {'file': open(captcha_img_path, 'rb')}
    res = post(url, files=files)
    items = res.text.split('<B>')[1].split('<')[0].split(' ')
    return ','.join([str(i) for i in map_items(items)])

# map items, for example: '5' --> (2, 1) --> (105, 35)
def map_items(items):
    cors = []
    for item in items:
        item = int(item)
        m, d = item%4, item//4
        x = 4 if m == 0 else m
        y = d if m == 0 else d + 1
        cors = cors + [(p-1)*70 + 35 for p in [x, y]]
    return cors

# verify captcha by hand .. 对深度学习还不熟悉, 想哭
def verify_captcha():
    nums = input('captcha id: ')
    items = nums.split(',')
    return ','.join([str(i) for i in map_items(items)])


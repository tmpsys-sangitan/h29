# coding: UTF-8
#
# FILE        :utility.py
# DATE        :2018.01.18
# DESCRIPTION :汎用関数
# NAME        :Hikaru Yoshida
#

from datetime import datetime as dt         # datatime型

def str2dt(string):
    """ yyyymmddHHMMSS(20180118113940)を日時型に変換する
        @string 日時文字列
    """
    try:
        return dt.strptime(string, '%Y%m%d%H%M%S')
    except:
        return None

def dt2str(date):
    """ 日時型をyyyy/mm/dd HH:MM:SS +TIMEZONE
        (2018/01/18 11:39:40 +0900)に変換する
        @string 日時文字列
    """
    try:
        return date.strftime('%Y/%m/%d %H:%M:%S') + " +0900"
    except:
        return None

def d2str(date):
    """ 日時型をyyyymmdd(20180118)に変換する
        @string 日時文字列
    """
    try:
        return date.strftime('%Y%m%d')
    except:
        return None

def ascii_encode_dict(data):
    """ jsonがunicodeにcastされないようにする
        例: json.load(f, object_hook=ascii_encode_dict)
    """
    ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
    return dict(map(ascii_encode, pair) for pair in data.items())


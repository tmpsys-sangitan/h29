# coding: UTF-8
#
# FILE        :utility.py
# DATE        :2018.01.18
# DESCRIPTION :汎用関数
# NAME        :Hikaru Yoshida
#

from datetime import datetime as dt         # datatime型
import json                                 # JSONファイル操作
from json import encoder                    # JSONエンコーダ

# 浮動小数点の出力を小数第一位までに制限
encoder.FLOAT_REPR = lambda o: format(o, '.1f')

def str2dt(string):
    """ yyyymmddHHMMSS(20180118113940)を日時型に変換する
        @string 日時文字列
    """
    try:
        return dt.strptime(string, '%Y%m%d%H%M%S')
    except ValueError:
        return None

def gen_jsdatatime(date):
    """ 日時型をDate(yyyy, mm, dd, HH, MM, SS)に変換する
        @string 日時文字列
    """
    try:
        jsmonth = str(date.month - 1)
        jsdt = date.strftime('Date(%Y, ') + jsmonth + date.strftime(', %d, %H, %M, %S)')
        return jsdt
    except ValueError:
        return None

def dt2str(date):
    """ 日時型をyyyy/mm/dd HH:MM:SS +TIMEZONE
        (2018/01/18 11:39:40 +0900)に変換する
        @string 日時文字列
    """
    try:
        return date.strftime('%Y/%m/%d %H:%M:%S') + " +0900"
    except ValueError:
        return None

def d2str(date):
    """ 日時型をyyyymmdd(20180118)に変換する
        @string 日時文字列
    """
    try:
        return date.strftime('%Y%m%d')
    except ValueError:
        return None

def t2str(date):
    """ 日時型をHHMM(1139)に変換する
        @string 日時文字列
    """
    try:
        return date.strftime('%H%M')
    except ValueError:
        return None

def ascii_encode_dict(data):
    """ jsonがunicode(u'unicode型')にcastされないようにする
        例: json.load(f, object_hook=ascii_encode_dict)
    """
    ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
    return dict(map(ascii_encode, pair) for pair in data.items())

def load_json(jsondata, charset="ascii"):
    """ JSONの読み込み
    """
    if charset == "ascii":
        return json.loads(jsondata, object_hook=ascii_encode_dict)
    else:
        return json.loads(jsondata)

def dump_json(dicdata):
    """ JSONの出力
    """
    return json.dumps(dicdata, sort_keys=True, ensure_ascii=False)

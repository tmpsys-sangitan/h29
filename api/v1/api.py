# coding: UTF-8

"""
FILE        :api.py
DATE        :2017.12.04
DESCRIPTION :バックエンドプログラム
NAME        :Hikaru Yoshida
"""

from datetime import datetime as dt         # datatime型
from datetime import timedelta      # 相対時間型

import graph    # グラフデータモジュール
import diary    # 日誌管理モジュール
import utility  # 汎用関数

def getPeriods():
    """ 期間一覧
    """
    return graph.Periods().get()

def getTags():
    """ タグ一覧
    """
    return graph.Tags().get()

def getKinds():
    """ データ種類一覧
    """
    return graph.Kinds().get()

def addDiary(datestr, devid, data):
    """ データの追加
    """
    # 日時の変換に失敗したら、現在日時を代入する
    date = utility.str2dt(datestr)
    if date is None:
        # 世界標準時 + 9時間 ＝ 日本標準時
        date = dt.now() + timedelta(hours=9)
    diary.Diary(date).add(date, devid, data)

def updateDiary():
    """ 日誌の更新
    """
    diary.Diary(dt.now()).storage.write()

def getGraph(handler, date, tag, kind):
    """ グラフを返す
    """
    if tag == '':
            tag = None

    # JSONを返却
    resjson = graph.gen_dayly(date, tag, kind)

    if resjson is not None:
        handler.response.headers['cache-control'] = 'public, max-age=3600'
        handler.response.headers['content-type'] = 'application/javascript; charset=utf-8'
        handler.response.out.write(
            "%s(%s)" %
            ('callback', resjson)
        )
    else:
        handler.error(404)

def getLatest(handler, kind):
    """ 各mapiの最新温度データを返す
    """
    handler.response.headers['cache-control'] = 'public, max-age=60'
    handler.response.headers['content-type'] = 'application/javascript; charset=utf-8'
    handler.response.out.write(
        "%s(%s)" %
        ('callback', utility.dump_json(diary.Latest(kind).get()))
    )

# coding: UTF-8

'''
# FILE        :graph.py
# DATE        :2018.01.25
# DESCRIPTION :グラフデータモジュール
# NAME        :Hikaru Yoshida
'''

from datetime import datetime as dt  # datatime型
from datetime import timedelta      # 相対時間型
from google.appengine.api import memcache   # Memcache API
from google.appengine.ext import ndb        # Datastore API
import datetime  # datatime
import logging                              # ログ出力

import model                # データモデル
import diary                # 日誌管理モジュール
import sensor               # センサ管理
import utility              # 汎用関数


def gen_dayly(date, tag, kind):
    """日間グラフを描画するJSONを生成する

    Arguments:
        date {[datatime]} -- 日付を指定
        tag {[string]} -- 場所を指定

    Returns:
        json -- 日間グラフ描画用のjsonを発行
    """

    # JSONの生成
    graph_json = {
        "cols": gen_cols(tag),
        "rows": gen_rows(utility.str2dt(date), tag, kind)
    }

    # 出力
    return utility.dump_json(graph_json)


def gen_cols(tag):
    """グラフを描画するJSONのヘッタを生成する

    Arguments:
        tag string list -- タグ

    Returns:
        dicstionary list -- ヘッタ部分の辞書リスト
    """

    # 雛形の定義
    cols = [{
        'type': "datetime"
    }]

    # sensorsのデータを追加
    append = cols.append  # 参照を事前に読み込むことで高速化
    for label in sensor.get_list_label(tag):
        append({
            'label': label,
            'type': "number"
        })

    # 生成したヘッタを返す
    return cols


def gen_rows(date, tag, kind):
    """グラフを描画するJSONの1日分のボディを生成する

    Arguments:
        date {[datatime]} -- 日付
        tag {[string]} -- 絞込タグ
        kind {[string]} -- 表示データ

    Returns:
        dicstionary list -- 1日分のボディ部分の辞書リスト
    """

    # 空のボディを作成
    rows = []
    rows_append = rows.append  # 参照を事前に読み込むことで高速化

    # 必要な日誌を読み込みリストに登録
    open_diarys = []
    diarys_append = open_diarys.append  # 参照を事前に読み込むことで高速化
    for devid in sensor.get_list_devid(tag):
        jsondata = diary.diary.get(date, devid)
        diarys_append(jsondata)

    # 引数の日付の00:00~23:59まで1分間隔
    time = dt.combine(date, datetime.time.min)
    while time < dt.combine(date, datetime.time.max):
        # 横軸の入力
        new_line = [{
            'v': utility.gen_jsdatatime(time)
        }]

        # 縦軸の入力
        new_line_append = new_line.append  # 参照を事前に読み込むことで高速化
        for open_diary in open_diarys:
            try:
                new_line_append({
                    'v': open_diary[utility.t2str(time)][kind]
                })
            except KeyError:
                new_line_append({
                    'v': None
                })

        # ボディの末端に追加
        rows_append({
            'c': new_line
        })

        # 1分進める
        time = time + timedelta(minutes=1)

    # 生成したボディを返す
    return rows



class Periods(model.Datastore):
    """ Datastore 期間のデータ
    """

    @classmethod
    def get_cache_name(cls):
        """ Memcacheでのキー名
        """
        return "option_periods"

class Tags(model.Datastore):
    """ Datastore タグのデータ
    """

    @classmethod
    def get_cache_name(cls):
        """ Memcacheでのキー名
        """
        return "option_tags"

class Kinds(model.Datastore):
    """ Datastore 種類のデータ
    """

    @classmethod
    def get_cache_name(cls):
        """ Memcacheでのキー名
        """
        return "option_types"

def gen_taglist():
    """ 指定された種類のセンサのリストを返す

    Returns:
        list -- tag、表示名のリスト
    """
    return Tags.get()

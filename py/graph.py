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

from py import diary                # 日誌管理モジュール
from py import sensor               # センサ管理
from py import utility              # 汎用関数


def gen_dayly(date, sensor_type, tag):
    """日間グラフを描画するJSONを生成する

    Arguments:
        date {[datatime]} -- 日付を指定
        tag {[string]} -- 場所を指定

    Returns:
        json -- 日間グラフ描画用のjsonを発行
    """

    # JSONの生成
    graph_json = {
        "cols": gen_cols(sensor.get_list_label(sensor_type, tag)),
        "rows": gen_rows(utility.str2dt(date), sensor.get_list_devid(sensor_type, tag))
    }

    # 出力
    return utility.dump_json(graph_json)


def gen_cols(labels):
    """グラフを描画するJSONのヘッタを生成する

    Arguments:
        labels string list -- データラベル名のリスト

    Returns:
        dicstionary list -- ヘッタ部分の辞書リスト
    """

    # 雛形の定義
    cols = [{
        'type': "datetime"
    }]

    # sensorsのデータを追加
    append = cols.append  # 参照を事前に読み込むことで高速化
    for label in labels:
        append({
            'label': label,
            'type': "number"
        })

    # 生成したヘッタを返す
    return cols


def gen_rows(date, devids):
    """グラフを描画するJSONの1日分のボディを生成する

    Arguments:
        date {[datatime]} -- 日付

    Keyword Arguments:
        devids {[type]} -- [description] (default: {None})

    Returns:
        dicstionary list -- 1日分のボディ部分の辞書リスト
    """

    # 空のボディを作成
    rows = []
    rows_append = rows.append  # 参照を事前に読み込むことで高速化

    # 必要な日誌を読み込みリストに登録
    open_diarys = []
    diarys_append = open_diarys.append  # 参照を事前に読み込むことで高速化
    for devid in devids:
        diarys_append(utility.load_json(diary.read(date, devid)))

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
            new_line_append({
                'v': open_diary[utility.t2str(time)]['val']
            })

        # ボディの末端に追加
        rows_append({
            'c': new_line
        })

        # 1分進める
        time = time + timedelta(minutes=1)

    # 生成したボディを返す
    return rows



class Datastore(ndb.Model):
    """[summary]
    """

    # Memcacheでのキー名
    cache_name = ""

    @classmethod
    def get(cls):
        """ データの取得
        """
        res = cls.get_cache()
        if res is None:
            res = cls.edit_datastore(cls.get_datastore())
            cls.set_cache(res)
        return res

    @classmethod
    def set_cache(cls, data):
        memcache.add(cls.cache_name, utility.dump_json(data))

    @classmethod
    def get_cache(cls):
        """ キャッシュからデータを取得

        Returns:
            listdic -- データ
        """
        # キャッシュからタグ一覧を取得
        data = memcache.get(cls.cache_name)

        # ヒットしたら変換
        if data is not None:
            data = utility.load_json(data, charset="ascii")

        return data

    @classmethod
    def get_datastore(cls):
        """ データストアからデータを取得

        Returns:
            listdic -- データ
        """
        return cls.query().fetch(keys_only=True)

    @classmethod
    def edit_datastore(cls, keys):
        res = []
        append = res.append   # 参照を事前に読み込むことで高速化
        for key in keys:
            append({
                "value" : key.string_id().split("_")[0],
                "name" : key.string_id().split("_")[1]
            })
        return res



class Periods(Datastore):
    """ Datastore 期間のデータ
    """

    # Memcacheでのキー名
    cache_name = "option_periods"


class Tags(Datastore):
    """ Datastore タグのデータ
    """

    # Memcacheでのキー名
    cache_name = "option_tags"

class Types(Datastore):
    """ Datastore 種類のデータ
    """

    # Memcacheでのキー名
    cache_name = "option_types"

def gen_taglist():
    """ 指定された種類のセンサのリストを返す

    Returns:
        list -- tag、表示名のリスト
    """
    return Tags.get()

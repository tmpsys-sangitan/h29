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


class Graph(object):
    """ グラフ生成クラス
    """

    def __init__(self, date, period, tag, kind):
        """ グラフの設定

        Arguments:
            date   {datetime} -- 日付
            period {int}      -- 期間
            tag    {string}   -- タグ
            kind   {string}   -- データ種類
        """
        self.date = date
        self.period = period - 1
        self.tag = tag
        self.kind = kind
        self.cols = GraphCols(tag)
        self.rows = GraphRows(date, tag, kind)

    def get(self):
        """ グラフJSONを生成する
        """
        graph_json = {
            "cols": self.cols.get(),
            "rows": self.rows.get(),
        }
        return utility.dump_json(graph_json)

class GraphCols(object):
    """ [summary]
    """
    def __init__(self, tag):
        """ タグからキャッシュ名を生成する

        Arguments:
            tag {string} -- タグ
        """
        self.tag = tag
        if self.tag is None:
            self.cache = model.Cache("graph_cols", charset="unicode")
        else:
            self.cache = model.Cache("graph_cols_" + self.tag, charset="unicode")

    def edit(self):
        """ Colsを生成する
        """
        cols = [{
            'type': "datetime"
        }]
        append = cols.append  # 参照を事前に読み込むことで高速化
        for label in sensor.get_list_label(self.tag):
            append({
                'label': label,
                'type': "number"
            })
        return cols

    def get(self):
        """ キャッシュまたは生成したColsを返す
        """
        cols = self.cache.get()
        if not bool(cols):
            cols = self.edit()
            self.cache.add(cols)
        return cols

class GraphRows(object):
    """ [summary]
    """
    def __init__(self, date, tag, kind):
        """ タグからキャッシュ名を生成する

        Arguments:
            date {[type]} -- [description]
            tag  {string} -- タグ
            kind {[type]} -- [description]
        """
        self.date = date
        self.tag = tag
        self.kind = kind
        if date != dt.now() + timedelta(hours=9):
            if tag is not None:
                self.cache = model.Cache('_'.join(["graph_rows", utility.d2str(date), tag, kind]))
            else:
                self.cache = model.Cache('_'.join(["graph_rows", utility.d2str(date), '_', kind]))

    def edit(self):
        """グラフを描画するJSONの1日分のボディを生成する

        Arguments:
            date {[datatime]} -- 日付

        Returns:
            dicstionary list -- 1日分のボディ部分の辞書リスト
        """

        # 空のボディを作成
        rows = []
        rows_append = rows.append  # 参照を事前に読み込むことで高速化

        # 必要な日誌を読み込みリストに登録
        open_diarys = []
        diarys_append = open_diarys.append  # 参照を事前に読み込むことで高速化
        for devid in sensor.get_list_devid(self.tag):
            jsondata = diary.Diary(self.date).get(self.date, devid)
            diarys_append(jsondata)

        # 引数の日付の00:00~23:59まで1分間隔
        time = dt.combine(self.date, datetime.time.min)
        while time < dt.combine(self.date, datetime.time.max):
            # 横軸の入力
            new_line = [{
                'v': utility.gen_jsdatatime(time)
            }]

            # 縦軸の入力
            new_line_append = new_line.append  # 参照を事前に読み込むことで高速化
            for open_diary in open_diarys:
                try:
                    new_line_append({
                        'v': open_diary[utility.t2str(time)][self.kind]
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

    def get(self):
        """ キャッシュまたは生成したColsを返す
        """
        if self.cache is not None:
            rows = self.cache.get()
        if not bool(rows):
            rows = self.edit()
            self.cache.add(rows)
        return rows


class Periods(model.Datastore):
    """ 期間
    """

    def __init__(self):
        """ 初期化
        """
        super(Periods, self).__init__("option_periods")


class Tags(model.Datastore):
    """ タグ
    """

    def __init__(self):
        """ 初期化
        """
        super(Tags, self).__init__("option_tags")


class Kinds(model.Datastore):
    """ データ種類
    """

    def __init__(self):
        """ 初期化
        """
        super(Kinds, self).__init__("option_types")

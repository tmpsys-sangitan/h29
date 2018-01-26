# coding: UTF-8
#
# FILE        :graph.py
# DATE        :2018.01.25
# DESCRIPTION :グラフデータモジュール
# NAME        :Hikaru Yoshida
#

from datetime import datetime as dt # datatime型
from datetime import timedelta      # 相対時間型
import datetime # datatime

from py import sensor               # センサ管理
from py import utility              # 汎用関数



def gen_dayly(sensors=None):
    """日間グラフを描画するJSONを生成する

    Keyword Arguments:
        sensors string -- mapidのリスト Noneなら全て (default: {None})
    """

    # JSONの生成
    graph_json = {
        "cols": gen_cols(sensor.get_list_label("temp")),
        "rows": gen_rows(utility.str2dt("20171122000000"))
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
    cols = [
            {
                'type': "datetime"
            }
    ]

    # sensorsのデータを追加
    append=cols.append  # 参照を事前に読み込むことで高速化
    for label in labels:
        append({
            'label': label,
            'type': "number"
        })

    # 生成したヘッタを返す
    return cols



def gen_rows(date, sensors=None):
    """グラフを描画するJSONの1日分のボディを生成する

    Arguments:

    Returns:
        dicstionary list -- 1日分のボディ部分の辞書リスト
    """
    rows = []
    rows_append=rows.append  # 参照を事前に読み込むことで高速化

    # 横軸の入力
    time = dt.combine(date, datetime.time.min)
    while time < dt.combine(date, datetime.time.max):
        rows_append({
            'c': [
                { 'v': utility.dt2date(time) }
            ]
        })
        time = time + timedelta(minutes=1)

    # 生成したボディを返す
    return None

# coding: UTF-8
#
# FILE        :graph.py
# DATE        :2018.01.25
# DESCRIPTION :グラフデータモジュール
# NAME        :Hikaru Yoshida
#

from py import sensor   # センサ管理
from py import utility  # 汎用関数



def gen_dayly(sensors=None):
    """日間グラフを描画するJSONを生成する

    Keyword Arguments:
        sensors string -- mapidのリスト Noneなら全て (default: {None})
    """

    # JSONの生成
    graph_json = {
        "cols": gen_cols(sensor.get_list_label("temp")),
        "rows": gen_rows()
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
        new_cols = {
            'label': label,
            'type': "number"
        }
        append(new_cols)

    # 生成したヘッタを返す
    return cols



def gen_rows():
    """グラフを描画するJSONの1日分のボディを生成する

    Arguments:

    Returns:
        dicstionary list -- 1日分のボディ部分の辞書リスト
    """

    # 生成したボディを返す
    return None

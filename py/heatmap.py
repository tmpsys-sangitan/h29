# coding: UTF-8

'''
# FILE        :heatmap.py
# DATE        :2018.02.01
# DESCRIPTION :マップデータモジュール
# NAME        :Hikaru Yoshida
'''

import random           # 乱数

from py import sensor   # センサ管理
from py import utility  # 汎用関数

def get_latest(sensor_type):
    """[指定されたマップidの最新温度データを返す]

    Arguments:
        mapids {[string]} -- マップidの配列
    """
    # 辞書の生成
    res_dic = {}

    # マップIDごとの配列生成
    for mapid in sensor.get_list_mapid(sensor_type):
        res_dic[mapid] = round(random.uniform(10.0, 35.0), 1)

    # JSONに変換して出力
    return utility.dump_json(res_dic)

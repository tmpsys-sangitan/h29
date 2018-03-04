# coding: UTF-8

'''
# FILE        :sensor.py
# DATE        :2018.01.17
# DESCRIPTION :センサ管理
# NAME        :Hikaru Yoshida
'''

from google.appengine.api import memcache   # Memcache API
from google.appengine.ext import ndb        # Datastore API
import logging                              # ログ出力

import model                        # データモデル
import utility                      # 汎用関数

class Sensor(model.Datastore):
    """ センサーリスト
    """
    # センサ種類
    tags = ndb.StringProperty(repeated=True)

    def __init__(self, tag=None):
        """ タグの指定

        Keyword Arguments:
            tag {string} -- 絞り込み用のタグを指定 (default: None)
        """
        if tag is not None:
            super(Sensor, self).__init__("sensor_" + tag)
        else:
            super(Sensor, self).__init__("sensor")
        self.tag = tag

    def read(self):
        """ データストアからデータを取得

        Arguments:
            tag {[type]} -- タグによる絞り込み

        Returns:
            string list -- 取得したキーのリスト
        """
        sensor_query = Sensor.query()
        if self.tag != None:
            sensor_query = sensor_query.filter(Sensor.tags == self.tag)
        return sensor_query.fetch(keys_only=True)

    def edit(self, keys):
        """ データストアから取得したデータをJSONに変換する
            @keys   データストアから取得したデータ
        """
        sensor_list = []
        append = sensor_list.append   # 参照を事前に読み込むことで高速化
        for key in keys:

            # 辞書に追加
            append({
                "mapid" : key.string_id().split("_")[0],
                "devid" : key.string_id().split("_")[1],
                "label" : key.string_id().split("_")[2]
            })
        return sensor_list



def get_list_mapid(tag=None):
    """マップIDのリストを返す

    Arguments:
        tag {string} -- タグによる絞り込み

    Returns:
        string -- マップID
    """
    # センサID辞書の取得
    sensor_list = Sensor(tag).get()

    # リストの検索
    results = [x['mapid'] for x in sensor_list]

    return results



def get_list_devid(tag=None):
    """機器IDのリストを返す

    Arguments:
        tag {string} -- タグによる絞り込み

    Returns:
        string -- 機器ID
    """
    # センサID辞書の取得
    sensor_list = Sensor(tag).get()

    # リストの検索
    results = [x['devid'] for x in sensor_list]

    return results



def get_list_label(tag=None):
    """表示名のリストを返す

    Returns:
        string -- 表示名のリスト
        tag {string} -- タグによる絞り込み
    """
    # センサID辞書の取得
    sensor_list = Sensor(tag).get()

    # リストの検索
    results = [x['label'] for x in sensor_list]

    return results



def get_mapid(devid):
    """機器IDから対応するマップIDを返す

    Arguments:
        mapid {string} -- 機器ID

    Returns:
        string -- マップIDまたはNone
    """
    # リストの取得
    sensor_list = Sensor().get()

    # リストの検索
    results = [x['mapid'] for x in sensor_list if x['devid'] == devid]

    # 最初にヒットした機器IDを返す
    result = results[0] if len(results) else None

    return result




def get_devid(mapid):
    """マップIDから対応する機器IDを返す

    Arguments:
        mapid {string} -- マップID

    Returns:
        string -- 機器IDまたはNone
    """
    # リストの取得
    sensor_list = Sensor().get()

    # リストの検索
    results = [x['devid'] for x in sensor_list if x['mapid'] == mapid]

    # 最初にヒットした機器IDを返す
    result = results[0] if len(results) else None

    return result

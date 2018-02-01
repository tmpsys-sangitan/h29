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

from py import utility                      # 汎用関数



class Sensor(ndb.Model):
    """ Datastore 種類センサのデータ
    """

    # センサ種類
    sensor_type = ndb.StringProperty()



def get_list(sensor_type):
    """ 指定された種類のセンサのリストを返す

    Arguments:
        sensor_type  {string} -- 種類

    Returns:
        list -- マップID、機器ID、表示名のリスト
    """
    # キャッシュからリストの取得
    sensor_json = memcache.get("sensor_" + sensor_type)

    # キャッシュ ミス
    if sensor_json is None:
        # データストアからリストの取得
        sensor_keys = Sensor.query(Sensor.sensor_type == sensor_type).fetch(keys_only=True)

        # 辞書の生成
        sensor_list = []
        append = sensor_list.append   # 参照を事前に読み込むことで高速化
        for skey in sensor_keys:

            # 辞書に追加
            append({
                "mapid" : skey.string_id().split("_")[0],
                "devid" : skey.string_id().split("_")[1],
                "label" : skey.string_id().split("_")[2]
            })

        # JSONに変換してキャッシュに保存
        memcache.add("sensor_" + sensor_type, utility.dump_json(sensor_list))
        logging.debug("SENSOR GET_LIST : READ FROM CLOUD STORAGE")

    # キャッシュ ヒット
    else:
        # JSONを読み込み
        sensor_list = utility.load_json(sensor_json, charset="ascii")
        logging.debug("SENSOR GET_LIST : READ FROM MEMCACHE")

    return sensor_list



def get_list_mapid(sensor_type):
    """指定された種類のマップIDのリストを返す

    Arguments:
        sensor_type  {string} -- 種類

    Returns:
        string -- マップID
    """
    # センサID辞書の取得
    sensor_list = get_list(sensor_type)

    # リストの検索
    results = [x['mapid'] for x in sensor_list]

    return results



def get_list_devid(sensor_type):
    """指定された種類の機器IDのリストを返す

    Arguments:
        sensor_type  {string} -- 種類

    Returns:
        string -- 機器ID
    """
    # センサID辞書の取得
    sensor_list = get_list(sensor_type)

    # リストの検索
    results = [x['devid'] for x in sensor_list]

    return results



def get_list_label(sensor_type):
    """表示名のリストを返す

    Returns:
        string -- 表示名のリスト
    """
    # センサID辞書の取得
    sensor_list = get_list(sensor_type)

    # リストの検索
    results = [x['label'] for x in sensor_list]

    return results



def get_devid(mapid, sensor_type):
    """マップIDと種類から対応する機器IDを返す

    Arguments:
        mapid {string} -- マップID
        sensor_type  {string} -- 種類

    Returns:
        string -- 機器IDまたはNone
    """
    # リストの取得
    sensor_list = get_list(sensor_type)

    # リストの検索
    results = [x['devid'] for x in sensor_list if x['mapid'] == mapid]

    # 最初にヒットした機器IDを返す
    result = results[0] if len(results) else None

    return result

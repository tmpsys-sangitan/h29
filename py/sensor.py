# coding: UTF-8
#
# FILE        :sensor.py
# DATE        :2018.01.17
# DESCRIPTION :センサ管理
# NAME        :Hikaru Yoshida
#

from google.appengine.api import memcache   # Memcache API
from google.appengine.ext import ndb        # Datastore API
import logging                              # ログ出力

from py import utility                      # 汎用関数



# Datastoreでの種類とプロパティ定義
class sensor(ndb.Model):
    """ データストア：種類センサのデータ
    """

    # センサ種類
    type = ndb.StringProperty()



def get_list(type):
    """ 指定された種類のセンサのリストを返す

    Arguments:
        type  {string} -- 種類

    Returns:
        list -- マップID、機器ID、表示名のリスト
    """
    # キャッシュからリストの取得
    sensor_json = memcache.get("sensor_" + type)
    if sensor_json is None:
        # データストアからリストの取得
        sensor_keys = sensor.query(sensor.type == type).fetch(keys_only=True)

        # 辞書の生成
        sensor_list = []
        for skey in sensor_keys:

            # 辞書に追加
            sensor_list.append({
                "mapid" : skey.string_id().split("_")[0]
                "devid" : skey.string_id().split("_")[1]
                "label" : skey.string_id().split("_")[2]
            })

        # JSONに変換してキャッシュに保存
        memcache.add("sensor_" + type, utility.dump_json(sensor_list))
        logging.debug("SENSOR GET_LIST : READ FROM CLOUD STORAGE")

    else:
        # JSONを読み込み
        sensor_list = utility.load_json(sensor_json)
        logging.debug("SENSOR GET_LIST : READ FROM MEMCACHE")

    return sensor_list



def get_list_devid(type):
    """指定された種類の機器IDのリストを返す

    Arguments:
        mapid {string} -- マップID
        type  {string} -- 種類

    Returns:
        string -- 機器ID
    """
    # センサID辞書の取得
    sensor_list = get_list(type)

    # リストの検索
    results = [x['devid'] for x in sensor_list]

    return results



def get_devid(mapid, type):
    """マップIDと種類から対応する機器IDを返す

    Arguments:
        mapid {string} -- マップID
        type  {string} -- 種類

    Returns:
        string -- 機器IDまたはNone
    """
    # リストの取得
    sensor_list = get_list(type)

    # リストの検索
    results = [x['devid'] for x in sensor_list if x['mapid'] == mapid]

    # 最初にヒットした機器IDを返す
    result = results[0] if len(results) else None

    return result

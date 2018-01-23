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



def get_sdic(type):
    """ 指定された種類のセンサをリストアップする
        @type 種類
    """
    # キャッシュからリストの取得
    sjson = memcache.get("sensor_" + type)
    if sjson is None:
        # データストアからリストの取得
        skeys = sensor.query(sensor.type == type).fetch(keys_only=True)

        # 辞書の生成
        sdic = {}
        for skey in skeys:
            # マップIDと機器ID
            mapid = skey.string_id().split("_")[0]
            devid = skey.string_id().split("_")[1]

            # 辞書に追加
            sdic[mapid] = devid

        # JSONに変換してキャッシュに保存
        memcache.add("sensor_" + type, utility.dump_json(sdic))
        logging.debug("SENSOR GET_SDIC : READ FROM CLOUD STORAGE")

    else:
        # JSONを読み込み
        sdic = utility.load_json(sjson)
        logging.debug("SENSOR GET_SDIC : READ FROM MEMCACHE")

    return sdic



def get_devid(mapid, type):
    """ 指定された種類のセンサをリストアップする
        @type 種類
    """
    # センサID辞書の取得
    sdic = get_sdic(type)

    # 辞書からmapidに対応するdevidを取り出し
    try:
        devid = sdic[mapid]
    except:
        devid = None

    return devid

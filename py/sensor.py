# coding: UTF-8
#
# FILE        :sensor.py
# DATE        :2018.01.17
# DESCRIPTION :センサ管理
# NAME        :Hikaru Yoshida
#

from google.appengine.api import memcache   # Memcache API
from google.appengine.ext import ndb        # Datastore API

# Datastoreでの種類とプロパティ定義
class sensor(ndb.Model):
    """ センサデータ
    """

    # センサ種類
    type = ndb.StringProperty()

    @staticmethod
    def get_sdic(type):
        """ 指定された種類のセンサをリストアップする
            @type 種類
        """
        # キャッシュからリストの取得
        skeys = memcache.get("sensor_" + type)
        if skeys is None:
            # データストアからリストの取得
            skeys = sensor.query(sensor.type == type).fetch(keys_only=True)
            memcache.add("sensor_" + type, nkeys)

        # 辞書の生成
        sdic = {}
        for nkey in nkeys:
            try:
                # マップIDと機器ID
                mapid = nkey.split("_")[0]
                devid = nkey.split("_")[1]

                # 辞書に追加
                sdic[mapid] = devid

            except:
                pass

        return sdic

    @staticmethod
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

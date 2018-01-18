# coding: UTF-8
#
# FILE        :sensor.py
# DATE        :2018.01.17
# DESCRIPTION :センサーモジュール
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
    def get_slist(type):
        """ 指定された種類のセンサをリストアップする
            @type 日付
        """
        # キャッシュからリストの取得
        nkeys = memcache.get("sensor_" + type)
        if nkeys is None:
            # ストレージからリストの取得
            nkeys = sensor.query(sensor.type == type).fetch(keys_only=True)
            memcache.add("sensor_" + type, nkeys)

        # 辞書リストの生成
        nlist = []
        for nkey in nkeys:
            try:
                # 文字列を区切って辞書の作成
                ndic = {
                    "devid": nkey.split("_")[0],
                    "mapid": nkey.split("_")[1],
                    "name" : nkey.split("_")[2]
                }

                # リストに辞書を追加
                nlist.append(ndic)

            except:
                pass

        return nlist

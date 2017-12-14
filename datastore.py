# coding: UTF-8
#
# FILE        :datastore.py
# DATE        :2017.12.04
# DESCRIPTION :メインプログラム
# NAME        :Hikaru Yoshida
#

from google.appengine.ext import ndb        # Datastore API
from google.appengine.api import memcache   # Memcache API

# Nameのプロパティ定義
class Name(ndb.Model):
    # リモートID
    id   = ndb.StringProperty()
    # 名称
    name = ndb.StringProperty()
    # データ種別
    type = ndb.StringProperty()

    # Nameデータ取得
    @staticmethod
    def get():
        names = memcache.get("name_table")
        if names is None:
            names = Name.query(Name.type == 'temp').fetch()
            memcache.add("name_table", names)
        return names

# Dataのプロパティ定義
class Data(ndb.Model):
    # 日付 & 時間
    date = ndb.DateTimeProperty(auto_now_add=True)
    # リモートID
    id   = ndb.StringProperty()
    # 電波状況
    q    = ndb.IntegerProperty()
    # 電源電圧
    vol  = ndb.IntegerProperty()
    # 測定値
    val  = ndb.FloatProperty(required=True)
    # A/D値
    ad   = ndb.IntegerProperty()

    # 取得
    @staticmethod
    def get(id, date):
        return Data.query(Data.id == id, Data.date > date, Data.date < (date + timedelta(days=1))).order(Data.date).fetch()

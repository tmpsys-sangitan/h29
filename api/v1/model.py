# coding: UTF-8

'''
# FILE        :model.py
# DATE        :2018.02.14
# DESCRIPTION :データモデル
# NAME        :Hikaru Yoshida
'''

from google.appengine.api import app_identity   # アプリケーション ID
from google.appengine.api import memcache       # Memcache API
from google.appengine.ext import ndb            # Datastore API
import cloudstorage as storage                  # Cloud Storage API
import logging                                  # ログ出力
import os                                       # OS

import utility              # 汎用関数

class Datastore(ndb.Model):
    """ データストアの汎用モデル
    """

    @classmethod
    def get_cache_name(cls):
        """ Memcacheでのキー名
        """
        raise NotImplementedError

    @classmethod
    def get(cls):
        """ データの取得
        """
        res = cls.get_cache()
        if res is None:
            logging.debug(cls.get_cache_name() + "MISS")
            res = cls.edit_datastore(cls.get_datastore())
            cls.set_cache(res)
            res = cls.get_cache()
        return res

    @classmethod
    def set_cache(cls, data):
        """ キャッシュへデータを格納
        """
        memcache.add(cls.get_cache_name(), utility.dump_json(data))

    @classmethod
    def get_cache(cls):
        """ キャッシュからデータを取得
        """
        data = memcache.get(cls.get_cache_name())
        if data is not None:
            data = utility.load_json(data, charset="ascii")
        return data

    @classmethod
    def get_datastore(cls):
        """ データストアからデータを取得
        """
        return cls.query().fetch(keys_only=True)

    @classmethod
    def edit_datastore(cls, keys):
        """ データストアから取得したデータをJSONに変換する
        """
        res = []
        append = res.append   # 参照を事前に読み込むことで高速化
        for key in keys:
            append({
                "value" : key.string_id().split("_")[0],
                "name" : key.string_id().split("_")[1]
            })
        return res

class Cache:

    def get_cache_name(self):
        """ Memcacheでのキー名
        """
        raise NotImplementedError

    def get(self):
        """ キャッシュからJSONを読み込む

        Returns:
            dictionary -- 読み込んだ辞書
        """
        data = memcache.get(self.get_cache_name())
        if data is not None:
            data = utility.load_json(data, charset="ascii")
        else:
            data = {}
        return data

    def set(self, data):
        """ 辞書型をJSONに変換し、キャッシュに保存する

        Arguments:
            data {dictionary} -- 保存したい辞書
        """
        if not memcache.set(self.get_cache_name(), utility.dump_json(data)):
            logging.error(self.get_cache_name() + " Memcache set failed")

# GCSタイムアウト設定
RETRY_PARAMS = storage.RetryParams(
    initial_delay=0.2,
    max_delay=5.0,
    backoff_factor=2,
    max_retry_period=15)
storage.set_default_retry_params(RETRY_PARAMS)

class Storage:

    @classmethod
    def get(cls):
        """ データの取得
        """
        raise NotImplementedError

    @classmethod
    def set_cache(cls, data):
        """ キャッシュへデータを格納
        """
        raise NotImplementedError

    @classmethod
    def get_cache(cls):
        """ キャッシュからデータを取得
        """
        raise NotImplementedError

    @classmethod
    def get_storage(cls):
        """ ストレージからデータを取得
        """
        raise NotImplementedError

    @classmethod
    def edit_storage(cls, datas):
        """ ストレージから取得したデータをJSONに変換する
        """
        raise NotImplementedError

    @staticmethod
    def get_bucket_name():
        """ バケット名を返す
        """
        return os.environ.get(
            'BUCKET_NAME',
            app_identity.get_default_gcs_bucket_name())

    @staticmethod
    def write_file(filename, content, content_type):
        """ GCSにファイル保存
            @filneame       ファイル名
            @content        内容
            @content_type   ファイルの種別
                            テキストなら'text/plain'
        """
        bucket_name = Storage.get_bucket_name()
        filepath = '/' + bucket_name + '/' + filename
        with storage.open(filepath, 'w', content_type=content_type) as gcs_file:
            gcs_file.write(content.encode('utf-8'))

    @staticmethod
    def read_file(filename):
        """ GCSからファイルを読み込み
            @filneame       ファイル名
        """
        bucket_name = Storage.get_bucket_name()
        filepath = '/' + bucket_name + '/' + filename
        with storage.open(filepath) as gcs_file:
            return gcs_file.read()

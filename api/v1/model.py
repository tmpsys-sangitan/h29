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

import utility                                  # 汎用関数

class Cache(object):
    """ Memcacheの汎用モデル
    """

    def __init__(self, name, charset='ascii', time=0):
        """ キャッシュの実体化

        Arguments:
            name {string} -- Memcacheのキー
            time {int}    -- キャッシュの有効期限[s]
        """
        self.name = name
        self.charset = charset
        self.time = time

    def get(self):
        """ キャッシュからJSONを読み込む

        Returns:
            dictionary -- 読み込んだ辞書
        """
        data = memcache.get(self.name)
        if data is not None:
            data = utility.load_json(data, charset=self.charset)
            logging.debug("Cache.get() : hit %s", self.name)
        else:
            data = {}
            logging.debug("Cache.get() : miss %s", self.name)
        return data

    def add(self, data):
        """ 辞書型をJSONに変換し、キャッシュに保存する

        Arguments:
            data {dictionary} -- 保存したい辞書
        """
        if not memcache.set(self.name, utility.dump_json(data), self.time):
            logging.error(self.name + " Memcache set failed")
        else:
            logging.debug("Cache.add() : set %s", self.name)


class Datastore(ndb.Model):
    """ データストアの汎用モデル
    """

    def __init__(self, name):
        """ キャッシュ名の指定

        Arguments:
            name {string} -- Memcacheのキー
        """
        self.cache = Cache(name, charset='unicode')

    def read(self):
        """ データストアからデータを取得

        Returns:
            string list -- 取得したキーのリスト
        """
        return self.query().fetch(keys_only=True)

    def edit(self, keys):
        """ データストアから取得したデータを辞書型に変換する

        Arguments:
            keys {string list} -- 取得したキーのリスト

        Returns:
            dictionary -- 編集済みの辞書
        """
        res = []
        append = res.append   # 参照を事前に読み込むことで高速化
        for key in keys:
            append({
                "value" : key.string_id().split("_")[0],
                "name" : key.string_id().split("_")[1]
            })
        return res

    def get(self):
        """ データの取得
        """
        res = self.cache.get()
        if not bool(res):
            logging.debug(self.cache.name + "MISS")
            self.cache.add(self.edit(self.read()))
            res = self.cache.get()
        return res


# GCSタイムアウト設定
RETRY_PARAMS = storage.RetryParams(
    initial_delay=0.2,
    max_delay=5.0,
    backoff_factor=2,
    max_retry_period=15)
storage.set_default_retry_params(RETRY_PARAMS)

class Storage:
    """ Google Cloud Storageの汎用モデル
    """

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

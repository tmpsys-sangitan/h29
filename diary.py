# coding: UTF-8
#
# FILE        :diary.py
# DATE        :2018.01.17
# DESCRIPTION :日誌管理モジュール
# NAME        :Hikaru Yoshida
#

from google.appengine.api import taskqueue  # TaskQueue API
from google.appengine.api import memcache   # Memcache API
from datetime import datetime as dt         # datatime型
import json                                 # jsonファイル操作
import logging                              # ログ出力
import errno
import os

import gcs                                  # GCS操作
import utility                              # 汎用関数

class diary:
    """ 日誌クラス
    """

    @staticmethod
    def keycache(date, devid):
        """ Memcacheキーの生成
        """
        return "data_" + utility.d2str(date) + "_" + devid


    @staticmethod
    def keystr(date):
        """ Storageキーの生成
        """
        return "data_" + utility.d2str(date) + ".json"


    @staticmethod
    def read(date, devid):
        """ 日誌をMemcacheから読み込む
        """

        # Memcacheから日誌データの読み込み
        djson = memcache.get(diary.keycache(date, devid))
        if djson is None:
            # 日誌をStorageから読み込み
            try:
                diary.cache(date)
                djson = memcache.get(diary.keycache(date, devid))
            except:
                raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), diary.keycache(date, devid))

        return djson


    @staticmethod
    def cache(date):
        """ 日誌をStorageから読み込み、Memcacheへ保存する
        """

        # StorageからJSONを読み込み
        sjson = gcs.read_file(diary.keystr(date))

        # jsonを辞書に変換
        dic = json.loads(sjson)

        # jsonを分解し、Memcacheへ保存
        for devid in sensor.get_slist("temp"):
            memcache.add(diary.keycache(data, devid), json.dumps(dic[devid]))


    @staticmethod
    def new(date, devid):
        """ 日誌を新規作成
        """

        # 新規作成するjsonの雛形を作る
        dic = {
            devid : []
        }

        # 辞書をjsonに変換
        njson = json.dumps(dic)

        # Storageにアップロード
        gcs.write_file(diary.keystr(date), njson, "application/json")

        return njson


    @staticmethod
    def add(date, devid, fi, bv, val, ad):
        """ 日誌に新たなデータを仮追加する
            @date  日付
            @devid 機器ID
        """

        try:
            # キャッシュから日誌データの読み込み
            djson = diary.read(date, devid)
        except IOError:
            djson = diary.new(date, devid)

        # jsonを辞書型に変換
        dic = json.loads(djson)

        # 新しいデータを辞書型に変換
        newdata = {
            "date"  : utility.dt2str(date),
            "fi"    : int(fi),
            "bv"    : int(bv),
            "val"   : float(val),
            "ad"    : int(ad)
        }

        # 新しいデータを辞書に追加してjsonに変換
        dic[devid].append(newdata)
        djson = json.dumps(dic)

        # キャッシュ更新
        memcache.delete(diary.keycache(date, devid))
        memcache.add(diary.keycache(date, devid), djson)

        # リクエストを作成
        payload = json.dumps({
            "devid" : devid,
            "date"  : utility.d2str(date),
            "data"  : newdata
        })

        # Storage更新リクエスト送信
        q = taskqueue.Queue('StorageWriteRequestQueue')
        tasks = []
        tasks.append(taskqueue.Task(payload=payload, method='PULL'))
        q.add(tasks)


    @staticmethod
    def write():
        """ 日誌への仮追加を確定し、Storageに書き込む
        """

        # タスクの取得
        q = taskqueue.Queue('StorageWriteRequestQueue')
        tasks = q.lease_tasks(60, 100)

        # タスクが空でないなら
        if bool(tasks):
            # 作業用辞書を生成
            sdics = {}

            # リクエストの消化
            for task in tasks:
                # リクエストを辞書型に変換
                req = json.loads(task.payload)

                # 辞書からJSONを読み込み
                if sdics is not req["date"]:
                    # StorageからJSONを読み込み作業用辞書に追加
                    try:
                        sjson = gcs.read_file(diary.keystr(req["date"]))
                        sdics[req["date"]] = json.loads(sjson)
                    except:
                        logging.warning(os.strerror(errno.ENOENT) + " data_" + req["date"])
                        continue

                # 辞書に新しいデータを追加
                sdics[req["date"]][req["devid"]].append(json.dumps(req["data"]))

            # 作業用辞書の変更をStorageにアップロード
            for sdic in sdics:
                # 辞書型をJSONに変換
                sjson = json.dumps(sdic)

                # Storageにアップロード、成功したらタスクを消去
                try:
                    gcs.write_file(diary.keystr(date), sjson, "application/json")
                    q.delete_tasks(tasks)
                except:
                    pass

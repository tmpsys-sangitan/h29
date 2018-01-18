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

class diary:
    """ 日誌クラス
    """

    @staticmethod
    def keycache(date, devid):
        """ Memcacheキーの生成
        """
        return "data_" + date.strftime('%Y%m%d') + "_" + devid


    @staticmethod
    def keystr(date):
        """ Storageキーの生成
        """
        return "data_" + date.strftime('%Y%m%d') + ".json"


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
            # 日時 String型→Datatime型→String型で整形
            "date"  : date.strftime('%Y/%m/%d %H:%M:%S') + " +0900",
            "fi"    : int(fi),
            "bv"    : int(bv),
            "val"   : float(val),
            "ad"    : int(ad)
        }

        # 辞書に新たなデータを追加
        dic[devid].append(newdata)

        # 辞書をjsonに変換
        djson = json.dumps(dic)
        payload = json.dumps(newdata)

        # キャッシュ更新
        memcache.delete(diary.keycache(date, devid))
        memcache.add(diary.keycache(date, devid), djson)

        # Storage更新リクエスト送信
        q = taskqueue.Queue('StorageWriteRequestQueue')
        tasks = []
        tasks.append(taskqueue.Task(payload=payload, method='PULL', tag=devid))
        q.add(tasks)


    @staticmethod
    def write():
        """ 日誌への仮追加を確定し、Storageに書き込む
        """

        # タスクの取得
        q = taskqueue.Queue('StorageWriteRequestQueue')
        tasks = q.lease_tasks(60, 100)

        # タスクが空でないなら
        if tasks is not None:
            # StorageからJSONを読み込み
            sjson = gcs.read_file(diary.keystr(date))

            # jsonを辞書に変換
            dic = json.loads(sjson)

            # Taskを辞書に反映
            for task in tasks:
                dic[task.tag].append(json.dumps(task.payload))

            # 辞書をjsonに変換
            sjson = json.dumps(dic)

            # Storageにアップロード、成功したらタスクを消去
            try:
                gcs.write_file(diary.keystr(date), sjson, "application/json")
                q.delete_tasks(tasks)
            except:
                pass


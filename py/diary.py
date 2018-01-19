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

from py import gcs                               # GCS操作
from py import sensor                            # センサ管理
from py import utility                           # 汎用関数

class diary:
    """ 日誌クラス
    """

    @staticmethod
    def keycache(date, devid):
        """ Memcacheキーの生成
        """
        if isinstance(date, dt):
            return "data_" + utility.d2str(date) + "_" + devid
        else:
            return "data_" + date + "_" + devid


    @staticmethod
    def keystr(date):
        """ Storageキーの生成
        """
        if isinstance(date, dt):
            return "data_" + utility.d2str(date) + ".json"
        else:
            return "data_" + date + ".json"


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
        dic = utility.load_json(sjson)

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
        dic = utility.load_json(djson)

        # データの重複チェック
        timekey = utility.t2str(date)
        if timekey in dic[devid]:
            # 重複エラーで終了
            return

        # 新しいデータを辞書型に変換
        newdata = {
            utility.t2str(date): {
                "fi"    : int(fi),
                "bv"    : int(bv),
                "val"   : float(val),
                "ad"    : int(ad)
            }
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
            # 作業用リストを生成
            slist_date = []
            slist_dic = []

            # リクエストの消化
            for task in tasks:

                # リクエストを辞書型に変換
                req = utility.load_json(task.payload)

                # 辞書からJSONを読み込み
                if req["date"] is not slist_date:
                    # StorageからJSONを読み込み作業用辞書に追加
                    try:
                        sjson = gcs.read_file(diary.keystr(req["date"]))
                        sdic = utility.load_json(sjson)
                        slist_dic.append(sdic)
                        slist_date.append(req["date"])
                    except:
                        slist_dic.append(diary.new(req["date"], req["devid"]))
                        logging.info("DIARY WRITE : NEW " + task.name)
                    else:
                        logging.info("OPEN : " + diary.keystr(req["date"]))

                # 辞書に新しいデータを追加
                index = slist_date.index(req["date"])
                slist_dic[index][req["devid"]].append(req["data"])

            # 作業用辞書の変更をStorageにアップロード
            try:
                for (date, dic) in zip(slist_date, slist_dic):
                    # 辞書型をJSONに変換
                    sjson = json.dumps(dic)

                    # Storageにアップロード、成功したらタスクを消去
                    try:
                        gcs.write_file(diary.keystr(date), sjson, "application/json")
                        logging.info("DIARY WRITE : " + diary.keystr(date))
                    except:
                        pass
            except:
                logging.info(sjson)
            else:
                q.delete_tasks(tasks)

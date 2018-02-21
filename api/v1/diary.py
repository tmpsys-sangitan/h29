# coding: UTF-8
'''
FILE        :diary.py
DATE        :2018.01.17
DESCRIPTION :日誌管理モジュール
NAME        :Hikaru Yoshida
'''

from datetime import datetime as dt         # datatime型
from google.appengine.api import memcache   # Memcache API
from google.appengine.api import taskqueue  # TaskQueue API
import cloudstorage as storage              # GCS API
import logging                              # ログ出力

import model                        # GCS操作
import sensor                       # センサ管理
import utility                      # 汎用関数


class diary(model.Storage):

    @classmethod
    def add(cls, date, devid, data):
        """ 日誌に新たなデータを仮追加する
            @date  日付
            @devid 機器ID
            @data 保存するパラメータの辞書
        """

        # キャッシュから日誌データの読み込み
        diary_dic = cls.get(date, devid)

        # データの重複チェック
        timekey = utility.t2str(date)
        if timekey in diary_dic:
            # 重複エラーで終了
            return

        # 新しいデータを辞書に追加してjsonに変換
        new_time = utility.t2str(date)
        if devid not in diary_dic:
            diary_dic[devid] = {}
        diary_dic[devid][new_time] = data
        diary_json = utility.dump_json(diary_dic)

        # キャッシュ更新
        memcache.delete(diary.keycache(date, devid))
        memcache.add(diary.keycache(date, devid), diary_json)

        # 最新温度データ更新
        Latest.updateLatest(devid, data)

        # リクエストを作成
        payload = utility.dump_json({
            'devid' : devid,
            'date'  : utility.d2str(date),
            'time'  : new_time,
            'data'  : data
        })

        # Storage更新リクエスト送信
        queue = taskqueue.Queue('StorageWriteRequestQueue')
        tasks = []
        tasks.append(taskqueue.Task(payload=payload, method='PULL'))
        queue.add(tasks)

    @classmethod
    def get(cls, date, devid):
        res = cls.get_cache(date, devid)
        if res is None:
            logging.debug(cls.keycache(date, devid) + "MISS")
            try:
                cls.edit_storage(date)
                res = cls.get_cache(date, devid)
            except storage.errors.NotFoundError:
                logging.debug(cls.keystr(date) + "MISS")
        return res or {} # res、resがNoneなら空辞書を返す

    @classmethod
    def set_cache(cls, date, devid, data):
        memcache.add(cls.keycache(date, devid), utility.dump_json(data))

    @classmethod
    def get_cache(cls, date, devid):
        res = memcache.get(cls.keycache(date, devid))
        return utility.load_json(res, charset="ascii") if res is not None else None

    @classmethod
    def set_storage(cls, date, data):
        model.Storage.write_file(cls.keystr(date), utility.dump_json(data), "application/json")

    @classmethod
    def get_storage(cls, date):
        return model.Storage.read_file(cls.keystr(date))

    @classmethod
    def edit_storage(cls, date):
        # StorageからJSONを読み込み
        str_json = cls.get_storage(date)

        # jsonを辞書に変換
        dic = utility.load_json(str_json)

        # jsonを分解し、Memcacheへ保存
        for devid in sensor.get_list_devid():
            if devid in dic:
                cls.set_cache(date, devid, dic[devid])
            else:
                cls.set_cache(date, devid, {devid : {}})
            logging.debug("DIARY CACHE : WRITE %s", diary.keycache(date, devid))

    @staticmethod
    def keycache(date, devid):
        """ Memcacheキーの生成
        """
        if date is None:
            return "data_latest_" + devid
        elif isinstance(date, dt):
            return "data_" + utility.d2str(date) + "_" + devid
        return "data_" + date + "_" + devid

    @staticmethod
    def keystr(date):
        """ Storageキーの生成
        """
        if isinstance(date, dt):
            return "data_" + utility.d2str(date) + ".json"
        return "data_" + date + ".json"

    @staticmethod
    def new(date, devid):
        """
        日誌を新規作成
        """

        # 新規作成するjsonの雛形を作る
        dic = {
            devid : {}
        }

        # 辞書をjsonに変換
        njson = utility.dump_json(dic)

        # Storageにアップロード
        model.Storage.write_file(diary.keystr(date), njson, "application/json")

        return njson

    @staticmethod
    def write():
        """ 日誌への仮追加を確定し、Storageに書き込む
        """

        # タスクの取得
        queue = taskqueue.Queue('StorageWriteRequestQueue')
        tasks = queue.lease_tasks(60, 100)

        # タスクが空でないなら
        if bool(tasks):
            # 作業用リストを生成
            temp_dic = {}

            # リクエストの消化
            for task in tasks:
                # リクエストから各データ取り出し
                payload = utility.load_json(task.payload)
                date = payload['date']
                devid = payload['devid']
                time = payload['time']
                data = payload['data']

                # 作業用辞書に読込済みか確認
                if date not in temp_dic:
                    # 新しい辞書を作成
                    temp_dic[date] = {}
                    temp_dic[date]['task'] = []

                    # StorageからJSONを読み込み作業用辞書に追加
                    try:
                        gcs_json = model.Storage.read_file(diary.keystr(date))
                        gcs_dic = utility.load_json(gcs_json)
                        temp_dic[date]['json'] = gcs_dic
                        logging.info("OPEN : %s", diary.keystr(date))

                    # Storageに新たなJSONを作成し作業用
                    except storage.NotFoundError:
                        temp_dic[date]['json'] = {}
                        logging.info("DIARY WRITE : NEW %s", task.name)

                # taskの紐づけ
                temp_dic[date]['task'].append(task)

                # 辞書確認、なければ追加
                if devid not in temp_dic[date]['json']:
                    temp_dic[date]['json'][devid] = {}

                # 辞書に新しいデータを追加
                temp_dic[date]['json'][devid][time] = data

            # 作業用辞書の変更をStorageにアップロード
            for (date, dic) in temp_dic.items():
                # 辞書型をJSONに変換
                gcs_json = utility.dump_json(dic['json'])

                # Storageにアップロード
                try:
                    model.Storage.write_file(diary.keystr(date), gcs_json, "application/json")
                    logging.info("DIARY WRITE : %s", diary.keystr(date))

                # エラーログ
                except storage.ServerError as error:
                    logging.warning("DIARY WRITE : ERROR %s", error)

                # 成功した場合のみタスクを消去
                else:
                    queue.delete_tasks(dic['task'])




class Latest(model.Cache):

    def __init__(self, kind):
        self.kind = kind

    def get_cache_name(self):
        """ Memcacheでのキー名
        """
        return "data_latest_" + self.kind

    def add(self, devid, val):
        latests = self.get()
        latests[sensor.get_mapid(devid)] = val
        self.set(latests)

    @staticmethod
    def updateLatest(devid, datas):
        for data in datas.items():
            Latest(data[0]).add(devid, data[1])
